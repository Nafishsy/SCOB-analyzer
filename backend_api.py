"""
FastAPI Backend for SCOB Legal Document RAG System
Handles PDF uploads, document ingestion, and query processing
"""

import sys
from pathlib import Path
import os
import shutil
from typing import List, Optional
from datetime import datetime

# Add src and config directories to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "config"))

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import uuid

from weaviate_manager import WeaviateManager
from pdf_processor import PDFProcessor
from metadata_extractor import LegalMetadataExtractor
import rag_config as config
from openai import OpenAI
from chatbot import Chatbot, ChatbotConfig, ChatSession, Message

# Initialize FastAPI app
app = FastAPI(
    title="SCOB Legal Document RAG API",
    description="API for uploading PDFs and querying legal documents",
    version="1.0.0"
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class QueryRequest(BaseModel):
    question: str
    num_results: int = 5
    use_ai_answer: bool = False

class QueryResponse(BaseModel):
    question: str
    results: List[dict]
    ai_answer: Optional[str] = None
    total_results: int
    source_citations: List[dict] = []

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    num_results: int = 5

class ChatResponse(BaseModel):
    response: str
    sources: List[dict] = []
    chat_history: List[ChatMessage] = []

class QARequest(BaseModel):
    """Request for Question-Answer endpoint"""
    question: str
    session_id: Optional[str] = None
    num_results: int = 5

class QAResponse(BaseModel):
    """Response for Question-Answer endpoint"""
    session_id: str
    question: str
    answer: str
    sources: List[dict] = []
    confidence: float = 0.0

class SessionCreateRequest(BaseModel):
    """Request to create a new session"""
    title: str = "New Chat"

class SessionResponse(BaseModel):
    """Response for session operations"""
    session_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0
    question_count: int = 0

class SessionListResponse(BaseModel):
    """Response for listing sessions"""
    sessions: List[dict]
    total: int

class SessionHistoryResponse(BaseModel):
    """Response for session conversation history"""
    session_id: str
    title: str
    messages: List[dict]
    metadata: dict

class UploadResponse(BaseModel):
    filename: str
    status: str
    message: str
    chunks_added: int = 0

class SystemStatus(BaseModel):
    status: str
    weaviate_connected: bool
    total_documents: int
    total_chunks: int

# Global instances
weaviate_manager = None
pdf_processor = None
metadata_extractor = None
openai_client = None
chatbot = None

# Initialize directories
DATA_DIR = Path(config.PDF_BASE_DIR).parent.parent / "uploads"
DATA_DIR.mkdir(parents=True, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    global weaviate_manager, pdf_processor, metadata_extractor, openai_client, chatbot

    print("Initializing SCOB RAG API...")

    # Initialize managers
    weaviate_manager = WeaviateManager()
    pdf_processor = PDFProcessor("")
    metadata_extractor = LegalMetadataExtractor()

    if config.OPENAI_API_KEY:
        openai_client = OpenAI(api_key=config.OPENAI_API_KEY)

    # Initialize chatbot
    chatbot_config = ChatbotConfig(
        max_context_messages=10,
        temperature=0.3,
        max_tokens=500,
        top_k_results=5,
        enable_source_citations=True
    )
    chatbot = Chatbot(config=chatbot_config)

    # Connect to Weaviate
    if not weaviate_manager.connect():
        print("WARNING: Could not connect to Weaviate on startup")
        print("Make sure Weaviate is running: docker-compose up -d")
    else:
        print("✓ Weaviate connected successfully")
        print("✓ Chatbot initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    if weaviate_manager:
        weaviate_manager.close()
        print("Connections closed")

@app.get("/health", tags=["System"])
async def health_check():
    """Check API health status"""
    return {
        "status": "healthy",
        "service": "SCOB RAG API",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status", tags=["System"])
async def get_status() -> SystemStatus:
    """Get system status including Weaviate connection"""
    try:
        # Check if Weaviate is connected
        weaviate_connected = weaviate_manager.client is not None

        # Try to get collection stats
        total_chunks = 0
        total_documents = 0
        if weaviate_connected:
            try:
                collection = weaviate_manager.client.collections.get(config.COLLECTION_NAME)
                total_chunks = collection.data.count()
                # Estimate documents (rough calculation)
                total_documents = max(1, total_chunks // 50)  # Assuming ~50 chunks per document
            except:
                pass

        return SystemStatus(
            status="ready" if weaviate_connected else "disconnected",
            weaviate_connected=weaviate_connected,
            total_documents=total_documents,
            total_chunks=total_chunks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", tags=["Documents"], response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Upload a PDF file and ingest it into the RAG system

    The PDF will be processed, chunked, and stored in Weaviate
    """
    try:
        if not weaviate_manager or not weaviate_manager.client:
            raise HTTPException(
                status_code=503,
                detail="Weaviate not connected. Make sure it's running."
            )

        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Save uploaded file
        file_path = DATA_DIR / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)

        print(f"Processing uploaded PDF: {file.filename}")

        # Extract text from PDF
        try:
            text = pdf_processor.extract_text_from_pdf(str(file_path))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")

        if not text.strip():
            raise HTTPException(status_code=400, detail="PDF contains no extractable text")

        # Prepare document for ingestion
        document = {
            'filename': file.filename,
            'filepath': str(file_path),
            'text': text,
            'source': 'User Upload',
            'year': datetime.now().year
        }

        # Ingest into Weaviate
        chunks_added = await ingest_document(document)

        return UploadResponse(
            filename=file.filename,
            status="success",
            message=f"Successfully uploaded and processed {file.filename}",
            chunks_added=chunks_added
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def ingest_document(document: dict) -> int:
    """Ingest a single document into Weaviate with batch processing"""
    import time
    try:
        start_time = time.time()

        # Extract metadata
        print(f"🔄 Extracting metadata from {document['filename']}...")
        doc_metadata = metadata_extractor.extract_all_metadata(
            document['text'],
            document['filename']
        )

        # Chunk the document
        print(f"🔄 Chunking text...")
        chunks = pdf_processor.chunk_text(
            document['text'],
            config.CHUNK_SIZE,
            config.CHUNK_OVERLAP,
            config.MIN_CHUNK_SIZE
        )

        print(f"📊 Created {len(chunks)} chunks from {document['filename']}")

        # Get or create collection
        if not weaviate_manager.collection:
            weaviate_manager.collection = weaviate_manager.client.collections.get(config.COLLECTION_NAME)

        # Process chunks in batches for better performance
        total_added = 0
        batch_size = 25  # Smaller batch for embeddings

        for batch_start in range(0, len(chunks), batch_size):
            batch_end = min(batch_start + batch_size, len(chunks))
            batch_chunks = chunks[batch_start:batch_end]

            # Filter empty chunks
            valid_chunks = [(idx, chunk) for idx, chunk in enumerate(batch_chunks, start=batch_start)
                          if chunk.strip()]

            if not valid_chunks:
                continue

            print(f"🧠 Generating embeddings for chunks {batch_start+1}-{batch_end}...")
            embed_start = time.time()

            # Generate embeddings in batch
            vectors = []
            for actual_idx, chunk in valid_chunks:
                try:
                    vector = weaviate_manager.generate_embedding(chunk)
                    vectors.append((actual_idx, chunk, vector))
                except Exception as e:
                    print(f"⚠️ Error generating embedding for chunk {actual_idx}: {e}")
                    continue

            embed_time = time.time() - embed_start
            print(f"⏱️ Embedded {len(vectors)} chunks in {embed_time:.2f}s")

            # Batch insert all vectors
            if vectors:
                print(f"📤 Indexing {len(vectors)} chunks in Weaviate...")
                insert_start = time.time()

                # Insert objects without batch context manager (simpler approach)
                for actual_idx, chunk, vector in vectors:
                    data_object = {
                        "text": chunk,
                        "filename": document['filename'],
                        "filepath": document['filepath'],
                        "source": document['source'],
                        "year": str(document['year']),
                        "chunk_index": actual_idx,
                        "case_name": doc_metadata.get('case_name') or "",
                        "case_number": doc_metadata.get('case_number') or "",
                        "court": doc_metadata.get('court') or "",
                        "judges": doc_metadata.get('judges') or [],
                        "judgment_date": doc_metadata.get('judgment_date') or "",
                        "citations": doc_metadata.get('citations') or [],
                        "subject_matter": doc_metadata.get('subject_matter') or [],
                    }

                    weaviate_manager.collection.data.insert(
                        properties=data_object,
                        vector=vector
                    )

                insert_time = time.time() - insert_start
                total_added += len(vectors)
                print(f"✅ Indexed batch in {insert_time:.2f}s ({len(vectors)} chunks)")

        total_time = time.time() - start_time
        print(f"🎉 Completed: Added {total_added} chunks in {total_time:.2f}s")
        print(f"⚡ Average time per chunk: {(total_time/max(total_added, 1)):.3f}s")

        return total_added

    except Exception as e:
        print(f"Error ingesting document: {e}")
        raise

@app.post("/query", tags=["Search"], response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the RAG system for relevant legal documents

    - **question**: The search query
    - **num_results**: Number of relevant chunks to retrieve (default: 5)
    - **use_ai_answer**: If true, generate an AI-powered answer using OpenAI
    """
    try:
        if not weaviate_manager or not weaviate_manager.client:
            raise HTTPException(
                status_code=503,
                detail="Weaviate not connected"
            )

        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        # Search Weaviate
        results = weaviate_manager.search(request.question, limit=request.num_results)

        # Format results
        formatted_results = []
        source_citations = []

        for idx, result in enumerate(results):
            formatted_result = {
                "text": result['text'],
                "filename": result['filename'],
                "source": result['source'],
                "year": result['year'],
                "chunk_index": result['chunk_index'],
                "relevance_score": 1 - result['distance'],  # Convert distance to similarity
                "case_name": result.get('case_name', ''),
                "case_number": result.get('case_number', ''),
                "court": result.get('court', ''),
                "judges": result.get('judges', []),
                "judgment_date": result.get('judgment_date', ''),
                "citations": result.get('citations', []),
                "subject_matter": result.get('subject_matter', []),
            }
            formatted_results.append(formatted_result)

            # Create source citation with location info
            source_citations.append({
                "id": idx + 1,
                "filename": result['filename'],
                "filepath": result['filepath'],
                "chunk_index": result['chunk_index'],
                "case_name": result.get('case_name', ''),
                "relevance_score": formatted_result["relevance_score"],
                "source_location": f"{result['filename']}:chunk_{result['chunk_index']}"
            })

        # Generate AI answer if requested
        ai_answer = None
        if request.use_ai_answer and openai_client and formatted_results:
            ai_answer = generate_answer(request.question, formatted_results)

        return QueryResponse(
            question=request.question,
            results=formatted_results,
            ai_answer=ai_answer,
            total_results=len(formatted_results),
            source_citations=source_citations
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

def generate_answer(question: str, results: List[dict]) -> str:
    """Generate an AI answer using OpenAI with RAG context, including source citations"""
    try:
        # Combine context from top chunks with source information
        context_parts = []
        for idx, r in enumerate(results[:3], 1):
            source_location = f"{r.get('filename', 'Unknown')}:chunk_{r.get('chunk_index', 0)}"
            context_parts.append(f"[Source {idx}: {source_location}]\n{r['text']}")

        context = "\n\n".join(context_parts)

        system_prompt = """You are a legal expert assistant specializing in Bangladesh law.
Answer questions based ONLY on the provided legal document context.
If the context doesn't contain relevant information, say so clearly.
Cite specific sections, case names, or legal provisions when applicable.
Reference the source citations [Source X: filename:chunk_number] when providing information."""

        user_prompt = f"""Context from legal documents:
{context}

Question: {question}

Please provide a clear, concise answer based on the context above.
Include source citations in your response using the format: [Source X: filename:chunk_number]"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating answer: {str(e)}"

@app.get("/documents", tags=["Documents"])
async def list_documents():
    """List all uploaded documents"""
    try:
        documents = []
        if DATA_DIR.exists():
            for pdf_file in DATA_DIR.glob("*.pdf"):
                documents.append({
                    "filename": pdf_file.name,
                    "size_bytes": pdf_file.stat().st_size,
                    "uploaded_at": datetime.fromtimestamp(pdf_file.stat().st_mtime).isoformat()
                })

        return {"documents": documents, "total": len(documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{filename}", tags=["Documents"])
async def delete_document(filename: str):
    """Delete an uploaded document and remove all its chunks from Weaviate"""
    try:
        file_path = DATA_DIR / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete chunks from Weaviate first
        if weaviate_manager and weaviate_manager.client:
            deletion_success = weaviate_manager.delete_by_filename(filename)
            if not deletion_success:
                print(f"Warning: Failed to delete chunks for {filename} from Weaviate")

        # Delete file from disk
        file_path.unlink()

        return {"status": "success", "message": f"Deleted {filename} and its chunks from database"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cleanup-orphaned-chunks", tags=["Documents"])
async def cleanup_orphaned_chunks():
    """
    Remove chunks from Weaviate that correspond to deleted documents
    This fixes the issue where deleted documents still have chunks in the vector database
    """
    try:
        if not weaviate_manager or not weaviate_manager.client:
            raise HTTPException(status_code=500, detail="Weaviate connection not available")

        # Get list of files currently on disk
        disk_files = [f.name for f in DATA_DIR.glob("*.pdf")]

        # Run cleanup
        result = weaviate_manager.cleanup_orphaned_chunks(disk_files)

        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Cleaned up {result['chunks_deleted']} orphaned chunks",
                "orphaned_files": result["orphaned_files"],
                "chunks_deleted": result["chunks_deleted"]
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", tags=["Chat"], response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Multi-turn chat endpoint for conversational document queries

    Supports continuous conversation with source citations for each response
    - **messages**: Array of chat messages with role and content
    - **num_results**: Number of relevant chunks to retrieve per query
    """
    try:
        if not weaviate_manager or not weaviate_manager.client:
            raise HTTPException(
                status_code=503,
                detail="Weaviate not connected"
            )

        if not request.messages or len(request.messages) == 0:
            raise HTTPException(status_code=400, detail="No messages provided")

        # Get the last user message
        last_message = None
        for msg in reversed(request.messages):
            if msg.role.lower() == "user":
                last_message = msg.content
                break

        if not last_message or not last_message.strip():
            raise HTTPException(status_code=400, detail="No user message found")

        # Search for relevant documents
        search_results = weaviate_manager.search(last_message, limit=request.num_results)

        # Format search results with citations
        formatted_results = []
        sources = []

        for idx, result in enumerate(search_results):
            formatted_result = {
                "text": result['text'],
                "filename": result['filename'],
                "source": result['source'],
                "year": result['year'],
                "chunk_index": result['chunk_index'],
                "relevance_score": 1 - result['distance'],
                "case_name": result.get('case_name', ''),
                "case_number": result.get('case_number', ''),
                "court": result.get('court', ''),
                "judges": result.get('judges', []),
                "judgment_date": result.get('judgment_date', ''),
                "citations": result.get('citations', []),
                "subject_matter": result.get('subject_matter', []),
            }
            formatted_results.append(formatted_result)

            # Create source citation
            sources.append({
                "id": idx + 1,
                "filename": result['filename'],
                "filepath": result['filepath'],
                "chunk_index": result['chunk_index'],
                "case_name": result.get('case_name', ''),
                "relevance_score": formatted_result["relevance_score"],
                "source_location": f"{result['filename']}:chunk_{result['chunk_index']}"
            })

        # Generate AI response using conversation history
        ai_response = None
        if openai_client and formatted_results:
            ai_response = generate_chat_answer(request.messages, formatted_results)

        # Build chat history response
        chat_history = [
            ChatMessage(role=msg.role, content=msg.content)
            for msg in request.messages
        ]
        # Add the assistant's new response
        if ai_response:
            chat_history.append(ChatMessage(role="assistant", content=ai_response))

        return ChatResponse(
            response=ai_response or "No response generated",
            sources=sources,
            chat_history=chat_history
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

def generate_chat_answer(messages: List[ChatMessage], results: List[dict]) -> str:
    """Generate an AI answer for chat using conversation history and RAG context"""
    try:
        # Combine context from top chunks with source information
        context_parts = []
        for idx, r in enumerate(results[:3], 1):
            source_location = f"{r.get('filename', 'Unknown')}:chunk_{r.get('chunk_index', 0)}"
            context_parts.append(f"[Source {idx}: {source_location}]\n{r['text']}")

        context = "\n\n".join(context_parts)

        system_prompt = """You are a legal expert assistant specializing in Bangladesh law.
You are having a conversation with a user about legal documents.
Answer questions based ONLY on the provided legal document context.
If the context doesn't contain relevant information, say so clearly.
Cite specific sections, case names, or legal provisions when applicable.
Reference the source citations [Source X: filename:chunk_number] when providing information.
Keep responses concise and conversational."""

        # Build messages for chat completion, excluding non-user/assistant messages
        chat_messages = []
        for msg in messages:
            if msg.role.lower() in ["user", "assistant"]:
                chat_messages.append({
                    "role": msg.role.lower(),
                    "content": msg.content
                })

        # Add the context for the current query
        last_user_msg = None
        for msg in reversed(messages):
            if msg.role.lower() == "user":
                last_user_msg = msg.content
                break

        # Modify the last user message to include context
        if chat_messages and chat_messages[-1]["role"] == "user":
            chat_messages[-1]["content"] = f"""{chat_messages[-1]["content"]}

[Document Context]:
{context}"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                *chat_messages
            ],
            temperature=0.3,
            max_tokens=500
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

# ==================== CHATBOT ENDPOINTS ====================

@app.post("/qa", tags=["Chatbot"], response_model=QAResponse)
async def question_answer(request: QARequest):
    """
    Question-Answer endpoint with session management

    - **question**: The user's question about legal documents
    - **session_id**: Optional session ID for conversation context. If not provided, a new session is created
    - **num_results**: Number of relevant chunks to retrieve (default: 5)
    """
    try:
        if not weaviate_manager or not weaviate_manager.client:
            raise HTTPException(status_code=503, detail="Weaviate not connected")

        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        # Create or load session
        session_id = request.session_id or str(uuid.uuid4())
        session = chatbot.load_session(session_id)
        if not session:
            session = chatbot.start_new_session(session_id, "Legal Q&A")

        # Add user question to session
        chatbot.add_user_message(request.question)

        # Search for relevant documents
        search_results = weaviate_manager.search(request.question, limit=request.num_results)

        # Format results with citations
        formatted_results = []
        sources = []

        for idx, result in enumerate(search_results):
            formatted_result = {
                "text": result['text'],
                "filename": result['filename'],
                "source": result['source'],
                "year": result['year'],
                "chunk_index": result['chunk_index'],
                "relevance_score": 1 - result['distance'],
                "case_name": result.get('case_name', ''),
                "case_number": result.get('case_number', ''),
                "court": result.get('court', ''),
                "judges": result.get('judges', []),
                "judgment_date": result.get('judgment_date', ''),
                "citations": result.get('citations', []),
                "subject_matter": result.get('subject_matter', []),
            }
            formatted_results.append(formatted_result)

            sources.append({
                "id": idx + 1,
                "filename": result['filename'],
                "filepath": result['filepath'],
                "chunk_index": result['chunk_index'],
                "case_name": result.get('case_name', ''),
                "relevance_score": formatted_result["relevance_score"],
                "source_location": f"{result['filename']}:chunk_{result['chunk_index']}"
            })

        # Generate AI answer
        ai_answer = None
        confidence = 0.0
        if openai_client and formatted_results:
            ai_answer = generate_qa_answer(request.question, formatted_results)
            # Calculate confidence based on relevance scores
            confidence = sum(r['relevance_score'] for r in sources) / len(sources) if sources else 0.0

        # Add assistant response to session
        if ai_answer:
            chatbot.add_assistant_response(ai_answer, sources)

        return QAResponse(
            session_id=session_id,
            question=request.question,
            answer=ai_answer or "Unable to generate answer from available documents",
            sources=sources,
            confidence=round(confidence, 2)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QA failed: {str(e)}")

@app.post("/sessions", tags=["Sessions"], response_model=SessionResponse)
async def create_session(request: SessionCreateRequest):
    """Create a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        session = chatbot.start_new_session(session_id, request.title)

        return SessionResponse(
            session_id=session.session_id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=0,
            question_count=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session creation failed: {str(e)}")

@app.get("/sessions", tags=["Sessions"], response_model=SessionListResponse)
async def list_sessions():
    """List all chat sessions"""
    try:
        sessions = chatbot.session_manager.list_sessions()
        return SessionListResponse(
            sessions=sessions,
            total=len(sessions)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@app.get("/sessions/{session_id}", tags=["Sessions"], response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    """Get conversation history for a specific session"""
    try:
        session = chatbot.session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionHistoryResponse(
            session_id=session.session_id,
            title=session.title,
            messages=session.get_conversation_history(),
            metadata=session.metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@app.delete("/sessions/{session_id}", tags=["Sessions"])
async def delete_session(session_id: str):
    """Delete a chat session"""
    try:
        if chatbot.session_manager.delete_session(session_id):
            return {
                "status": "success",
                "message": f"Session {session_id} deleted"
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@app.get("/sessions/{session_id}/summary", tags=["Sessions"])
async def get_session_summary(session_id: str):
    """Get a summary of a session"""
    try:
        session = chatbot.session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session.session_id,
            "title": session.title,
            "message_count": len(session.messages),
            "question_count": session.metadata.get("question_count", 0),
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "last_message": session.messages[-1].content if session.messages else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

def generate_qa_answer(question: str, results: List[dict]) -> str:
    """Generate a focused Q&A answer from search results"""
    try:
        # Combine context from top chunks with source information
        context_parts = []
        for idx, r in enumerate(results[:3], 1):
            source_location = f"{r.get('filename', 'Unknown')}:chunk_{r.get('chunk_index', 0)}"
            context_parts.append(f"[Source {idx}: {source_location}]\n{r['text']}")

        context = "\n\n".join(context_parts)

        system_prompt = """You are an expert legal assistant specializing in Bangladesh law.
Provide clear, accurate, and concise answers to legal questions.
Base your answer ONLY on the provided legal document context.
If the context doesn't contain relevant information, state that clearly.
Always cite specific sections, case names, and legal provisions.
Format source citations as [Source X: filename:chunk_number]."""

        user_prompt = f"""Based on the following legal document excerpts, answer this question:

Question: {question}

Document Context:
{context}

Please provide a direct, concise answer that:
1. Directly addresses the question
2. Cites relevant sources
3. Includes specific legal references when applicable
4. Is written in clear, professional language"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating answer: {str(e)}"

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "backend_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

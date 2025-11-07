# Legal Document RAG System - SCOB

A Retrieval-Augmented Generation (RAG) system for searching and querying legal documents from SCOB (Supreme Court of Bangladesh) law reports using Weaviate vector database.

## Overview

This system implements a complete RAG pipeline that:
1. Extracts text from PDF legal documents
2. Chunks documents into manageable pieces
3. Generates embeddings using sentence-transformers
4. Stores embeddings in Weaviate vector database
5. Enables semantic search over the documents

## Architecture

```
PDFs → Text Extraction → Chunking → Embeddings → Weaviate → Search Interface
```

## Directory Structure

```
SCOB_RAG/
├── src/                       # Source code
│   ├── pdf_processor.py      # PDF text extraction and chunking
│   └── weaviate_manager.py   # Weaviate database operations
├── config/                    # Configuration files
│   └── rag_config.py         # System configuration
├── docs/                      # Documentation
│   ├── README.md             # This file
│   └── QUICKSTART.md         # Quick start guide
├── ingest_documents.py        # Data ingestion script
├── rag_query.py              # Query interface
├── requirements.txt           # Python dependencies
└── docker-compose.yml         # Weaviate setup
```

## Quick Start

### 1. Install Dependencies

```bash
cd SCOB_RAG
pip install -r requirements.txt
```

### 2. Start Weaviate

```bash
docker-compose up -d
```

Verify Weaviate is running:
```bash
curl http://localhost:8080/v1/meta
```

### 3. Ingest Documents

```bash
python ingest_documents.py
```

This will:
- Extract text from all PDFs in `../Data/PDF/SCOB/2015/`
- Split documents into chunks (1000 chars with 200 char overlap)
- Generate embeddings using `all-MiniLM-L6-v2` model
- Store in Weaviate vector database

### 4. Query the System

Interactive mode:
```bash
python rag_query.py
```

Single query:
```bash
python rag_query.py "What are the key principles of contract law?"
```

## Example Queries

- "What is the judgment regarding property disputes?"
- "Find cases related to criminal negligence"
- "What are the precedents for land acquisition?"
- "Show me cases about constitutional rights"

## Configuration

Edit `config/rag_config.py` to customize:

- `PDF_BASE_DIR` - Directory containing PDFs
- `CHUNK_SIZE` - Size of text chunks (default: 1000)
- `CHUNK_OVERLAP` - Overlap between chunks (default: 200)
- `EMBEDDING_MODEL` - Model for generating embeddings
- `WEAVIATE_URL` - Weaviate instance URL

## How It Works

### 1. Document Processing
- PDFs are read using `pypdf`
- Text is extracted page by page
- Documents are split into overlapping chunks for better context retention

### 2. Embedding Generation
- Uses `sentence-transformers/all-MiniLM-L6-v2` (local, no API key needed)
- Generates 384-dimensional embeddings
- Fast and accurate for semantic search

### 3. Vector Storage
- Weaviate stores document chunks with metadata
- Each chunk includes: text, filename, source, year, chunk index
- Vector similarity search enables semantic retrieval

### 4. Query Processing
- User query is converted to embedding
- Weaviate finds most similar document chunks
- Results ranked by cosine similarity
- Top results returned with context

## Extending the System

### Add More Document Sources

Edit `config/rag_config.py`:

```python
PDF_BASE_DIR = str(PROJECT_ROOT / "Data" / "PDF" / "SCOB" / "2016")
```

Or process multiple years by modifying `ingest_documents.py`.

### Use Different Embedding Models

```python
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

### Integrate with LLM for Answer Generation

Add to `rag_query.py`:

```python
from openai import OpenAI

def generate_answer(context, question):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a legal expert. Answer based on the context."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content
```

## Troubleshooting

### Weaviate Connection Failed
- Ensure Docker is running: `docker ps`
- Check Weaviate logs: `docker logs scob_rag_weaviate_1`
- Verify port 8080 is available

### PDF Text Extraction Issues
- Some scanned PDFs may need OCR
- Consider using `pytesseract` for image-based PDFs

### Memory Issues
- Reduce `CHUNK_SIZE` for smaller chunks
- Process PDFs in batches

## Next Steps for Production

1. **Add OCR Support** - For scanned PDFs
2. **Implement LLM Integration** - GPT-4, Claude, or local models
3. **Add Metadata Filtering** - Filter by year, court, case type
4. **Improve Chunking** - Legal document-aware splitting
5. **Add Citation Extraction** - Extract and link case citations
6. **Build Web Interface** - Flask/FastAPI + React frontend
7. **Add Authentication** - Secure access control
8. **Implement Caching** - Redis for frequently accessed queries
9. **Add Monitoring** - Track usage, performance metrics

## Maintenance

### Stop Weaviate
```bash
docker-compose down
```

### Clear All Data
```bash
docker-compose down -v
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

## License

This is a proof of concept for educational purposes.

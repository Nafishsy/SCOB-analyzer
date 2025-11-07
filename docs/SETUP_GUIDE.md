# SCOB Legal RAG System - Complete Setup Guide

This guide walks you through setting up the complete SCOB Legal RAG system with a React frontend and FastAPI backend.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Running the System](#running-the-system)
5. [Using the Application](#using-the-application)
6. [Troubleshooting](#troubleshooting)
7. [API Documentation](#api-documentation)

## Prerequisites

### System Requirements

- Python 3.9 or higher
- Node.js 16 or higher
- Docker and Docker Compose (for Weaviate)
- OpenAI API key (for AI answer generation)

### Environment Variables

Create a `.env` file in the `SCOB_RAG` directory:

```bash
cd /Users/periscopelabs/RagOnBLD/SCOB_RAG
cat > .env << 'EOF'
OPENAI_API_KEY=your-openai-api-key-here
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=
EOF
```

Replace `your-openai-api-key-here` with your actual OpenAI API key.

## Backend Setup

### 1. Install Dependencies

```bash
cd /Users/periscopelabs/RagOnBLD/SCOB_RAG
pip install -r requirements.txt
```

### 2. Start Weaviate (Vector Database)

The system uses Weaviate for vector storage. Make sure Docker is running, then:

```bash
# From SCOB_RAG directory
docker-compose up -d
```

Verify Weaviate is running:
```bash
curl http://localhost:8080/v1/meta
```

### 3. Run the Backend API Server

```bash
python backend_api.py
```

The API server will start on `http://localhost:8000`

Check the API is working:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "SCOB RAG API",
  "timestamp": "2024-..."
}
```

### Backend API Endpoints

- **POST** `/upload` - Upload a PDF file
- **POST** `/query` - Query the RAG system
- **GET** `/health` - Check API health
- **GET** `/status` - Get system status
- **GET** `/documents` - List uploaded documents
- **DELETE** `/documents/{filename}` - Delete a document

## Frontend Setup

### 1. Install Dependencies

```bash
cd /Users/periscopelabs/RagOnBLD/SCOB_RAG/frontend
npm install
```

### 2. Configure API URL (Optional)

By default, the frontend connects to `http://localhost:8000`. To change this:

```bash
# Create .env file in frontend directory
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

### 3. Start the Frontend Development Server

```bash
npm start
```

The frontend will open automatically at `http://localhost:3000`

## Running the System

### Quick Start (All Components)

Open 3 terminals and run:

**Terminal 1 - Weaviate:**
```bash
cd /Users/periscopelabs/RagOnBLD/SCOB_RAG
docker-compose up -d
```

**Terminal 2 - Backend API:**
```bash
cd /Users/periscopelabs/RagOnBLD/SCOB_RAG
python backend_api.py
```

**Terminal 3 - Frontend:**
```bash
cd /Users/periscopelabs/RagOnBLD/SCOB_RAG/frontend
npm start
```

Wait a few seconds, then open http://localhost:3000 in your browser.

### Checking Component Status

```bash
# Check Weaviate
curl http://localhost:8080/v1/meta

# Check API
curl http://localhost:8000/health

# Frontend runs on localhost:3000
```

## Using the Application

### Page 1: Search (Home Page)

1. **Ask a Question**: Enter any legal question
2. **Configure Search**:
   - Toggle "Generate AI Answer" to get AI-powered summaries
   - Select number of results to retrieve (3, 5, 10, or 15)
3. **View Results**: Click on results to expand and see full metadata

### Page 2: Upload

1. **Upload PDF**: Drag and drop or browse for PDF files
2. **Wait for Processing**: The file will be:
   - Extracted for text
   - Split into chunks
   - Analyzed for legal metadata
   - Added to the vector database
3. **Confirmation**: You'll see the number of chunks added

### Page 3: Documents

1. **View All Documents**: See all uploaded PDFs
2. **Document Details**: File size and upload date
3. **Manage Documents**: Delete documents if needed

## Troubleshooting

### Weaviate Connection Issues

**Problem**: "Failed to connect to Weaviate"

**Solutions**:
```bash
# Check if Weaviate container is running
docker ps | grep weaviate

# Start Weaviate
docker-compose up -d

# Check Weaviate is healthy
curl http://localhost:8080/v1/meta

# View Weaviate logs
docker-compose logs -f
```

### Backend API Issues

**Problem**: "API server is not responding"

**Solutions**:
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill any existing process on port 8000
kill -9 <PID>

# Restart backend
python backend_api.py
```

### Frontend Connection Issues

**Problem**: "Cannot connect to API server"

**Solutions**:
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS settings in backend_api.py
# The frontend URL should be in allow_origins

# Clear browser cache
# Then refresh page
```

### PDF Upload Fails

**Problem**: "Failed to extract text from PDF"

**Solutions**:
- Ensure the PDF is not corrupted
- Try a different PDF file
- Check that the file is actually a PDF

### No Search Results

**Problem**: "No relevant documents found"

**Solutions**:
1. Upload documents first (go to Upload page)
2. Ensure documents are in SCOB/data directory
3. Check that documents have extractable text
4. Try simpler search queries

## API Documentation

### Upload PDF

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@yourfile.pdf"
```

**Response**:
```json
{
  "filename": "yourfile.pdf",
  "status": "success",
  "message": "Successfully uploaded and processed yourfile.pdf",
  "chunks_added": 25
}
```

### Query Documents

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the penalties for theft?",
    "num_results": 5,
    "use_ai_answer": true
  }'
```

**Response**:
```json
{
  "question": "What are the penalties for theft?",
  "results": [
    {
      "text": "...",
      "filename": "example.pdf",
      "relevance_score": 0.89,
      "case_name": "Case v. State",
      "citations": ["2020 SCR 123"]
    }
  ],
  "ai_answer": "According to the legal documents...",
  "total_results": 5
}
```

### Get System Status

```bash
curl http://localhost:8000/status
```

**Response**:
```json
{
  "status": "ready",
  "weaviate_connected": true,
  "total_documents": 3,
  "total_chunks": 150
}
```

### List Documents

```bash
curl http://localhost:8000/documents
```

**Response**:
```json
{
  "documents": [
    {
      "filename": "document.pdf",
      "size_bytes": 1024000,
      "uploaded_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 1
}
```

### Delete Document

```bash
curl -X DELETE http://localhost:8000/documents/filename.pdf
```

## Project Structure

```
SCOB_RAG/
├── backend_api.py           # FastAPI backend server
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Weaviate configuration
├── config/
│   └── rag_config.py       # Configuration settings
├── src/
│   ├── weaviate_manager.py
│   ├── pdf_processor.py
│   └── metadata_extractor.py
├── frontend/               # React frontend
│   ├── package.json
│   ├── public/
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── api.js         # API client
│   │   ├── index.js
│   │   ├── components/
│   │   │   └── Header.js
│   │   └── pages/
│   │       ├── Search.js
│   │       ├── Upload.js
│   │       └── Documents.js
│   └── .env               # Frontend environment variables
└── SETUP_GUIDE.md        # This file
```

## Performance Notes

- **Embedding Generation**: ~0.5-2 seconds per chunk (using OpenAI)
- **Search**: ~1-2 seconds per query
- **AI Answer Generation**: ~3-5 seconds (if enabled)
- **File Upload**: Depends on PDF size

## Security Considerations

- Keep your OpenAI API key secure (in .env file)
- The frontend allows all origins by default (change in production)
- API has no authentication (add if needed for production)
- Uploaded PDFs are stored in `SCOB/data/uploads`

## Next Steps

1. Upload your first PDF document
2. Try searching for legal concepts
3. Enable AI answer generation for better summaries
4. Explore the metadata extraction features

## Support

For issues:
1. Check the Troubleshooting section above
2. Verify all components are running
3. Check the server logs for error messages
4. Ensure your OpenAI API key is valid

## Advanced Configuration

### Change Chunk Size

Edit `config/rag_config.py`:
```python
CHUNK_SIZE = 2000  # Increase for larger chunks
CHUNK_OVERLAP = 400
```

### Change Backend Port

Edit `backend_api.py`:
```python
uvicorn.run(
    "backend_api:app",
    host="0.0.0.0",
    port=8001,  # Change port here
    reload=True,
)
```

Update frontend `.env`:
```
REACT_APP_API_URL=http://localhost:8001
```

### Change Frontend Port

```bash
PORT=3001 npm start
```

---

**Last Updated**: 2024
**Version**: 1.0.0

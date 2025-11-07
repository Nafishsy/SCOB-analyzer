# SCOB Legal RAG System - React Frontend & API

A complete web application for searching and managing legal documents using a RAG (Retrieval-Augmented Generation) system.

## 🎯 What You Can Do

- **Upload PDFs** - Add legal documents to your knowledge base
- **Search Intelligently** - Ask natural language questions about law
- **Get AI Answers** - Optionally receive AI-generated summaries
- **View Metadata** - See case names, judges, citations, and more
- **Manage Documents** - Upload, view, and delete PDFs

## 🚀 Quick Start (5 minutes)

### 1. Prerequisites
```bash
# Check you have these installed
python --version  # 3.9+
node --version    # 16+
docker --version
```

### 2. Setup
```bash
cd /Users/periscopelabs/RagOnBLD/SCOB_RAG

# Create environment file with your OpenAI API key
cat > .env << EOF
OPENAI_API_KEY=sk-your-api-key-here
EOF

# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

### 3. Run All Services
```bash
./run_all.sh
```

That's it! Your browser will open to http://localhost:3000

## 📱 How to Use

### Search Page (Home)
1. Type your legal question in the search box
2. Choose how many results to retrieve (3-15)
3. Toggle "Generate AI Answer" for AI-powered summaries
4. Click Search or press Enter
5. Expand results to see full metadata and document text

**Example Questions:**
- "What are the penalties for theft under Bangladesh law?"
- "Explain the bail procedures in criminal cases"
- "What is the statute of limitations for property disputes?"

### Upload Page
1. Click the Upload tab
2. Drag and drop a PDF or click to browse
3. Select your PDF file
4. Click "Upload Document"
5. Wait for processing to complete
6. See the success message with chunk count

**Supported:** PDF files only (text-extractable)

### Documents Page
1. View all uploaded documents
2. See file size and upload date
3. Delete documents you no longer need
4. Monitor your document storage

## 🏗️ System Architecture

```
┌─────────────────────────────┐
│   React Web Interface       │
│   (localhost:3000)          │
│ • Search Page              │
│ • Upload Page              │
│ • Documents Page           │
└────────────┬────────────────┘
             │
        API Calls (HTTP)
             │
┌────────────▼────────────────┐
│   FastAPI Backend           │
│   (localhost:8000)          │
│ • Upload Endpoint          │
│ • Search Endpoint          │
│ • Document Management      │
└────────────┬────────────────┘
             │
    ┌────────┴──────────┐
    │                   │
┌───▼──────┐      ┌────▼─────┐
│ Weaviate │      │ OpenAI    │
│ Vector   │      │ API       │
│ Database │      │           │
└──────────┘      └───────────┘
```

## 📖 Features

### Search Features
- ✅ Semantic search using embeddings
- ✅ Relevance scoring (0-100%)
- ✅ AI answer generation (optional)
- ✅ Configurable result count
- ✅ Full metadata display
- ✅ Expandable result cards
- ✅ Mobile-friendly interface

### Upload Features
- ✅ Drag and drop interface
- ✅ Automatic text extraction
- ✅ Intelligent chunking
- ✅ Metadata extraction
- ✅ Progress feedback
- ✅ Error handling
- ✅ File size display

### Document Management
- ✅ List all documents
- ✅ View upload dates
- ✅ Delete documents
- ✅ File size information
- ✅ Status indicators

### Technical Features
- ✅ Real-time API status
- ✅ Error handling & recovery
- ✅ Loading indicators
- ✅ Responsive design
- ✅ Mobile optimization
- ✅ Keyboard shortcuts
- ✅ Browser caching

## 🔧 API Endpoints

All endpoints are available at `http://localhost:8000`

### Upload Document
```bash
POST /upload
Content-Type: multipart/form-data

Request:
  file: <PDF file>

Response:
  {
    "filename": "document.pdf",
    "status": "success",
    "chunks_added": 25,
    "message": "Successfully uploaded..."
  }
```

### Search Documents
```bash
POST /query
Content-Type: application/json

Request:
  {
    "question": "What are theft penalties?",
    "num_results": 5,
    "use_ai_answer": true
  }

Response:
  {
    "question": "...",
    "results": [
      {
        "text": "...",
        "filename": "document.pdf",
        "relevance_score": 0.89,
        "case_name": "Case v. State",
        "citations": ["2020 SCR 123"]
      }
    ],
    "ai_answer": "According to the documents...",
    "total_results": 5
  }
```

### System Status
```bash
GET /status

Response:
  {
    "status": "ready",
    "weaviate_connected": true,
    "total_documents": 3,
    "total_chunks": 150
  }
```

### List Documents
```bash
GET /documents

Response:
  {
    "documents": [
      {
        "filename": "case.pdf",
        "size_bytes": 1024000,
        "uploaded_at": "2024-01-15T10:30:00"
      }
    ],
    "total": 1
  }
```

### Delete Document
```bash
DELETE /documents/filename.pdf

Response:
  {
    "status": "success",
    "message": "Deleted filename.pdf"
  }
```

## 🛠️ Configuration

### Frontend (.env)
```bash
# API endpoint (optional, defaults to localhost:8000)
REACT_APP_API_URL=http://localhost:8000
```

### Backend (.env)
```bash
# Required: OpenAI API Key for embeddings and answers
OPENAI_API_KEY=sk-...

# Weaviate connection
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=
```

## 📁 Project Structure

```
SCOB_RAG/
├── backend_api.py              # FastAPI server
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── docker-compose.yml          # Weaviate configuration
│
├── config/
│   └── rag_config.py          # RAG system config
│
├── src/
│   ├── weaviate_manager.py    # Vector DB operations
│   ├── pdf_processor.py       # PDF handling
│   └── metadata_extractor.py  # Legal metadata parsing
│
├── frontend/                   # React application
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── index.js           # React entry point
│   │   ├── App.js             # Main component
│   │   ├── api.js             # API client
│   │   ├── components/
│   │   │   ├── Header.js
│   │   │   └── Header.css
│   │   └── pages/
│   │       ├── Search.js      # Search page
│   │       ├── Upload.js      # Upload page
│   │       ├── Documents.js   # Documents page
│   │       └── *.css          # Page styles
│   └── .env                   # Frontend env (optional)
│
├── QUICK_START.md             # Quick reference
├── SETUP_GUIDE.md             # Detailed setup
├── INTEGRATION_SUMMARY.md     # Technical details
└── run_all.sh                 # Auto-startup script
```

## 🐛 Troubleshooting

### "Cannot connect to API server"
```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend if needed
python backend_api.py
```

### "Weaviate connection failed"
```bash
# Start Weaviate
docker-compose up -d

# Verify it's running
curl http://localhost:8080/v1/meta
```

### "No search results"
1. Make sure you've uploaded documents first
2. Check documents have extractable text
3. Try a simpler search query

### "PDF upload fails"
1. Ensure file is a valid PDF
2. Check file permissions
3. Verify SCOB/data/uploads directory exists

### Frontend won't load
1. Check browser console for errors (F12)
2. Verify API endpoint is correct
3. Clear browser cache
4. Try different browser

## 📊 Performance Tips

- **Faster Searches**: Upload relevant documents only
- **Faster Processing**: Use smaller PDF files
- **Better Results**: Use specific, detailed queries
- **Cost Reduction**: Disable AI answers when not needed

## 🔒 Security & Privacy

- ⚠️ No authentication (add for production)
- ⚠️ Files stored in plaintext on disk
- ✅ API keys stored in .env (not committed)
- ✅ CORS configured for frontend
- ✅ Input validation on both sides

## 🚀 Deployment

### Production Build (Frontend)
```bash
cd frontend
npm run build
# Output in 'build' folder - ready for web server
```

### Production Server (Backend)
```bash
# Use production ASGI server
pip install gunicorn
gunicorn backend_api:app --workers 4 --bind 0.0.0.0:8000
```

## 📚 Learn More

- **Quick Start**: See QUICK_START.md
- **Setup Details**: See SETUP_GUIDE.md
- **Architecture**: See INTEGRATION_SUMMARY.md
- **API Docs**: http://localhost:8000/docs (when running)

## 🆘 Getting Help

1. Check the documentation files
2. Review the troubleshooting section
3. Check server logs: `backend.log`
4. Verify all services are running
5. Check browser console (F12)

## 📈 Next Steps

1. ✅ Install and run the system
2. ✅ Upload your first PDF
3. ✅ Try searching
4. ✅ Explore metadata features
5. ✅ Enable AI answers
6. ✅ Customize for your needs

## 🤝 Contributing

To modify the system:

### Frontend Changes
```bash
cd frontend
npm start  # Development server
npm run build  # Production build
```

### Backend Changes
```bash
# Edit backend_api.py
python backend_api.py  # Will auto-reload with changes
```

## 📄 License & Attribution

SCOB Legal RAG System
- Version 1.0.0
- Built with React, FastAPI, and Weaviate
- Legal document RAG for Bangladesh Supreme Court cases

## 🎉 You're All Set!

```
┌─────────────────────────────────────────┐
│  SCOB Legal RAG System Ready to Use!   │
│                                         │
│  🌐 Frontend: http://localhost:3000    │
│  🔌 API: http://localhost:8000         │
│  📦 Weaviate: http://localhost:8080    │
│                                         │
│  Start searching! 🔍⚖️                  │
└─────────────────────────────────────────┘
```

---

**Last Updated**: 2024
**Status**: Production Ready ✅

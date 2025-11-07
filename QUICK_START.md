# SCOB Legal RAG - Quick Start Guide

## 🚀 1-Minute Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- OpenAI API key

### Step 1: Configure Environment

```bash
cd /Users/periscopelabs/RagOnBLD/SCOB_RAG

# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### Step 2: Install Dependencies

```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

### Step 3: Run Everything

**Option A - Automatic (Recommended)**
```bash
./run_all.sh
```

**Option B - Manual (3 terminals)**

Terminal 1:
```bash
docker-compose up -d
```

Terminal 2:
```bash
python backend_api.py
```

Terminal 3:
```bash
cd frontend && npm start
```

### Step 4: Open in Browser

```
http://localhost:3000
```

## 📖 Usage

### Upload Documents
1. Go to **Upload** page
2. Drag & drop PDF files
3. Wait for processing

### Search
1. Go to **Search** page
2. Ask any legal question
3. View results with sources

### Manage Documents
1. Go to **Documents** page
2. View/delete uploaded PDFs

## 🔗 Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | `http://localhost:3000` | Web application |
| API | `http://localhost:8000` | Backend server |
| API Docs | `http://localhost:8000/docs` | Interactive API docs |
| Weaviate | `http://localhost:8080` | Vector database |

## ⚠️ Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
kill -9 <PID>
```

### Weaviate won't start
```bash
# Start Docker daemon first
docker-compose up -d

# View logs
docker-compose logs -f
```

### Frontend won't connect
```bash
# Make sure backend is running
curl http://localhost:8000/health

# Check CORS in backend_api.py
```

### No search results
1. Ensure documents are uploaded
2. Wait for processing to complete
3. Try simpler queries

## 📁 File Structure

```
SCOB_RAG/
├── backend_api.py         # FastAPI server
├── requirements.txt       # Python packages
├── docker-compose.yml     # Weaviate config
├── SETUP_GUIDE.md        # Detailed setup
├── QUICK_START.md        # This file
├── run_all.sh           # Auto-startup script
├── frontend/            # React app
│   ├── public/
│   ├── src/
│   │   ├── App.js
│   │   ├── api.js
│   │   ├── components/
│   │   └── pages/
│   │       ├── Search.js
│   │       ├── Upload.js
│   │       └── Documents.js
│   ├── package.json
│   └── .env
└── src/                 # Backend modules
    ├── weaviate_manager.py
    ├── pdf_processor.py
    └── metadata_extractor.py
```

## 🔧 API Examples

### Upload PDF
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"
```

### Search Documents
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are theft penalties?",
    "num_results": 5,
    "use_ai_answer": true
  }'
```

### Get Status
```bash
curl http://localhost:8000/status
```

## ✅ Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed
- [ ] Docker running
- [ ] .env file created with OpenAI key
- [ ] Dependencies installed
- [ ] All components started
- [ ] Browser opens to localhost:3000

## 🆘 Need Help?

1. Check SETUP_GUIDE.md for detailed instructions
2. Review server logs: `backend.log`
3. Verify all services are running:
   - `curl http://localhost:8000/health`
   - `curl http://localhost:8080/v1/meta`
4. Check firewall/port conflicts

## 🚀 Next Steps

1. **Upload Documents**: Add your legal PDFs
2. **Try Searches**: Test the search functionality
3. **Explore Results**: Examine metadata extraction
4. **Enable AI Answers**: Toggle for AI summaries
5. **Deploy**: See SETUP_GUIDE.md for production setup

---

**Happy searching! 📚⚖️**

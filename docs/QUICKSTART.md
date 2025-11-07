# Quick Start Guide - SCOB Legal RAG System

## 5-Minute Setup

### 1. Navigate to SCOB_RAG Directory

```bash
cd /Users/periscopelabs/RagOnBLD/SCOB_RAG
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Weaviate

```bash
docker-compose up -d
```

Check if running:
```bash
docker ps
```

You should see a container with `semitechnologies/weaviate` image.

### 4. Ingest Documents

**Important:** Use `python3.14` (or the wrapper script) due to dependency requirements:

```bash
python3.14 ingest_documents.py
```

Or use the wrapper script:
```bash
./run_ingest.sh
```

Expected output:
```
============================================================
Legal Document RAG System - Data Ingestion
============================================================

[Step 1] Extracting text from PDFs...
PDF Directory: /Users/periscopelabs/RagOnBLD/Data/PDF/SCOB/2015
Found 3 PDF files
Processing: 1_SCOB_2015.pdf
Processing: 2_SCOB_2015.pdf
Processing: 3_SCOB_2015.pdf
Successfully extracted text from 3 documents

[Step 2] Connecting to Weaviate...
Connected to Weaviate successfully

[Step 3] Creating Weaviate schema...
Created collection: LegalDocument

[Step 4] Adding documents to Weaviate...
...
Total chunks added to Weaviate: 2729

Ingestion completed successfully!
```

### 5. Query the System

```bash
python3.14 rag_query.py
```

Or use the wrapper script:
```bash
./run_query.sh
```

Try these example queries:
- "property rights"
- "criminal procedure"
- "contract enforcement"
- "constitutional law"

Example with a specific query:
```bash
python3.14 rag_query.py "property rights"
```

## System Overview

```
SCOB PDFs (2015)
      ↓
Text Extraction (pypdf)
      ↓
Chunking (1000 chars)
      ↓
Embeddings (sentence-transformers)
      ↓
Weaviate Vector DB
      ↓
Semantic Search
```

## File Structure

```
SCOB_RAG/
├── src/
│   ├── pdf_processor.py       # PDF handling
│   └── weaviate_manager.py    # Database operations
├── config/
│   └── rag_config.py          # Configuration
├── docs/
│   ├── README.md              # Full documentation
│   └── QUICKSTART.md          # This file
├── ingest_documents.py        # Data ingestion pipeline
├── rag_query.py              # Query interface
├── requirements.txt           # Dependencies
└── docker-compose.yml         # Weaviate setup
```

## Commands Reference

### Start Weaviate
```bash
docker-compose up -d
```

### Stop Weaviate
```bash
docker-compose down
```

### Check Weaviate Status
```bash
curl http://localhost:8080/v1/meta
```

### View Weaviate Logs
```bash
docker-compose logs -f weaviate
```

### Run Ingestion
```bash
python3.14 ingest_documents.py
# OR
./run_ingest.sh
```

### Interactive Query
```bash
python3.14 rag_query.py
# OR
./run_query.sh
```

### Single Query
```bash
python3.14 rag_query.py "your question here"
# OR
./run_query.sh "your question here"
```

## Troubleshooting

### Problem: Can't connect to Weaviate

**Solution**:
```bash
# Check if Docker is running
docker ps

# Check Weaviate logs
docker-compose logs weaviate

# Restart Weaviate
docker-compose down
docker-compose up -d
```

### Problem: PDF text extraction fails

**Solution**: Check if PDFs are text-based (not scanned images). For scanned PDFs, you'll need OCR support.

### Problem: Out of memory

**Solution**: Edit `config/rag_config.py`:
```python
CHUNK_SIZE = 500  # Reduce from 1000
```

### Problem: Port 8080 already in use

**Solution**:
```bash
# Find what's using port 8080
lsof -i :8080

# Or modify docker-compose.yml to use different port
```

## Next Steps

1. **Test with different queries** - Try legal terms specific to your use case
2. **Add more documents** - Update `PDF_BASE_DIR` in config
3. **Integrate with LLM** - Add GPT-4 or Claude for answer generation
4. **Build web interface** - Create a user-friendly frontend

## Need Help?

- See `docs/README.md` for detailed documentation
- Check configuration in `config/rag_config.py`
- Review code in `src/` directory

## Performance Tips

- First run downloads embedding model (~90MB)
- Ingestion time depends on PDF size and count
- Query response is typically under 1 second
- Weaviate uses ~500MB RAM for this dataset

# SCOB RAG System - Enhanced Features

## 🎯 What's New

### 1. **Chatbot Mode** - Simple AI Answers
Get direct answers to legal questions instead of raw document chunks.

```bash
python3.14 rag_query.py --chat "What are property rights?"
```

**Output:**
```
📝 Answer:
Based on Section 5 of the Ordinance, property rights state that...

📚 Sources:
1. 3_SCOB_2015.pdf - Case Name (3 SCOB 2015)
```

### 2. **Legal Metadata Extraction**
Automatically extracts:
- Case names (parties involved)
- Case numbers
- Court information
- Judge names
- Judgment dates
- Legal citations (e.g., "3 SCOB 2015")
- Subject matter (Contract, Property, Criminal, etc.)

### 3. **OpenAI Embeddings**
- Uses OpenAI's `text-embedding-3-small` for better legal document understanding
- More accurate semantic search than local models
- Optimized for legal terminology

### 4. **Improved Chunking**
- Larger chunks (1500 chars) for better legal context
- Smart boundaries: breaks at paragraphs, sections, and sentences
- Preserves legal structure and numbering

### 5. **Progress Tracking**
Clear feedback during ingestion:
```
Processing document: 1_SCOB_2015.pdf
  Extracted metadata: Case: ABC vs XYZ | Court: High Court Division
  Processing 800 chunks in batches...
    Batch 1: Processing chunks 1-100/800
    Batch 2: Processing chunks 101-200/800
  ✓ Completed: Added 800 chunks
```

## 📊 Comparison: Old vs New

| Feature | Before | Now |
|---------|--------|-----|
| **Answer Format** | Raw text chunks | AI-generated answer + sources |
| **Metadata** | Filename only | Case name, judges, dates, citations |
| **Embeddings** | Local (384-dim) | OpenAI (1536-dim) |
| **Chunk Size** | 1000 chars | 1500 chars |
| **Progress** | Silent | Real-time updates |
| **Chunking** | Simple breaks | Legal-aware boundaries |

## 🚀 Usage

### Quick Start - Chatbot Mode
```bash
# Single question
python3.14 rag_query.py --chat "Explain land transfer rules"

# Interactive chatbot
python3.14 rag_query.py --chat
```

### Advanced Options
```bash
# More sources for better context
python3.14 rag_query.py --chat --results 10 "complex legal question"

# Standard search mode (detailed)
python3.14 rag_query.py "property rights"

# Interactive with mode switching
python3.14 rag_query.py
> mode  # Switch between chat/search
```

## 📁 New Files

- `CHATBOT_USAGE.md` - Detailed chatbot guide
- `src/metadata_extractor.py` - Legal metadata extraction
- `.env` - OpenAI API key configuration
- `FEATURES.md` - This file

## ⚙️ Configuration

Edit `config/rag_config.py`:

```python
# Use OpenAI or local embeddings
USE_OPENAI_EMBEDDINGS = True  # False for local

# Chunk sizes
CHUNK_SIZE = 1500  # Larger for legal context
CHUNK_OVERLAP = 300  # More overlap

# OpenAI model
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
```

## 🎓 Examples

### Example 1: Property Law
```bash
$ python3.14 rag_query.py --chat "What is benami property?"

📝 Answer:
Benami property refers to immovable property purchased in the name of
another person while the beneficial interest remains with the actual
purchaser. According to Section 5 of the Ordinance, such transactions
are prohibited...

📚 Sources:
1. 3_SCOB_2015.pdf - State vs Rahman (3 SCOB 2015)
```

### Example 2: Case Research
```bash
$ python3.14 rag_query.py "High Court Division 2015"

--- Result 1 ---
Source: 1_SCOB_2015.pdf (Chunk 45)
Case Name: ABC vs XYZ
Court: High Court Division
Judges: Justice Rahman, Justice Ahmed
Judgment Date: 15th March, 2015
Citations: 1 SCOB 2015
Subject Matter: Constitutional, Administrative

Text Preview: [Legal text...]
```

## 🔧 Technical Details

### Metadata Extraction Patterns
- Case names: "ABC vs XYZ", "Name and Others"
- Citations: "X SCOB YYYY", "X BLD YYYY", "X DLR YYYY"
- Courts: "Supreme Court", "High Court Division", "Appellate Division"
- Judges: "Justice Name", "Hon'ble Justice Name"
- Dates: Multiple formats supported

### Embedding Dimensions
- OpenAI: 1536 dimensions
- Local (fallback): 384 dimensions

### Batch Processing
- Processes 100 chunks per batch
- Shows progress every batch
- Prevents API rate limits

## 📚 Documentation

- `CHATBOT_USAGE.md` - How to use chatbot mode
- `HOW_TO_RUN.txt` - Quick reference
- `docs/README.md` - Full documentation
- `docs/QUICKSTART.md` - Setup guide

## 🛠️ Requirements

- Python 3.14
- OpenAI API key (in `.env`)
- Weaviate (Docker)
- All dependencies in `requirements.txt`

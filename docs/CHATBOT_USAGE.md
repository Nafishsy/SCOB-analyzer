# Chatbot Mode - Quick Usage Guide

## What is Chatbot Mode?

Chatbot mode gives you **AI-generated answers** instead of raw document chunks. It uses OpenAI GPT-4 to read the relevant legal documents and provide a concise answer with sources.

## Usage Examples

### Simple Chatbot Query (Recommended)

Get a direct answer with sources:

```bash
python3.14 rag_query.py --chat "What are the property rights laws?"
```

**Output:**
```
📝 Answer:
------------------------------------------------------------
Based on the legal documents, property rights in Bangladesh are governed
by Section 5 of the Ordinance, which states that no person shall purchase
immovable property for their own benefit in the name of another person...

📚 Sources:
1. 3_SCOB_2015.pdf - Case Name vs Case Name (3 SCOB 2015)
2. 1_SCOB_2015.pdf - Another Case (1 SCOB 2015)
```

### Standard Search Mode (Detailed)

See full document chunks and metadata:

```bash
python3.14 rag_query.py "property rights"
```

### Interactive Chatbot Mode

```bash
python3.14 rag_query.py --chat
```

Then ask questions naturally:
```
🔍 Your question: What are the rules for land transfer?
🔍 Your question: Tell me about criminal negligence
🔍 Your question: exit
```

### Switch Modes in Interactive

```bash
python3.14 rag_query.py
```

Type `mode` to toggle between chatbot and search:
```
🔍 Your question: mode
Switched to Chatbot mode

🔍 Your question: What is contract law?
📝 Answer: [AI-generated answer]

🔍 Your question: mode
Switched to Search mode
```

## Command Options

```bash
# Chatbot mode with custom number of sources
python3.14 rag_query.py --chat --results 10 "your question"

# Short flags
python3.14 rag_query.py -c -r 10 "your question"

# Help
python3.14 rag_query.py --help
```

## When to Use Each Mode

**Chatbot Mode** (`--chat` or `-c`):
- ✅ Quick answers to legal questions
- ✅ Summary of legal principles
- ✅ General understanding
- ✅ Easier to read

**Search Mode** (default):
- ✅ See exact legal text
- ✅ View all metadata (judges, dates, citations)
- ✅ Multiple relevant sections
- ✅ Deep research

## Examples

```bash
# Property law question
python3.14 rag_query.py --chat "What is required for valid property transfer?"

# Criminal law question
python3.14 rag_query.py --chat "Explain criminal negligence"

# Constitutional law
python3.14 rag_query.py --chat "What are fundamental rights?"

# Get more context (10 sources instead of 5)
python3.14 rag_query.py --chat --results 10 "land acquisition rules"
```

## Tips

1. **Be specific** in your questions for better answers
2. **Use --results** to increase context if answer seems incomplete
3. **Check sources** to verify the AI's interpretation
4. **Use search mode** when you need exact legal text
5. **Interactive mode** is great for exploring multiple questions

## Requirements

- OpenAI API key must be configured in `.env` file
- Weaviate must be running (`docker-compose up -d`)
- Documents must be ingested (`python3.14 ingest_documents.py`)

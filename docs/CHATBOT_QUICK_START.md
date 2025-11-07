# Chatbot Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Backend API running (`backend_api.py`)
- Frontend server running (React app)
- Weaviate database connected
- OpenAI API key configured

### Step 1: Start the Backend

```bash
cd /Users/periscopelabs/RagOnBLD/SCOB_RAG
python backend_api.py
```

You should see:
```
✓ Weaviate connected successfully
✓ Chatbot initialized successfully
```

### Step 2: Start the Frontend

```bash
cd /Users/periscopelabs/RagOnBLD/SCOB_RAG/frontend
npm start
```

The chatbot interface will open at `http://localhost:3000`

### Step 3: Ask Your First Question

1. Type a question in the chat box
2. Press Enter or click Send
3. Wait for the AI to respond with sources

Example questions:
- "What are the procedures for filing a case?"
- "Explain the law regarding inheritance"
- "What is a tort and provide examples"

## 📝 Key Features

### New Chat
Click **+ New Chat** to start a fresh conversation.

### Chat History
Click **Chat History** to see all previous conversations.

### Source Citations
Each answer includes source links in format: `filename:chunk_number`
- Click on sources to view document details
- Check relevance score for answer quality

### Session Management
- **Load Session**: Click any session in history to continue that conversation
- **Delete Session**: Click ✕ next to a session to remove it
- **Current Session**: Selected session is highlighted

## 💡 Tips & Tricks

### For Better Answers
1. **Be specific** - "What is the procedure for civil appeal?" instead of "Tell me about procedure"
2. **Ask one question at a time** - Easier for the AI to find relevant documents
3. **Use legal terms** - "plaintiff", "defendant", "tort", "statute" help with accuracy
4. **Follow up naturally** - "What are the penalties?" after asking about violations

### Understanding Confidence
- **0.9-1.0** = Very confident (multiple strong sources)
- **0.7-0.9** = Confident (good sources found)
- **0.5-0.7** = Moderate (some relevant sources)
- **Below 0.5** = Low confidence (limited relevant sources)

### Working with Sources
- Each source shows the document name and chunk number
- Relevance score (0-1) indicates how relevant the content is
- Click sources to verify information in original documents

## 🔧 API Endpoints Reference

### Ask a Question
```bash
curl -X POST "http://localhost:8000/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Your question here",
    "num_results": 5
  }'
```

### Create New Session
```bash
curl -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d '{"title": "Session title"}'
```

### List All Sessions
```bash
curl -X GET "http://localhost:8000/sessions"
```

### Get Session Details
```bash
curl -X GET "http://localhost:8000/sessions/{session_id}"
```

## 🎯 Common Use Cases

### Case 1: Learning About a Topic
1. Start new chat with title "Topic: [Subject]"
2. Ask broad questions first
3. Ask specific follow-up questions
4. Review sources for deep understanding

### Case 2: Legal Research
1. Create session: "Research: [Case/Topic]"
2. Ask detailed questions
3. Review all source documents
4. Export chat history if needed

### Case 3: Quick Answer
1. Ask single question without session
2. Check confidence score
3. Review sources
4. Ask follow-up if needed

## 📊 Chatbot Structure

```
Frontend (React)
    ↓
Backend API (FastAPI)
    ↓
Chatbot Module
    ├─ Session Management
    ├─ Message History
    └─ Q&A Logic
    ↓
Weaviate (Vector DB)
    └─ Document Search
    ↓
OpenAI (GPT-4)
    └─ Answer Generation
```

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| No answer from chatbot | Check if documents are uploaded in Weaviate |
| Low confidence scores | Try rewording question with different terms |
| Slow responses | Reduce `num_results` from 5 to 3 |
| Session not loading | Refresh browser and try again |
| API error 503 | Ensure Weaviate and OpenAI are connected |

## 📚 File Structure

```
SCOB_RAG/
├── backend_api.py           # Main API server
├── src/
│   └── chatbot.py           # Core chatbot logic
├── frontend/src/
│   └── components/
│       ├── Chatbot.tsx      # React component
│       └── Chatbot.css      # Styles
├── CHATBOT_GUIDE.md         # Full documentation
└── CHATBOT_QUICK_START.md   # This file
```

## 🔐 Environment Setup

Required environment variables in `.env`:
```
OPENAI_API_KEY=your-api-key
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your-key-if-needed
```

## 📈 Performance Tips

1. **First question slower** - Initializes session and searches documents
2. **Follow-ups faster** - Uses cached session context
3. **Batch questions** - Ask multiple related questions in one session
4. **Manage sessions** - Delete old sessions to keep interface responsive

## 🎓 Example Conversation Flow

**User**: "What is contract law?" (New session created)
- Response: Overview of contract law with 2-3 sources
- Confidence: 0.92

**User**: "What are the elements of a valid contract?"
- Response: Lists elements with examples from sources
- Confidence: 0.88

**User**: "How do I dispute a breach?"
- Response: Procedures for disputing breach with legal references
- Confidence: 0.85

**Session saved** with 3 questions and full conversation history

## 🚨 Important Notes

1. **Source citations are key** - Always verify answers with source documents
2. **Not a substitute for lawyer** - Use as research tool, not legal advice
3. **Limited by uploaded documents** - Answers based only on available documents
4. **Session-specific context** - Each session maintains conversation context
5. **Automatic cleanup** - Old sessions can be manually deleted

## 📞 Support Resources

- **API Docs**: Swagger UI at `http://localhost:8000/docs`
- **Full Guide**: See `CHATBOT_GUIDE.md`
- **Backend Logs**: Check console output from `backend_api.py`
- **Frontend Errors**: Check browser Developer Tools (F12)

## ✅ Verification Checklist

Before using the chatbot:
- [ ] Backend API is running
- [ ] Frontend server is running
- [ ] Documents are uploaded to Weaviate
- [ ] OpenAI API key is configured
- [ ] CORS is enabled on backend
- [ ] Can see welcome message in chat

## 🎉 You're Ready!

You now have a fully functional legal document chatbot with:
- ✅ Question-Answer capability
- ✅ Session management
- ✅ Source citations
- ✅ Confidence scoring
- ✅ Multi-turn conversations
- ✅ Chat history

**Start asking questions about your legal documents!**

---

**Need help?** Check the full CHATBOT_GUIDE.md or the troubleshooting section above.

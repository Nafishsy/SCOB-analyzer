# SCOB Legal Chatbot - Complete Guide

## Overview

The SCOB Legal Chatbot is a comprehensive question-answering system that allows users to interact with legal documents through a conversational interface. It features session management, source citations, and multi-turn conversations.

## Architecture

### Components

1. **Backend API** (`backend_api.py`)
   - FastAPI-based REST API
   - Weaviate vector database integration
   - OpenAI GPT-4 integration for answer generation
   - Session management system

2. **Chatbot Module** (`src/chatbot.py`)
   - Core chatbot logic and session management
   - Message history tracking
   - Q&A pair extraction
   - Configuration management

3. **Frontend Component** (`frontend/src/components/Chatbot.tsx`)
   - React-based UI
   - Real-time chat interface
   - Session management
   - Source citation display

## Backend Endpoints

### Question-Answer Endpoint

**POST** `/qa`

Ask a question about legal documents with automatic session management.

**Request:**
```json
{
  "question": "What are the procedures for filing a case?",
  "session_id": "optional-session-id",
  "num_results": 5
}
```

**Response:**
```json
{
  "session_id": "unique-session-id",
  "question": "What are the procedures for filing a case?",
  "answer": "Based on the legal documents...",
  "sources": [
    {
      "id": 1,
      "filename": "case_file.pdf",
      "filepath": "/path/to/file",
      "chunk_index": 0,
      "case_name": "Case Name",
      "relevance_score": 0.95,
      "source_location": "case_file.pdf:chunk_0"
    }
  ],
  "confidence": 0.89
}
```

### Session Management Endpoints

#### Create New Session

**POST** `/sessions`

Create a new chat session.

**Request:**
```json
{
  "title": "My Legal Question Chat"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "title": "My Legal Question Chat",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "message_count": 0,
  "question_count": 0
}
```

#### List All Sessions

**GET** `/sessions`

Get all chat sessions.

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "uuid",
      "title": "Chat Title",
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00",
      "message_count": 5,
      "question_count": 3
    }
  ],
  "total": 1
}
```

#### Get Session History

**GET** `/sessions/{session_id}`

Get full conversation history for a session.

**Response:**
```json
{
  "session_id": "uuid",
  "title": "Chat Title",
  "messages": [
    {
      "role": "user",
      "content": "What is contract law?",
      "timestamp": "2024-01-01T12:00:00",
      "sources": []
    },
    {
      "role": "assistant",
      "content": "Contract law is...",
      "timestamp": "2024-01-01T12:00:05",
      "sources": [...]
    }
  ],
  "metadata": {
    "topic": null,
    "question_count": 1,
    "document_count": 0
  }
}
```

#### Get Session Summary

**GET** `/sessions/{session_id}/summary`

Get quick summary of a session.

**Response:**
```json
{
  "session_id": "uuid",
  "title": "Chat Title",
  "message_count": 5,
  "question_count": 2,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:01:30",
  "last_message": "Thank you for the information"
}
```

#### Delete Session

**DELETE** `/sessions/{session_id}`

Delete a chat session.

**Response:**
```json
{
  "status": "success",
  "message": "Session deleted"
}
```

## Features

### 1. **Session Management**
- Each conversation is stored in a session
- Sessions persist across browser sessions
- View conversation history anytime
- Delete sessions when no longer needed

### 2. **Source Citations**
- Every answer includes source document references
- Format: `filename:chunk_number`
- Relevance scores for each source
- Easy navigation to source documents

### 3. **Multi-Turn Conversations**
- Maintain context across multiple questions
- Ask follow-up questions naturally
- Full conversation history saved
- Automatic session creation

### 4. **Confidence Scoring**
- Confidence metric based on source relevance
- Indicates reliability of the answer
- Helps users assess answer quality

### 5. **Advanced Search**
- Configurable number of search results
- Relevance-based ranking
- Metadata extraction from documents
- Automatic chunking optimization

## Usage Examples

### Example 1: Simple Question

**Request:**
```json
POST /qa
{
  "question": "What is the law regarding marriage in Bangladesh?"
}
```

**Response:**
```json
{
  "session_id": "a1b2c3d4",
  "question": "What is the law regarding marriage in Bangladesh?",
  "answer": "According to the documents, the law regarding marriage in Bangladesh is governed by the Muslim Family Laws Ordinance for Muslim marriages...[Source 1: marriage_law.pdf:chunk_2]...",
  "sources": [
    {
      "id": 1,
      "filename": "marriage_law.pdf",
      "source_location": "marriage_law.pdf:chunk_2",
      "case_name": "Marriage Law Provisions",
      "relevance_score": 0.96
    }
  ],
  "confidence": 0.94
}
```

### Example 2: Follow-up Question with Session

**First Question:**
```json
POST /qa
{
  "question": "Explain copyright infringement",
  "num_results": 5
}
```

**Follow-up Question (same session):**
```json
POST /qa
{
  "question": "What are the penalties?",
  "session_id": "a1b2c3d4",
  "num_results": 3
}
```

The system maintains context and provides relevant answers to the follow-up question within the context of copyright infringement.

### Example 3: Session Management

**Create new session:**
```json
POST /sessions
{
  "title": "Copyright Law Questions"
}
```

**Later, retrieve previous conversation:**
```json
GET /sessions/a1b2c3d4
```

## Frontend Integration

### Using the Chatbot Component

```tsx
import Chatbot from './components/Chatbot';

function App() {
  return <Chatbot />;
}
```

### Features Included

- Real-time chat interface
- Automatic session management
- Chat history sidebar
- Source citation display
- Typing indicators
- Error handling
- Responsive design

## Configuration

### Chatbot Config (`src/chatbot.py`)

```python
chatbot_config = ChatbotConfig(
    max_context_messages=10,      # Messages to keep in context
    temperature=0.3,               # Response creativity (0-1)
    max_tokens=500,               # Max response length
    top_k_results=5,              # Search results per query
    enable_source_citations=True  # Show source links
)
```

### Backend Config

Edit `backend_api.py` startup event:
```python
chatbot_config = ChatbotConfig(
    max_context_messages=10,
    temperature=0.3,
    max_tokens=500,
    top_k_results=5,
    enable_source_citations=True
)
```

## API Response Formats

### Success Response
```json
{
  "session_id": "string",
  "question": "string",
  "answer": "string",
  "sources": [
    {
      "id": integer,
      "filename": "string",
      "filepath": "string",
      "chunk_index": integer,
      "case_name": "string",
      "relevance_score": float,
      "source_location": "string"
    }
  ],
  "confidence": float
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Best Practices

1. **Session Management**
   - Create a new session for different topics
   - Reuse sessions for related questions
   - Delete old sessions to keep the interface clean

2. **Asking Questions**
   - Be specific and clear
   - Ask one question at a time
   - Use legal terminology when possible
   - Provide context if asking follow-ups

3. **Evaluating Answers**
   - Check the confidence score
   - Review source citations
   - Cross-reference multiple sources
   - Ask for clarification if needed

4. **Source Citations**
   - Click on sources to view documents
   - Note the chunk references
   - Verify answers with original sources

## Troubleshooting

### Issue: No results from search
**Solution:**
- Try rewording your question
- Use different legal terminology
- Check if documents are uploaded
- Increase num_results parameter

### Issue: Low confidence score
**Solution:**
- Review source documents
- Ask a more specific question
- Check if documents contain relevant information
- Ask a follow-up question for clarification

### Issue: API connection error
**Solution:**
- Ensure backend API is running
- Check CORS configuration
- Verify API URL in frontend
- Check network connectivity

### Issue: Session not found
**Solution:**
- Create a new session
- Refresh the page
- Check session ID
- Clear browser cache

## Performance Tips

1. **Optimize search results**
   - Start with default num_results=5
   - Increase only if needed
   - Reduces API response time

2. **Conversation management**
   - Archive old sessions
   - Delete unnecessary sessions
   - Keep active sessions focused on topic

3. **API efficiency**
   - Batch related questions
   - Reuse sessions for context
   - Avoid redundant searches

## Development

### Adding Custom Features

To extend the chatbot:

1. **Backend Extension**
   - Edit `/qa` endpoint for new logic
   - Modify `generate_qa_answer()` for custom prompts
   - Add new endpoints in `backend_api.py`

2. **Frontend Extension**
   - Modify `Chatbot.tsx` for UI changes
   - Update `Chatbot.css` for styling
   - Add new components as needed

3. **Chatbot Logic**
   - Edit `src/chatbot.py` for core changes
   - Extend `ChatSession` for new features
   - Modify `ChatbotConfig` for new settings

## Testing

### Test Example Queries

1. **Basic Question**
   ```
   "What are the main provisions of the Contract Act?"
   ```

2. **Procedural Question**
   ```
   "How do I file a case in the Supreme Court?"
   ```

3. **Definition Question**
   ```
   "Define tort and give examples"
   ```

4. **Follow-up Question**
   ```
   "What are the penalties for violations?"
   (Asked after previous question)
   ```

## API Examples Using cURL

### Ask a Question
```bash
curl -X POST "http://localhost:8000/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is contract law?",
    "num_results": 5
  }'
```

### Create Session
```bash
curl -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Legal Chat"}'
```

### List Sessions
```bash
curl -X GET "http://localhost:8000/sessions"
```

### Get Session History
```bash
curl -X GET "http://localhost:8000/sessions/{session_id}"
```

### Delete Session
```bash
curl -X DELETE "http://localhost:8000/sessions/{session_id}"
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check browser console for errors
4. Review backend logs

---

**Version**: 1.0.0
**Last Updated**: 2024-01-01
**Author**: SCOB RAG Team

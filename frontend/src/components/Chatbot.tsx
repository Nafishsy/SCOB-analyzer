import React, { useState, useRef, useEffect } from 'react';
import './Chatbot.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  sources?: Source[];
}

interface Source {
  id: number;
  filename: string;
  source_location: string;
  case_name?: string;
  relevance_score?: number;
}

interface ChatSession {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  question_count: number;
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [showSessions, setShowSessions] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const API_BASE = 'http://localhost:8000';

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadSessions = async () => {
    try {
      const response = await fetch(`${API_BASE}/sessions`);
      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const createNewSession = async () => {
    try {
      const response = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: `Chat - ${new Date().toLocaleString()}` }),
      });

      if (response.ok) {
        const newSession = await response.json();
        setSessionId(newSession.session_id);
        setMessages([]);
        loadSessions();
        setShowSessions(false);
      }
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const loadSessionHistory = async (sessionId: string) => {
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setSessionId(sessionId);
        setMessages(data.messages || []);
        setShowSessions(false);
      }
    } catch (error) {
      console.error('Failed to load session:', error);
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        if (sessionId === sessionId) {
          setSessionId(null);
          setMessages([]);
        }
        loadSessions();
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim()) return;

    // Initialize session if needed
    let currentSessionId = sessionId;
    if (!currentSessionId) {
      const response = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'New Chat' }),
      });

      if (!response.ok) return;

      const newSession = await response.json();
      currentSessionId = newSession.session_id;
      setSessionId(currentSessionId);
      loadSessions();
    }

    // Add user message to UI
    const userMessage: Message = {
      role: 'user',
      content: input,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Send to QA endpoint
      const response = await fetch(`${API_BASE}/qa`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: input,
          session_id: currentSessionId,
          num_results: 5,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      loadSessions(); // Refresh session list
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(e as any);
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-sidebar">
        <button className="new-chat-btn" onClick={createNewSession}>
          + New Chat
        </button>

        <div className="sessions-section">
          <button
            className="sessions-toggle"
            onClick={() => setShowSessions(!showSessions)}
          >
            {showSessions ? '▼' : '▶'} Chat History
          </button>

          {showSessions && (
            <div className="sessions-list">
              {sessions.length === 0 ? (
                <p className="no-sessions">No chats yet</p>
              ) : (
                sessions.map((session) => (
                  <div
                    key={session.session_id}
                    className={`session-item ${
                      session.session_id === sessionId ? 'active' : ''
                    }`}
                  >
                    <button
                      className="session-title"
                      onClick={() => loadSessionHistory(session.session_id)}
                      title={session.title}
                    >
                      {session.title.substring(0, 30)}
                      {session.title.length > 30 ? '...' : ''}
                    </button>
                    <button
                      className="session-delete"
                      onClick={() => deleteSession(session.session_id)}
                      title="Delete"
                    >
                      ✕
                    </button>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      <div className="chatbot-main">
        <div className="chatbot-header">
          <h1>Legal Document Assistant</h1>
          <p>Ask questions about SCOB legal documents</p>
        </div>

        <div className="chatbot-messages">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <h2>Welcome to Legal Document Assistant</h2>
              <p>Ask me anything about legal documents, cases, and procedures.</p>
              <div className="example-questions">
                <p>Example questions:</p>
                <ul>
                  <li>What are the procedures for filing a case?</li>
                  <li>Tell me about contract law</li>
                  <li>What is the law regarding inheritance?</li>
                </ul>
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <p className="message-text">{msg.content}</p>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="message-sources">
                      <p className="sources-title">Sources:</p>
                      {msg.sources.map((source) => (
                        <a
                          key={source.id}
                          href="#"
                          className="source-link"
                          onClick={(e) => {
                            e.preventDefault();
                            console.log('Source:', source);
                          }}
                          title={`${source.source_location} (Relevance: ${(source.relevance_score || 0).toFixed(2)})`}
                        >
                          [{source.id}] {source.source_location}
                          {source.case_name && ` - ${source.case_name}`}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {loading && (
            <div className="message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form className="chatbot-input-form" onSubmit={sendMessage}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about legal documents... (Shift+Enter for new line, Enter to send)"
            disabled={loading}
            rows={1}
            style={{
              minHeight: '50px',
              maxHeight: '150px',
              resize: 'vertical',
            }}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            {loading ? 'Thinking...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chatbot;

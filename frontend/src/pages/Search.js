import React, { useState } from 'react';
import { Search, Loader, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { queryDocuments } from '../api';
import './Search.css';

function SearchPage() {
  const [question, setQuestion] = useState('');
  const [numResults, setNumResults] = useState(5);
  const [useAIAnswer, setUseAIAnswer] = useState(true);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [expandedResult, setExpandedResult] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!question.trim()) {
      setError('Please enter a search query');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await queryDocuments(question, numResults, useAIAnswer);
      setResults(data);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Search failed';
      setError(`Failed to search: ${errorMessage}`);
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (index) => {
    setExpandedResult(expandedResult === index ? null : index);
  };

  return (
    <div className="search-page">
      <div className="search-container">
        {/* Search Form */}
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-wrapper">
            <input
              type="text"
              placeholder="Ask a legal question about Bangladesh law..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="search-input"
              disabled={loading}
            />
            <button
              type="submit"
              className="search-button"
              disabled={loading || !question.trim()}
            >
              {loading ? (
                <Loader size={20} className="spinner" />
              ) : (
                <Search size={20} />
              )}
            </button>
          </div>

          {/* Options */}
          <div className="search-options">
            <div className="option-group">
              <label>
                <input
                  type="checkbox"
                  checked={useAIAnswer}
                  onChange={(e) => setUseAIAnswer(e.target.checked)}
                  disabled={loading}
                />
                <span>Generate AI Answer</span>
              </label>
              <p className="option-help">Get an AI-generated summary with sources</p>
            </div>

            <div className="option-group">
              <label htmlFor="num-results">Number of Results:</label>
              <select
                id="num-results"
                value={numResults}
                onChange={(e) => setNumResults(parseInt(e.target.value))}
                disabled={loading}
                className="results-select"
              >
                <option value={3}>3 results</option>
                <option value={5}>5 results</option>
                <option value={10}>10 results</option>
                <option value={15}>15 results</option>
              </select>
            </div>
          </div>
        </form>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="results-section">
            {results.ai_answer && (
              <div className="ai-answer-box">
                <h3>AI-Generated Answer</h3>
                <p>{results.ai_answer}</p>
              </div>
            )}

            <div className="results-header">
              <h3>Found {results.total_results} relevant document chunks</h3>
            </div>

            {results.results.length === 0 ? (
              <div className="no-results">
                <p>No documents found matching your query. Try uploading relevant documents first.</p>
              </div>
            ) : (
              <div className="results-list">
                {results.results.map((result, index) => (
                  <div key={index} className="result-item">
                    <div
                      className="result-header"
                      onClick={() => toggleExpand(index)}
                    >
                      <div className="result-meta">
                        <span className="result-number">{index + 1}</span>
                        <div className="result-info">
                          <h4 className="result-filename">{result.filename}</h4>
                          {result.case_name && (
                            <p className="result-case">{result.case_name}</p>
                          )}
                          <p className="result-source">
                            {result.source} • Chunk {result.chunk_index} • Score: {(result.relevance_score * 100).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                      <button className="expand-button">
                        {expandedResult === index ? (
                          <ChevronUp size={20} />
                        ) : (
                          <ChevronDown size={20} />
                        )}
                      </button>
                    </div>

                    {expandedResult === index && (
                      <div className="result-content">
                        {result.case_number && (
                          <div className="metadata-item">
                            <strong>Case Number:</strong> {result.case_number}
                          </div>
                        )}
                        {result.court && (
                          <div className="metadata-item">
                            <strong>Court:</strong> {result.court}
                          </div>
                        )}
                        {result.judges && result.judges.length > 0 && (
                          <div className="metadata-item">
                            <strong>Judges:</strong> {result.judges.join(', ')}
                          </div>
                        )}
                        {result.judgment_date && (
                          <div className="metadata-item">
                            <strong>Judgment Date:</strong> {result.judgment_date}
                          </div>
                        )}
                        {result.citations && result.citations.length > 0 && (
                          <div className="metadata-item">
                            <strong>Citations:</strong> {result.citations.join(', ')}
                          </div>
                        )}
                        {result.subject_matter && result.subject_matter.length > 0 && (
                          <div className="metadata-item">
                            <strong>Subject Matter:</strong> {result.subject_matter.join(', ')}
                          </div>
                        )}

                        <div className="result-text">
                          <h5>Document Text</h5>
                          <p>{result.text}</p>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Empty State */}
        {!results && !loading && (
          <div className="empty-state">
            <Search size={48} />
            <h3>Search Legal Documents</h3>
            <p>Enter a question to search across your uploaded legal documents.</p>
            <div className="example-queries">
              <p className="example-label">Example queries:</p>
              <ul>
                <li>"What are the penalties for theft?"</li>
                <li>"Explain the bail procedures"</li>
                <li>"What is the statute of limitations?"</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default SearchPage;

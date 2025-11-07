import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

// Get system status
export const getSystemStatus = async () => {
  try {
    const response = await api.get('/status');
    return response.data;
  } catch (error) {
    console.error('Failed to get system status:', error);
    throw error;
  }
};

// Upload PDF
export const uploadPDF = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Failed to upload PDF:', error);
    throw error;
  }
};

// Query documents
export const queryDocuments = async (question, numResults = 5, useAIAnswer = false) => {
  try {
    const response = await api.post('/query', {
      question,
      num_results: numResults,
      use_ai_answer: useAIAnswer,
    });

    return response.data;
  } catch (error) {
    console.error('Failed to query documents:', error);
    throw error;
  }
};

// List documents
export const listDocuments = async () => {
  try {
    const response = await api.get('/documents');
    return response.data;
  } catch (error) {
    console.error('Failed to list documents:', error);
    throw error;
  }
};

// Delete document
export const deleteDocument = async (filename) => {
  try {
    const response = await api.delete(`/documents/${filename}`);
    return response.data;
  } catch (error) {
    console.error('Failed to delete document:', error);
    throw error;
  }
};

export default api;

import axios from 'axios';

const aiAxios = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 60000,
});

export const api = {
  scanCode: async (code: string, language: string) => {
    const response = await aiAxios.post('/security/scan', { code, language });
    return response.data;
  },

  submitFeedback: async (feedbackId: string, isFalsePositive: boolean, comment?: string) => {
    const response = await aiAxios.post('/feedback/', {
      session_id: feedbackId,
      rating: isFalsePositive ? 1 : 5, // if false positive, low rating.
      comments: comment
    });
    return response.data;
  },

  generateDocs: async (code: string, language: string) => {
    const response = await aiAxios.post('/docs/', { code, language, doc_type: "technical" });
    return response.data;
  },

  generateCode: async (prompt: string) => {
    const response = await aiAxios.post('/code/', { task: prompt, language: "python", security_level: "high" });
    return response.data;
  },
  
  // [NEW] WebSocket connection for live UI streaming
  connectScanSocket: () => {
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/scan');
    return ws;
  }
};

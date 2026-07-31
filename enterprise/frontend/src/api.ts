import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const securityApi = {
  scanCode: async (code: string, language: string) => {
    const response = await api.post('/scan', { code, language });
    return response.data;
  },
};

export const aiApi = {
  chat: async (query: string) => {
    const response = await api.post('/chat', { query });
    return response.data;
  },
};

export default api;

import axios from 'axios';
import type {
  GenerateCodeRequest,
  GenerateCodeResponse,
  SecurityResult,
  AutoFixRequest,
  AutoFixResponse,
  DocGenerationRequest,
  DocGenerationResponse,
  HistoryFilters,
  Session,
  FeedbackRequest,
  DashboardMetrics,
  AnalyticsData,
  UserPreferences,
} from '../types';

// ==========================================
// Axios Instance
// ==========================================
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Could add auth tokens here in future
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const status = error.response.status;
      const message = error.response.data?.detail || error.message;

      if (status === 429) {
        console.warn('Rate limited — slow down requests');
      } else if (status >= 500) {
        console.error('Server error:', message);
      }
    } else if (error.request) {
      console.error('Network error — is the backend running?');
    }
    return Promise.reject(error);
  }
);

// ==========================================
// API Functions
// ==========================================

export const generateCode = async (
  request: GenerateCodeRequest
): Promise<GenerateCodeResponse> => {
  const { data } = await api.post<GenerateCodeResponse>('/api/generate', request);
  return data;
};

export const analyzeSecurity = async (code: string): Promise<SecurityResult> => {
  const { data } = await api.post<SecurityResult>('/api/security/analyze', { code });
  return data;
};

export const autoFix = async (request: AutoFixRequest): Promise<AutoFixResponse> => {
  const { data } = await api.post<AutoFixResponse>('/api/security/fix', request);
  return data;
};

export const generateDocs = async (
  request: DocGenerationRequest
): Promise<DocGenerationResponse> => {
  const { data } = await api.post<DocGenerationResponse>('/api/docs/generate', request);
  return data;
};

export const getHistory = async (filters?: Partial<HistoryFilters>): Promise<Session[]> => {
  const { data } = await api.get<Session[]>('/api/history', { params: filters });
  return data;
};

export const deleteSession = async (sessionId: string): Promise<void> => {
  await api.delete(`/api/history/${sessionId}`);
};

export const submitFeedback = async (request: FeedbackRequest): Promise<void> => {
  await api.post('/api/feedback', request);
};

export const getDashboardMetrics = async (): Promise<DashboardMetrics> => {
  const { data } = await api.get<DashboardMetrics>('/api/dashboard');
  return data;
};

export const getAnalytics = async (): Promise<AnalyticsData> => {
  const { data } = await api.get<AnalyticsData>('/api/analytics');
  return data;
};

export const getUserPreferences = async (): Promise<UserPreferences> => {
  const { data } = await api.get<UserPreferences>('/api/preferences');
  return data;
};

export const updateUserPreferences = async (
  preferences: Partial<UserPreferences>
): Promise<UserPreferences> => {
  const { data } = await api.put<UserPreferences>('/api/preferences', preferences);
  return data;
};

export const exportReport = async (
  sessionId: string,
  format: 'pdf' | 'json' | 'csv'
): Promise<Blob> => {
  const { data } = await api.get(`/api/export/${sessionId}`, {
    params: { format },
    responseType: 'blob',
  });
  return data;
};

export default api;

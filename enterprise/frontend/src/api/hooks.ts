import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  generateCode,
  analyzeSecurity,
  autoFix,
  generateDocs,
  getHistory,
  submitFeedback,
  getDashboardMetrics,
  getAnalytics,
  getUserPreferences,
  updateUserPreferences,
  deleteSession,
} from './client';
import type {
  GenerateCodeRequest,
  AutoFixRequest,
  DocGenerationRequest,
  HistoryFilters,
  FeedbackRequest,
  UserPreferences,
} from '../types';
import toast from 'react-hot-toast';

// ==========================================
// Dashboard
// ==========================================
export const useDashboardMetrics = () =>
  useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: getDashboardMetrics,
    refetchInterval: 30000,
    retry: 2,
  });

// ==========================================
// Code Generation
// ==========================================
export const useGenerateCode = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request: GenerateCodeRequest) => generateCode(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard-metrics'] });
      queryClient.invalidateQueries({ queryKey: ['history'] });
      toast.success('Code generated successfully!');
    },
    onError: (error: Error) => {
      toast.error(`Generation failed: ${error.message}`);
    },
  });
};

// ==========================================
// Security
// ==========================================
export const useAnalyzeSecurity = () =>
  useMutation({
    mutationFn: (code: string) => analyzeSecurity(code),
    onSuccess: () => {
      toast.success('Security scan complete');
    },
    onError: (error: Error) => {
      toast.error(`Scan failed: ${error.message}`);
    },
  });

export const useAutoFix = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request: AutoFixRequest) => autoFix(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard-metrics'] });
      toast.success('Vulnerabilities fixed!');
    },
    onError: (error: Error) => {
      toast.error(`Auto-fix failed: ${error.message}`);
    },
  });
};

// ==========================================
// Documentation
// ==========================================
export const useGenerateDocs = () =>
  useMutation({
    mutationFn: (request: DocGenerationRequest) => generateDocs(request),
    onSuccess: () => {
      toast.success('Documentation generated');
    },
    onError: (error: Error) => {
      toast.error(`Doc generation failed: ${error.message}`);
    },
  });

// ==========================================
// History
// ==========================================
export const useHistory = (filters?: Partial<HistoryFilters>) =>
  useQuery({
    queryKey: ['history', filters],
    queryFn: () => getHistory(filters),
    retry: 2,
  });

export const useDeleteSession = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) => deleteSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] });
      toast.success('Session deleted');
    },
    onError: (error: Error) => {
      toast.error(`Delete failed: ${error.message}`);
    },
  });
};

// ==========================================
// Feedback
// ==========================================
export const useSubmitFeedback = () =>
  useMutation({
    mutationFn: (request: FeedbackRequest) => submitFeedback(request),
    onSuccess: () => {
      toast.success('Feedback submitted — thank you!');
    },
    onError: (error: Error) => {
      toast.error(`Feedback failed: ${error.message}`);
    },
  });

// ==========================================
// Analytics
// ==========================================
export const useAnalytics = () =>
  useQuery({
    queryKey: ['analytics'],
    queryFn: getAnalytics,
    refetchInterval: 60000,
    retry: 2,
  });

// ==========================================
// Preferences
// ==========================================
export const useUserPreferences = () =>
  useQuery({
    queryKey: ['preferences'],
    queryFn: getUserPreferences,
    retry: 1,
  });

export const useUpdatePreferences = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (preferences: Partial<UserPreferences>) =>
      updateUserPreferences(preferences),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['preferences'] });
      toast.success('Preferences saved');
    },
    onError: (error: Error) => {
      toast.error(`Failed to save preferences: ${error.message}`);
    },
  });
};

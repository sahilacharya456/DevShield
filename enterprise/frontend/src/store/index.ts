import { create } from 'zustand';
import type { AIStatus, Language, SecurityLevel, UserPreferences } from '../types';

// ==========================================
// Sidebar Store
// ==========================================
interface SidebarState {
  collapsed: boolean;
  toggle: () => void;
  setCollapsed: (collapsed: boolean) => void;
}

export const useSidebarStore = create<SidebarState>((set) => ({
  collapsed: false,
  toggle: () => set((state) => ({ collapsed: !state.collapsed })),
  setCollapsed: (collapsed) => set({ collapsed }),
}));

// ==========================================
// AI Status Store
// ==========================================
interface AIStatusState {
  status: AIStatus;
  provider: 'gemini' | 'claude';
  tokensRemaining: number;
  setStatus: (status: AIStatus) => void;
  setProvider: (provider: 'gemini' | 'claude') => void;
  decrementTokens: (count: number) => void;
}

export const useAIStatusStore = create<AIStatusState>((set) => ({
  status: 'active',
  provider: 'gemini',
  tokensRemaining: 1000000,
  setStatus: (status) => set({ status }),
  setProvider: (provider) => set({ provider }),
  decrementTokens: (count) =>
    set((state) => ({ tokensRemaining: Math.max(0, state.tokensRemaining - count) })),
}));

// ==========================================
// User Preferences Store
// ==========================================
interface PreferencesState {
  preferences: UserPreferences;
  updatePreference: <K extends keyof UserPreferences>(key: K, value: UserPreferences[K]) => void;
  resetPreferences: () => void;
}

const defaultPreferences: UserPreferences = {
  theme: 'dark',
  default_language: 'python',
  default_security_level: 'high',
  ai_provider: 'gemini',
  notifications_enabled: true,
  auto_scan: true,
  token_budget: 1000000,
};

export const usePreferencesStore = create<PreferencesState>((set) => ({
  preferences: defaultPreferences,
  updatePreference: (key, value) =>
    set((state) => ({
      preferences: { ...state.preferences, [key]: value },
    })),
  resetPreferences: () => set({ preferences: defaultPreferences }),
}));

// ==========================================
// Code Generator Store
// ==========================================
interface CodeGeneratorState {
  task: string;
  language: Language;
  securityLevel: SecurityLevel;
  generatedCode: string;
  isGenerating: boolean;
  confidenceScore: number;
  tokenCount: number;
  estimatedCost: number;
  generationPhase: string;
  setTask: (task: string) => void;
  setLanguage: (language: Language) => void;
  setSecurityLevel: (level: SecurityLevel) => void;
  setGeneratedCode: (code: string) => void;
  setIsGenerating: (generating: boolean) => void;
  setConfidenceScore: (score: number) => void;
  setTokenCount: (count: number) => void;
  setEstimatedCost: (cost: number) => void;
  setGenerationPhase: (phase: string) => void;
  reset: () => void;
}

export const useCodeGeneratorStore = create<CodeGeneratorState>((set) => ({
  task: '',
  language: 'python',
  securityLevel: 'high',
  generatedCode: '',
  isGenerating: false,
  confidenceScore: 0,
  tokenCount: 0,
  estimatedCost: 0,
  generationPhase: '',
  setTask: (task) => set({ task }),
  setLanguage: (language) => set({ language }),
  setSecurityLevel: (securityLevel) => set({ securityLevel }),
  setGeneratedCode: (generatedCode) => set({ generatedCode }),
  setIsGenerating: (isGenerating) => set({ isGenerating }),
  setConfidenceScore: (confidenceScore) => set({ confidenceScore }),
  setTokenCount: (tokenCount) => set({ tokenCount }),
  setEstimatedCost: (estimatedCost) => set({ estimatedCost }),
  setGenerationPhase: (generationPhase) => set({ generationPhase }),
  reset: () =>
    set({
      task: '',
      generatedCode: '',
      isGenerating: false,
      confidenceScore: 0,
      tokenCount: 0,
      estimatedCost: 0,
      generationPhase: '',
    }),
}));

// ==========================================
// Notification Store
// ==========================================
interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: string;
  read: boolean;
}

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearAll: () => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [
    {
      id: '1',
      title: 'Welcome to DevShield',
      message: 'Your AI-powered secure coding platform is ready.',
      type: 'info',
      timestamp: new Date().toISOString(),
      read: false,
    },
    {
      id: '2',
      title: 'Security Update',
      message: '3 new vulnerability patterns added to scanner.',
      type: 'success',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      read: false,
    },
  ],
  unreadCount: 2,
  addNotification: (notification) =>
    set((state) => {
      const newNotification: Notification = {
        ...notification,
        id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        read: false,
      };
      return {
        notifications: [newNotification, ...state.notifications],
        unreadCount: state.unreadCount + 1,
      };
    }),
  markAsRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),
  markAllAsRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
      unreadCount: 0,
    })),
  clearAll: () => set({ notifications: [], unreadCount: 0 }),
}));

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { AnimatePresence } from 'framer-motion';
import { lazy, Suspense } from 'react';

import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import ErrorBoundary from './components/ErrorBoundary';
import { DashboardSkeleton, EditorSkeleton } from './components/Skeleton';
import { useSidebarStore } from './store';

// Lazy-loaded pages
const Dashboard = lazy(() => import('./pages/Dashboard'));
const CodeGenerator = lazy(() => import('./pages/CodeGenerator'));
const SecurityAnalyzer = lazy(() => import('./pages/SecurityAnalyzer'));
const DocGenerator = lazy(() => import('./pages/DocGenerator'));
const History = lazy(() => import('./pages/History'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Settings = lazy(() => import('./pages/Settings'));

// React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

function AppLayout() {
  const collapsed = useSidebarStore((s) => s.collapsed);

  return (
    <div className="flex min-h-screen bg-[#0D0D0F]">
      <Sidebar />
      <main
        className="flex-1 flex flex-col transition-all duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]"
        style={{ marginLeft: collapsed ? 72 : 260 }}
      >
        <TopBar />
        <div className="flex-1 overflow-y-auto">
          <ErrorBoundary>
            <AnimatePresence mode="wait">
              <Suspense fallback={<DashboardSkeleton />}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route
                    path="/generate"
                    element={
                      <Suspense fallback={<EditorSkeleton />}>
                        <CodeGenerator />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/security"
                    element={
                      <Suspense fallback={<EditorSkeleton />}>
                        <SecurityAnalyzer />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/docs"
                    element={
                      <Suspense fallback={<EditorSkeleton />}>
                        <DocGenerator />
                      </Suspense>
                    }
                  />
                  <Route path="/history" element={<History />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </Suspense>
            </AnimatePresence>
          </ErrorBoundary>
        </div>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppLayout />
        <Toaster
          position="bottom-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#1A1A1E',
              color: '#F1F5F9',
              border: '1px solid #2A2A30',
              borderRadius: '12px',
              fontSize: '14px',
            },
            success: {
              iconTheme: { primary: '#10B981', secondary: '#F1F5F9' },
            },
            error: {
              iconTheme: { primary: '#EF4444', secondary: '#F1F5F9' },
            },
          }}
        />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

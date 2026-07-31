import { motion } from 'framer-motion';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'card' | 'chart' | 'editor';
  lines?: number;
}

export function Skeleton({ className = '', variant = 'text', lines = 1 }: SkeletonProps) {
  if (variant === 'card') {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className={`glass-card p-6 ${className}`}
      >
        <div className="skeleton h-4 w-24 mb-4" />
        <div className="skeleton h-8 w-32 mb-3" />
        <div className="skeleton h-3 w-20" />
      </motion.div>
    );
  }

  if (variant === 'chart') {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className={`glass-card p-6 ${className}`}
      >
        <div className="skeleton h-4 w-32 mb-6" />
        <div className="flex items-end gap-2 h-40">
          {[60, 80, 45, 95, 70, 55, 85].map((h, i) => (
            <div key={i} className="flex-1">
              <div className="skeleton rounded-sm" style={{ height: `${h}%` }} />
            </div>
          ))}
        </div>
      </motion.div>
    );
  }

  if (variant === 'editor') {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className={`glass-card p-4 ${className}`}
      >
        <div className="flex gap-2 mb-4">
          <div className="skeleton w-3 h-3 rounded-full" />
          <div className="skeleton w-3 h-3 rounded-full" />
          <div className="skeleton w-3 h-3 rounded-full" />
        </div>
        {Array.from({ length: 12 }, (_, i) => (
          <div key={i} className="flex gap-3 mb-2">
            <div className="skeleton h-3 w-6" />
            <div className="skeleton h-3" style={{ width: `${30 + Math.random() * 50}%` }} />
          </div>
        ))}
      </motion.div>
    );
  }

  return (
    <div className={className}>
      {Array.from({ length: lines }, (_, i) => (
        <div
          key={i}
          className="skeleton h-3 mb-2"
          style={{ width: i === lines - 1 ? '60%' : '100%' }}
        />
      ))}
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="page-container space-y-8 animate-pulse">
      {/* Hero */}
      <div className="skeleton h-10 w-72 mb-2" />
      <div className="skeleton h-5 w-48" />

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} variant="card" />
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Skeleton variant="chart" />
        <Skeleton variant="chart" />
      </div>
    </div>
  );
}

export function EditorSkeleton() {
  return (
    <div className="page-container">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-120px)]">
        <div className="space-y-4">
          <Skeleton variant="editor" className="h-48" />
          <div className="skeleton h-10 w-40" />
        </div>
        <Skeleton variant="editor" className="h-full" />
      </div>
    </div>
  );
}

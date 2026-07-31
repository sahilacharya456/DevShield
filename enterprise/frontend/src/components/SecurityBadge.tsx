import { motion } from 'framer-motion';
import type { Severity } from '../types';

interface SecurityBadgeProps {
  severity: Severity;
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean;
}

const severityConfig: Record<Severity, { bg: string; text: string; border: string; glow: string }> = {
  Critical: {
    bg: 'rgba(239, 68, 68, 0.15)',
    text: '#EF4444',
    border: 'rgba(239, 68, 68, 0.3)',
    glow: '0 0 12px rgba(239, 68, 68, 0.3)',
  },
  High: {
    bg: 'rgba(245, 158, 11, 0.15)',
    text: '#F59E0B',
    border: 'rgba(245, 158, 11, 0.3)',
    glow: '0 0 12px rgba(245, 158, 11, 0.2)',
  },
  Medium: {
    bg: 'rgba(234, 179, 8, 0.15)',
    text: '#EAB308',
    border: 'rgba(234, 179, 8, 0.3)',
    glow: '0 0 12px rgba(234, 179, 8, 0.15)',
  },
  Low: {
    bg: 'rgba(59, 130, 246, 0.15)',
    text: '#3B82F6',
    border: 'rgba(59, 130, 246, 0.3)',
    glow: '0 0 12px rgba(59, 130, 246, 0.15)',
  },
};

const sizeClasses: Record<string, string> = {
  sm: 'text-[10px] px-2 py-0.5',
  md: 'text-[11px] px-2.5 py-1',
  lg: 'text-xs px-3 py-1.5',
};

export default function SecurityBadge({ severity, size = 'md', animated = true }: SecurityBadgeProps) {
  const config = severityConfig[severity];

  return (
    <motion.span
      className={`inline-flex items-center gap-1.5 rounded-full font-semibold uppercase tracking-wider ${sizeClasses[size]}`}
      style={{
        background: config.bg,
        color: config.text,
        border: `1px solid ${config.border}`,
      }}
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      whileHover={animated ? { scale: 1.05, boxShadow: config.glow } : undefined}
      transition={{ duration: 0.2 }}
    >
      {severity === 'Critical' && animated && (
        <motion.span
          className="w-1.5 h-1.5 rounded-full"
          style={{ backgroundColor: config.text }}
          animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      )}
      {severity}
    </motion.span>
  );
}

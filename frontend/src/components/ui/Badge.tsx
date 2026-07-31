import React from 'react';

interface BadgeProps {
  label: string;
  variant?: 'danger' | 'warning' | 'success' | 'info' | 'neutral';
}

export function Badge({ label, variant = 'neutral' }: BadgeProps) {
  const variants = {
    danger: 'border-ds-danger text-ds-danger bg-ds-danger/10',
    warning: 'border-ds-warning text-ds-warning bg-ds-warning/10',
    success: 'border-ds-success text-ds-success bg-ds-success/10',
    info: 'border-ds-info text-ds-info bg-ds-info/10',
    neutral: 'border-text-muted text-text-secondary bg-ds-elevated',
  };

  return (
    <span className={`px-2 py-0.5 rounded text-xs font-semibold tracking-wide uppercase border ${variants[variant]}`}>
      {label}
    </span>
  );
}

export function SeverityBadge({ severity }: { severity: string }) {
  const sev = severity.toUpperCase();
  const v = sev === 'CRITICAL' || sev === 'HIGH' ? 'danger' : sev === 'MEDIUM' ? 'warning' : sev === 'LOW' ? 'success' : 'info';
  return <Badge label={sev} variant={v} />;
}

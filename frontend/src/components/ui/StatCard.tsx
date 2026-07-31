import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: string;
  color?: 'blue' | 'indigo' | 'danger' | 'warning' | 'success' | 'info';
  trend?: string;
}

export function StatCard({ title, value, icon, color = 'blue', trend }: StatCardProps) {
  const colorMap = {
    blue: 'text-ds-blue',
    indigo: 'text-ds-indigo',
    danger: 'text-ds-danger',
    warning: 'text-ds-warning',
    success: 'text-ds-success',
    info: 'text-ds-info',
  };

  return (
    <div className="ds-card flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-bold text-text-muted uppercase tracking-wider">{title}</span>
        <span className="text-xl bg-ds-elevated w-8 h-8 rounded flex items-center justify-center border border-ds-border">
          {icon}
        </span>
      </div>
      <div className="flex items-end justify-between">
        <span className={`text-3xl font-bold ${colorMap[color]}`}>{value}</span>
        {trend && <span className="text-xs font-medium text-ds-success">{trend}</span>}
      </div>
    </div>
  );
}

import React from "react";

interface MetricCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: string;
  borderTopColor?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  icon,
  trend,
  borderTopColor = "#6366F1",
}) => {
  return (
    <div
      className="glass-card glass-card-hover p-4 relative overflow-hidden flex flex-col justify-between"
      style={{ borderTop: `3px solid ${borderTopColor}` }}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
          {label}
        </span>
        {icon && <div className="text-slate-400">{icon}</div>}
      </div>
      <div className="text-2xl font-extrabold text-slate-100 truncate">
        {value}
      </div>
      {trend && (
        <span className="text-xs text-slate-400 mt-1 font-medium">{trend}</span>
      )}
    </div>
  );
};

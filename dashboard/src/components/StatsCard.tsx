import { ArrowUp, ArrowDown } from 'lucide-react';
import type { StatsCardProps } from '../types';

const colorClasses = {
  blue: {
    bg: 'from-blue-500/20 to-blue-600/20',
    border: 'border-blue-500/30',
    icon: 'text-blue-400',
    text: 'text-blue-300',
    progress: 'bg-blue-500'
  },
  green: {
    bg: 'from-green-500/20 to-green-600/20',
    border: 'border-green-500/30',
    icon: 'text-green-400',
    text: 'text-green-300',
    progress: 'bg-green-500'
  },
  purple: {
    bg: 'from-purple-500/20 to-purple-600/20',
    border: 'border-purple-500/30',
    icon: 'text-purple-400',
    text: 'text-purple-300',
    progress: 'bg-purple-500'
  },
  orange: {
    bg: 'from-orange-500/20 to-orange-600/20',
    border: 'border-orange-500/30',
    icon: 'text-orange-400',
    text: 'text-orange-300',
    progress: 'bg-orange-500'
  }
};

export default function StatsCard({ title, value, icon, trend, color, progress }: StatsCardProps) {
  const colors = colorClasses[color];
  const isPositiveTrend = trend && trend.startsWith('+');

  return (
    <div className={`bg-gradient-to-br ${colors.bg} backdrop-blur-lg rounded-xl border ${colors.border} p-6 hover:scale-105 transition-transform duration-200`}>
      <div className="flex items-start justify-between mb-4">
        <div className={colors.icon}>
          {icon}
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-xs font-semibold ${isPositiveTrend ? 'text-green-400' : 'text-red-400'}`}>
            {isPositiveTrend ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
            {trend}
          </div>
        )}
      </div>

      <div className="space-y-2">
        <p className={`text-sm font-medium ${colors.text}`}>{title}</p>
        <p className="text-3xl font-bold text-white">{value}</p>
        
        {progress !== undefined && (
          <div className="w-full bg-white/10 rounded-full h-2 mt-3">
            <div 
              className={`h-full rounded-full ${colors.progress} transition-all duration-500`}
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
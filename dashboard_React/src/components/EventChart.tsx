import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp } from 'lucide-react';
import type { EventChartProps } from '../types';

export default function EventChart({ data }: EventChartProps) {
  // Format data for chart - handle both hourly (hour field) and interval (time_interval field) data
  const chartData = data.map(item => {
    const timeValue = item.hour || item.time_interval;
    const date = new Date(timeValue);
    return {
      time: date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
      }),
      events: item.event_count
    };
  });

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 p-6">
      <div className="flex items-center gap-3 mb-6">
        <TrendingUp className="w-6 h-6 text-purple-400" />
        <div>
          <h3 className="text-lg font-semibold text-white">Event Activity (10 min)</h3>
          <p className="text-sm text-purple-300">Event distribution (10s intervals)</p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={250}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorEvents" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#a78bfa" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#a78bfa" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis 
            dataKey="time" 
            stroke="rgba(255,255,255,0.5)" 
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="rgba(255,255,255,0.5)" 
            style={{ fontSize: '12px' }}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'rgba(17, 24, 39, 0.95)',
              border: '1px solid rgba(167, 139, 250, 0.3)',
              borderRadius: '8px',
              color: '#fff'
            }}
          />
          <Area 
            type="monotone" 
            dataKey="events" 
            stroke="#a78bfa" 
            strokeWidth={2}
            fillOpacity={1} 
            fill="url(#colorEvents)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
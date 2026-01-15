import { Activity, MousePointer, Search, Eye, PlayCircle, StopCircle, AlertTriangle } from 'lucide-react';
import type { RecentEventsProps } from '../types';

const eventConfig = {
  session_start: {
    icon: PlayCircle,
    color: 'text-green-400',
    bg: 'bg-green-500/20',
    label: 'Session Start'
  },
  session_end: {
    icon: StopCircle,
    color: 'text-blue-400',
    bg: 'bg-blue-500/20',
    label: 'Session End'
  },
  click: {
    icon: MousePointer,
    color: 'text-purple-400',
    bg: 'bg-purple-500/20',
    label: 'Click'
  },
  search: {
    icon: Search,
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/20',
    label: 'Search'
  },
  page_view: {
    icon: Eye,
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/20',
    label: 'Page View'
  },
  ip_rotation: {
    icon: Activity,
    color: 'text-orange-400',
    bg: 'bg-orange-500/20',
    label: 'IP Rotation'
  },
  error: {
    icon: AlertTriangle,
    color: 'text-red-400',
    bg: 'bg-red-500/20',
    label: 'Error'
  }
};

function getEventDetails(event: any): string {
  const data = event.data;
  
  switch (event.event_type) {
    case 'click':
      return `Position: ${data.position || 'N/A'}`;
    case 'search':
      return `Query: "${data.query || 'N/A'}"`;
    case 'page_view':
      return `Dwell: ${data.dwell_time ? data.dwell_time.toFixed(1) + 's' : 'N/A'}`;
    case 'session_start':
      return `Device: ${data.device_type || 'N/A'}`;
    case 'session_end':
      return `Duration: ${data.actual_duration ? data.actual_duration.toFixed(1) + 's' : 'N/A'}`;
    case 'ip_rotation':
      return `${data.old_ip || 'N/A'} → ${data.new_ip || 'N/A'}`;
    case 'error':
      return data.error || 'Unknown error';
    default:
      return '';
  }
}

export default function RecentEvents({ data }: RecentEventsProps) {
  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 overflow-hidden">
      <div className="p-6 border-b border-white/20">
        <div className="flex items-center gap-3">
          <Activity className="w-6 h-6 text-purple-400" />
          <div>
            <h2 className="text-xl font-bold text-white">Recent Events</h2>
            <p className="text-sm text-purple-300">Last {data.length} events in real-time</p>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-white/5">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-purple-300 uppercase tracking-wider">
                Time
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-purple-300 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-purple-300 uppercase tracking-wider">
                Session
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-purple-300 uppercase tracking-wider">
                IP Address
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-purple-300 uppercase tracking-wider">
                Details
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {data.map((event) => {
              const config = eventConfig[event.event_type] || eventConfig.error;
              const Icon = config.icon;
              const timestamp = new Date(event.timestamp);
              const timeStr = timestamp.toLocaleTimeString();
              const sessionShort = event.session_id ? event.session_id.slice(-8) : 'N/A';
              const details = getEventDetails(event);

              return (
                <tr key={event.id} className="hover:bg-white/5 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-xs text-purple-300">{timeStr}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-semibold ${config.bg} ${config.color}`}>
                      <Icon className="w-3 h-3" />
                      {config.label}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <code className="text-xs text-white bg-white/10 px-2 py-1 rounded">
                      {sessionShort}
                    </code>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-mono text-sm text-purple-300">{event.ip_address}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-white">{details}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {data.length === 0 && (
          <div className="text-center py-12">
            <p className="text-purple-300">No events available</p>
          </div>
        )}
      </div>
    </div>
  );
}
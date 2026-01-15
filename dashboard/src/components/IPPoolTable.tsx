import { CheckCircle, AlertCircle, XCircle, Globe } from 'lucide-react';
import type { IPPoolTableProps } from '../types';

const statusConfig = {
  active: {
    icon: CheckCircle,
    color: 'text-green-400',
    bg: 'bg-green-500/20',
    border: 'border-green-500/30',
    label: 'Active'
  },
  warning: {
    icon: AlertCircle,
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/20',
    border: 'border-yellow-500/30',
    label: 'Warning'
  },
  blocked: {
    icon: XCircle,
    color: 'text-red-400',
    bg: 'bg-red-500/20',
    border: 'border-red-500/30',
    label: 'Blocked'
  }
};

export default function IPPoolTable({ data }: IPPoolTableProps) {
  // Sort by total requests descending
  const sortedData = [...data].sort((a, b) => b.total_requests - a.total_requests);

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 overflow-hidden">
      <div className="p-6 border-b border-white/20">
        <div className="flex items-center gap-3">
          <Globe className="w-6 h-6 text-purple-400" />
          <div>
            <h2 className="text-xl font-bold text-white">IP Pool Status</h2>
            <p className="text-sm text-purple-300">{sortedData.length} IPs monitored</p>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-white/5">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-purple-300 uppercase tracking-wider">
                IP Address
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-purple-300 uppercase tracking-wider">
                Country
              </th>
              <th className="px-6 py-3 text-right text-xs font-semibold text-purple-300 uppercase tracking-wider">
                Requests
              </th>
              <th className="px-6 py-3 text-right text-xs font-semibold text-purple-300 uppercase tracking-wider">
                Success
              </th>
              <th className="px-6 py-3 text-right text-xs font-semibold text-purple-300 uppercase tracking-wider">
                Success Rate
              </th>
              <th className="px-6 py-3 text-center text-xs font-semibold text-purple-300 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {sortedData.map((ip) => {
              const config = statusConfig[ip.status];
              const StatusIcon = config.icon;
              const successRate = (ip.success_rate * 100).toFixed(1);

              return (
                <tr key={ip.ip_address} className="hover:bg-white/5 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-mono text-sm text-white">{ip.ip_address}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-purple-300">{ip.country}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <span className="text-sm text-white">{ip.total_requests.toLocaleString()}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <span className="text-sm text-white">{ip.successful_requests.toLocaleString()}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="flex items-center justify-end gap-2">
                      <div className="w-16 bg-white/10 rounded-full h-1.5">
                        <div 
                          className={`h-full rounded-full ${
                            parseFloat(successRate) >= 85 ? 'bg-green-500' : 
                            parseFloat(successRate) >= 70 ? 'bg-yellow-500' : 
                            'bg-red-500'
                          }`}
                          style={{ width: `${successRate}%` }}
                        />
                      </div>
                      <span className="text-sm font-semibold text-white">{successRate}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex justify-center">
                      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${config.bg} ${config.color} border ${config.border}`}>
                        <StatusIcon className="w-3 h-3" />
                        {config.label}
                      </span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {sortedData.length === 0 && (
          <div className="text-center py-12">
            <p className="text-purple-300">No IP data available</p>
          </div>
        )}
      </div>
    </div>
  );
}
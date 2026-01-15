import { useEffect, useState } from 'react';
import { Activity, Server, TrendingUp, AlertCircle } from 'lucide-react';
import StatsCard from './components/StatsCard';
import IPPoolTable from './components/IPPoolTable';
import RecentEvents from './components/RecentEvents';
import EventChart from './components/EventChart';
import { fetchSummaryStats, fetchIPPool, fetchRecentEvents, fetchIntervalActivity10s } from './api/dashboard';
import type { SummaryStats, IPStats, Event, HourlyActivity } from './types';

function App() {
  const [stats, setStats] = useState<SummaryStats | null>(null);
  const [ipPool, setIPPool] = useState<IPStats[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [intervalData, setIntervalData] = useState<HourlyActivity[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Fetch all data
  const fetchAllData = async () => {
    try {
      const [summaryData, ipData, eventsData, intervalData] = await Promise.all([
        fetchSummaryStats(),
        fetchIPPool(),
        fetchRecentEvents(30),
        fetchIntervalActivity10s(10)
      ]);

      setStats(summaryData);
      setIPPool(ipData);
      setEvents(eventsData);
      setIntervalData(intervalData);
      setIsConnected(true);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to fetch data:', error);
      setIsConnected(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchAllData();
  }, []);

  // Auto-refresh every 3 seconds
  useEffect(() => {
    const interval = setInterval(fetchAllData, 3000);
    return () => clearInterval(interval);
  }, []);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:3000');

    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'new_events') {
        console.log('📡 Received new events:', message.data.length);
        fetchAllData(); // Refresh all data when new events arrive
      }
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  const successRate = stats ? (stats.overallSuccessRate * 100).toFixed(1) : '0';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-lg border-b border-white/20">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Activity className="w-8 h-8 text-purple-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">Human B.O.T Dashboard</h1>
                <p className="text-sm text-purple-300">Real-time Traffic Simulation Monitor</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
                <span className="text-white">{isConnected ? 'Live' : 'Disconnected'}</span>
              </div>
              <div className="text-xs text-purple-300">
                Last update: {lastUpdate.toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Total Sessions"
            value={stats?.totalSessions.toLocaleString() || '0'}
            icon={<Server className="w-6 h-6" />}
            trend="+12.5%"
            color="blue"
          />
          <StatsCard
            title="Total Clicks"
            value={stats?.totalClicks.toLocaleString() || '0'}
            icon={<TrendingUp className="w-6 h-6" />}
            trend="+8.3%"
            color="green"
          />
          <StatsCard
            title="Total Events"
            value={stats?.totalEvents.toLocaleString() || '0'}
            icon={<Activity className="w-6 h-6" />}
            trend="+15.7%"
            color="purple"
          />
          <StatsCard
            title="Success Rate"
            value={`${successRate}%`}
            icon={<AlertCircle className="w-6 h-6" />}
            trend={parseFloat(successRate) > 85 ? '+2.1%' : '-1.2%'}
            color="orange"
            progress={parseFloat(successRate)}
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <EventChart data={intervalData} />
          
          <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">System Status</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-purple-300">Active IPs</span>
                <span className="text-white font-semibold">{stats?.activeIPs || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-purple-300">Total IPs</span>
                <span className="text-white font-semibold">{stats?.totalIPs || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-purple-300">Total Requests</span>
                <span className="text-white font-semibold">{stats?.totalRequests || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-purple-300">Errors</span>
                <span className="text-white font-semibold">{stats?.totalErrors || 0}</span>
              </div>
            </div>
          </div>
        </div>

        {/* IP Pool Table */}
        <IPPoolTable data={ipPool} />

        {/* Recent Events */}
        <RecentEvents data={events} />
      </main>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-6 py-4 text-center text-sm text-purple-300">
        <p>Human B.O.T MVP • Real-time Dashboard • {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;
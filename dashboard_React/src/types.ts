// API Response Types

export interface SummaryStats {
    totalEvents: number;
    totalSessions: number;
    totalClicks: number;
    totalErrors: number;
    totalIPs: number;
    activeIPs: number;
    totalRequests: number;
    totalSuccess: number;
    overallSuccessRate: number;
  }
  
  export interface IPStats {
    ip_address: string;
    proxy_type: string;
    country: string;
    total_requests: number;
    successful_requests: number;
    failed_requests: number;
    success_rate: number;
    reputation_score: number;
    status: 'active' | 'warning' | 'blocked';
    last_used: string | null;
  }
  
  export interface Event {
    id: string;
    timestamp: string;
    event_type: 'session_start' | 'session_end' | 'click' | 'search' | 'page_view' | 'ip_rotation' | 'error';
    session_id: string;
    ip_address: string;
    data: EventData;
  }
  
  export interface EventData {
    [key: string]: any;
    query?: string;
    position?: number;
    dwell_time?: number;
    device_type?: string;
    actual_duration?: number;
    url?: string;
  }
  
  export interface HourlyActivity {
    hour?: string;
    time_interval?: string;
    event_count: number;
  }
  
  // Component Props Types
  
  export interface StatsCardProps {
    title: string;
    value: string;
    icon: React.ReactNode;
    trend?: string;
    color: 'blue' | 'green' | 'purple' | 'orange';
    progress?: number;
  }
  
  export interface IPPoolTableProps {
    data: IPStats[];
  }
  
  export interface RecentEventsProps {
    data: Event[];
  }
  
  export interface EventChartProps {
    data: HourlyActivity[];
  }
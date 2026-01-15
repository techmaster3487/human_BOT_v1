import type { SummaryStats, IPStats, Event, HourlyActivity } from '../types';

const API_BASE = 'http://localhost:3000/api';

// Fetch summary statistics
export async function fetchSummaryStats(): Promise<SummaryStats> {
  const response = await fetch(`${API_BASE}/stats/summary`);
  if (!response.ok) {
    throw new Error('Failed to fetch summary stats');
  }
  return response.json();
}

// Fetch IP pool data
export async function fetchIPPool(): Promise<IPStats[]> {
  const response = await fetch(`${API_BASE}/stats/ip-pool`);
  if (!response.ok) {
    throw new Error('Failed to fetch IP pool');
  }
  return response.json();
}

// Fetch recent events
export async function fetchRecentEvents(limit: number = 30): Promise<Event[]> {
  const response = await fetch(`${API_BASE}/events/recent?limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to fetch events');
  }
  return response.json();
}

// Fetch hourly activity
export async function fetchHourlyActivity(hours: number = 24): Promise<HourlyActivity[]> {
  const response = await fetch(`${API_BASE}/stats/hourly?hours=${hours}`);
  if (!response.ok) {
    throw new Error('Failed to fetch hourly activity');
  }
  return response.json();
}

// Fetch 10-second interval activity
export async function fetchIntervalActivity10s(minutes: number = 10): Promise<HourlyActivity[]> {
  const response = await fetch(`${API_BASE}/stats/interval-10s?minutes=${minutes}`);
  if (!response.ok) {
    throw new Error('Failed to fetch 10-second interval activity');
  }
  return response.json();
}

// Fetch events by type
export async function fetchEventsByType(): Promise<{ event_type: string; count: number }[]> {
  const response = await fetch(`${API_BASE}/events/by-type`);
  if (!response.ok) {
    throw new Error('Failed to fetch events by type');
  }
  return response.json();
}

// Fetch session details
export async function fetchSessionDetails(sessionId: string): Promise<any> {
  const response = await fetch(`${API_BASE}/session/${sessionId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch session details');
  }
  return response.json();
}

// Health check
export async function checkHealth(): Promise<{ status: string; timestamp: string; database: string }> {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error('Health check failed');
  }
  return response.json();
}
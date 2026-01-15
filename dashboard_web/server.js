/**
 * Human B.O.T Web Dashboard - Node.js Backend
 * 
 * Installation:
 * npm init -y
 * npm install express sqlite3 cors ws
 * 
 * Usage:
 * node server.js
 */

const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const path = require('path');
const WebSocket = require('ws');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Database connection
const DB_PATH = path.join(__dirname, '..', 'data', 'events.db');
let db;

function initDatabase() {
    db = new sqlite3.Database(DB_PATH, (err) => {
        if (err) {
            console.error('❌ Database connection failed:', err.message);
            console.error('Make sure to run demo.py first to create the database!');
            process.exit(1);
        }
        console.log('✅ Connected to SQLite database');
    });
}

// ============================================================================
// API ENDPOINTS
// ============================================================================

// Summary Statistics
app.get('/api/stats/summary', (req, res) => {
    const queries = {
        totalEvents: 'SELECT COUNT(*) as count FROM events',
        totalSessions: 'SELECT COUNT(*) as count FROM sessions',
        totalClicks: 'SELECT COUNT(*) as count FROM events WHERE event_type = "click"',
        totalErrors: 'SELECT COUNT(*) as count FROM events WHERE event_type = "error"',
        totalIPs: 'SELECT COUNT(*) as count FROM ip_stats',
        activeIPs: 'SELECT COUNT(*) as count FROM ip_stats WHERE status = "active"',
        totalRequests: 'SELECT SUM(total_requests) as total FROM ip_stats',
        totalSuccess: 'SELECT SUM(successful_requests) as total FROM ip_stats'
    };

    const stats = {};
    let completed = 0;
    const total = Object.keys(queries).length;

    Object.entries(queries).forEach(([key, query]) => {
        db.get(query, (err, row) => {
            if (err) {
                console.error(`Error fetching ${key}:`, err);
                stats[key] = 0;
            } else {
                stats[key] = row.count || row.total || 0;
            }

            completed++;
            if (completed === total) {
                // Calculate success rate
                stats.overallSuccessRate = stats.totalRequests > 0 
                    ? stats.totalSuccess / stats.totalRequests 
                    : 0;

                res.json(stats);
            }
        });
    });
});

// IP Pool Statistics
app.get('/api/stats/ip-pool', (req, res) => {
    const query = `
        SELECT 
            ip_address,
            proxy_type,
            country,
            total_requests,
            successful_requests,
            failed_requests,
            success_rate,
            reputation_score,
            status,
            last_used
        FROM ip_stats
        ORDER BY total_requests DESC
        LIMIT 20
    `;

    db.all(query, (err, rows) => {
        if (err) {
            console.error('Error fetching IP stats:', err);
            return res.status(500).json({ error: err.message });
        }
        res.json(rows || []);
    });
});

// Recent Events
app.get('/api/events/recent', (req, res) => {
    const limit = parseInt(req.query.limit) || 50;
    
    const query = `
        SELECT 
            id,
            timestamp,
            event_type,
            session_id,
            ip_address,
            data
        FROM events
        ORDER BY timestamp DESC
        LIMIT ?
    `;

    db.all(query, [limit], (err, rows) => {
        if (err) {
            console.error('Error fetching events:', err);
            return res.status(500).json({ error: err.message });
        }

        // Parse JSON data field
        const events = rows.map(row => ({
            ...row,
            data: typeof row.data === 'string' ? JSON.parse(row.data) : row.data
        }));

        res.json(events);
    });
});

// Events by Type
app.get('/api/events/by-type', (req, res) => {
    const query = `
        SELECT 
            event_type,
            COUNT(*) as count
        FROM events
        GROUP BY event_type
        ORDER BY count DESC
    `;

    db.all(query, (err, rows) => {
        if (err) {
            console.error('Error fetching event types:', err);
            return res.status(500).json({ error: err.message });
        }
        res.json(rows || []);
    });
});

// Sessions Statistics
app.get('/api/stats/sessions', (req, res) => {
    const queries = {
        byStatus: `
            SELECT status, COUNT(*) as count 
            FROM sessions 
            GROUP BY status
        `,
        byDevice: `
            SELECT device_type, COUNT(*) as count 
            FROM sessions 
            GROUP BY device_type
        `,
        avgDuration: `
            SELECT AVG(duration) as avg_duration 
            FROM sessions 
            WHERE duration IS NOT NULL
        `,
        avgClicks: `
            SELECT AVG(total_clicks) as avg_clicks 
            FROM sessions
        `
    };

    const stats = {};
    let completed = 0;
    const total = Object.keys(queries).length;

    // Fetch status distribution
    db.all(queries.byStatus, (err, rows) => {
        stats.byStatus = rows || [];
        if (++completed === total) res.json(stats);
    });

    // Fetch device distribution
    db.all(queries.byDevice, (err, rows) => {
        stats.byDevice = rows || [];
        if (++completed === total) res.json(stats);
    });

    // Fetch average duration
    db.get(queries.avgDuration, (err, row) => {
        stats.avgDuration = row?.avg_duration || 0;
        if (++completed === total) res.json(stats);
    });

    // Fetch average clicks
    db.get(queries.avgClicks, (err, row) => {
        stats.avgClicks = row?.avg_clicks || 0;
        if (++completed === total) res.json(stats);
    });
});

// Hourly Activity
app.get('/api/stats/hourly', (req, res) => {
    const hours = parseInt(req.query.hours) || 24;
    
    const query = `
        SELECT 
            strftime('%Y-%m-%d %H:00', timestamp) as hour,
            COUNT(*) as event_count
        FROM events
        WHERE timestamp >= datetime('now', '-${hours} hours')
        GROUP BY hour
        ORDER BY hour ASC
    `;

    db.all(query, (err, rows) => {
        if (err) {
            console.error('Error fetching hourly stats:', err);
            return res.status(500).json({ error: err.message });
        }
        res.json(rows || []);
    });
});

// 10-Second Interval Activity
app.get('/api/stats/interval-10s', (req, res) => {
    const minutes = parseInt(req.query.minutes) || 10; // Default to last 10 minutes
    
    // SQLite query to group events into 10-second intervals
    // We truncate seconds to the nearest 10-second mark
    const query = `
        SELECT 
            datetime(
                (strftime('%s', timestamp) / 10) * 10,
                'unixepoch'
            ) as time_interval,
            COUNT(*) as event_count
        FROM events
        WHERE timestamp >= datetime('now', '-${minutes} minutes')
        GROUP BY time_interval
        ORDER BY time_interval ASC
    `;

    db.all(query, (err, rows) => {
        if (err) {
            console.error('Error fetching 10-second interval stats:', err);
            return res.status(500).json({ error: err.message });
        }
        res.json(rows || []);
    });
});

// Session Details
app.get('/api/session/:id', (req, res) => {
    const sessionId = req.params.id;
    
    const sessionQuery = `
        SELECT * FROM sessions WHERE id = ?
    `;
    
    const eventsQuery = `
        SELECT * FROM events WHERE session_id = ? ORDER BY timestamp ASC
    `;

    db.get(sessionQuery, [sessionId], (err, session) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (!session) {
            return res.status(404).json({ error: 'Session not found' });
        }

        db.all(eventsQuery, [sessionId], (err, events) => {
            if (err) {
                return res.status(500).json({ error: err.message });
            }

            res.json({
                session,
                events: events.map(e => ({
                    ...e,
                    data: typeof e.data === 'string' ? JSON.parse(e.data) : e.data
                }))
            });
        });
    });
});

// Top Search Queries
app.get('/api/stats/top-queries', (req, res) => {
    const limit = parseInt(req.query.limit) || 10;
    
    const query = `
        SELECT 
            json_extract(data, '$.query') as query,
            COUNT(*) as count
        FROM events
        WHERE event_type = 'search' 
        AND json_extract(data, '$.query') IS NOT NULL
        GROUP BY query
        ORDER BY count DESC
        LIMIT ?
    `;

    db.all(query, [limit], (err, rows) => {
        if (err) {
            console.error('Error fetching top queries:', err);
            return res.status(500).json({ error: err.message });
        }
        res.json(rows || []);
    });
});

// System Health
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        database: db ? 'connected' : 'disconnected'
    });
});

// ============================================================================
// WEBSOCKET FOR REAL-TIME UPDATES
// ============================================================================

const wss = new WebSocket.Server({ noServer: true });

wss.on('connection', (ws) => {
    console.log('📡 WebSocket client connected');
    
    ws.on('close', () => {
        console.log('📡 WebSocket client disconnected');
    });
});

// Broadcast function for real-time updates
function broadcastUpdate(type, data) {
    wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify({ type, data }));
        }
    });
}

// Poll for new events and broadcast
let lastEventId = null;
setInterval(() => {
    const query = lastEventId 
        ? `SELECT * FROM events WHERE id > ? ORDER BY id DESC LIMIT 10`
        : `SELECT * FROM events ORDER BY id DESC LIMIT 1`;
    
    db.all(query, lastEventId ? [lastEventId] : [], (err, rows) => {
        if (err || !rows || rows.length === 0) return;
        
        const events = rows.map(row => ({
            ...row,
            data: typeof row.data === 'string' ? JSON.parse(row.data) : row.data
        }));
        
        lastEventId = events[0].id;
        broadcastUpdate('new_events', events);
    });
}, 2000); // Check every 2 seconds

// ============================================================================
// SERVER SETUP
// ============================================================================

const server = app.listen(PORT, () => {
    console.log('');
    console.log('🤖 Human B.O.T Web Dashboard');
    console.log('========================================');
    console.log(`✅ Server running on http://localhost:${PORT}`);
    console.log(`✅ WebSocket available for real-time updates`);
    console.log('========================================');
    console.log('');
    console.log('📊 Available endpoints:');
    console.log('   GET  /api/stats/summary');
    console.log('   GET  /api/stats/ip-pool');
    console.log('   GET  /api/events/recent?limit=50');
    console.log('   GET  /api/events/by-type');
    console.log('   GET  /api/stats/sessions');
    console.log('   GET  /api/stats/hourly?hours=24');
    console.log('   GET  /api/session/:id');
    console.log('   GET  /api/stats/top-queries?limit=10');
    console.log('   GET  /api/health');
    console.log('');
    console.log('🌐 Open browser: http://localhost:3000');
    console.log('');
});

// WebSocket upgrade
server.on('upgrade', (request, socket, head) => {
    wss.handleUpgrade(request, socket, head, (ws) => {
        wss.emit('connection', ws, request);
    });
});

// Initialize database
initDatabase();

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n\n🛑 Shutting down server...');
    if (db) {
        db.close((err) => {
            if (err) {
                console.error('Error closing database:', err);
            }
            console.log('✅ Database connection closed');
            process.exit(0);
        });
    } else {
        process.exit(0);
    }
});
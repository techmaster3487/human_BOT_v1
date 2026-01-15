"""
Human B.O.T Dashboard - FastAPI Backend Server

This is a backend-only API server that provides REST endpoints and WebSocket
connections for the React frontend dashboard.

Installation:
    pip install -r requirements.txt

Usage:
    uvicorn main:app --host 0.0.0.0 --port 3000 --reload
"""

import json
import sqlite3
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(
    title="Human B.O.T Dashboard API",
    description="API Backend Server for Human B.O.T Dashboard",
    version="1.0.0"
)

# CORS middleware - Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DB_PATH = Path(__file__).parent.parent / "data" / "events.db"
db: Optional[sqlite3.Connection] = None

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("📡 WebSocket client connected")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print("📡 WebSocket client disconnected")

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# Database helper functions
def get_db():
    """Get database connection"""
    global db
    if db is None:
        db = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        db.row_factory = sqlite3.Row
    return db

def init_database():
    """Initialize database connection"""
    try:
        conn = get_db()
        # Test connection
        conn.execute("SELECT 1")
        print("✅ Connected to SQLite database")
    except sqlite3.Error as e:
        print(f"❌ Database connection failed: {e}")
        print("Make sure to run demo.py first to create the database!")
        raise

# Response models
class SummaryStats(BaseModel):
    totalEvents: int
    totalSessions: int
    totalClicks: int
    totalErrors: int
    totalIPs: int
    activeIPs: int
    totalRequests: int
    totalSuccess: int
    overallSuccessRate: float

class IPStats(BaseModel):
    ip_address: str
    proxy_type: str
    country: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    reputation_score: float
    status: str
    last_used: Optional[str] = None

class Event(BaseModel):
    id: str
    timestamp: str
    event_type: str
    session_id: str
    ip_address: str
    data: Dict[str, Any]

class HourlyActivity(BaseModel):
    hour: Optional[str] = None
    time_interval: Optional[str] = None
    event_count: int

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/api/stats/summary", response_model=SummaryStats)
async def get_summary_stats():
    """Get summary statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        stats = {}
        
        # Total events
        cursor.execute("SELECT COUNT(*) as count FROM events")
        stats["totalEvents"] = cursor.fetchone()["count"] or 0
        
        # Total sessions
        cursor.execute("SELECT COUNT(*) as count FROM sessions")
        stats["totalSessions"] = cursor.fetchone()["count"] or 0
        
        # Total clicks
        cursor.execute('SELECT COUNT(*) as count FROM events WHERE event_type = "click"')
        stats["totalClicks"] = cursor.fetchone()["count"] or 0
        
        # Total errors
        cursor.execute('SELECT COUNT(*) as count FROM events WHERE event_type = "error"')
        stats["totalErrors"] = cursor.fetchone()["count"] or 0
        
        # Total IPs
        cursor.execute("SELECT COUNT(*) as count FROM ip_stats")
        stats["totalIPs"] = cursor.fetchone()["count"] or 0
        
        # Active IPs
        cursor.execute('SELECT COUNT(*) as count FROM ip_stats WHERE status = "active"')
        stats["activeIPs"] = cursor.fetchone()["count"] or 0
        
        # Total requests
        cursor.execute("SELECT SUM(total_requests) as total FROM ip_stats")
        result = cursor.fetchone()
        stats["totalRequests"] = result["total"] or 0
        
        # Total success
        cursor.execute("SELECT SUM(successful_requests) as total FROM ip_stats")
        result = cursor.fetchone()
        stats["totalSuccess"] = result["total"] or 0
        
        # Calculate success rate
        stats["overallSuccessRate"] = (
            stats["totalSuccess"] / stats["totalRequests"]
            if stats["totalRequests"] > 0
            else 0
        )
        
        return SummaryStats(**stats)
    except sqlite3.Error as e:
        print(f"Error fetching summary stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/ip-pool", response_model=List[IPStats])
async def get_ip_pool():
    """Get IP pool statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
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
        """)
        
        rows = cursor.fetchall()
        return [IPStats(**dict(row)) for row in rows]
    except sqlite3.Error as e:
        print(f"Error fetching IP stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events/recent", response_model=List[Event])
async def get_recent_events(limit: int = Query(50, ge=1, le=1000)):
    """Get recent events"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
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
        """, (limit,))
        
        rows = cursor.fetchall()
        events = []
        for row in rows:
            event_dict = dict(row)
            # Parse JSON data field
            if isinstance(event_dict["data"], str):
                try:
                    event_dict["data"] = json.loads(event_dict["data"])
                except:
                    event_dict["data"] = {}
            events.append(Event(**event_dict))
        
        return events
    except sqlite3.Error as e:
        print(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events/by-type")
async def get_events_by_type():
    """Get events grouped by type"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                event_type,
                COUNT(*) as count
            FROM events
            GROUP BY event_type
            ORDER BY count DESC
        """)
        
        rows = cursor.fetchall()
        return [{"event_type": row["event_type"], "count": row["count"]} for row in rows]
    except sqlite3.Error as e:
        print(f"Error fetching event types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/sessions")
async def get_sessions_stats():
    """Get session statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        stats = {}
        
        # By status
        cursor.execute("SELECT status, COUNT(*) as count FROM sessions GROUP BY status")
        stats["byStatus"] = [{"status": row["status"], "count": row["count"]} for row in cursor.fetchall()]
        
        # By device
        cursor.execute("SELECT device_type, COUNT(*) as count FROM sessions GROUP BY device_type")
        stats["byDevice"] = [{"device_type": row["device_type"], "count": row["count"]} for row in cursor.fetchall()]
        
        # Average duration
        cursor.execute("SELECT AVG(duration) as avg_duration FROM sessions WHERE duration IS NOT NULL")
        result = cursor.fetchone()
        stats["avgDuration"] = result["avg_duration"] or 0 if result else 0
        
        # Average clicks
        cursor.execute("SELECT AVG(total_clicks) as avg_clicks FROM sessions")
        result = cursor.fetchone()
        stats["avgClicks"] = result["avg_clicks"] or 0 if result else 0
        
        return stats
    except sqlite3.Error as e:
        print(f"Error fetching session stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/hourly", response_model=List[HourlyActivity])
async def get_hourly_activity(hours: int = Query(24, ge=1, le=168)):
    """Get hourly activity statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"""
            SELECT 
                strftime('%Y-%m-%d %H:00', timestamp) as hour,
                COUNT(*) as event_count
            FROM events
            WHERE timestamp >= datetime('now', '-{hours} hours')
            GROUP BY hour
            ORDER BY hour ASC
        """)
        
        rows = cursor.fetchall()
        return [HourlyActivity(hour=row["hour"], event_count=row["event_count"]) for row in rows]
    except sqlite3.Error as e:
        print(f"Error fetching hourly stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/interval-10s", response_model=List[HourlyActivity])
async def get_interval_activity_10s(minutes: int = Query(10, ge=1, le=60)):
    """Get 10-second interval activity statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"""
            SELECT 
                datetime(
                    (strftime('%s', timestamp) / 10) * 10,
                    'unixepoch'
                ) as time_interval,
                COUNT(*) as event_count
            FROM events
            WHERE timestamp >= datetime('now', '-{minutes} minutes')
            GROUP BY time_interval
            ORDER BY time_interval ASC
        """)
        
        rows = cursor.fetchall()
        return [HourlyActivity(time_interval=row["time_interval"], event_count=row["event_count"]) for row in rows]
    except sqlite3.Error as e:
        print(f"Error fetching 10-second interval stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}")
async def get_session_details(session_id: str):
    """Get session details with events"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Get session
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        session_row = cursor.fetchone()
        
        if not session_row:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get events
        cursor.execute("SELECT * FROM events WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
        event_rows = cursor.fetchall()
        
        events = []
        for row in event_rows:
            event_dict = dict(row)
            # Parse JSON data field
            if isinstance(event_dict["data"], str):
                try:
                    event_dict["data"] = json.loads(event_dict["data"])
                except:
                    event_dict["data"] = {}
            events.append(event_dict)
        
        return {
            "session": dict(session_row),
            "events": events
        }
    except HTTPException:
        raise
    except sqlite3.Error as e:
        print(f"Error fetching session details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/top-queries")
async def get_top_queries(limit: int = Query(10, ge=1, le=100)):
    """Get top search queries"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                json_extract(data, '$.query') as query,
                COUNT(*) as count
            FROM events
            WHERE event_type = 'search' 
            AND json_extract(data, '$.query') IS NOT NULL
            GROUP BY query
            ORDER BY count DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [{"query": row["query"], "count": row["count"]} for row in rows]
    except sqlite3.Error as e:
        print(f"Error fetching top queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """System health check"""
    global db
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if db else "disconnected"
    }

# ============================================================================
# WEBSOCKET FOR REAL-TIME UPDATES
# ============================================================================

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        # Keep connection alive - server will broadcast updates
        while True:
            # Wait for any message (or disconnect)
            try:
                # Wait for message with timeout to keep connection alive
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                # Optional: handle client messages if needed
            except asyncio.TimeoutError:
                # Connection is still alive, continue waiting
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task to poll for new events and broadcast
last_event_id: Optional[str] = None

async def poll_and_broadcast_events():
    """Poll database for new events and broadcast to WebSocket clients"""
    global last_event_id
    conn = get_db()
    cursor = conn.cursor()
    
    while True:
        try:
            if last_event_id:
                cursor.execute(
                    "SELECT * FROM events WHERE id > ? ORDER BY id DESC LIMIT 10",
                    (last_event_id,)
                )
            else:
                cursor.execute("SELECT * FROM events ORDER BY id DESC LIMIT 1")
            
            rows = cursor.fetchall()
            
            if rows:
                events = []
                for row in rows:
                    event_dict = dict(row)
                    # Parse JSON data field
                    if isinstance(event_dict["data"], str):
                        try:
                            event_dict["data"] = json.loads(event_dict["data"])
                        except:
                            event_dict["data"] = {}
                    events.append(event_dict)
                
                if events:
                    last_event_id = events[0]["id"]
                    await manager.broadcast({"type": "new_events", "data": events})
        except Exception as e:
            print(f"Error polling events: {e}")
        
        await asyncio.sleep(2)  # Check every 2 seconds

# 404 handler for non-API routes (must be after WebSocket)
@app.get("/{path:path}")
async def catch_all(path: str):
    """Catch-all handler for non-API routes"""
    if not path.startswith("api"):
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": "This is an API-only server. Please use the React frontend dashboard.",
                "availableEndpoints": "/api/stats/summary, /api/stats/ip-pool, /api/events/recent, etc."
            }
        )
    else:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": "API endpoint not found"
            }
        )

# ============================================================================
# STARTUP AND SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database and start background tasks"""
    init_database()
    # Start background task for polling events
    asyncio.create_task(poll_and_broadcast_events())
    print("")
    print("🤖 Human B.O.T Dashboard - API Backend (FastAPI)")
    print("=" * 40)
    print(f"✅ API Server running on http://localhost:3000")
    print(f"✅ WebSocket available at ws://localhost:3000/")
    print("=" * 40)
    print("")
    print("📊 Available API endpoints:")
    print("   GET  /api/stats/summary")
    print("   GET  /api/stats/ip-pool")
    print("   GET  /api/events/recent?limit=50")
    print("   GET  /api/events/by-type")
    print("   GET  /api/stats/sessions")
    print("   GET  /api/stats/hourly?hours=24")
    print("   GET  /api/stats/interval-10s?minutes=10")
    print("   GET  /api/session/:id")
    print("   GET  /api/stats/top-queries?limit=10")
    print("   GET  /api/health")
    print("")
    print("💡 Connect your React frontend to http://localhost:3000/api")
    print("")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    global db
    if db:
        db.close()
        print("✅ Database connection closed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)

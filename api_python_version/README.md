# Human B.O.T Dashboard - FastAPI Backend

This is a Python FastAPI backend server that provides REST API endpoints and WebSocket connections for the React frontend dashboard.

## Features

- ✅ REST API endpoints matching the Node.js backend
- ✅ WebSocket support for real-time updates
- ✅ SQLite database integration
- ✅ CORS enabled for React frontend
- ✅ Automatic API documentation (Swagger UI)

## Installation

1. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

## Usage

### Development Mode (with auto-reload):

```bash
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

### Production Mode:

```bash
uvicorn main:app --host 0.0.0.0 --port 3000
```

### Using Python directly:

```bash
python main.py
```

## API Endpoints

All endpoints are prefixed with `/api`:

- `GET /api/stats/summary` - Get summary statistics
- `GET /api/stats/ip-pool` - Get IP pool statistics
- `GET /api/events/recent?limit=50` - Get recent events
- `GET /api/events/by-type` - Get events grouped by type
- `GET /api/stats/sessions` - Get session statistics
- `GET /api/stats/hourly?hours=24` - Get hourly activity
- `GET /api/stats/interval-10s?minutes=10` - Get 10-second interval activity
- `GET /api/session/{session_id}` - Get session details
- `GET /api/stats/top-queries?limit=10` - Get top search queries
- `GET /api/health` - Health check

## WebSocket

WebSocket endpoint: `ws://localhost:3000/`

The server broadcasts new events every 2 seconds to all connected clients.

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

## Database

The server expects the SQLite database at `../data/events.db` (relative to this directory).

Make sure to run `demo.py` first to create the database schema.

## Notes

- The server runs on port 3000 by default
- CORS is enabled for all origins (configure `allow_origins` in production)
- The React frontend should connect to `http://localhost:3000/api`

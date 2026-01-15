# Human B.O.T MVP (Web Version)

A sophisticated web traffic simulation system that mimics human browsing behavior with IP rotation, session management, and real-time monitoring dashboard.

## 🎯 Features

- **Human-like Behavior Simulation**: Realistic browsing patterns with dwell time, scrolling, and click delays
- **IP Pool Management**: Rotate through IP addresses with weighted selection and reputation scoring
- **Session Engine**: Manage concurrent sessions with configurable duration and interaction patterns
- **Event Logging**: Comprehensive event tracking stored in SQLite database
- **Real-time Dashboard**: React-based web dashboard with live updates via WebSocket
- **Dual Backend Support**: Choose between Node.js (Express) or Python (FastAPI) backend
- **RESTful API**: Complete API for statistics, events, and session management

## 📋 Prerequisites

- **Python 3.11+** - For core simulation engine
- **Node.js 20+** - For backend API and frontend dashboard
- **npm** - Node package manager
- **SQLite** - Database (included with Python)

## 🚀 Quick Start

### 1. Prerequisites

Install the following software:
- **Python 3.11+** - Download from [python.org](https://www.python.org/)
- **Node.js 20+** - Download from [nodejs.org](https://nodejs.org/)

### 2. Clone the Repository

```bash
git clone <repository-url>
cd human-bot-mvp
```

### 3. Initial Setup

**Run the setup script first** (Windows):

```bash
setup.bat
```

This will:
- Create directory structure
- Set up Python virtual environment
- Install Python dependencies
- Create default configuration files
- Set up IP pool configuration

### 4. Start the System

After setup, you can start the components:

**Start Human Bot (Run Demo Sessions):**
```bash
run_human_bot.bat
```

**Start Backend API** (Choose one):

- **Python Backend (FastAPI):**
  ```bash
  start_python_backend.bat
  ```

- **Node.js Backend (Express):**
  ```bash
  start_node_backend.bat
  ```

**Start Dashboard Frontend:**
```bash
start_dashboard.bat
```

### 5. Access the Dashboard

Once all components are running:
- **Dashboard**: http://localhost:5173
- **API**: http://localhost:3000
- **API Docs** (FastAPI only): http://localhost:3000/docs

## 📁 Project Structure

```
human-bot-mvp/
├── config/                 # Configuration files
│   ├── config.yaml        # Main configuration
│   └── ips.csv            # IP pool configuration
├── core/                  # Core simulation engine
│   ├── session_engine.py  # Session management
│   ├── behavior_simulator.py  # Human behavior simulation
│   └── serp_simulator.py  # Search results simulation
├── ip_management/          # IP pool management
│   ├── ip_pool.py         # IP rotation and selection
│   └── scorer.py          # IP reputation scoring
├── event_logging/          # Event tracking
│   ├── event_logger.py    # Event logging system
│   ├── models.py          # Database models
│   └── storage.py        # Database operations
├── demo/                  # Demo scripts
│   ├── demo.py           # Main demo script
│   └── load_test.py      # Load testing
├── api_python_version/    # Python FastAPI backend
│   ├── main.py           # FastAPI application
│   └── requirements.txt  # Python dependencies
├── api_node_version/      # Node.js Express backend
│   ├── server.js         # Express server
│   └── package.json     # Node dependencies
├── dashboard/             # React frontend
│   ├── src/              # React source code
│   └── package.json     # Frontend dependencies
├── data/                  # Database storage
│   └── events.db         # SQLite database
└── logs/                  # Application logs
```

## ⚙️ Configuration

Edit `config/config.yaml` to customize behavior:

```yaml
simulation:
  concurrent_sessions: 5
  total_sessions: 100
  session_duration_range: [30, 180]  # seconds
  clicks_per_session_range: [2, 8]

ip_pool:
  source: "config/ips.csv"
  rotation_strategy: "weighted"  # round-robin, random, weighted
  reputation_threshold: 0.7
  max_requests_per_ip: 1000

behavior:
  dwell_time_mean: 45  # seconds
  dwell_time_stddev: 15
  scroll_probability: 0.8
  click_delay_range: [1, 5]
  search_queries:
    - "example search query"
    - "another query"

logging:
  database: "data/events.db"
  log_level: "INFO"
  log_file: "logs/bot.log"
```

## 🌐 API Endpoints

### Summary Statistics
- `GET /api/stats/summary` - Overall statistics
- `GET /api/stats/ip-pool` - IP pool status
- `GET /api/stats/sessions` - Session statistics

### Events
- `GET /api/events/recent?limit=50` - Recent events
- `GET /api/events/by-type` - Events grouped by type

### Analytics
- `GET /api/stats/hourly?hours=24` - Hourly activity
- `GET /api/stats/interval-10s?minutes=10` - 10-second interval activity
- `GET /api/stats/top-queries?limit=10` - Top search queries

### Session Details
- `GET /api/session/{session_id}` - Get session details with events

### Health Check
- `GET /api/health` - Server health status

### WebSocket
- `ws://localhost:3000/` - Real-time event updates

## 📊 Dashboard Features

The React dashboard provides:

- **Real-time Statistics**: Live updates of sessions, clicks, events
- **Event Activity Chart**: Visual representation of event distribution (10-second intervals)
- **IP Pool Status**: Monitor IP addresses, success rates, and status
- **Recent Events**: Live feed of all events
- **System Status**: Active IPs, total requests, error tracking

Access the dashboard at: `http://localhost:5173`

## 🛠️ Development

### Running Tests

```bash
pytest tests/
```

### Building Frontend

```bash
cd dashboard
npm run build
```

### Database Schema

The SQLite database (`data/events.db`) contains:

- **sessions**: Session metadata and statistics
- **events**: Individual events (clicks, searches, page views)
- **ip_stats**: IP pool statistics and reputation scores

## 📝 Usage Examples

### Run 100 Sessions with 10 Workers

```bash
python demo/demo.py --session 100 --workers 10
```

### Run Load Test

```bash
python demo/load_test.py
```

### Access API Documentation

**FastAPI (Python backend):**
- Swagger UI: http://localhost:3000/docs
- ReDoc: http://localhost:3000/redoc

## 🔧 Troubleshooting

### Database Connection Issues

If you see database errors, make sure:
1. The `data/` directory exists
2. Run `demo.py` at least once to create the schema
3. Check file permissions

### Port Already in Use

If port 3000 or 5173 is in use:
- Backend: Change `PORT` in `server.js` or `main.py`
- Frontend: Vite will automatically use next available port

### IP Pool Empty

Ensure `config/ips.csv` has valid IP addresses:
```csv
ip_address,proxy_type,country
192.168.1.1,residential,US
```

## 📄 License

ISC

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on the repository.

---

**Note**: This is an MVP (Minimum Viable Product) for demonstration purposes. Use responsibly and in accordance with applicable laws and terms of service.

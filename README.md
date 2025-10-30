# Real-Time Notification System

A FastAPI-based WebSocket application for real-time notifications with Memcached caching support.

## Project Structure

```
Real-Time-Notification-System/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application with WebSocket endpoints
│   ├── cache_manager.py     # Memcached connection and caching logic
│   └── requirements.txt     # Python dependencies
├── Dockerfile               # Docker image configuration
├── docker-compose.yml       # Multi-container Docker setup
└── README.md               # This file
```

## Features

- WebSocket-based real-time notifications
- Admin and user client types with authorization
- Memcached for caching recent notifications (with in-memory fallback)
- Docker Compose setup for easy deployment
- Stores last 5 notifications with 1-hour expiry

## Requirements

### Local Development
- Python 3.10 or higher
- pip (Python package manager)

### Docker Deployment
- Docker Desktop
- Docker Compose

## Installation and Setup

### Option 1: Run with Docker (Recommended)

1. Navigate to the project directory:
```powershell
cd C:\projects\memcach\Real-Time-Notification-System
```

2. Build and start the containers:
```powershell
docker-compose up --build
```

3. The application will be available at:
   - HTTP API: http://localhost:8000
   - WebSocket: ws://localhost:8000/ws

4. Stop the containers:
```powershell
docker-compose down
```

### Option 2: Run Locally

1. Navigate to the project directory:
```powershell
cd C:\projects\memcach\Real-Time-Notification-System
```

2. Create and activate virtual environment:
```powershell
python -m venv fastapienv
.\fastapienv\Scripts\Activate.ps1
```

3. Install dependencies:
```powershell
pip install -r .\app\requirements.txt
```

4. Run the application:
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. The application will be available at:
   - HTTP API: http://localhost:8000
   - WebSocket: ws://localhost:8000/ws

Note: When running locally without Memcached, the app will use in-memory storage as a fallback.

## API Endpoints

### HTTP Endpoints

**GET /** - Root endpoint
```
Returns: {"message": "FastAPI real-time notifications running!"}
```

**GET /health** - Health check with cache status
```
Returns: {
  "status": "healthy",
  "cache_status": "connected" or "fallback",
  "recent_notifications_count": 5,
  "connected_websockets": 2
}
```

**GET /messages** - Get recent notifications from cache
```
Returns: {"recent_messages": ["msg1", "msg2", ...]}
```

### WebSocket Endpoint

**ws://localhost:8000/ws** - WebSocket connection

Query Parameters:
- `client`: Client type (optional, default: "user")
  - `admin` - Authorized to send notifications
  - `user` - Receive-only

## WebSocket Usage

### Connect as Admin (Can send notifications)
```
ws://localhost:8000/ws?client=admin
```

Send any message to broadcast:
```
Hello World!
```

### Connect as User (Receive-only)
```
ws://localhost:8000/ws
```

Send admin-prefixed message to broadcast:
```
admin:Hello World!
```

Regular messages will receive "You are not authorized" response.

### Message Flow

1. When a client connects, they receive recent notifications (last 5 messages)
2. Admin clients or admin-prefixed messages are broadcast to all connected clients
3. Notifications are stored in cache with 1-hour expiry
4. Only the last 5 notifications are kept

## Testing with Postman

1. Create a new WebSocket Request in Postman
2. Enter URL: `ws://localhost:8000/ws?client=admin`
3. Click "Connect"
4. Send test messages:
   - `Test notification 1`
   - `Test notification 2`
5. Open multiple connections to see broadcasting in action

## Cache Manager Behavior

The cache manager handles Memcached connections with automatic fallback:

1. First tries to connect to `localhost:11211` (local development)
2. Then tries `memcached:11211` (Docker environment)
3. If both fail, uses in-memory storage (MockCacheClient)

Cache operations:
- Stores last 5 notifications
- 1-hour expiry for cached data
- Automatically handles connection failures
- Thread-safe for single-process usage

## Docker Services

**fastapi_app** - Main application
- Port: 8000
- Depends on memcache service

**memcache** - Memcached server
- Port: 11211
- Image: memcached:latest

## Environment Variables

The application uses these environment variables (set automatically in Docker):

- `MEMCACHED_HOST` - Default: "memcached" (Docker) or "localhost" (local)
- `MEMCACHED_PORT` - Default: 11211

## Troubleshooting

**Issue: Cannot connect to WebSocket**
- Ensure server is running on port 8000
- Use `ws://localhost:8000/ws` not `ws://0.0.0.0:8000/ws`
- Check Docker containers are running: `docker-compose ps`

**Issue: Getting "not authorized" messages**
- Use `?client=admin` query parameter, or
- Prefix messages with `admin:`, or
- Send from an admin-connected client

**Issue: Memcached connection errors**
- The app will automatically fallback to in-memory storage
- In Docker, memcached should connect automatically
- Locally without Memcached, fallback works fine

**Issue: Docker containers not starting**
- Ensure Docker Desktop is running
- Run: `docker-compose down` then `docker-compose up --build`
- Check logs: `docker-compose logs fastapi_app`

## Dependencies

Core packages (see app/requirements.txt):
- fastapi - Web framework
- uvicorn[standard] - ASGI server with WebSocket support
- pymemcache - Memcached client
- websockets - WebSocket support

## Development

To modify the application:

1. Edit files in the `app/` directory
2. If running with `--reload`, changes apply automatically
3. If using Docker, rebuild: `docker-compose up --build`

Key files to modify:
- `app/main.py` - Add endpoints or modify WebSocket logic
- `app/cache_manager.py` - Modify caching behavior
- `docker-compose.yml` - Change ports or add services
- `Dockerfile` - Modify container setup


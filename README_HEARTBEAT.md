# Heartbeat Function Implementation Guide

This guide shows multiple ways to implement a heartbeat function between a Python backend server and React frontend.

## Backend Implementations

### 1. Flask Backend (`heartbeat_backend.py`)

Simple Flask server with heartbeat and health check endpoints:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python heartbeat_backend.py
```

**Endpoints:**
- `GET /heartbeat` - Simple heartbeat check
- `GET /health` - Detailed health check with service status
- `GET /` - Basic server status

### 2. FastAPI Backend (`heartbeat_fastapi.py`)

Modern async FastAPI server with WebSocket support:

```bash
# Run the server
python heartbeat_fastapi.py
```

**Endpoints:**
- `GET /heartbeat` - Simple heartbeat check
- `GET /health` - Async health check with concurrent service checks
- `WS /ws/heartbeat` - WebSocket endpoint for real-time heartbeat

## Frontend Implementations

### 1. Basic React Component (`HeartbeatComponent.jsx`)

Full-featured component with both axios and fetch implementations:

```jsx
import HeartbeatComponent from './HeartbeatComponent';

function App() {
  return <HeartbeatComponent />;
}
```

**Features:**
- Automatic periodic checking (every 30 seconds)
- Manual check button
- Error handling with timeout
- Server uptime display

### 2. Custom Hook (`useHeartbeat.js`)

Reusable React hook for heartbeat functionality:

```jsx
import useHeartbeat from './useHeartbeat';

function MyComponent() {
  const heartbeat = useHeartbeat('http://localhost:5000', 30000, true);
  
  return (
    <div>
      {heartbeat.isAlive ? '✅ Server is alive' : '❌ Server is down'}
      <button onClick={heartbeat.checkNow}>Check Now</button>
    </div>
  );
}
```

### 3. Simple Usage Example (`ExampleUsage.jsx`)

Demonstrates the custom hook in action with minimal code.

### 4. WebSocket Component (`WebSocketHeartbeat.jsx`)

Real-time heartbeat monitoring using WebSocket:

```jsx
import WebSocketHeartbeat from './WebSocketHeartbeat';

function App() {
  return <WebSocketHeartbeat wsUrl="ws://localhost:5000/ws/heartbeat" />;
}
```

**Features:**
- Real-time updates every 5 seconds
- Auto-reconnect on disconnect
- Connection status indicator
- Manual reconnect/disconnect controls

## Quick Start

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the backend server:**
   ```bash
   # Flask version
   python heartbeat_backend.py
   
   # OR FastAPI version
   python heartbeat_fastapi.py
   ```

3. **Install React dependencies (if using axios):**
   ```bash
   npm install axios
   ```

4. **Use in your React app:**
   ```jsx
   // Option 1: Full component
   import HeartbeatComponent from './HeartbeatComponent';
   
   // Option 2: Custom hook
   import useHeartbeat from './useHeartbeat';
   
   // Option 3: WebSocket
   import WebSocketHeartbeat from './WebSocketHeartbeat';
   ```

## Configuration

### Backend Configuration

- **Port**: Default is 5000, change in the server files
- **CORS**: Currently allows all origins (`*`), restrict in production
- **Timeout**: Heartbeat checks have a 5-second timeout

### Frontend Configuration

- **Backend URL**: Update `BACKEND_URL` in components
- **Check Interval**: Default 30 seconds, adjustable
- **Timeout**: 5-second timeout for HTTP requests

## Production Considerations

1. **CORS**: Replace `allow_origins=["*"]` with specific frontend URLs
2. **HTTPS**: Use HTTPS in production, update URLs accordingly
3. **Authentication**: Add authentication tokens to heartbeat requests
4. **Rate Limiting**: Implement rate limiting on backend
5. **Error Logging**: Add proper error logging and monitoring
6. **Load Balancing**: Consider health checks for load balancer integration

## Testing

Test the heartbeat endpoint manually:

```bash
# Using curl
curl http://localhost:5000/heartbeat

# Using httpie
http GET localhost:5000/heartbeat

# WebSocket test (requires wscat)
wscat -c ws://localhost:5000/ws/heartbeat
```

## Troubleshooting

1. **CORS errors**: Ensure backend CORS is properly configured
2. **Connection refused**: Check if backend server is running
3. **Timeout errors**: Increase timeout or check network latency
4. **WebSocket issues**: Ensure WebSocket support in deployment environment
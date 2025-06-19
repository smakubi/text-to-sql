from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time
from typing import Dict, Any
import asyncio

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store server start time
server_start_time = time.time()

@app.get("/heartbeat")
async def heartbeat() -> Dict[str, Any]:
    """
    Simple heartbeat endpoint that returns server status
    """
    current_time = datetime.now().isoformat()
    uptime_seconds = int(time.time() - server_start_time)
    
    return {
        "status": "alive",
        "timestamp": current_time,
        "uptime_seconds": uptime_seconds,
        "message": "Server is running"
    }

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    More detailed health check endpoint with async checks
    """
    try:
        # Simulate async health checks
        async def check_database():
            # Simulate database check
            await asyncio.sleep(0.1)
            return True
        
        async def check_cache():
            # Simulate cache check
            await asyncio.sleep(0.1)
            return True
        
        # Run checks concurrently
        db_status, cache_status = await asyncio.gather(
            check_database(),
            check_cache()
        )
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(time.time() - server_start_time),
            "services": {
                "database": "connected" if db_status else "disconnected",
                "cache": "connected" if cache_status else "disconnected"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/")
async def root():
    return {"message": "Backend server is running"}

# WebSocket endpoint for real-time heartbeat
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/heartbeat")
async def websocket_heartbeat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time heartbeat monitoring
    """
    await websocket.accept()
    try:
        while True:
            # Send heartbeat every 5 seconds
            await asyncio.sleep(5)
            await websocket.send_json({
                "type": "heartbeat",
                "status": "alive",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": int(time.time() - server_start_time)
            })
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.cache_manager import store_notification, get_recent_notifications

app = FastAPI()
connected_user = []


@app.get("/")
async def root():
    return {"message": "FastAPI real-time notifications running!"}


@app.get("/health")
async def health_check():
    """Health check endpoint with cache status."""
    try:
        from app.cache_manager import get_cache_client
        cache = get_cache_client()
        cache_status = "connected" if hasattr(cache, '_storage') == False else "fallback"
        recent_count = len(get_recent_notifications())
        return {
            "status": "healthy",
            "cache_status": cache_status,
            "recent_notifications_count": recent_count,
            "connected_websockets": len(connected_user)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/messages")
async def get_messages():
    """Get recent messages from cache."""
    return {"recent_messages": get_recent_notifications()}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint that allows clients to receive real-time notifications."""
    # ✅ Get the client type from the query string (default to 'user')
    client_type = websocket.query_params.get("client", "user")

    try:
        await websocket.accept()
        connected_user.append((client_type, websocket))
        print(f"{client_type} connected. Total connections: {len(connected_user)}")
    except Exception as e:
        print(f"WebSocket connection failed: {e}")
        return

    # Send recent notifications to everyone
    recent = get_recent_notifications()
    for msg in recent:
        await websocket.send_text(f"[Recent] {msg}")

    try:
        while True:
            data = await websocket.receive_text()

            #  Check authorization: admin client OR message starts with admin:
            if client_type == "admin" or data.startswith("admin:"):
                # Extract message content
                if data.startswith("admin:"):
                    message = data.replace("admin:", "").strip()
                else:
                    message = data.strip()

                # Store the notification in cache
                store_notification(message)

                # Broadcast to everyone
                for _, user_socket in connected_user:
                    await user_socket.send_text(f"[Notification] {message}")
            else:
                await websocket.send_text("You are not authorized to send notifications.")
    except WebSocketDisconnect:
        # Remove disconnected client
        connected_user.remove((client_type, websocket))
        print(f"{client_type} disconnected. Total connections: {len(connected_user)}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        connected_user.remove((client_type, websocket))
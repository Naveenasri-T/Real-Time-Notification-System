from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.cache_manager import cache,store_notification, get_recent_notifications

app = FastAPI()
connected_user =[]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint that allows clients to receive real-time notifications.
    Clients should connect to ws://<host>:8000/ws.
    """
    await websocket.accept()
    connected_user.append(websocket)

    recent= get_recent_notifications()
    for msg in recent:
        await websocket.send_text(f"[Recent] {msg}")
    try:
        while True:
            data =await websocket.receive_text()

            if data.startswith("admin:"):
                message = data.replace("admin:", "").strip()
                # Store the notification in the cache
                store_notification(message)

                for user in connected_user:
                    await user.send_text(f"[Notification] {message}")
            else:
                await websocket.send_text("you are not authorized to send notifications.")
    except WebSocketDisconnect:
        connected_user.remove(websocket)
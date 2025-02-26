# File: app/api/endpoints/live_updates.py

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from typing import Dict, List, Any

from app.infrastructure.auth.jwt_handler import decode_access_token
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import UserModel

router = APIRouter()

# Store active connections
class ConnectionManager:
    def __init__(self):
        # Map of user_id -> List[WebSocket]
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            # Clean up if no connections left for this user
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: Any, user_id: int):
        """Send a message to a specific user's connections."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

    async def broadcast(self, message: Any):
        """Send a message to all connected clients."""
        for user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)


# Create a singleton connection manager
manager = ConnectionManager()


@router.websocket("/live-updates")
async def websocket_endpoint(
    websocket: WebSocket, 
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time craving updates.
    
    Clients connect with a JWT token to authenticate:
    ws://example.com/api/live-updates?token=your_jwt_token
    
    The server will push updates about new cravings, analytics,
    or other relevant events to the connected client.
    """
    # Validate the token
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    try:
        # Decode the token to get the user ID
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
        
        # Connect this websocket
        await manager.connect(websocket, user_id)
        
        try:
            # Keep the connection alive and process messages
            while True:
                # Receive JSON data from the client
                data = await websocket.receive_json()
                
                # Process any incoming messages (if needed)
                # For now, we just echo back the message
                await manager.send_personal_message(
                    {"message": "Received", "data": data},
                    user_id
                )
                
        except WebSocketDisconnect:
            # Handle disconnection
            manager.disconnect(websocket, user_id)
        
    except Exception as e:
        # Invalid token or other error
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
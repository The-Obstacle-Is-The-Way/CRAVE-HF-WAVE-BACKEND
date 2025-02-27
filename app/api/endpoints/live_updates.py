# File: app/api/endpoints/live_updates.py

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any
from datetime import datetime
import json

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
                try:
                    await connection.send_json(message)
                except Exception:
                    # Connection might be closed or broken
                    self.disconnect(connection, user_id)

    async def broadcast(self, message: Any):
        """Send a message to all connected clients."""
        disconnected_users = []
        for user_id, connections in self.active_connections.items():
            disconnected_connections = []
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected_connections.append(connection)
            
            # Remove broken connections
            for conn in disconnected_connections:
                self.active_connections[user_id].remove(conn)
            
            # Track empty user entries for cleanup
            if not self.active_connections[user_id]:
                disconnected_users.append(user_id)
        
        # Clean up empty user entries
        for user_id in disconnected_users:
            del self.active_connections[user_id]


# Create a singleton connection manager
manager = ConnectionManager()


@router.websocket("/live-updates")
async def websocket_endpoint(
    websocket: WebSocket, 
    token: str = Query(None),
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
        
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to real-time updates",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id
        })
        
        try:
            # Keep the connection alive and process messages
            while True:
                # Receive JSON data from the client
                data = await websocket.receive_json()
                
                # Process any incoming messages
                # For now, we just echo back the message
                await manager.send_personal_message(
                    {
                        "type": "echo",
                        "message": "Server received your message",
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    user_id
                )
                
        except WebSocketDisconnect:
            # Handle disconnection
            manager.disconnect(websocket, user_id)
        
    except Exception as e:
        # Invalid token or other error
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)


# Utility function to notify users about new cravings
# This would be called from the craving creation endpoint
async def notify_new_craving(user_id: int, craving_data: dict):
    """
    Send a notification about a new craving to the user.
    
    Args:
        user_id: The ID of the user who created the craving
        craving_data: Data about the craving that was created
    """
    await manager.send_personal_message(
        {
            "type": "new_craving",
            "message": "New craving logged",
            "data": craving_data,
            "timestamp": datetime.utcnow().isoformat()
        },
        user_id
    )


# Utility function to notify users about completed transcriptions
# This would be called when a transcription is completed
async def notify_transcription_complete(user_id: int, voice_log_id: int, transcript: str):
    """
    Send a notification about a completed voice log transcription.
    
    Args:
        user_id: The ID of the user who owns the voice log
        voice_log_id: The ID of the voice log that was transcribed
        transcript: The transcribed text
    """
    await manager.send_personal_message(
        {
            "type": "transcription_complete",
            "message": "Voice log transcription completed",
            "data": {
                "voice_log_id": voice_log_id,
                "transcript": transcript
            },
            "timestamp": datetime.utcnow().isoformat()
        },
        user_id
    )
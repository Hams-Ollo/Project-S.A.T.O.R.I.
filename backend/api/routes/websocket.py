from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
import logging
import json
from uuid import uuid4

from ...core.websocket.manager import manager
from ...core.websocket.models import ChatMessage, SystemMessage, MessageType, MessageStatus

router = APIRouter()
logger = logging.getLogger(__name__)

async def get_user_id(websocket: WebSocket) -> str:
    """Extract user ID from WebSocket connection query params."""
    params = websocket.query_params
    user_id = params.get("user_id")
    if not user_id:
        user_id = str(uuid4())  # Generate temporary ID if none provided
    return user_id

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for chat connections."""
    user_id = await get_user_id(websocket)
    
    try:
        await manager.connect(websocket, user_id)
        
        # Notify others of new connection
        system_msg = SystemMessage(
            sender_id="system",
            content=f"User {user_id} has joined the chat.",
            severity="info"
        )
        await manager.broadcast(system_msg, exclude={user_id})
        
        try:
            while True:
                # Wait for messages from the client
                data = await websocket.receive_text()
                try:
                    message_data = json.loads(data)
                    
                    # Create chat message
                    message = ChatMessage(
                        sender_id=user_id,
                        content=message_data.get("content", ""),
                        reply_to=message_data.get("reply_to"),
                        agent_id=message_data.get("agent_id")
                    )
                    
                    # Broadcast message to all users
                    await manager.broadcast(message)
                    
                except json.JSONDecodeError:
                    logger.error(f"Invalid message format from {user_id}: {data}")
                    error_msg = SystemMessage(
                        sender_id="system",
                        content="Invalid message format. Please send valid JSON.",
                        severity="error"
                    )
                    await manager.send_personal_message(error_msg, user_id)
                    
        except WebSocketDisconnect:
            manager.disconnect(user_id)
            # Notify others of disconnection
            system_msg = SystemMessage(
                sender_id="system",
                content=f"User {user_id} has left the chat.",
                severity="info"
            )
            await manager.broadcast(system_msg)
            
    except Exception as e:
        logger.error(f"Error in WebSocket connection for {user_id}: {str(e)}")
        manager.disconnect(user_id)
        raise

@router.get("/chat/active-users")
async def get_active_users():
    """Get list of currently active users."""
    return {"active_users": list(manager.get_active_users())}

@router.get("/chat/user-session/{user_id}")
async def get_user_session(user_id: str):
    """Get session information for a specific user."""
    session = manager.get_user_session(user_id)
    if not session:
        raise HTTPException(status_code=404, detail="User session not found")
    return session 
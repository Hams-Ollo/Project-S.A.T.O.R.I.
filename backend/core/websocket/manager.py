from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional
import logging
import json
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict

from .models import Message, MessageStatus, SystemMessage

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_messages: int = 60, window_seconds: int = 60):
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self.message_counts = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> bool:
        now = datetime.utcnow()
        # Remove old messages from the window
        self.message_counts[user_id] = [
            timestamp for timestamp in self.message_counts[user_id]
            if now - timestamp < timedelta(seconds=self.window_seconds)
        ]
        
        # Check if under rate limit
        return len(self.message_counts[user_id]) < self.max_messages
    
    def add_message(self, user_id: str):
        self.message_counts[user_id].append(datetime.utcnow())

class ConnectionManager:
    def __init__(self):
        # Active connections: user_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # User sessions: user_id -> session_data
        self.user_sessions: Dict[str, dict] = {}
        # Rate limiter
        self.rate_limiter = RateLimiter()
        # Heartbeat task
        self._heartbeat_task = None
        # Shutdown flag
        self._shutdown = False
        # Start heartbeat
        self.start_heartbeat()
    
    def start_heartbeat(self):
        """Start the heartbeat task."""
        self._heartbeat_task = asyncio.create_task(self._heartbeat())
    
    async def shutdown(self):
        """Gracefully shutdown the connection manager."""
        logger.info("Initiating connection manager shutdown...")
        self._shutdown = True
        
        # Cancel heartbeat task
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Send shutdown message to all clients
        shutdown_msg = SystemMessage(
            sender_id="system",
            content="Server is shutting down. Please reconnect later.",
            severity="warning"
        )
        
        # Notify and disconnect all clients
        for user_id in list(self.active_connections.keys()):
            try:
                await self.send_personal_message(shutdown_msg, user_id)
                await self.active_connections[user_id].close()
            except Exception as e:
                logger.error(f"Error during shutdown for user {user_id}: {str(e)}")
            finally:
                self.disconnect(user_id)
        
        logger.info("Connection manager shutdown complete.")

    async def _heartbeat(self):
        """Send periodic heartbeat to check connection health."""
        while not self._shutdown:
            try:
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                if self._shutdown:
                    break
                    
                current_time = datetime.utcnow()
                disconnected_users = []
                
                for user_id, session in self.user_sessions.items():
                    try:
                        # Check if client has been inactive for too long
                        if current_time - session["last_heartbeat"] > timedelta(minutes=2):
                            disconnected_users.append(user_id)
                            continue
                            
                        # Send heartbeat
                        heartbeat_msg = SystemMessage(
                            sender_id="system",
                            content="heartbeat",
                            severity="debug"
                        )
                        await self.send_personal_message(heartbeat_msg, user_id)
                        session["last_heartbeat"] = current_time
                        
                    except WebSocketDisconnect:
                        disconnected_users.append(user_id)
                    except Exception as e:
                        logger.error(f"Error in heartbeat for {user_id}: {str(e)}")
                        disconnected_users.append(user_id)
                
                # Clean up disconnected users
                for user_id in disconnected_users:
                    self.disconnect(user_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {str(e)}")
                if not self._shutdown:
                    await asyncio.sleep(5)  # Wait before retrying

    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a new WebSocket client."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_sessions[user_id] = {
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "messages_sent": 0,
            "messages_received": 0,
            "last_heartbeat": datetime.utcnow()
        }
        logger.info(f"Client connected: {user_id}")
        
        # Send welcome message
        welcome_msg = SystemMessage(
            sender_id="system",
            content=f"Welcome to SATORI AI! You are connected as {user_id}.",
            severity="info"
        )
        await self.send_personal_message(welcome_msg, user_id)

    def disconnect(self, user_id: str):
        """Disconnect a WebSocket client."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        logger.info(f"Client disconnected: {user_id}")

    async def send_personal_message(self, message: Message, user_id: str):
        """Send a message to a specific user."""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                # Check rate limit for non-system messages
                if message.type != "system" and not self.rate_limiter.is_allowed(user_id):
                    error_msg = SystemMessage(
                        sender_id="system",
                        content="Rate limit exceeded. Please wait before sending more messages.",
                        severity="error"
                    )
                    await websocket.send_json(error_msg.model_dump())
                    return

                await websocket.send_json(message.model_dump())
                message.status = MessageStatus.DELIVERED
                self.user_sessions[user_id]["messages_received"] += 1
                self.user_sessions[user_id]["last_activity"] = datetime.utcnow()
                
                if message.type != "system":
                    self.rate_limiter.add_message(user_id)
                
            except Exception as e:
                logger.error(f"Error sending message to {user_id}: {str(e)}")
                message.status = MessageStatus.ERROR
                raise

    async def broadcast(self, message: Message, exclude: Optional[Set[str]] = None):
        """Broadcast a message to all connected clients except those in exclude set."""
        exclude = exclude or set()
        for user_id in self.active_connections:
            if user_id not in exclude:
                await self.send_personal_message(message, user_id)

    def get_active_users(self) -> Set[str]:
        """Get set of currently connected user IDs."""
        return set(self.active_connections.keys())

    def get_user_session(self, user_id: str) -> Optional[dict]:
        """Get session data for a specific user."""
        return self.user_sessions.get(user_id)

# Global connection manager instance
manager = ConnectionManager() 
import streamlit as st
import websockets
import asyncio
import json
import uuid
from datetime import datetime
import logging
from typing import Optional, Dict, Any
import atexit

logger = logging.getLogger(__name__)

class ChatInterface:
    def __init__(self):
        self.websocket = None
        self.messages = []
        self.is_connected = False
        self.should_run = True
        
        # Initialize session state for messages if not exists
        if 'messages' not in st.session_state:
            st.session_state.messages = []
            
        # Initialize the WebSocket connection
        asyncio.run(self.connect_websocket())

    async def connect_websocket(self):
        """Establish WebSocket connection."""
        try:
            self.websocket = await websockets.connect(
                f"ws://localhost:8000/ws/chat",
                ping_interval=None
            )
            self.is_connected = True
            logger.info("WebSocket connection established")
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {str(e)}")
            self.is_connected = False

    async def disconnect_websocket(self):
        """Close WebSocket connection."""
        if self.websocket:
            try:
                # Close WebSocket connection
                await self.websocket.close()
                logger.info(f"WebSocket disconnected for user {st.session_state.user_id}")
            except Exception as e:
                logger.error(f"Error during WebSocket disconnect: {str(e)}")
            finally:
                self.is_connected = False
                self.websocket = None

    async def send_message(self, content: str, reply_to: Optional[str] = None):
        """Send a message through WebSocket."""
        if not self.is_connected:
            await self.connect_websocket()

        if self.websocket:
            try:
                message = {
                    "content": content,
                    "reply_to": reply_to,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await self.websocket.send(json.dumps(message))
                logger.debug(f"Message sent: {content}")
            except Exception as e:
                logger.error(f"Failed to send message: {str(e)}")
                st.error("Failed to send message. Please try again.")
                await self.disconnect_websocket()

    async def _listen_for_messages(self):
        """Listen for incoming WebSocket messages."""
        if not self.websocket:
            return

        try:
            while self.should_run:
                message = await self.websocket.recv()
                message_data = json.loads(message)
                
                # Handle heartbeat messages silently
                if message_data.get("type") == "system" and message_data.get("content") == "heartbeat":
                    continue
                
                # Add message to session state
                st.session_state.messages.append(message_data)
                logger.debug(f"Message received: {message_data}")
                
                # Force streamlit to update
                st.experimental_rerun()
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            await self.disconnect_websocket()
        except Exception as e:
            logger.error(f"Error in message listener: {str(e)}")
            await self.disconnect_websocket()

    def render_message(self, message: Dict[str, Any]):
        """Render a single message in the chat interface."""
        is_user = message["sender_id"] == st.session_state.user_id
        
        with st.container():
            if is_user:
                st.write(f"You: {message['content']}")
            else:
                if message["type"] == "system":
                    st.info(message["content"])
                else:
                    st.write(f"{message['sender_id']}: {message['content']}")

    def render(self):
        """Render the chat interface."""
        st.title("💬 Chat")
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                self.render_message(message)
        
        # Input field for new messages
        with st.container():
            message_input = st.text_input("Message", key="message_input")
            col1, col2 = st.columns([4, 1])
            
            with col1:
                if st.button("Send", use_container_width=True):
                    if message_input.strip():
                        asyncio.run(self.send_message(message_input.strip()))
                        st.session_state.message_input = ""  # Clear input
            
            with col2:
                if st.button("Clear", use_container_width=True):
                    st.session_state.messages = []
                    st.experimental_rerun()

def initialize_chat():
    """Initialize and return chat interface."""
    chat = ChatInterface()
    # Establish WebSocket connection
    asyncio.run(chat.connect_websocket())
    return chat 
import streamlit as st
import websockets
import asyncio
import json
import uuid
from datetime import datetime
import logging
from typing import Optional, Dict, Any
import atexit

from .voice import VoiceComponent

logger = logging.getLogger(__name__)

class ChatInterface:
    def __init__(self):
        self.websocket = None
        self.messages = []
        self.is_connected = False
        self.should_run = True
        self.voice = VoiceComponent()
        
        # Initialize session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'voice_enabled' not in st.session_state:
            st.session_state.voice_enabled = False
        if 'recording' not in st.session_state:
            st.session_state.recording = False
            
        # Initialize the WebSocket connection
        asyncio.run(self.connect_websocket())
        
    def render(self):
        """Render the chat interface."""
        # Voice control section
        with st.sidebar:
            st.subheader("Voice Controls")
            st.session_state.voice_enabled = st.toggle("Enable Voice Input", st.session_state.voice_enabled)
            
            if st.session_state.voice_enabled:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Start Recording" if not st.session_state.recording else "Stop Recording"):
                        if not st.session_state.recording:
                            self.start_voice_recording()
                        else:
                            self.stop_voice_recording()
                            
                with col2:
                    if st.button("Upload Voice Note"):
                        self.handle_voice_note_upload()
        
        # Main chat interface
        st.title("SATORI AI Chat")
        
        # Display messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Input section
        if prompt := st.chat_input("Type your message here..."):
            self.handle_user_input(prompt)
            
    def start_voice_recording(self):
        """Start recording voice input."""
        st.session_state.recording = True
        asyncio.create_task(self.handle_live_transcription())
        
    def stop_voice_recording(self):
        """Stop recording voice input."""
        st.session_state.recording = False
        if hasattr(self, 'voice_task'):
            self.voice_task.cancel()
        
    async def handle_live_transcription(self):
        """Handle live voice transcription."""
        try:
            async for transcript in self.voice.start_live_transcription():
                if transcript and not st.session_state.recording:
                    # Send transcribed text as message
                    await self.send_message(transcript)
                    break
        except Exception as e:
            logger.error(f"Error in live transcription: {str(e)}")
            st.error("Error processing voice input. Please try again.")
            
    def handle_voice_note_upload(self):
        """Handle voice note file upload."""
        uploaded_file = st.file_uploader("Upload Voice Note", type=['wav', 'mp3'])
        if uploaded_file:
            # Save uploaded file
            file_path = f"frontend/static/audio/input/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Transcribe audio
            transcription = self.voice.transcribe_audio_file(file_path)
            if transcription:
                text = transcription["results"]["channels"][0]["alternatives"][0]["transcript"]
                if text:
                    asyncio.run(self.send_message(text))
                    
    def handle_user_input(self, text: str):
        """Handle user text input."""
        asyncio.run(self.send_message(text))
        
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

def initialize_chat():
    """Initialize and return chat interface."""
    chat = ChatInterface()
    # Establish WebSocket connection
    asyncio.run(chat.connect_websocket())
    return chat 
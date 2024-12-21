"""
Voice interaction component for the frontend.
"""
import streamlit as st
import requests
import os
from typing import Optional, Dict
import base64

class VoiceComponent:
    def __init__(self):
        self.api_base = f"http://localhost:{os.getenv('PORT', '8000')}"
        self.available_voices = self._fetch_voices()
        
    def _fetch_voices(self) -> list:
        """Fetch available voices from the API."""
        try:
            response = requests.get(f"{self.api_base}/voice/voices")
            response.raise_for_status()
            return response.json()["voices"]
        except Exception as e:
            st.error(f"Error fetching voices: {str(e)}")
            return []
            
    def render_voice_settings(self) -> Dict:
        """Render voice settings controls."""
        with st.expander("🎙️ Voice Settings"):
            # Voice selection
            voice_options = {v["name"]: v["voice_id"] for v in self.available_voices}
            selected_voice = st.selectbox(
                "Select Voice",
                options=list(voice_options.keys()),
                index=0
            )
            voice_id = voice_options[selected_voice]
            
            # Voice parameters
            col1, col2 = st.columns(2)
            with col1:
                stability = st.slider(
                    "Stability",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.5,
                    help="Higher values make the voice more stable and consistent"
                )
                style = st.slider(
                    "Style",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.0,
                    help="Higher values enhance the style of speech"
                )
            
            with col2:
                similarity_boost = st.slider(
                    "Similarity Boost",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.75,
                    help="Higher values make the voice more similar to the original"
                )
                speaker_boost = st.checkbox(
                    "Speaker Boost",
                    value=True,
                    help="Enhance speaker clarity"
                )
                
            return {
                "voice_id": voice_id,
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": speaker_boost
            }
            
    def text_to_speech(self, text: str, settings: Optional[Dict] = None) -> None:
        """Convert text to speech and play audio."""
        try:
            # Get voice settings
            if settings is None:
                settings = {}
                
            # Make API request
            response = requests.post(
                f"{self.api_base}/voice/text-to-speech",
                json={"text": text, **settings}
            )
            response.raise_for_status()
            
            # Play audio
            audio_data = response.content
            audio_b64 = base64.b64encode(audio_data).decode()
            
            # Display audio player
            st.audio(audio_data, format="audio/mp3")
            
            # Add download button
            st.download_button(
                "Download Audio",
                audio_data,
                file_name="speech.mp3",
                mime="audio/mp3"
            )
            
        except Exception as e:
            st.error(f"Error generating speech: {str(e)}")
            
    def process_chat_response(self, response: Dict, settings: Optional[Dict] = None) -> Dict:
        """Process chat response and add audio if needed."""
        try:
            if settings is None:
                settings = {}
                
            # Check if response should be converted to speech
            if st.session_state.get("enable_voice", False):
                response = requests.post(
                    f"{self.api_base}/voice/chat-response-audio",
                    json={"response": response, **settings}
                ).json()
                
                # Play audio if available
                if "audio_path" in response:
                    with open(response["audio_path"], "rb") as f:
                        audio_data = f.read()
                        st.audio(audio_data, format="audio/mp3")
                        
            return response
            
        except Exception as e:
            st.error(f"Error processing chat response: {str(e)}")
            return response 
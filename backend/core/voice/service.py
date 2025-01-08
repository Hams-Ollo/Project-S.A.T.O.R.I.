"""
Voice synthesis service using Eleven Labs API.
"""
import os
from typing import Optional, Dict, List
import aiohttp
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class VoiceService:
    """Service for handling text-to-speech operations using Eleven Labs."""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVEN_LABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVEN_LABS_API_KEY environment variable is not set")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Create audio output directory if it doesn't exist
        self.output_dir = Path("frontend/static/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def list_voices(self) -> List[Dict]:
        """Get available voices from Eleven Labs."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/voices",
                    headers=self.headers
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data["voices"]
        except Exception as e:
            logger.error(f"Error fetching voices: {str(e)}")
            raise

    async def text_to_speech(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Default voice
        model_id: str = "eleven_monolingual_v1",
        output_format: str = "mp3",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ) -> bytes:
        """
        Convert text to speech using Eleven Labs API.
        
        Args:
            text: The text to convert to speech
            voice_id: The ID of the voice to use
            model_id: The ID of the model to use
            output_format: The desired output format (mp3 or wav)
            stability: Voice stability (0-1)
            similarity_boost: Similarity boost factor (0-1)
            style: Speaking style (0-1)
            use_speaker_boost: Whether to use speaker boost
            
        Returns:
            bytes: The audio data
        """
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            payload = {
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    response.raise_for_status()
                    return await response.read()
            
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {str(e)}")
            raise

    async def save_audio(self, audio_data: bytes, filename: str) -> str:
        """
        Save audio data to a file.
        
        Args:
            audio_data: The audio data in bytes
            filename: The desired filename
            
        Returns:
            str: The path to the saved audio file
        """
        try:
            filepath = self.output_dir / filename
            async with aiohttp.ClientSession() as session:
                with open(filepath, "wb") as f:
                    f.write(audio_data)
            return str(filepath)
        except Exception as e:
            logger.error(f"Error saving audio file: {str(e)}")
            raise

    async def generate_and_save_speech(
        self,
        text: str,
        filename: str,
        voice_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate speech from text and save it to a file.
        
        Args:
            text: The text to convert to speech
            filename: The desired filename
            voice_id: Optional voice ID to use
            **kwargs: Additional parameters for text_to_speech
            
        Returns:
            str: The path to the saved audio file
        """
        try:
            audio_data = await self.text_to_speech(text, voice_id=voice_id, **kwargs)
            return await self.save_audio(audio_data, filename)
        except Exception as e:
            logger.error(f"Error generating and saving speech: {str(e)}")
            raise 
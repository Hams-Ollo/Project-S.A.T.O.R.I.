"""Service for handling voice transcription using Deepgram."""
from deepgram import Deepgram
import os
import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class DeepgramService:
    """Service for handling voice transcription using Deepgram."""
    
    def __init__(self):
        # Load environment variables from project root
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        env_path = project_root / '.env'
        load_dotenv(dotenv_path=env_path)
        
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        logger.debug(f"Deepgram API Key found: {bool(self.api_key)}")
        logger.debug(f"Looking for .env file at: {env_path}")
        
        if not self.api_key:
            logger.error("DEEPGRAM_API_KEY environment variable is not set")
            raise ValueError("DEEPGRAM_API_KEY environment variable is not set")
        
        # Initialize Deepgram client
        self.deepgram = Deepgram(self.api_key)
        
        # Create audio input directory if it doesn't exist
        self.input_dir = project_root / "frontend/static/audio/input"
        self.input_dir.mkdir(parents=True, exist_ok=True)

    async def transcribe_audio_file(self, file_path: str, options: Optional[Dict[str, Any]] = None) -> Dict:
        """Transcribe a pre-recorded audio file."""
        try:
            # Set default options if none provided
            if options is None:
                options = {
                    "model": "nova-2",
                    "smart_format": True,
                    "language": "en-US"
                }

            # Open the audio file
            with open(file_path, 'rb') as audio:
                source = {
                    "buffer": audio,
                    "mimetype": 'audio/wav'
                }
                response = await self.deepgram.transcription.prerecorded(source, options)
                return response

        except Exception as e:
            logger.error(f"Error transcribing audio file: {str(e)}")
            raise

    async def get_live_transcription_connection(self, options: Optional[Dict[str, Any]] = None) -> Tuple[Any, Dict[str, Any]]:
        """Get a WebSocket connection for live transcription."""
        try:
            # Set default options if none provided
            if options is None:
                options = {
                    "model": "nova-2",
                    "punctuate": True,
                    "language": "en-US",
                    "encoding": "linear16",
                    "channels": 1,
                    "sample_rate": 16000,
                    "interim_results": True,
                    "utterance_end_ms": 1000,
                    "vad_events": True
                }

            # Create live transcription client
            live_client = await self.deepgram.transcription.live(options)
            return live_client, options

        except Exception as e:
            logger.error(f"Error creating live transcription connection: {str(e)}")
            raise 
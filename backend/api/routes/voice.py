"""
Voice-related API endpoints.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, Dict
import uuid
from datetime import datetime

from backend.core.voice.service import VoiceService

router = APIRouter()
voice_service = VoiceService()

@router.get("/voices")
async def list_voices():
    """Get available voices from Eleven Labs."""
    try:
        voices = await voice_service.list_voices()
        return JSONResponse(content={"voices": voices})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-speech")
async def text_to_speech(
    text: str,
    voice_id: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    **kwargs
):
    """
    Convert text to speech and return audio file path.
    
    Args:
        text: Text to convert to speech
        voice_id: Optional voice ID to use
        background_tasks: FastAPI background tasks
        **kwargs: Additional parameters for text_to_speech
    """
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"speech_{timestamp}_{uuid.uuid4().hex[:8]}.mp3"
        
        # Generate and save speech
        filepath = await voice_service.generate_and_save_speech(
            text=text,
            filename=filename,
            voice_id=voice_id,
            **kwargs
        )
        
        # Return audio file
        return FileResponse(
            filepath,
            media_type="audio/mpeg",
            filename=filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat-response-audio")
async def generate_chat_response_audio(
    response: Dict,
    voice_id: Optional[str] = None,
    **kwargs
):
    """
    Convert chat response to audio.
    
    Args:
        response: Chat response containing text
        voice_id: Optional voice ID to use
        **kwargs: Additional parameters for text_to_speech
    """
    try:
        text = response.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="No text provided in response")
            
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_response_{timestamp}_{uuid.uuid4().hex[:8]}.mp3"
        
        # Generate and save speech
        filepath = await voice_service.generate_and_save_speech(
            text=text,
            filename=filename,
            voice_id=voice_id,
            **kwargs
        )
        
        # Add audio path to response
        response["audio_path"] = filepath
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
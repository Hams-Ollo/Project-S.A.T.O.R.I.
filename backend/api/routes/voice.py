"""
Voice-related API endpoints.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, WebSocket
from fastapi.responses import FileResponse, JSONResponse
from fastapi.websockets import WebSocketState
from typing import Optional, Dict
import uuid
from datetime import datetime
import os
import logging
from pathlib import Path
from deepgram import Deepgram

from backend.core.voice.service import VoiceService
from backend.core.voice.deepgram_service import DeepgramService

router = APIRouter()
logger = logging.getLogger(__name__)
voice_service = VoiceService()
deepgram_service = DeepgramService()

@router.get("/voices")
async def list_voices():
    """Get available voices from Eleven Labs."""
    try:
        voices = await voice_service.list_voices()
        return {"voices": voices}
    except Exception as e:
        logger.error(f"Error listing voices: {str(e)}")
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
        logger.error(f"Error generating speech: {str(e)}")
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
        response["audio_path"] = str(filepath)
        return response
        
    except Exception as e:
        logger.error(f"Error generating chat response audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    options: Optional[Dict] = None
):
    """
    Transcribe uploaded audio file using Deepgram.
    """
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"input_{timestamp}_{uuid.uuid4().hex[:8]}{os.path.splitext(file.filename)[1]}"
        file_path = deepgram_service.input_dir / filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Transcribe audio
        response = await deepgram_service.transcribe_audio_file(str(file_path), options)
        
        return response
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/live-transcription")
async def live_transcription(websocket: WebSocket):
    """
    WebSocket endpoint for live voice transcription.
    """
    try:
        # Accept WebSocket connection
        await websocket.accept()
        logger.info("WebSocket connection accepted for live transcription")
        
        # Get Deepgram client and options
        dg_client, options = await deepgram_service.get_live_transcription_connection()
        
        # Create a connection
        async with dg_client as connection:
            logger.info("Deepgram connection started")
            
            # Set up event handlers
            @connection.on('transcriptReceived')
            async def handle_transcript(transcript):
                try:
                    sentence = transcript.get('channel', {}).get('alternatives', [{}])[0].get('transcript', '')
                    if len(sentence) > 0:
                        await websocket.send_json({
                            "type": "transcript",
                            "text": sentence
                        })
                except Exception as e:
                    logger.error(f"Error in transcription message handler: {str(e)}")
            
            @connection.on('error')
            async def handle_error(error):
                try:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(error)
                    })
                except Exception as e:
                    logger.error(f"Error in transcription error handler: {str(e)}")
            
            try:
                while True:
                    # Receive audio data from client
                    data = await websocket.receive_bytes()
                    await connection.send(data)
                    
            except Exception as e:
                logger.error(f"Error in live transcription loop: {str(e)}")
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
                
    except Exception as e:
        logger.error(f"Error setting up live transcription: {str(e)}")
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close() 
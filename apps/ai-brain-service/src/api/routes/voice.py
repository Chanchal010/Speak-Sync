"""
Voice API Routes - HTTP endpoints for STT
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from src.services.voice_service import get_voice_service
from src.services.tts_service import get_tts_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai/voice", tags=["Voice AI"])


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file (WAV, MP3, M4A, etc.)"),
    language: Optional[str] = Form(None, description="Language code (en, hi, etc.) or auto-detect")
):
    """
    Transcribe audio file to text using Whisper
    
    **Supported Formats**: WAV, MP3, M4A, WEBM, OGG, FLAC
    
    **Example**:
    ```bash
    curl -X POST http://localhost:8000/api/ai/voice/transcribe \
      -F "audio=@recording.wav" \
      -F "language=en"
    ```
    
    **Response**:
    ```json
    {
        "text": "Hello, this is a test transcription",
        "language": "en",
        "confidence": 0.95,
        "duration_ms": 3500
    }
    ```
    """
    try:
        # Validate file size (max 25MB)
        MAX_SIZE = 25 * 1024 * 1024  # 25MB
        audio_data = await audio.read()
        
        if len(audio_data) > MAX_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Audio file too large. Maximum size: 25MB"
            )
        
        if len(audio_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty audio file"
            )
        
        # Detect format from filename
        filename = audio.filename or "audio.wav"
        file_ext = filename.split('.')[-1].lower()
        
        # Get voice service
        voice_service = get_voice_service()
        
        # Validate audio
        validation = await voice_service.validate_audio(audio_data, format=file_ext)
        if not validation['valid']:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid audio file: {validation.get('error', 'Unknown error')}"
            )
        
        logger.info(f"Transcribing audio: {filename} ({len(audio_data)} bytes, {validation['duration_ms']}ms)")
        
        # Transcribe
        result = await voice_service.transcribe_audio(
            audio_data=audio_data,
            language=language,
            format=file_ext
        )
        
        return JSONResponse(content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post("/transcribe-url")
async def transcribe_from_url(
    url: str = Form(..., description="URL to audio file"),
    language: Optional[str] = Form(None, description="Language code")
):
    """
    Transcribe audio from URL
    
    **Example**:
    ```bash
    curl -X POST http://localhost:8000/api/ai/voice/transcribe-url \
      -F "url=https://example.com/audio.mp3" \
      -F "language=en"
    ```
    """
    try:
        import httpx
        
        # Download audio file
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to download audio: HTTP {response.status_code}"
                )
            
            audio_data = response.content
        
        # Detect format from URL
        file_ext = url.split('.')[-1].split('?')[0].lower()
        if file_ext not in ['wav', 'mp3', 'm4a', 'webm', 'ogg', 'flac']:
            file_ext = 'wav'  # Default
        
        # Get voice service
        voice_service = get_voice_service()
        
        # Transcribe
        result = await voice_service.transcribe_audio(
            audio_data=audio_data,
            language=language,
            format=file_ext
        )
        
        return JSONResponse(content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL transcription error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transcribe from URL: {str(e)}"
        )


@router.post("/validate")
async def validate_audio_file(
    audio: UploadFile = File(..., description="Audio file to validate")
):
    """
    Validate audio file quality and format
    
    **Response**:
    ```json
    {
        "valid": true,
        "duration_ms": 5000,
        "sample_rate": 16000,
        "channels": 1,
        "format": "wav",
        "bit_depth": 16
    }
    ```
    """
    try:
        audio_data = await audio.read()
        filename = audio.filename or "audio.wav"
        file_ext = filename.split('.')[-1].lower()
        
        voice_service = get_voice_service()
        
        result = await voice_service.validate_audio(audio_data, format=file_ext)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/convert")
async def convert_audio_format(
    audio: UploadFile = File(..., description="Audio file to convert"),
    to_format: str = Form("wav", description="Target format (wav, mp3, etc.)"),
    sample_rate: int = Form(16000, description="Target sample rate")
):
    """
    Convert audio to different format/sample rate
    
    **Example**:
    ```bash
    curl -X POST http://localhost:8000/api/ai/voice/convert \
      -F "audio=@input.m4a" \
      -F "to_format=wav" \
      -F "sample_rate=16000" \
      --output converted.wav
    ```
    """
    try:
        from fastapi.responses import Response
        
        audio_data = await audio.read()
        filename = audio.filename or "audio.wav"
        from_format = filename.split('.')[-1].lower()
        
        voice_service = get_voice_service()
        
        converted_audio = await voice_service.convert_audio_format(
            audio_data=audio_data,
            from_format=from_format,
            to_format=to_format,
            sample_rate=sample_rate
        )
        
        return Response(
            content=converted_audio,
            media_type=f"audio/{to_format}",
            headers={
                "Content-Disposition": f'attachment; filename="converted.{to_format}"'
            }
        )
    
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Conversion failed: {str(e)}"
        )


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported audio formats
    
    **Response**:
    ```json
    {
        "formats": ["wav", "mp3", "m4a", "webm", "ogg", "flac"],
        "max_file_size_mb": 25,
        "max_duration_minutes": 10
    }
    ```
    """
    return {
        "formats": ["wav", "mp3", "m4a", "webm", "ogg", "flac"],
        "max_file_size_mb": 25,
        "max_duration_minutes": 10,
        "supported_languages": [
            {"code": "en", "name": "English"},
            {"code": "hi", "name": "Hindi"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "auto", "name": "Auto-detect"}
        ]
    }


# ==================== TTS Endpoints ====================

@router.post("/synthesize")
async def synthesize_speech(
    text: str = Form(..., description="Text to convert to speech"),
    voice: str = Form("nova", description="Voice to use (alloy, echo, fable, onyx, nova, shimmer)"),
    speed: float = Form(1.0, description="Speech speed (0.25 to 4.0)"),
    use_cache: bool = Form(True, description="Use cached audio if available")
):
    """
    Convert text to speech using OpenAI TTS
    
    **Voices**:
    - `alloy` - Neutral, balanced tone
    - `echo` - Male, warm tone
    - `fable` - Neutral, expressive
    - `onyx` - Male, deep voice
    - `nova` - Female, friendly (default)
    - `shimmer` - Female, gentle
    
    **Example**:
    ```bash
    curl -X POST http://localhost:8000/api/ai/voice/synthesize \
      -F "text=Hello, how can I help you today?" \
      -F "voice=nova" \
      -F "speed=1.0" \
      --output speech.mp3
    ```
    
    **Response**: MP3 audio file
    """
    try:
        from fastapi.responses import Response
        
        if not text or len(text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty"
            )
        
        if len(text) > 4096:
            raise HTTPException(
                status_code=400,
                detail="Text too long. Maximum 4096 characters"
            )
        
        tts_service = get_tts_service()
        
        logger.info(f"Synthesizing: '{text[:50]}...' (voice: {voice})")
        
        audio_bytes = await tts_service.synthesize(
            text=text,
            voice=voice,
            speed=speed,
            use_cache=use_cache
        )
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'attachment; filename="speech.mp3"',
                "X-Audio-Duration": "estimated",
                "X-Voice-Used": voice
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Speech synthesis failed: {str(e)}"
        )


@router.post("/synthesize-emotion")
async def synthesize_with_emotion(
    text: str = Form(..., description="Text to synthesize"),
    emotion: str = Form("neutral", description="Emotion (neutral, happy, sad, excited, calm)"),
    gender: Optional[str] = Form(None, description="Gender preference (male, female, neutral)")
):
    """
    Synthesize speech with emotion-based voice selection
    
    **Emotions**:
    - `neutral` - Balanced tone (alloy)
    - `happy` - Upbeat, friendly (nova)
    - `sad` - Gentle, soft (shimmer)
    - `excited` - Expressive (fable)
    - `calm` - Warm, soothing (echo)
    
    **Example**:
    ```bash
    curl -X POST http://localhost:8000/api/ai/voice/synthesize-emotion \
      -F "text=I'm so excited to help you!" \
      -F "emotion=excited" \
      --output excited_speech.mp3
    ```
    """
    try:
        from fastapi.responses import Response
        
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        valid_emotions = ["neutral", "happy", "sad", "excited", "calm"]
        if emotion not in valid_emotions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid emotion. Choose from: {', '.join(valid_emotions)}"
            )
        
        tts_service = get_tts_service()
        
        audio_bytes = await tts_service.synthesize_with_emotion(
            text=text,
            emotion=emotion,
            gender_preference=gender
        )
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="speech_{emotion}.mp3"',
                "X-Emotion": emotion
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Emotion synthesis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Synthesis failed: {str(e)}"
        )


@router.get("/voices")
async def list_voices():
    """
    List all available TTS voices with characteristics
    
    **Response**:
    ```json
    {
        "nova": {
            "gender": "female",
            "tone": "friendly",
            "speed": "medium",
            "available": true
        },
        ...
    }
    ```
    """
    try:
        tts_service = get_tts_service()
        voices = tts_service.list_voices()
        
        return {
            "voices": voices,
            "total": len(voices),
            "default": "nova"
        }
    
    except Exception as e:
        logger.error(f"List voices error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list voices"
        )


@router.delete("/cache")
async def clear_tts_cache():
    """
    Clear all cached TTS audio files
    
    **Response**:
    ```json
    {
        "cleared": 42,
        "message": "Cache cleared successfully"
    }
    ```
    """
    try:
        tts_service = get_tts_service()
        count = await tts_service.clear_cache()
        
        return {
            "cleared": count,
            "message": f"Cleared {count} cached audio files"
        }
    
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear cache"
        )

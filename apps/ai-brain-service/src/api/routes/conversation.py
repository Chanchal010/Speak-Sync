"""
Conversation API Routes - Complete voice interaction endpoints
Integrates STT → NLU → TTS pipeline
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict
import logging
import base64
import asyncio

from src.services.conversation_service import get_conversation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai/conversation", tags=["Conversation"])


# Request/Response Models
class VoiceConversationRequest(BaseModel):
    """Request for voice conversation (audio upload)"""
    user_id: str = Field(..., description="User identifier")
    voice_profile: str = Field(default="default", description="Voice style: default, friendly, professional, energetic")
    language: Optional[str] = Field(default=None, description="Language code (e.g., 'en', 'es')")


class TextConversationRequest(BaseModel):
    """Request for text-based conversation"""
    text: str = Field(..., description="User's text input")
    user_id: str = Field(..., description="User identifier")
    voice_profile: str = Field(default="default", description="Voice style for audio response")
    include_audio: bool = Field(default=True, description="Include audio response")


class ConversationResponse(BaseModel):
    """Response from conversation endpoint"""
    session_id: str
    turn: int
    understanding: Dict
    response: Dict
    audio: Optional[Dict] = None
    audio_base64: Optional[str] = None


# Endpoints
@router.post("/voice", response_model=ConversationResponse)
async def voice_conversation(
    audio: UploadFile = File(..., description="Audio file (wav, mp3, m4a, webm, ogg, flac)"),
    user_id: str = "default_user",
    voice_profile: str = "default",
    language: Optional[str] = None
):
    """
    Complete voice interaction: Upload audio → Get transcription + understanding + audio response
    
    This endpoint processes voice input through the complete STT → NLU → TTS pipeline:
    1. Transcribes audio to text (OpenAI Whisper)
    2. Understands intent and extracts entities (OpenRouter LLM)
    3. Generates conversational response
    4. Synthesizes speech response (OpenAI TTS)
    
    **Example Usage:**
    ```bash
    curl -X POST "http://localhost:8000/api/ai/conversation/voice?user_id=user123" \\
      -H "Content-Type: multipart/form-data" \\
      -F "audio=@recording.mp3" \\
      -F "voice_profile=friendly"
    ```
    
    **Voice Profiles:**
    - `default`: Balanced and clear (alloy)
    - `friendly`: Warm and approachable (nova)
    - `professional`: Formal and confident (onyx)
    - `energetic`: Upbeat and dynamic (shimmer)
    """
    try:
        # Read audio data
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Process through conversation service
        conversation_service = get_conversation_service()
        result = await conversation_service.process_voice_input(
            audio_data=audio_data,
            user_id=user_id,
            voice_profile=voice_profile,
            language=language
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result.get("message"))
        
        # Extract audio data and encode as base64
        audio_response = result.pop("audio_data", None)
        if audio_response:
            result["audio_base64"] = base64.b64encode(audio_response).decode('utf-8')
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice conversation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Conversation processing failed: {str(e)}")


@router.post("/text")
async def text_conversation(request: TextConversationRequest):
    """
    Text-based conversation: Send text → Get understanding + audio response
    
    Bypasses STT but includes NLU → TTS pipeline for voice response.
    
    **Example:**
    ```json
    {
      "text": "I want to schedule a workout tomorrow",
      "user_id": "user123",
      "voice_profile": "friendly",
      "include_audio": true
    }
    ```
    """
    try:
        conversation_service = get_conversation_service()
        result = await conversation_service.process_text_input(
            text=request.text,
            user_id=request.user_id,
            voice_profile=request.voice_profile
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result.get("message"))
        
        # Handle audio response
        audio_response = result.pop("audio_data", None)
        
        if request.include_audio and audio_response:
            result["audio_base64"] = base64.b64encode(audio_response).decode('utf-8')
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text conversation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Conversation processing failed: {str(e)}")


@router.post("/voice/audio-response")
async def voice_conversation_audio_only(
    audio: UploadFile = File(...),
    user_id: str = "default_user",
    voice_profile: str = "default",
    language: Optional[str] = None
):
    """
    Voice conversation with audio response only (no JSON)
    
    Returns the synthesized audio directly as MP3.
    Useful for streaming audio players.
    """
    try:
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        conversation_service = get_conversation_service()
        result = await conversation_service.process_voice_input(
            audio_data=audio_data,
            user_id=user_id,
            voice_profile=voice_profile,
            language=language
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result.get("message"))
        
        # Return audio response directly
        audio_response = result.get("audio_data")
        if not audio_response:
            raise HTTPException(status_code=500, detail="No audio response generated")
        
        return Response(
            content=audio_response,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=response.mp3",
                "X-Session-Id": result.get("session_id", ""),
                "X-Intent": result.get("understanding", {}).get("intent", "unknown"),
                "X-Response-Text": result.get("response", {}).get("text", "")
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice conversation (audio-only) failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/stream")
async def conversation_stream(websocket: WebSocket):
    """
    Real-time streaming conversation via WebSocket
    
    **Protocol:**
    1. Client sends: `{"type": "audio", "data": "<base64>", "user_id": "user123"}`
    2. Server sends: Status updates and final response
    
    **Message Types:**
    - `status`: Connection/processing status
    - `progress`: Audio upload progress
    - `transcription`: Transcribed text
    - `understanding`: Intent detection result
    - `response`: Generated response text
    - `audio`: Audio response (base64)
    - `complete`: Conversation turn complete
    - `error`: Error occurred
    """
    await websocket.accept()
    conversation_service = get_conversation_service()
    user_id = None
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "status",
            "message": "Connected to conversation service"
        })
        
        while True:
            # Receive message from client
            message = await websocket.receive_json()
            msg_type = message.get("type")
            
            if msg_type == "audio":
                # Process audio message
                user_id = message.get("user_id", "websocket_user")
                audio_base64 = message.get("data")
                voice_profile = message.get("voice_profile", "default")
                
                if not audio_base64:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No audio data provided"
                    })
                    continue
                
                # Decode audio
                audio_data = base64.b64decode(audio_base64)
                
                # Send processing status
                await websocket.send_json({
                    "type": "status",
                    "message": "Processing audio..."
                })
                
                # Process conversation
                result = await conversation_service.process_voice_input(
                    audio_data=audio_data,
                    user_id=user_id,
                    voice_profile=voice_profile
                )
                
                if result.get("error"):
                    await websocket.send_json({
                        "type": "error",
                        "message": result.get("message")
                    })
                    continue
                
                # Send transcription
                if "transcription" in result:
                    await websocket.send_json({
                        "type": "transcription",
                        "data": result["transcription"]
                    })
                
                # Send understanding
                if "understanding" in result:
                    await websocket.send_json({
                        "type": "understanding",
                        "data": result["understanding"]
                    })
                
                # Send response text
                if "response" in result:
                    await websocket.send_json({
                        "type": "response",
                        "data": result["response"]
                    })
                
                # Send audio response
                audio_response = result.pop("audio_data", None)
                if audio_response:
                    await websocket.send_json({
                        "type": "audio",
                        "data": base64.b64encode(audio_response).decode('utf-8'),
                        "format": "mp3"
                    })
                
                # Send completion
                await websocket.send_json({
                    "type": "complete",
                    "session_id": result.get("session_id"),
                    "turn": result.get("turn")
                })
            
            elif msg_type == "text":
                # Process text message
                user_id = message.get("user_id", "websocket_user")
                text = message.get("text")
                voice_profile = message.get("voice_profile", "default")
                
                if not text:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No text provided"
                    })
                    continue
                
                # Process text conversation
                result = await conversation_service.process_text_input(
                    text=text,
                    user_id=user_id,
                    voice_profile=voice_profile
                )
                
                # Send results (similar to audio processing)
                if "understanding" in result:
                    await websocket.send_json({
                        "type": "understanding",
                        "data": result["understanding"]
                    })
                
                if "response" in result:
                    await websocket.send_json({
                        "type": "response",
                        "data": result["response"]
                    })
                
                audio_response = result.pop("audio_data", None)
                if audio_response:
                    await websocket.send_json({
                        "type": "audio",
                        "data": base64.b64encode(audio_response).decode('utf-8'),
                        "format": "mp3"
                    })
                
                await websocket.send_json({
                    "type": "complete",
                    "session_id": result.get("session_id"),
                    "turn": result.get("turn")
                })
            
            elif msg_type == "ping":
                # Heartbeat
                await websocket.send_json({"type": "pong"})
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}"
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {user_id}")
        if user_id:
            conversation_service.end_session(user_id)
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass


@router.get("/session/{user_id}")
async def get_session_info(user_id: str):
    """
    Get information about active conversation session
    
    **Returns:**
    - Session metadata
    - Turn count
    - Last activity
    - Last intent
    """
    conversation_service = get_conversation_service()
    session_info = conversation_service.get_session_info(user_id)
    
    if not session_info:
        raise HTTPException(status_code=404, detail="No active session found")
    
    return session_info


@router.delete("/session/{user_id}")
async def end_session(user_id: str):
    """
    End conversation session for user
    
    Clears conversation history and context.
    """
    conversation_service = get_conversation_service()
    success = conversation_service.end_session(user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="No active session found")
    
    return {"message": "Session ended", "user_id": user_id}


@router.get("/health")
async def conversation_health():
    """Health check for conversation service"""
    try:
        conversation_service = get_conversation_service()
        
        # Check if all sub-services are available
        has_voice = conversation_service.voice_service is not None
        has_nlu = conversation_service.nlu_service is not None
        has_tts = conversation_service.tts_service is not None
        
        active_sessions = len(conversation_service.active_sessions)
        
        status = "healthy" if (has_voice and has_nlu and has_tts) else "degraded"
        
        return {
            "status": status,
            "services": {
                "voice": "available" if has_voice else "unavailable",
                "nlu": "available" if has_nlu else "unavailable",
                "tts": "available" if has_tts else "unavailable"
            },
            "active_sessions": active_sessions,
            "voice_profiles": list(conversation_service.voice_profiles.keys())
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

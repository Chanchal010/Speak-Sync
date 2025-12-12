"""
gRPC server for Voice AI Service
Handles real-time voice streaming, transcription, and synthesis
"""
import grpc
from concurrent import futures
import asyncio
import logging
from typing import AsyncIterator

from grpc_generated import voice_pb2, voice_pb2_grpc
from services.voice_service import VoiceService
from services.tts_service import TTSService
from services.conversation_service import ConversationService

logger = logging.getLogger(__name__)


class VoiceServicer(voice_pb2_grpc.VoiceServiceServicer):
    """Implementation of VoiceService gRPC service"""
    
    def __init__(
        self, 
        voice_service: VoiceService,
        tts_service: TTSService,
        conversation_service: ConversationService
    ):
        self.voice_service = voice_service
        self.tts_service = tts_service
        self.conversation_service = conversation_service
        logger.info("VoiceServicer initialized")
    
    async def StreamTranscribe(
        self,
        request_iterator: AsyncIterator[voice_pb2.AudioChunk],
        context: grpc.aio.ServicerContext
    ) -> AsyncIterator[voice_pb2.TranscriptChunk]:
        """
        Real-time audio transcription (streaming)
        Client sends audio chunks, we stream back transcription
        """
        logger.info("StreamTranscribe called")
        
        try:
            audio_buffer = bytearray()
            session_id = None
            chunk_count = 0
            
            async for audio_chunk in request_iterator:
                if session_id is None:
                    session_id = audio_chunk.session_id
                    logger.info(f"Starting transcription session: {session_id}")
                
                audio_buffer.extend(audio_chunk.audio_data)
                chunk_count += 1
                
                # Process every 3 seconds of audio (48000 samples at 16kHz)
                if len(audio_buffer) >= 48000 * 2:  # 2 bytes per sample (16-bit)
                    transcript_result = await self.voice_service.transcribe_chunk(
                        audio_data=bytes(audio_buffer),
                        language=audio_chunk.format or "en"
                    )
                    
                    # Yield partial transcription
                    yield voice_pb2.TranscriptChunk(
                        text=transcript_result['text'],
                        is_final=False,
                        confidence=transcript_result.get('confidence', 0.0),
                        language=transcript_result.get('language', 'en')
                    )
                    
                    audio_buffer.clear()
            
            # Final transcription with remaining buffer
            if audio_buffer:
                transcript_result = await self.voice_service.transcribe_chunk(
                    audio_data=bytes(audio_buffer)
                )
                
                yield voice_pb2.TranscriptChunk(
                    text=transcript_result['text'],
                    is_final=True,
                    confidence=transcript_result.get('confidence', 0.0),
                    language=transcript_result.get('language', 'en')
                )
            
            logger.info(f"Transcription session {session_id} complete ({chunk_count} chunks)")
        
        except Exception as e:
            logger.error(f"Error in StreamTranscribe: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Transcription failed: {e}")
    
    async def TranscribeAudio(
        self,
        request: voice_pb2.AudioRequest,
        context: grpc.aio.ServicerContext
    ) -> voice_pb2.TranscriptResponse:
        """
        Single audio file transcription
        """
        logger.info(f"TranscribeAudio called for user: {request.user_id}")
        
        try:
            result = await self.voice_service.transcribe_audio(
                audio_data=request.audio_data,
                language=request.language or None
            )
            
            return voice_pb2.TranscriptResponse(
                text=result['text'],
                language=result['language'],
                confidence=result['confidence'],
                duration_ms=result.get('duration_ms', 0)
            )
        
        except Exception as e:
            logger.error(f"Error in TranscribeAudio: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Transcription failed: {e}")
    
    async def Synthesize(
        self,
        request: voice_pb2.SynthesizeRequest,
        context: grpc.aio.ServicerContext
    ) -> voice_pb2.AudioResponse:
        """
        Single text-to-speech synthesis using OpenAI TTS
        """
        logger.info(f"Synthesize called: '{request.text[:50]}...'")
        
        try:
            # Map request voice to OpenAI voice
            voice_map = {
                "en-us-female-calm": "shimmer",
                "en-us-female-friendly": "nova",
                "en-us-male-warm": "echo",
                "en-us-male-deep": "onyx",
                "neutral": "alloy",
                "expressive": "fable"
            }
            voice = voice_map.get(request.voice, "nova")
            
            # Synthesize with OpenAI TTS
            audio_bytes = await self.tts_service.synthesize(
                text=request.text,
                voice=voice,
                speed=request.speaking_rate if request.HasField('speaking_rate') else 1.0,
                use_cache=request.use_cache if request.HasField('use_cache') else True
            )
            
            return voice_pb2.AudioResponse(
                audio_data=audio_bytes,
                format="mp3",  # OpenAI TTS returns MP3
                duration_ms=0,  # Calculated on client side
                sample_rate=24000,  # OpenAI TTS default
                from_cache=False  # We can add cache detection later
            )
        
        except Exception as e:
            logger.error(f"Error in Synthesize: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Synthesis failed: {e}")
    
    async def StreamSynthesize(
        self,
        request: voice_pb2.SynthesizeRequest,
        context: grpc.aio.ServicerContext
    ) -> AsyncIterator[voice_pb2.AudioChunk]:
        """
        Streaming text-to-speech using OpenAI TTS streaming
        """
        logger.info(f"StreamSynthesize called: '{request.text[:50]}...'")
        
        try:
            # Map voice
            voice_map = {
                "en-us-female-calm": "shimmer",
                "en-us-female-friendly": "nova",
                "en-us-male-warm": "echo",
                "en-us-male-deep": "onyx",
                "neutral": "alloy",
                "expressive": "fable"
            }
            voice = voice_map.get(request.voice, "nova")
            
            # Stream synthesis
            async for audio_chunk in self.tts_service.synthesize_streaming(
                text=request.text,
                voice=voice,
                speed=request.speaking_rate if request.HasField('speaking_rate') else 1.0
            ):
                yield voice_pb2.AudioChunk(
                    audio_data=audio_chunk,
                    session_id=request.user_id if request.HasField('user_id') else "default",
                    format="mp3"
                )
        
        except Exception as e:
            logger.error(f"Error in StreamSynthesize: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Synthesis streaming failed: {e}")
    
    async def Converse(
        self,
        request_iterator: AsyncIterator[voice_pb2.AudioChunk],
        context: grpc.aio.ServicerContext
    ) -> AsyncIterator[voice_pb2.ConversationResponse]:
        """
        Complete conversation flow: STT → LLM → TTS
        """
        logger.info("Converse called - full voice conversation")
        
        try:
            session_id = None
            user_id = None
            
            # Collect audio chunks
            audio_chunks = []
            async for audio_chunk in request_iterator:
                if session_id is None:
                    session_id = audio_chunk.session_id
                    logger.info(f"Conversation session started: {session_id}")
                
                audio_chunks.append(audio_chunk.audio_data)
            
            # Combine audio
            full_audio = b''.join(audio_chunks)
            
            # Process conversation
            async for response in self.conversation_service.handle_conversation(
                audio_data=full_audio,
                session_id=session_id,
                user_id=user_id or "anonymous"
            ):
                # Map response types to protobuf
                if response['type'] == 'transcript':
                    yield voice_pb2.ConversationResponse(
                        transcript=voice_pb2.TranscriptChunk(
                            text=response['text'],
                            is_final=response.get('is_final', True),
                            confidence=response.get('confidence', 0.0)
                        ),
                        is_final=False,
                        session_id=session_id
                    )
                
                elif response['type'] == 'processing':
                    yield voice_pb2.ConversationResponse(
                        processing=voice_pb2.ProcessingStatus(
                            status=response['status'],
                            message=response.get('message', ''),
                            progress=response.get('progress', 0.0)
                        ),
                        is_final=False,
                        session_id=session_id
                    )
                
                elif response['type'] == 'llm_response':
                    yield voice_pb2.ConversationResponse(
                        llm_text=response['text'],
                        is_final=False,
                        session_id=session_id
                    )
                
                elif response['type'] == 'audio':
                    yield voice_pb2.ConversationResponse(
                        audio=voice_pb2.AudioChunk(
                            audio_data=response['audio_data'],
                            session_id=session_id
                        ),
                        is_final=response.get('is_final', False),
                        session_id=session_id
                    )
                
                elif response['type'] == 'action':
                    yield voice_pb2.ConversationResponse(
                        action=voice_pb2.ActionResult(
                            action_type=response['action_type'],
                            entity_id=response.get('entity_id', ''),
                            success=response.get('success', True),
                            message=response.get('message', '')
                        ),
                        is_final=response.get('is_final', False),
                        session_id=session_id
                    )
        
        except Exception as e:
            logger.error(f"Error in Converse: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Conversation failed: {e}")


class HealthServicer(voice_pb2_grpc.HealthServiceServicer):
    """Health check service"""
    
    async def Check(
        self,
        request: voice_pb2.HealthCheckRequest,
        context: grpc.aio.ServicerContext
    ) -> voice_pb2.HealthCheckResponse:
        """Health check endpoint"""
        
        # TODO: Add actual health checks for DB, Redis, etc.
        return voice_pb2.HealthCheckResponse(
            status=voice_pb2.HealthCheckResponse.SERVING,
            message="AI Brain Service is healthy",
            details={
                "version": "1.0.0",
                "service": "ai-brain-service"
            }
        )


async def serve(host: str = "0.0.0.0", port: int = 50051):
    """
    Start gRPC server
    
    Args:
        host: Server host (default: 0.0.0.0)
        port: Server port (default: 50051)
    """
    # Initialize services (will be created in main.py)
    from core.dependencies import get_voice_service, get_tts_service, get_conversation_service
    
    voice_service = await get_voice_service()
    tts_service = await get_tts_service()
    conversation_service = await get_conversation_service()
    
    # Create server with thread pool
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.so_reuseport', 1),
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.keepalive_timeout_ms', 5000),
        ]
    )
    
    # Add servicers
    voice_pb2_grpc.add_VoiceServiceServicer_to_server(
        VoiceServicer(voice_service, tts_service, conversation_service),
        server
    )
    voice_pb2_grpc.add_HealthServiceServicer_to_server(
        HealthServicer(),
        server
    )
    
    # Bind to address
    server.add_insecure_port(f'{host}:{port}')
    
    # Start server
    await server.start()
    logger.info(f"✓ gRPC server started on {host}:{port}")
    logger.info(f"  - VoiceService available")
    logger.info(f"  - HealthService available")
    
    # Wait for termination
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())

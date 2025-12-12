"""
Voice Service - Speech-to-Text using OpenAI Whisper
Handles audio transcription with support for multiple formats and languages
"""
import openai
from openai import AsyncOpenAI
from typing import Optional, Dict, AsyncIterator
import aiofiles
import os
import io
import tempfile
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Singleton instance
_voice_service_instance: Optional['VoiceService'] = None

# Try to import pydub, but don't fail if not available
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logger.warning("pydub not available - audio format conversion disabled")


class VoiceService:
    """
    Speech-to-Text service using OpenAI Whisper API
    Supports: WAV, MP3, M4A, WEBM, OGG formats
    Languages: Auto-detect or specify (en, hi, es, fr, etc.)
    """
    
    def __init__(self, api_key: str, model: str = "whisper-1"):
        """
        Initialize Whisper STT service
        
        Args:
            api_key: OpenAI API key
            model: Whisper model (default: whisper-1)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.supported_formats = ['wav', 'mp3', 'm4a', 'webm', 'ogg', 'flac']
        
        logger.info(f"✓ VoiceService initialized with model: {model}")
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        format: str = "wav"
    ) -> Dict:
        """
        Transcribe audio file
        
        Args:
            audio_data: Raw audio bytes
            language: Language code (e.g., 'en', 'hi') or None for auto-detect
            format: Audio format (wav, mp3, m4a, etc.)
        
        Returns:
            {
                'text': 'Transcribed text',
                'language': 'en',
                'confidence': 0.95,
                'duration_ms': 5000
            }
        """
        try:
            # Validate format
            if format.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported format: {format}. Supported: {self.supported_formats}")
            
            # Create temporary file (Whisper API requires file upload)
            with tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                # Get audio duration for metrics (if pydub available)
                duration_ms = 0
                if PYDUB_AVAILABLE:
                    audio = AudioSegment.from_file(temp_path, format=format)
                    duration_ms = len(audio)
                
                # Transcribe with Whisper
                async with aiofiles.open(temp_path, 'rb') as audio_file:
                    audio_bytes = await audio_file.read()
                    
                    # OpenAI Whisper API call
                    transcript = await self.client.audio.transcriptions.create(
                        model=self.model,
                        file=(f"audio.{format}", audio_bytes),
                        language=language,
                        response_format="verbose_json"  # Get detailed response with confidence
                    )
                
                # Calculate average confidence from segments
                confidence = self._calculate_confidence(transcript)
                
                result = {
                    'text': transcript.text,
                    'language': transcript.language,
                    'confidence': confidence,
                    'duration_ms': duration_ms
                }
                
                logger.info(f"✓ Transcribed {duration_ms}ms audio: '{transcript.text[:50]}...'")
                return result
            
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    async def transcribe_chunk(
        self,
        audio_data: bytes,
        language: Optional[str] = "en"
    ) -> Dict:
        """
        Transcribe audio chunk for streaming (optimized for real-time)
        
        Args:
            audio_data: Raw audio bytes
            language: Language code (default: en)
        
        Returns:
            {
                'text': 'Partial transcription',
                'confidence': 0.9,
                'language': 'en'
            }
        """
        try:
            # For streaming, we process smaller chunks
            # If pydub available, convert to WAV, otherwise send as-is
            if PYDUB_AVAILABLE:
                audio = AudioSegment.from_file(
                    io.BytesIO(audio_data),
                    format="wav"
                )
                
                # Export as WAV for Whisper
                wav_buffer = io.BytesIO()
                audio.export(wav_buffer, format="wav")
                wav_buffer.seek(0)
                audio_bytes = wav_buffer.read()
            else:
                # Send audio directly (assume WAV format)
                audio_bytes = audio_data
            
            # Transcribe chunk
            transcript = await self.client.audio.transcriptions.create(
                model=self.model,
                file=("chunk.wav", audio_bytes),
                language=language,
                response_format="verbose_json"
            )
            
            confidence = self._calculate_confidence(transcript)
            
            return {
                'text': transcript.text,
                'confidence': confidence,
                'language': transcript.language
            }
        
        except Exception as e:
            logger.error(f"Chunk transcription failed: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'language': language or 'en'
            }
    
    async def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None
    ) -> Dict:
        """
        Transcribe audio from file path
        
        Args:
            file_path: Path to audio file
            language: Language code or None for auto-detect
        
        Returns:
            Transcription result dictionary
        """
        try:
            # Detect format from file extension
            format = Path(file_path).suffix[1:].lower()
            
            # Read file
            async with aiofiles.open(file_path, 'rb') as f:
                audio_data = await f.read()
            
            # Transcribe
            return await self.transcribe_audio(
                audio_data=audio_data,
                language=language,
                format=format
            )
        
        except Exception as e:
            logger.error(f"File transcription failed: {e}")
            raise
    
    def _calculate_confidence(self, transcript) -> float:
        """
        Calculate average confidence score from transcript segments
        
        Args:
            transcript: Whisper API response
        
        Returns:
            Average confidence (0.0 to 1.0)
        """
        try:
            # Whisper doesn't provide confidence in basic response
            # For verbose_json, we can estimate from segments if available
            if hasattr(transcript, 'segments') and transcript.segments:
                # Calculate from segment probabilities
                total_confidence = sum(
                    segment.get('avg_logprob', -1.0) 
                    for segment in transcript.segments
                )
                avg_confidence = total_confidence / len(transcript.segments)
                # Convert log probability to confidence (0-1)
                # avg_logprob ranges from -inf to 0, normalize to 0-1
                confidence = max(0.0, min(1.0, (avg_confidence + 1.0)))
                return confidence
            
            # Default confidence if segments not available
            return 0.95  # Whisper is generally very accurate
        
        except Exception:
            return 0.90  # Conservative default
    
    async def validate_audio(
        self,
        audio_data: bytes,
        format: str = "wav"
    ) -> Dict:
        """
        Validate audio file quality and characteristics
        
        Args:
            audio_data: Raw audio bytes
            format: Audio format
        
        Returns:
            {
                'valid': True,
                'duration_ms': 5000,
                'sample_rate': 16000,
                'channels': 1,
                'format': 'wav'
            }
        """
        try:
            if not PYDUB_AVAILABLE:
                # Basic validation without pydub
                return {
                    'valid': True,
                    'duration_ms': 0,
                    'format': format,
                    'note': 'Advanced validation unavailable (pydub not installed)'
                }
            
            audio = AudioSegment.from_file(
                io.BytesIO(audio_data),
                format=format
            )
            
            return {
                'valid': True,
                'duration_ms': len(audio),
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
                'format': format,
                'bit_depth': audio.sample_width * 8
            }
        
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    async def convert_audio_format(
        self,
        audio_data: bytes,
        from_format: str,
        to_format: str = "wav",
        sample_rate: int = 16000
    ) -> bytes:
        """
        Convert audio from one format to another
        
        Args:
            audio_data: Raw audio bytes
            from_format: Source format
            to_format: Target format (default: wav)
            sample_rate: Target sample rate (default: 16000)
        
        Returns:
            Converted audio bytes
        """
        try:
            if not PYDUB_AVAILABLE:
                raise NotImplementedError("Audio conversion requires pydub. Please install: pip install pydub ffmpeg-python")
            
            # Load audio
            audio = AudioSegment.from_file(
                io.BytesIO(audio_data),
                format=from_format
            )
            
            # Convert to mono if stereo (reduce size)
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Resample if needed
            if audio.frame_rate != sample_rate:
                audio = audio.set_frame_rate(sample_rate)
            
            # Export to target format
            output_buffer = io.BytesIO()
            audio.export(output_buffer, format=to_format)
            output_buffer.seek(0)
            
            return output_buffer.read()
        
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            raise


# Singleton instance (will be initialized in dependencies)
_voice_service_instance: Optional[VoiceService] = None


def get_voice_service() -> VoiceService:
    """Get or create VoiceService singleton"""
    global _voice_service_instance
    
    if _voice_service_instance is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        _voice_service_instance = VoiceService(api_key=api_key)
    
    return _voice_service_instance

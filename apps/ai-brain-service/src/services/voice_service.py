"""
Voice Service - Speech-to-Text using Google Speech Recognition (FREE!)
No API key needed, no quota limits for reasonable usage.
Falls back gracefully if service is unavailable.
"""
import speech_recognition as sr
from typing import Optional, Dict
import os
import io
import tempfile
from pathlib import Path
import logging
import asyncio

logger = logging.getLogger(__name__)

# Singleton instance
_voice_service_instance: Optional['VoiceService'] = None

# Try to import pydub for audio conversion
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logger.warning("pydub not available - audio format conversion disabled")


class VoiceService:
    """
    Speech-to-Text service using Google Speech Recognition (FREE!)
    Supports: WAV, MP3, M4A, WEBM, OGG, FLAC formats
    Languages: Auto-detect or specify (en, hi, es, fr, etc.)
    """
    
    def __init__(self, model: str = "google-free"):
        """
        Initialize free STT service
        
        Args:
            model: Model identifier (for logging/compatibility)
        """
        self.recognizer = sr.Recognizer()
        self.model = model
        self.supported_formats = ['wav', 'mp3', 'm4a', 'webm', 'ogg', 'flac']
        
        # Tune recognizer settings
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        
        logger.info(f"✓ VoiceService initialized with model: {model} (FREE, no API key!)")
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        format: str = "wav"
    ) -> Dict:
        """
        Transcribe audio using Google Speech Recognition (free)
        
        Args:
            audio_data: Raw audio bytes
            language: Language code (e.g., 'en', 'hi', 'en-IN') or None for auto
            format: Audio format (wav, mp3, m4a, etc.)
        
        Returns:
            {
                'text': 'Transcribed text',
                'language': 'en',
                'confidence': 0.90,
                'duration_ms': 5000
            }
        """
        try:
            # Validate format
            if format.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported format: {format}. Supported: {self.supported_formats}")
            
            # Convert to WAV if needed (Google SR needs WAV)
            wav_data = await self._ensure_wav(audio_data, format)
            
            # Run transcription in executor (blocking operation)
            result = await asyncio.get_event_loop().run_in_executor(
                None, self._transcribe_sync, wav_data, language
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def _transcribe_sync(self, wav_data: bytes, language: Optional[str]) -> Dict:
        """Synchronous transcription using Google Speech Recognition"""
        try:
            # Load audio from bytes
            audio_file = sr.AudioFile(io.BytesIO(wav_data))
            
            with audio_file as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.record(source)
            
            # Map language codes for Google SR
            lang_code = self._map_language(language)
            
            # Try Google free recognition first
            try:
                text = self.recognizer.recognize_google(
                    audio,
                    language=lang_code,
                    show_all=False
                )
                
                logger.info(f"✓ Transcribed: '{text[:50]}...' (Google Free STT)")
                
                return {
                    'text': text,
                    'language': language or 'en',
                    'confidence': 0.90,  # Google free doesn't return confidence
                    'duration_ms': int(len(wav_data) / 32)  # Rough estimate
                }
                
            except sr.UnknownValueError:
                logger.warning("Google SR could not understand audio")
                return {
                    'text': '',
                    'language': language or 'en',
                    'confidence': 0.0,
                    'duration_ms': 0
                }
                
            except sr.RequestError as e:
                logger.error(f"Google SR service error: {e}")
                raise
                
        except Exception as e:
            logger.error(f"Sync transcription failed: {e}")
            raise
    
    def _map_language(self, language: Optional[str]) -> str:
        """Map language codes to Google Speech Recognition format"""
        if not language or language == 'auto':
            return 'en-US'
        
        lang_map = {
            'en': 'en-US',
            'hi': 'hi-IN',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'ja': 'ja-JP',
            'zh': 'zh-CN',
            'ko': 'ko-KR',
            'pt': 'pt-BR',
            'ru': 'ru-RU',
            'ar': 'ar-SA',
            'it': 'it-IT',
        }
        
        return lang_map.get(language, language)
    
    async def _ensure_wav(self, audio_data: bytes, format: str) -> bytes:
        """Convert audio to WAV format if needed"""
        if format.lower() == 'wav':
            return audio_data
        
        if not PYDUB_AVAILABLE:
            # If pydub not available, try to use the raw data
            logger.warning(f"Cannot convert {format} to WAV (pydub not available), trying raw")
            return audio_data
        
        try:
            def convert():
                audio = AudioSegment.from_file(io.BytesIO(audio_data), format=format)
                # Convert to mono, 16kHz WAV
                audio = audio.set_channels(1).set_frame_rate(16000)
                wav_buffer = io.BytesIO()
                audio.export(wav_buffer, format='wav')
                return wav_buffer.getvalue()
            
            return await asyncio.get_event_loop().run_in_executor(None, convert)
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            return audio_data  # Try with raw data
    
    async def transcribe_chunk(
        self,
        audio_data: bytes,
        language: Optional[str] = "en"
    ) -> Dict:
        """Transcribe audio chunk for streaming"""
        try:
            return await self.transcribe_audio(audio_data, language, format="wav")
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
        """Transcribe audio from file path"""
        try:
            format = Path(file_path).suffix[1:].lower()
            
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            
            return await self.transcribe_audio(
                audio_data=audio_data,
                language=language,
                format=format
            )
        except Exception as e:
            logger.error(f"File transcription failed: {e}")
            raise
    
    async def validate_audio(
        self,
        audio_data: bytes,
        format: str = "wav"
    ) -> Dict:
        """Validate audio file quality"""
        try:
            if not PYDUB_AVAILABLE:
                return {
                    'valid': True,
                    'duration_ms': 0,
                    'format': format,
                    'note': 'Advanced validation unavailable'
                }
            
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=format)
            
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
            return {'valid': False, 'error': str(e)}


def get_voice_service() -> VoiceService:
    """Get or create VoiceService singleton"""
    global _voice_service_instance
    
    if _voice_service_instance is None:
        _voice_service_instance = VoiceService()  # No API key needed!
    
    return _voice_service_instance

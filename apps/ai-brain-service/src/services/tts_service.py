"""
TTS Service - Text-to-Speech using OpenAI TTS API
Provides high-quality voice synthesis with multiple voices and emotions
"""
from openai import AsyncOpenAI
from typing import Optional, Dict, Literal
import logging
import io
import aiofiles
import os
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

# Singleton instance
_tts_service_instance: Optional['TTSService'] = None

# Voice mappings with emotional characteristics
VOICE_PROFILES = {
    "alloy": {"gender": "neutral", "tone": "balanced", "speed": "medium"},
    "echo": {"gender": "male", "tone": "warm", "speed": "medium"},
    "fable": {"gender": "neutral", "tone": "expressive", "speed": "medium"},
    "onyx": {"gender": "male", "tone": "deep", "speed": "slow"},
    "nova": {"gender": "female", "tone": "friendly", "speed": "medium"},
    "shimmer": {"gender": "female", "tone": "gentle", "speed": "medium"}
}


class TTSService:
    """
    OpenAI TTS Service for high-quality speech synthesis
    """
    
    def __init__(self, api_key: str, cache_dir: Optional[str] = None):
        """
        Initialize TTS service
        
        Args:
            api_key: OpenAI API key
            cache_dir: Directory for caching synthesized audio
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "tts-1"  # or tts-1-hd for higher quality
        self.cache_dir = Path(cache_dir) if cache_dir else Path("cache/tts")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported voices
        self.supported_voices = list(VOICE_PROFILES.keys())
        
        logger.info(f"✓ TTS Service initialized with {len(self.supported_voices)} voices")
    
    async def synthesize(
        self,
        text: str,
        voice: str = "nova",
        speed: float = 1.0,
        use_cache: bool = True
    ) -> bytes:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speech speed (0.25 to 4.0)
            use_cache: Whether to use cached audio if available
        
        Returns:
            Audio bytes in MP3 format
        
        Example:
            audio = await tts_service.synthesize(
                text="Hello, how can I help you?",
                voice="nova",
                speed=1.0
            )
        """
        try:
            # Validate inputs
            if voice not in self.supported_voices:
                logger.warning(f"Invalid voice '{voice}', using 'nova'")
                voice = "nova"
            
            speed = max(0.25, min(4.0, speed))
            
            # Check cache
            if use_cache:
                cache_key = self._get_cache_key(text, voice, speed)
                cached_audio = await self._get_from_cache(cache_key)
                if cached_audio:
                    logger.info(f"✓ Cache hit for: '{text[:50]}...'")
                    return cached_audio
            
            # Synthesize with OpenAI
            logger.info(f"Synthesizing: '{text[:50]}...' (voice: {voice}, speed: {speed})")
            
            response = await self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3"
            )
            
            # Get audio bytes
            audio_bytes = response.content
            
            # Cache if enabled
            if use_cache:
                await self._save_to_cache(cache_key, audio_bytes)
            
            logger.info(f"✓ Synthesized {len(audio_bytes)} bytes")
            return audio_bytes
        
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise
    
    async def synthesize_streaming(
        self,
        text: str,
        voice: str = "nova",
        speed: float = 1.0
    ):
        """
        Stream synthesized audio (for real-time playback)
        
        Args:
            text: Text to synthesize
            voice: Voice to use
            speed: Speech speed
        
        Yields:
            Audio chunks as they're generated
        """
        try:
            if voice not in self.supported_voices:
                voice = "nova"
            
            speed = max(0.25, min(4.0, speed))
            
            logger.info(f"Streaming synthesis: '{text[:50]}...'")
            
            async with self.client.audio.speech.with_streaming_response.create(
                model=self.model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3"
            ) as response:
                async for chunk in response.iter_bytes(chunk_size=4096):
                    yield chunk
        
        except Exception as e:
            logger.error(f"Streaming synthesis failed: {e}")
            raise
    
    async def synthesize_with_emotion(
        self,
        text: str,
        emotion: Literal["neutral", "happy", "sad", "excited", "calm"] = "neutral",
        gender_preference: Optional[Literal["male", "female", "neutral"]] = None
    ) -> bytes:
        """
        Synthesize with emotion-appropriate voice selection
        
        Args:
            text: Text to synthesize
            emotion: Desired emotion
            gender_preference: Preferred voice gender
        
        Returns:
            Audio bytes
        """
        # Emotion to voice mapping
        emotion_voice_map = {
            "neutral": "alloy",
            "happy": "nova",      # Friendly, upbeat
            "sad": "shimmer",     # Gentle, soft
            "excited": "fable",   # Expressive
            "calm": "echo"        # Warm, soothing
        }
        
        # Gender preference override
        if gender_preference:
            gender_voices = {
                "male": ["echo", "onyx"],
                "female": ["nova", "shimmer"],
                "neutral": ["alloy", "fable"]
            }
            voice_options = gender_voices.get(gender_preference, ["nova"])
            voice = voice_options[0]
        else:
            voice = emotion_voice_map.get(emotion, "nova")
        
        # Adjust speed based on emotion
        speed_map = {
            "neutral": 1.0,
            "happy": 1.1,
            "sad": 0.9,
            "excited": 1.2,
            "calm": 0.85
        }
        speed = speed_map.get(emotion, 1.0)
        
        logger.info(f"Emotion: {emotion}, Voice: {voice}, Speed: {speed}")
        
        return await self.synthesize(text, voice=voice, speed=speed)
    
    async def save_to_file(
        self,
        text: str,
        output_path: str,
        voice: str = "nova",
        speed: float = 1.0
    ):
        """
        Synthesize and save to file
        
        Args:
            text: Text to synthesize
            output_path: Output file path
            voice: Voice to use
            speed: Speech speed
        """
        audio_bytes = await self.synthesize(text, voice, speed)
        
        async with aiofiles.open(output_path, 'wb') as f:
            await f.write(audio_bytes)
        
        logger.info(f"✓ Saved audio to: {output_path}")
    
    def _get_cache_key(self, text: str, voice: str, speed: float) -> str:
        """Generate cache key from parameters"""
        content = f"{text}|{voice}|{speed}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _get_from_cache(self, cache_key: str) -> Optional[bytes]:
        """Retrieve from cache"""
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        
        if cache_file.exists():
            async with aiofiles.open(cache_file, 'rb') as f:
                return await f.read()
        
        return None
    
    async def _save_to_cache(self, cache_key: str, audio_bytes: bytes):
        """Save to cache"""
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        
        async with aiofiles.open(cache_file, 'wb') as f:
            await f.write(audio_bytes)
    
    async def clear_cache(self):
        """Clear all cached audio files"""
        count = 0
        for cache_file in self.cache_dir.glob("*.mp3"):
            cache_file.unlink()
            count += 1
        
        logger.info(f"✓ Cleared {count} cached files")
        return count
    
    def get_voice_info(self, voice: str) -> Dict:
        """Get information about a voice"""
        return VOICE_PROFILES.get(voice, {})
    
    def list_voices(self) -> Dict:
        """List all available voices with their characteristics"""
        return {
            voice: {
                **profile,
                "available": True
            }
            for voice, profile in VOICE_PROFILES.items()
        }


def get_tts_service() -> TTSService:
    """Get or create TTS service singleton"""
    global _tts_service_instance
    
    if _tts_service_instance is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        cache_dir = os.getenv("TTS_CACHE_DIR", "cache/tts")
        _tts_service_instance = TTSService(api_key=api_key, cache_dir=cache_dir)
    
    return _tts_service_instance

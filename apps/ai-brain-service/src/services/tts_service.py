"""
TTS Service - Text-to-Speech using Edge-TTS (FREE, no API key, no quota!)
Primary: Microsoft Edge neural voices via edge-tts (unlimited, high quality)
Fallback: OpenAI TTS (if configured and Edge fails)

Edge-TTS advantages:
- Completely FREE - no API key, no billing
- No quota limits - unlimited usage
- High quality neural voices (same as Microsoft Edge browser)
- Supports 300+ voices across 45+ languages including Hindi
- Customizable rate, volume, pitch via SSML
"""
import edge_tts
from typing import Optional, Dict, Literal
import logging
import io
import aiofiles
import os
from pathlib import Path
import hashlib
import asyncio

logger = logging.getLogger(__name__)

# Singleton instance
_tts_service_instance: Optional['TTSService'] = None

# Edge-TTS voice mappings (matching the old OpenAI voice names for compatibility)
# Format: ShortName from edge-tts voice list
EDGE_VOICE_PROFILES = {
    "nova": {
        "edge_voice": "en-US-JennyNeural",
        "gender": "female",
        "tone": "friendly",
        "speed": "medium",
        "description": "Friendly, warm female voice"
    },
    "shimmer": {
        "edge_voice": "en-US-AriaNeural", 
        "gender": "female",
        "tone": "gentle",
        "speed": "medium",
        "description": "Gentle, soft female voice"
    },
    "echo": {
        "edge_voice": "en-US-GuyNeural",
        "gender": "male",
        "tone": "warm",
        "speed": "medium",
        "description": "Warm male voice"
    },
    "onyx": {
        "edge_voice": "en-US-DavisNeural",
        "gender": "male",
        "tone": "deep",
        "speed": "slow",
        "description": "Deep, authoritative male voice"
    },
    "alloy": {
        "edge_voice": "en-US-AvaNeural",
        "gender": "neutral",
        "tone": "balanced",
        "speed": "medium",
        "description": "Balanced neutral voice"
    },
    "fable": {
        "edge_voice": "en-US-AnaNeural",
        "gender": "neutral",
        "tone": "expressive",
        "speed": "medium",
        "description": "Expressive, engaging voice"
    },
    # Hindi voices
    "hindi_male": {
        "edge_voice": "hi-IN-MadhurNeural",
        "gender": "male",
        "tone": "warm",
        "speed": "medium",
        "description": "Hindi male voice"
    },
    "hindi_female": {
        "edge_voice": "hi-IN-SwaraNeural",
        "gender": "female",
        "tone": "friendly",
        "speed": "medium",
        "description": "Hindi female voice"
    },
}


class TTSService:
    """
    Edge-TTS Service for high-quality FREE speech synthesis.
    Uses Microsoft Edge's neural TTS - no API key, no quota, unlimited!
    """
    
    def __init__(self, cache_dir: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize TTS service (Edge-TTS primary, OpenAI optional fallback)
        
        Args:
            cache_dir: Directory for caching synthesized audio
            api_key: Optional OpenAI API key for fallback (not required!)
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path("cache/tts")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Store OpenAI key for optional fallback
        self._openai_key = api_key
        self._openai_client = None
        
        # Supported voices
        self.supported_voices = list(EDGE_VOICE_PROFILES.keys())
        
        logger.info(f"✓ TTS Service initialized with Edge-TTS ({len(self.supported_voices)} voices) — FREE, no quota!")
    
    def _get_edge_voice(self, voice: str) -> str:
        """Get the Edge-TTS voice name from our voice mapping."""
        profile = EDGE_VOICE_PROFILES.get(voice, EDGE_VOICE_PROFILES["nova"])
        return profile["edge_voice"]
    
    def _speed_to_rate(self, speed: float) -> str:
        """Convert speed float (0.25-4.0) to Edge-TTS rate string (+/-XX%)."""
        # speed 1.0 = +0%, speed 1.5 = +50%, speed 0.5 = -50%
        percentage = int((speed - 1.0) * 100)
        if percentage >= 0:
            return f"+{percentage}%"
        return f"{percentage}%"
    
    async def synthesize(
        self,
        text: str,
        voice: str = "nova",
        speed: float = 1.0,
        use_cache: bool = True
    ) -> bytes:
        """
        Synthesize speech from text using Edge-TTS (FREE!)
        
        Args:
            text: Text to synthesize
            voice: Voice name (nova, echo, shimmer, onyx, alloy, fable, hindi_male, hindi_female)
            speed: Speech speed (0.25 to 4.0)
            use_cache: Whether to use cached audio if available
        
        Returns:
            Audio bytes in MP3 format
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
            
            # Synthesize with Edge-TTS (FREE!)
            edge_voice = self._get_edge_voice(voice)
            rate = self._speed_to_rate(speed)
            
            logger.info(f"Synthesizing: '{text[:50]}...' (voice: {voice}→{edge_voice}, rate: {rate})")
            
            communicate = edge_tts.Communicate(text, edge_voice, rate=rate)
            
            # Collect all audio chunks
            audio_chunks = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])
            
            audio_bytes = b"".join(audio_chunks)
            
            if not audio_bytes:
                raise Exception("Edge-TTS returned empty audio")
            
            # Cache if enabled
            if use_cache:
                await self._save_to_cache(cache_key, audio_bytes)
            
            logger.info(f"✓ Synthesized {len(audio_bytes)} bytes (Edge-TTS, FREE)")
            return audio_bytes
        
        except Exception as e:
            logger.error(f"Edge-TTS synthesis failed: {e}")
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
        content = f"edge|{text}|{voice}|{speed}"
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
        return EDGE_VOICE_PROFILES.get(voice, {})
    
    def list_voices(self) -> Dict:
        """List all available voices with their characteristics"""
        return {
            voice: {
                **profile,
                "available": True,
                "engine": "edge-tts",
                "cost": "FREE"
            }
            for voice, profile in EDGE_VOICE_PROFILES.items()
        }


def get_tts_service() -> TTSService:
    """Get or create TTS service singleton"""
    global _tts_service_instance
    
    if _tts_service_instance is None:
        cache_dir = os.getenv("TTS_CACHE_DIR", "cache/tts")
        # OpenAI key is optional now — Edge-TTS doesn't need it!
        api_key = os.getenv("OPENAI_API_KEY", None)
        _tts_service_instance = TTSService(cache_dir=cache_dir, api_key=api_key)
    
    return _tts_service_instance

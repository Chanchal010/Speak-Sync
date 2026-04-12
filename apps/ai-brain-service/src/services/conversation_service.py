"""
Conversation Service - Orchestrates complete voice interaction flow
Integrates: STT → NLU → TTS for natural voice conversations
"""
from typing import Optional, Dict, List, AsyncIterator
import logging
import asyncio
from datetime import datetime
import json

from src.services.voice_service import get_voice_service
from src.services.nlu_service import get_nlu_service
from src.services.tts_service import get_tts_service
from src.services.action_executor_service import get_action_executor

logger = logging.getLogger(__name__)

# Singleton instance
_conversation_service_instance: Optional['ConversationService'] = None


class ConversationState:
    """Represents the state of an ongoing conversation"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_id = f"{user_id}_{datetime.now().timestamp()}"
        self.started_at = datetime.now()
        self.last_activity = datetime.now()
        self.turn_count = 0
        self.context: Dict = {}
        self.awaiting_clarification = False
        self.last_intent: Optional[str] = None
        self.last_entities: Dict = {}
        self.is_first_interaction = True  # Track first-time greeting
        self.pending_action: Optional[Dict] = None  # For multi-turn follow-ups
        
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        self.turn_count += 1
    
    def is_active(self, timeout_seconds: int = 300) -> bool:
        """Check if conversation is still active"""
        elapsed = (datetime.now() - self.last_activity).total_seconds()
        return elapsed < timeout_seconds


class ConversationService:
    """
    Complete Voice Conversation Service
    Orchestrates STT → NLU → TTS pipeline for natural interactions
    """
    
    def __init__(self):
        """Initialize conversation service"""
        self.voice_service = get_voice_service()
        self.nlu_service = get_nlu_service()
        self.tts_service = get_tts_service()
        self.action_executor = get_action_executor()
        
        # Track which users have interacted before (in-memory for now)
        self._greeted_users: set = set()
        
        # Active conversation sessions
        self.active_sessions: Dict[str, ConversationState] = {}
        
        # Voice settings for different interaction modes
        self.voice_profiles = {
            "default": {"voice": "alloy", "speed": 1.0},
            "friendly": {"voice": "nova", "speed": 1.0},
            "professional": {"voice": "onyx", "speed": 0.95},
            "energetic": {"voice": "shimmer", "speed": 1.1}
        }
        
        logger.info("✓ Conversation Service initialized")
    
    def get_or_create_session(self, user_id: str) -> ConversationState:
        """Get existing conversation session or create new one"""
        if user_id not in self.active_sessions:
            self.active_sessions[user_id] = ConversationState(user_id)
            logger.info(f"New conversation session started for user: {user_id}")
        
        session = self.active_sessions[user_id]
        session.update_activity()
        return session
    
    def cleanup_inactive_sessions(self, timeout_seconds: int = 300):
        """Remove inactive conversation sessions"""
        inactive_users = [
            user_id for user_id, session in self.active_sessions.items()
            if not session.is_active(timeout_seconds)
        ]
        
        for user_id in inactive_users:
            del self.active_sessions[user_id]
            logger.info(f"Cleaned up inactive session for user: {user_id}")
    
    async def process_voice_input(
        self,
        audio_data: bytes,
        user_id: str,
        voice_profile: str = "default",
        language: Optional[str] = None
    ) -> Dict:
        """
        Process voice input through complete STT → NLU → TTS pipeline
        
        Args:
            audio_data: Raw audio bytes
            user_id: User identifier
            voice_profile: Voice style (default, friendly, professional, energetic)
            language: Optional language code for STT
        
        Returns:
            {
                "session_id": "user123_1234567890",
                "turn": 1,
                "transcription": {
                    "text": "I want to log my workout",
                    "confidence": 0.95,
                    "language": "en"
                },
                "understanding": {
                    "intent": "log_exercise",
                    "domain": "exercise",
                    "confidence": 0.92,
                    "entities": {...}
                },
                "response": {
                    "text": "Great! What type of exercise did you do?",
                    "sentiment": {...}
                },
                "audio": {
                    "format": "mp3",
                    "size_bytes": 12345,
                    "duration_ms": 2500
                }
            }
        """
        session = self.get_or_create_session(user_id)
        
        try:
            # Step 1: Speech-to-Text
            logger.info(f"[{session.session_id}] Step 1: Transcribing audio...")
            transcription = await self.voice_service.transcribe_audio(
                audio_data=audio_data,
                language=language
            )
            
            if not transcription or not transcription.get("text"):
                return self._create_error_response(
                    session, "Could not understand the audio"
                )
            
            transcript_text = transcription["text"]
            logger.info(f"[{session.session_id}] Transcribed: {transcript_text}")
            
            # Step 2: Check for first-time greeting
            is_first_time = user_id not in self._greeted_users
            if is_first_time:
                self._greeted_users.add(user_id)
                session.is_first_interaction = True
                session.context["is_first_interaction"] = True
            else:
                session.is_first_interaction = False
                session.context["is_first_interaction"] = False
            
            # Step 3: Natural Language Understanding
            logger.info(f"[{session.session_id}] Step 2: Understanding intent...")
            
            # Enrich context with time of day for greeting style
            now = datetime.now()
            hour = now.hour
            if hour < 12:
                time_of_day = "morning"
            elif hour < 17:
                time_of_day = "afternoon"
            elif hour < 21:
                time_of_day = "evening"
            else:
                time_of_day = "night"
            session.context["current_time"] = now.isoformat()
            session.context["time_of_day"] = time_of_day
            
            understanding = await self.nlu_service.detect_intent(
                text=transcript_text,
                user_id=user_id,
                context=session.context
            )
            
            # Update session context
            session.last_intent = understanding.get("intent")
            session.last_entities = understanding.get("entities", {})
            session.context["last_transcript"] = transcript_text
            
            # Step 4: Execute Action (NEW — the Jarvis magic)
            logger.info(f"[{session.session_id}] Step 3: Executing action...")
            action_result = await self.action_executor.execute_action(
                intent=understanding.get("intent", "unknown"),
                domain=understanding.get("domain", "general"),
                entities=understanding.get("entities", {}),
                confidence=understanding.get("confidence", 0.0),
                user_id=user_id,
                user_message=transcript_text
            )
            
            # Step 5: Generate conversational response (with action context)
            logger.info(f"[{session.session_id}] Step 4: Generating response...")
            
            # Build response with action awareness
            if is_first_time and understanding.get("intent") in ["greeting", "chitchat", "help"]:
                # First-time greeting — warm welcome + app intro
                response_text = self._generate_first_time_greeting(time_of_day)
            elif action_result.get("action_executed"):
                # Action was performed — generate confirmation response
                intent_data_with_action = {**understanding}
                intent_data_with_action["action_result"] = action_result
                response_text = await self.nlu_service.generate_response(
                    user_message=f"{transcript_text}\n\n[ACTION COMPLETED: {action_result.get('confirmation_text', '')}]",
                    intent_data=intent_data_with_action,
                    user_id=user_id
                )
            elif action_result.get("action_type") == "needs_clarification":
                # Need more info — soft follow-up
                response_text = await self.nlu_service.generate_response(
                    user_message=f"{transcript_text}\n\n[NEED CLARIFICATION: {action_result.get('error', '')}]",
                    intent_data=understanding,
                    user_id=user_id
                )
            else:
                # Conversation only (greeting, chitchat, help)
                response_text = understanding.get("response_suggestion", "I understand.")
                if understanding.get("intent") != "unknown":
                    response_text = await self.nlu_service.generate_response(
                        user_message=transcript_text,
                        intent_data=understanding,
                        user_id=user_id
                    )
            
            # Step 6: Text-to-Speech (graceful — pipeline works without audio)
            logger.info(f"[{session.session_id}] Step 5: Synthesizing speech...")
            voice_settings = self.voice_profiles.get(voice_profile, self.voice_profiles["default"])
            
            audio_response = None
            try:
                audio_response = await self.tts_service.synthesize(
                    text=response_text,
                    voice=voice_settings["voice"],
                    speed=voice_settings["speed"]
                )
            except Exception as tts_err:
                logger.warning(f"[{session.session_id}] TTS failed (pipeline continues without audio): {tts_err}")
            
            # Analyze sentiment for better interaction
            sentiment = None
            try:
                sentiment = await self.nlu_service.analyze_sentiment(response_text)
            except Exception:
                sentiment = {"sentiment": "neutral", "emotion": "calm", "intensity": 0.5}
            
            logger.info(f"[{session.session_id}] ✓ Conversation turn {session.turn_count} complete")
            
            return {
                "session_id": session.session_id,
                "turn": session.turn_count,
                "transcription": {
                    "text": transcript_text,
                    "confidence": transcription.get("confidence", 0.0),
                    "language": transcription.get("language", "en")
                },
                "understanding": {
                    "intent": understanding.get("intent"),
                    "domain": understanding.get("domain"),
                    "confidence": understanding.get("confidence"),
                    "entities": understanding.get("entities", {})
                },
                "action_result": action_result,
                "response": {
                    "text": response_text,
                    "sentiment": sentiment
                },
                "audio": {
                    "format": "mp3",
                    "size_bytes": len(audio_response) if audio_response else 0,
                    "duration_ms": self._estimate_audio_duration(len(audio_response)) if audio_response else 0
                },
                "audio_data": audio_response  # Base64 encode this in the API route
            }
        
        except Exception as e:
            logger.error(f"[{session.session_id}] Conversation processing failed: {e}")
            return self._create_error_response(session, str(e))
    
    async def process_text_input(
        self,
        text: str,
        user_id: str,
        voice_profile: str = "default"
    ) -> Dict:
        """
        Process text input (bypass STT) through NLU → TTS pipeline
        
        Args:
            text: User's text input
            user_id: User identifier
            voice_profile: Voice style for response
        
        Returns:
            Same structure as process_voice_input but without transcription step
        """
        session = self.get_or_create_session(user_id)
        
        try:
            # Step 1: Check for first-time greeting
            is_first_time = user_id not in self._greeted_users
            if is_first_time:
                self._greeted_users.add(user_id)
                session.is_first_interaction = True
                session.context["is_first_interaction"] = True
            
            # Enrich context
            now = datetime.now()
            hour = now.hour
            time_of_day = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening" if hour < 21 else "night"
            session.context["current_time"] = now.isoformat()
            session.context["time_of_day"] = time_of_day
            
            # Step 2: Natural Language Understanding
            logger.info(f"[{session.session_id}] Understanding: {text}")
            understanding = await self.nlu_service.detect_intent(
                text=text,
                user_id=user_id,
                context=session.context
            )
            
            # Update session context
            session.last_intent = understanding.get("intent")
            session.last_entities = understanding.get("entities", {})
            session.context["last_input"] = text
            
            # Step 3: Execute Action
            action_result = await self.action_executor.execute_action(
                intent=understanding.get("intent", "unknown"),
                domain=understanding.get("domain", "general"),
                entities=understanding.get("entities", {}),
                confidence=understanding.get("confidence", 0.0),
                user_id=user_id,
                user_message=text
            )
            
            # Step 4: Generate response
            if is_first_time and understanding.get("intent") in ["greeting", "chitchat", "help"]:
                response_text = self._generate_first_time_greeting(time_of_day)
            elif action_result.get("action_executed"):
                intent_data_with_action = {**understanding}
                intent_data_with_action["action_result"] = action_result
                response_text = await self.nlu_service.generate_response(
                    user_message=f"{text}\n\n[ACTION COMPLETED: {action_result.get('confirmation_text', '')}]",
                    intent_data=intent_data_with_action,
                    user_id=user_id
                )
            elif action_result.get("action_type") == "needs_clarification":
                response_text = await self.nlu_service.generate_response(
                    user_message=f"{text}\n\n[NEED CLARIFICATION: {action_result.get('error', '')}]",
                    intent_data=understanding,
                    user_id=user_id
                )
            else:
                response_text = understanding.get("response_suggestion", "I understand.")
                if understanding.get("intent") != "unknown":
                    response_text = await self.nlu_service.generate_response(
                        user_message=text,
                        intent_data=understanding,
                        user_id=user_id
                    )
            
            # Step 5: Text-to-Speech (graceful — pipeline works without audio)
            voice_settings = self.voice_profiles.get(voice_profile, self.voice_profiles["default"])
            
            audio_response = None
            try:
                audio_response = await self.tts_service.synthesize(
                    text=response_text,
                    voice=voice_settings["voice"],
                    speed=voice_settings["speed"]
                )
            except Exception as tts_err:
                logger.warning(f"[{session.session_id}] TTS failed (pipeline continues without audio): {tts_err}")
            
            sentiment = None
            try:
                sentiment = await self.nlu_service.analyze_sentiment(response_text)
            except Exception:
                sentiment = {"sentiment": "neutral", "emotion": "calm", "intensity": 0.5}
            
            logger.info(f"[{session.session_id}] ✓ Text conversation turn {session.turn_count} complete")
            
            return {
                "session_id": session.session_id,
                "turn": session.turn_count,
                "input": {
                    "text": text,
                    "mode": "text"
                },
                "understanding": {
                    "intent": understanding.get("intent"),
                    "domain": understanding.get("domain"),
                    "confidence": understanding.get("confidence"),
                    "entities": understanding.get("entities", {})
                },
                "action_result": action_result,
                "response": {
                    "text": response_text,
                    "sentiment": sentiment
                },
                "audio": {
                    "format": "mp3",
                    "size_bytes": len(audio_response) if audio_response else 0,
                    "duration_ms": self._estimate_audio_duration(len(audio_response)) if audio_response else 0
                },
                "audio_data": audio_response
            }
        
        except Exception as e:
            logger.error(f"[{session.session_id}] Text conversation failed: {e}")
            return self._create_error_response(session, str(e))
    
    async def stream_conversation(
        self,
        audio_chunks: AsyncIterator[bytes],
        user_id: str,
        voice_profile: str = "default"
    ) -> AsyncIterator[Dict]:
        """
        Process streaming audio for real-time conversation
        
        Args:
            audio_chunks: Async iterator of audio chunks
            user_id: User identifier
            voice_profile: Voice style
        
        Yields:
            Status updates and response chunks
        """
        session = self.get_or_create_session(user_id)
        
        try:
            # Yield initial status
            yield {
                "type": "status",
                "message": "Listening...",
                "session_id": session.session_id
            }
            
            # Collect audio chunks (in real implementation, use streaming STT)
            audio_buffer = bytearray()
            async for chunk in audio_chunks:
                audio_buffer.extend(chunk)
                
                # Yield progress
                yield {
                    "type": "progress",
                    "bytes_received": len(audio_buffer)
                }
            
            # Process complete audio
            result = await self.process_voice_input(
                audio_data=bytes(audio_buffer),
                user_id=user_id,
                voice_profile=voice_profile
            )
            
            # Yield final result
            yield {
                "type": "complete",
                **result
            }
        
        except Exception as e:
            logger.error(f"[{session.session_id}] Streaming conversation failed: {e}")
            yield {
                "type": "error",
                "message": str(e),
                "session_id": session.session_id
            }
    
    def get_session_info(self, user_id: str) -> Optional[Dict]:
        """Get information about active conversation session"""
        if user_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[user_id]
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "started_at": session.started_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "turn_count": session.turn_count,
            "last_intent": session.last_intent,
            "is_active": session.is_active()
        }
    
    def end_session(self, user_id: str) -> bool:
        """End conversation session"""
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
            logger.info(f"Conversation session ended for user: {user_id}")
            return True
        return False
    
    def _generate_first_time_greeting(self, time_of_day: str) -> str:
        """Generate a warm first-time greeting like Jarvis."""
        greetings = {
            "morning": "Good morning! I'm your Speak Sync AI assistant — think of me like your personal Jarvis. I can help you manage tasks, track habits, log workouts, manage finances, and much more — all through voice. Just tell me what you need!",
            "afternoon": "Good afternoon! Welcome to Speak Sync! I'm your AI assistant — like having Jarvis in your pocket. You can ask me to create tasks, log your meals or workouts, track expenses, schedule events — anything you need. Let's make your day productive!",
            "evening": "Good evening! I'm your Speak Sync AI — your personal Jarvis. I'm here to help you manage your life through voice. Tasks, habits, workouts, expenses, sleep — just tell me what you need and I'll handle it!",
            "night": "Hey there! I'm your Speak Sync AI assistant. Think of me as your Jarvis. Whether it's adding tasks, logging today's activities, or checking your schedule — just say it and I'll take care of it. What can I do for you?"
        }
        return greetings.get(time_of_day, greetings["morning"])
    
    def _create_error_response(self, session: ConversationState, error_message: str) -> Dict:
        """Create standardized error response"""
        return {
            "session_id": session.session_id,
            "turn": session.turn_count,
            "error": True,
            "message": error_message,
            "response": {
                "text": "I'm having trouble processing that. Could you try again?",
                "sentiment": {"sentiment": "neutral", "emotion": "calm", "intensity": 0.5}
            }
        }
    
    def _estimate_audio_duration(self, audio_bytes: int) -> int:
        """Estimate audio duration in milliseconds from byte size"""
        # Rough estimate: ~128kbps MP3 = 16KB per second
        return int((audio_bytes / 16000) * 1000)


def get_conversation_service() -> ConversationService:
    """Get or create conversation service singleton"""
    global _conversation_service_instance
    
    if _conversation_service_instance is None:
        _conversation_service_instance = ConversationService()
    
    return _conversation_service_instance

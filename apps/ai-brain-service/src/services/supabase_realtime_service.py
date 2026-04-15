"""
Supabase Realtime Client
────────────────────────
Wraps Supabase's Realtime WebSocket to push live events to Flutter.

What this powers:
  - Habit completion → instant notification in Flutter UI
  - Task creation/update → live sync across devices
  - Proactive nudges from BehavioralObserver → push to Flutter
  - Conversation history → real-time sync

Uses: supabase-py (async client)
FREE: Supabase Realtime is included in free tier (200 concurrent connections)
"""

import logging
import os
import json
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Singleton
_realtime_instance: Optional['SupabaseRealtimeService'] = None


class SupabaseRealtimeService:
    """
    Supabase Realtime Service
    Pushes live events to Flutter via WebSocket subscriptions.

    Flutter subscribes to channels → backend inserts to Supabase tables
    → Supabase Realtime pushes changes to Flutter instantly.
    """

    def __init__(self, supabase_url: str, supabase_service_key: str):
        try:
            from supabase import create_client, Client
            from supabase.lib.client_options import ClientOptions

            self.supabase: Client = create_client(
                supabase_url,
                supabase_service_key,
                options=ClientOptions(
                    schema="public",
                    auto_refresh_token=True,
                    persist_session=False
                )
            )
            self.url = supabase_url
            self._available = True
            logger.info("✓ Supabase Realtime client initialized")

        except ImportError:
            logger.warning("⚠ supabase-py not installed — Realtime disabled. Run: pip install supabase")
            self._available = False
        except Exception as e:
            logger.warning(f"⚠ Supabase Realtime init failed: {e}")
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    # ─────────────────────────────────────────────────────────
    # Core broadcast methods — push events to Flutter
    # ─────────────────────────────────────────────────────────

    async def push_habit_update(self, user_id: str, habit_data: Dict) -> bool:
        """
        Push habit completion/update to Flutter in real-time.

        Flutter subscribes to:
          supabase.from('realtime_events').on('INSERT', ...)
        """
        return await self._broadcast_event(
            channel=f"user:{user_id}",
            event="habit_update",
            payload={
                "user_id": user_id,
                "type": "habit_update",
                "data": habit_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def push_task_update(self, user_id: str, task_data: Dict) -> bool:
        """Push task creation/update/completion to Flutter"""
        return await self._broadcast_event(
            channel=f"user:{user_id}",
            event="task_update",
            payload={
                "user_id": user_id,
                "type": "task_update",
                "data": task_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def push_proactive_nudge(self, user_id: str, message: str) -> bool:
        """
        Push AI-generated proactive nudge to Flutter.
        Called by BehavioralObserver when it detects a good moment to nudge.
        Flutter shows this as a non-intrusive banner/notification.
        """
        return await self._broadcast_event(
            channel=f"user:{user_id}",
            event="ai_nudge",
            payload={
                "user_id": user_id,
                "type": "ai_nudge",
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def push_conversation_update(
        self,
        user_id: str,
        session_id: str,
        transcript: str,
        response: str
    ) -> bool:
        """Push conversation turn to Flutter for real-time transcript display"""
        return await self._broadcast_event(
            channel=f"conversation:{user_id}",
            event="message",
            payload={
                "user_id": user_id,
                "session_id": session_id,
                "transcript": transcript,
                "response": response,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    # ─────────────────────────────────────────────────────────
    # Storage helpers — Supabase Storage (1GB free)
    # ─────────────────────────────────────────────────────────

    async def upload_tts_cache(self, cache_key: str, audio_bytes: bytes) -> Optional[str]:
        """
        Upload TTS audio to Supabase Storage (instead of local filesystem).
        Returns public URL for the cached audio.
        """
        if not self._available:
            return None

        try:
            bucket = "tts-cache"
            file_path = f"{cache_key}.mp3"

            self.supabase.storage.from_(bucket).upload(
                path=file_path,
                file=audio_bytes,
                file_options={"content-type": "audio/mpeg", "upsert": "true"}
            )

            # Get public URL
            result = self.supabase.storage.from_(bucket).get_public_url(file_path)
            logger.debug(f"TTS cached to Supabase Storage: {file_path}")
            return result

        except Exception as e:
            logger.warning(f"Supabase Storage upload failed: {e}")
            return None

    async def get_tts_cache(self, cache_key: str) -> Optional[bytes]:
        """Retrieve cached TTS audio from Supabase Storage"""
        if not self._available:
            return None

        try:
            file_path = f"{cache_key}.mp3"
            result = self.supabase.storage.from_("tts-cache").download(file_path)
            return result

        except Exception:
            return None

    # ─────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────

    async def _broadcast_event(self, channel: str, event: str, payload: Dict) -> bool:
        """Broadcast an event via Supabase Realtime channel"""
        if not self._available:
            return False

        try:
            # Insert into a realtime_events table which triggers Supabase Realtime
            # Flutter subscribes to changes on this table filtered by user_id
            self.supabase.table("realtime_events").insert({
                "channel": channel,
                "event": event,
                "payload": json.dumps(payload),
                "user_id": payload.get("user_id"),
                "created_at": datetime.utcnow().isoformat()
            }).execute()

            logger.debug(f"Realtime event broadcast: {event} → {channel}")
            return True

        except Exception as e:
            logger.warning(f"Realtime broadcast failed (non-critical): {e}")
            return False


def get_realtime_service() -> Optional[SupabaseRealtimeService]:
    """Get or create SupabaseRealtimeService singleton"""
    global _realtime_instance

    if _realtime_instance is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not url or not key:
            logger.warning("⚠ SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set — Realtime disabled")
            return None

        _realtime_instance = SupabaseRealtimeService(url, key)

    return _realtime_instance

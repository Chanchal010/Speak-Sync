"""
Behavioral Observer Service
──────────────────────────
Continuously learns from EVERY user action to build a humanly mental model.

LLM Used: google/gemini-2.0-flash-exp:free  (via OpenRouter — 100% FREE)
          Fast, capable, no cost for insight extraction per action.

Architecture:
  Every action → extract behavioral signal → store in pgvector as embedding
  On next conversation → retrieve relevant memories → LLM sees YOUR patterns
  Result: responses feel personal, not generic.
"""

import logging
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Singleton instance
_observer_instance: Optional['BehavioralObserver'] = None


class BehavioralObserver:
    """
    24/7 Humanly Behavioral Learning System

    Uses google/gemini-2.0-flash-exp:free (OpenRouter FREE) to extract
    behavioral patterns from every user action — building a continuously
    growing personal model of the user.

    The more they use the app, the smarter and more personalized it gets.
    Day 1: generic. Day 30: feels like it knows you. Day 180: feels like a friend.
    """

    def __init__(self, openrouter_api_key: str, vector_memory=None):
        # Uses FREE Gemini Flash model via OpenRouter
        self.client = AsyncOpenAI(
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = "google/gemini-2.0-flash-exp:free"  # 100% FREE, fast
        self.vector_memory = vector_memory  # Optional: store in pgvector

        # In-memory observation store (fallback if no vector DB)
        self._observations: Dict[str, List[Dict]] = {}

        logger.info("✓ BehavioralObserver initialized (FREE Gemini Flash via OpenRouter)")

    async def observe(self, user_id: str, event: Dict) -> Optional[str]:
        """
        Called after EVERY user action.
        Extracts 1 behavioral insight and stores it.

        Args:
            user_id: User identifier
            event: {
                'type': 'habit_logged' | 'task_created' | 'voice_conversation' | 'sleep_logged' etc,
                'data': { ...event specific data... },
                'timestamp': ISO string,
                'metadata': { 'time_of_day': 'morning', 'day_of_week': 'Monday' }
            }

        Returns:
            Extracted behavioral insight string (or None if extraction failed)
        """
        try:
            event_type = event.get('type', 'unknown')
            event_data = event.get('data', {})
            timestamp = event.get('timestamp', datetime.utcnow().isoformat())
            metadata = event.get('metadata', {})

            # Build context-rich prompt for insight extraction
            prompt = f"""Analyze this user action and extract ONE concise behavioral insight.

Action: {event_type}
Data: {json.dumps(event_data, indent=2)}
Time: {timestamp}
Context: {json.dumps(metadata)}

Extract a single behavioral pattern or insight about this user.
Focus on: timing patterns, frequency, mood signals, motivation cues, struggles.

Return a single sentence starting with "User" describing the pattern.
Example outputs:
- "User consistently logs workouts before 8am on weekdays"
- "User tends to skip water logging on stressful days (many tasks due)"  
- "User's mood is notably higher when they complete morning exercise"
- "User prefers short tasks (< 30min) on Monday mornings"

Return ONLY the insight sentence, nothing else."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=60  # Short insight only
            )

            insight = response.choices[0].message.content.strip()

            # Store the observation
            await self._store_observation(user_id, insight, event_type, timestamp)

            logger.debug(f"[{user_id}] Behavioral insight: {insight}")
            return insight

        except Exception as e:
            logger.warning(f"Behavioral observation failed (non-critical): {e}")
            return None  # Never block the main flow

    async def get_user_profile(self, user_id: str, query: str = None) -> str:
        """
        Build a dynamic user profile from all stored observations.
        Called before LLM responses to give context about the user.

        Args:
            user_id: User identifier
            query: Optional — if provided, retrieve observations relevant to this query

        Returns:
            Natural language user profile summary
        """
        try:
            observations = await self._retrieve_observations(user_id, query, limit=15)

            if not observations:
                return ""  # New user — no profile yet

            obs_text = "\n".join([f"- {obs}" for obs in observations])

            profile_prompt = f"""Based on these behavioral observations about a user, write a brief 3-4 sentence profile.
Focus on their habits, preferences, patterns, and what motivates them.

Observations:
{obs_text}

Write a concise, warm, humanly profile. Start with "This user..."
Do NOT include any harmful assumptions. Focus only on positive behavioral patterns."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": profile_prompt}],
                temperature=0.4,
                max_tokens=150
            )

            profile = response.choices[0].message.content.strip()
            logger.debug(f"[{user_id}] Profile generated: {profile[:80]}...")
            return profile

        except Exception as e:
            logger.warning(f"Profile generation failed (non-critical): {e}")
            return ""

    async def get_proactive_nudge(self, user_id: str, current_time: datetime) -> Optional[str]:
        """
        Generate a proactive nudge based on behavioral patterns.
        Called by the background scheduler every 15-30 minutes.

        Returns None if no nudge is appropriate right now.
        """
        try:
            observations = await self._retrieve_observations(user_id, limit=20)
            if not observations:
                return None

            hour = current_time.hour
            day_name = current_time.strftime('%A')
            obs_text = "\n".join([f"- {obs}" for obs in observations[:10]])

            nudge_prompt = f"""Based on behavioral patterns, decide if this user needs a nudge RIGHT NOW.

Current time: {hour}:00 on {day_name}
User patterns:
{obs_text}

Should we send a nudge? Consider:
- Is this their usual time for a habit they might forget?
- Has there been a concerning pattern (skipping, stress)?
- Would they appreciate a check-in right now?

If YES → respond with ONLY the nudge message (1-2 sentences, warm and natural)
If NO  → respond with exactly: NO_NUDGE

Be conservative — only nudge when genuinely useful. People hate spam."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": nudge_prompt}],
                temperature=0.5,
                max_tokens=80
            )

            result = response.choices[0].message.content.strip()

            if result == "NO_NUDGE" or "NO_NUDGE" in result:
                return None

            return result

        except Exception as e:
            logger.warning(f"Proactive nudge generation failed: {e}")
            return None

    async def enrich_conversation_context(self, user_id: str, current_message: str) -> str:
        """
        Called BEFORE every LLM response to inject behavioral context.
        Makes the AI feel like it truly knows the user.

        Returns a context string to prepend to the LLM system prompt.
        """
        try:
            # Get relevant observations for this specific message
            observations = await self._retrieve_observations(
                user_id, query=current_message, limit=5
            )

            if not observations:
                return ""

            context_lines = "\n".join([f"  • {obs}" for obs in observations])
            return f"\nWhat you know about this specific user:\n{context_lines}\n"

        except Exception:
            return ""  # Never block conversation

    # ──────────────── Private Methods ────────────────

    async def _store_observation(
        self, user_id: str, insight: str, event_type: str, timestamp: str
    ):
        """Store behavioral observation in memory"""

        observation = {
            "insight": insight,
            "event_type": event_type,
            "timestamp": timestamp,
            "stored_at": datetime.utcnow().isoformat()
        }

        # Try vector memory first (persistent, semantic search)
        if self.vector_memory:
            try:
                await self.vector_memory.store_user_context(
                    user_id=user_id,
                    context_type="behavioral_pattern",
                    context_key=f"{event_type}_{datetime.utcnow().timestamp()}",
                    context_value=insight,
                    importance=0.6
                )
                return
            except Exception as e:
                logger.debug(f"Vector store failed, using in-memory: {e}")

        # Fallback: in-memory (lost on restart)
        if user_id not in self._observations:
            self._observations[user_id] = []

        self._observations[user_id].append(observation)

        # Keep only last 200 observations per user in memory
        if len(self._observations[user_id]) > 200:
            self._observations[user_id] = self._observations[user_id][-200:]

    async def _retrieve_observations(
        self, user_id: str, query: str = None, limit: int = 15
    ) -> List[str]:
        """Retrieve observations from memory"""

        # Try vector memory (semantic search)
        if self.vector_memory and query:
            try:
                result = await self.vector_memory.retrieve_relevant_context(
                    user_id=user_id,
                    query=query,
                    context_type="behavioral_pattern",
                    limit=limit
                )
                return [ctx['value'] for ctx in result.get('contexts', [])]
            except Exception:
                pass

        # Fallback: in-memory
        observations = self._observations.get(user_id, [])
        recent = sorted(observations, key=lambda x: x['stored_at'], reverse=True)[:limit]
        return [obs['insight'] for obs in recent]


def get_behavioral_observer() -> BehavioralObserver:
    """Get or create BehavioralObserver singleton"""
    global _observer_instance

    if _observer_instance is None:
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("⚠ No API key for BehavioralObserver — behavioral learning disabled")
            return None

        _observer_instance = BehavioralObserver(openrouter_api_key=api_key)

    return _observer_instance

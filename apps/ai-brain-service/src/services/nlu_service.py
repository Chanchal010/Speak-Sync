"""
NLU Service - Natural Language Understanding with LLM
Handles intent detection, entity extraction, and context understanding
Supports: Groq, OpenRouter, OpenAI
"""
from openai import AsyncOpenAI
from typing import Optional, Dict, List, Literal
import logging
import os
import json
import re

logger = logging.getLogger(__name__)

# Singleton instance
_nlu_service_instance: Optional['NLUService'] = None

# Intent categories for LifeOS domains
INTENT_CATEGORIES = {
    "scheduling": ["create_task", "update_task", "delete_task", "query_schedule", "find_free_time"],
    "calendar": ["create_event", "update_event", "delete_event", "query_events"],
    "exercise": ["log_exercise", "query_workout", "set_fitness_goal", "track_progress"],
    "finance": ["log_expense", "log_income", "query_budget", "financial_advice"],
    "sleep": ["log_sleep", "query_sleep_pattern", "sleep_advice"],
    "food": ["log_food", "query_meals"],
    "study": ["log_study", "query_study_sessions"],
    "productivity": ["start_timer", "track_habit", "query_habits", "productivity_stats"],
    "hydration": ["log_water", "set_water_goal", "hydration_reminder"],
    "general": ["greeting", "goodbye", "help", "thanks", "chitchat"]
}


class NLUService:
    """
    Natural Language Understanding Service using LLM (Groq/OpenRouter/OpenAI)
    """
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, model: str = "meta-llama/llama-3.3-70b-instruct"):
        """
        Initialize NLU service with LLM provider
        
        Args:
            api_key: API key (Groq, OpenRouter, or OpenAI)
            base_url: Base URL for API (OpenRouter: https://openrouter.ai/api/v1, Groq: https://api.groq.com/openai/v1)
            model: Model to use (OpenRouter: meta-llama/llama-3.3-70b-instruct, Groq: llama-3.3-70b-versatile)
        """
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url) if base_url else AsyncOpenAI(api_key=api_key)
        self.model = model
        self.conversation_history = {}  # user_id -> messages
        
        provider = "OpenRouter" if base_url and "openrouter" in base_url else "Groq" if base_url and "groq" in base_url else "OpenAI"
        logger.info(f"✓ NLU Service initialized with {provider} - model: {model}")
    
    async def detect_intent(
        self,
        text: str,
        user_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Detect user intent from text
        
        Args:
            text: User's input text
            user_id: User identifier for context
            context: Additional context (current time, user preferences, etc.)
        
        Returns:
            {
                "intent": "create_task",
                "domain": "scheduling",
                "confidence": 0.95,
                "entities": {...},
                "response_suggestion": "..."
            }
        """
        try:
            # Build intent detection prompt
            prompt = self._build_intent_prompt(text, context)
            
            # Call Groq LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are JARVIS — the AI intent detection engine for Speak-Sync, a personal life management app.
Your job: analyze what the user wants and return structured JSON.

Return JSON with these fields:
- intent: specific action (see list below)
- domain: category domain
- confidence: 0.0 to 1.0 score
- entities: all extracted data (dates as ISO, times as HH:MM, amounts as numbers, durations in minutes)
- response_suggestion: a SHORT, natural, conversational acknowledgement (1-2 sentences max)

Available intents by domain:
- scheduling: create_task, update_task, delete_task, query_schedule, find_free_time
- calendar: create_event, update_event, delete_event, query_events
- exercise: log_exercise, query_workout, set_fitness_goal, track_progress
- finance: log_expense, log_income, query_budget, financial_advice
- food: log_food, query_meals
- study: log_study, query_study_sessions
- sleep: log_sleep, query_sleep_pattern, sleep_advice
- productivity: start_timer, track_habit, query_habits, productivity_stats
- hydration: log_water, set_water_goal, hydration_reminder
- general: greeting, goodbye, help, thanks, chitchat

IMPORTANT RULES:
1. NEVER interrogate the user. If data is missing, infer smart defaults.
2. Extract "tomorrow", "today", "next week" etc. as relative date strings.
3. Infer mood from emotional language (e.g., "killed me" → intensity high, "great" → positive).
4. Infer categories from context (e.g., "bought a jacket" → clothing, "had chai" → food/beverage).
5. When amounts mention rupees/bucks/rs, extract as numeric INR amounts.
6. For durations, extract "an hour" as 60, "half hour" as 30, etc.
7. If user is just chatting/venting, set intent to "chitchat" — DO NOT force a task.
8. Match the user's energy in response_suggestion — casual if they're casual, enthusiastic if they're excited."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower for consistent intent detection
                max_tokens=500
            )
            
            # Parse response - extract JSON from response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON if it's wrapped in markdown or text
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Remove any leading/trailing text that isn't JSON
            # Find the first { and last }
            json_start = content.find('{')
            json_end = content.rfind('}')
            if json_start != -1 and json_end != -1:
                content = content[json_start:json_end + 1]
            
            # Fix common LLM JSON issues: trailing commas before }
            import re
            content = re.sub(r',\s*}', '}', content)
            content = re.sub(r',\s*]', ']', content)
            
            # Parse JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError as parse_err:
                logger.warning(f"JSON parse failed, trying cleanup: {parse_err}")
                logger.warning(f"Raw LLM content: {response.choices[0].message.content[:500]}")
                
                # Last resort: try to extract key fields via regex
                intent_match = re.search(r'"intent"\s*:\s*"([^"]+)"', content)
                domain_match = re.search(r'"domain"\s*:\s*"([^"]+)"', content)
                conf_match = re.search(r'"confidence"\s*:\s*([\d.]+)', content)
                resp_match = re.search(r'"response_suggestion"\s*:\s*"([^"]*)"', content)
                
                if intent_match:
                    result = {
                        "intent": intent_match.group(1),
                        "domain": domain_match.group(1) if domain_match else "general",
                        "confidence": float(conf_match.group(1)) if conf_match else 0.7,
                        "entities": {},
                        "response_suggestion": resp_match.group(1) if resp_match else "Got it!"
                    }
                    logger.info(f"Recovered intent via regex: {result['intent']}")
                else:
                    raise parse_err
            
            logger.info(f"Intent detected: {result.get('intent')} (domain: {result.get('domain')}, confidence: {result.get('confidence')})")
            
            return result
        
        except Exception as e:
            logger.error(f"Intent detection failed: {e}")
            return {
                "intent": "unknown",
                "domain": "general",
                "confidence": 0.0,
                "entities": {},
                "response_suggestion": "I'm not sure I understood that. Could you rephrase?"
            }
    
    async def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> Dict:
        """
        Extract entities from text
        
        Args:
            text: Input text
            entity_types: Specific entities to extract (dates, times, amounts, etc.)
        
        Returns:
            {
                "dates": ["2025-12-05"],
                "times": ["14:30"],
                "amounts": [50.0],
                "persons": ["John"],
                ...
            }
        """
        try:
            entity_types_str = ", ".join(entity_types) if entity_types else "all relevant entities"
            
            prompt = f"""Extract {entity_types_str} from this text: "{text}"

Return JSON with extracted entities. Include:
- dates (ISO format)
- times (24h format)
- amounts (numeric)
- durations (in minutes)
- categories (activity types)
- persons (names)
- locations

Example: {{"dates": ["2025-12-05"], "times": ["14:30"], "amounts": [50.0]}}"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an entity extraction AI. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            entities = json.loads(response.choices[0].message.content)
            return entities
        
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {}
    
    async def generate_response(
        self,
        user_message: str,
        intent_data: Dict,
        user_id: Optional[str] = None,
        include_history: bool = True
    ) -> str:
        """
        Generate conversational response based on intent
        
        Args:
            user_message: User's original message
            intent_data: Intent detection result
            user_id: User identifier
            include_history: Whether to include conversation history
        
        Returns:
            Natural language response
        """
        try:
            # Get conversation history
            history = []
            if include_history and user_id:
                history = self.conversation_history.get(user_id, [])[-6:]  # Last 3 exchanges
            
            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": """You are JARVIS — the AI voice assistant for Speak-Sync, like Iron Man's JARVIS.
You're talking to the user through voice. Be their intelligent life companion.

PERSONALITY RULES:
1. Be CONVERSATIONAL — talk like a helpful friend, NOT a data-entry form
2. NEVER ask multiple questions at once. One soft follow-up at most.
3. Show genuine care — "Nice!", "That's awesome!", "Hope it was good!"
4. Keep responses SHORT — 1-2 sentences max (this gets spoken aloud)
5. Match the user's energy — casual if casual, enthusiastic if excited
6. If an action was performed, confirm it naturally ("Done!", "Got it!", "Logged!")
7. Infer what you can — don't ask for data the user didn't offer
8. Use the user's language style — mix Hindi/English if they do (hinglish)

You help with:
- Tasks & to-do management
- Calendar events & scheduling
- Exercise & fitness tracking
- Financial tracking (expenses/income)
- Sleep tracking
- Food & meal logging
- Water intake
- Study sessions
- Habit tracking
- Daily reports & insights"""
                }
            ]
            
            # Add history
            messages.extend(history)
            
            # Add current message with intent context
            user_content = f"""User said: "{user_message}"

Detected intent: {intent_data.get('intent')}
Domain: {intent_data.get('domain')}
Entities: {json.dumps(intent_data.get('entities', {}))}

Generate a natural, conversational response."""
            
            messages.append({"role": "user", "content": user_content})
            
            # Generate response
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # More creative for natural responses
                max_tokens=150
            )
            
            ai_response = response.choices[0].message.content
            
            # Update conversation history
            if user_id:
                if user_id not in self.conversation_history:
                    self.conversation_history[user_id] = []
                
                self.conversation_history[user_id].extend([
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": ai_response}
                ])
                
                # Keep only last 10 exchanges (20 messages)
                self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
            
            return ai_response
        
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return "I'm having trouble processing that right now. Could you try again?"
    
    async def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment and emotion from text
        
        Returns:
            {
                "sentiment": "positive",  # positive, negative, neutral
                "emotion": "happy",       # happy, sad, angry, excited, calm, stressed
                "intensity": 0.8
            }
        """
        try:
            prompt = f"""Analyze the sentiment and emotion in this text: "{text}"

Return JSON with:
- sentiment: positive/negative/neutral
- emotion: happy/sad/angry/excited/calm/stressed/anxious/confident
- intensity: 0-1 score

Example: {{"sentiment": "positive", "emotion": "excited", "intensity": 0.8}}"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis AI. Return only JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=100,
                response_format={"type": "json_object"}
            )
            
            sentiment = json.loads(response.choices[0].message.content)
            return sentiment
        
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"sentiment": "neutral", "emotion": "calm", "intensity": 0.5}
    
    async def summarize_conversation(
        self,
        user_id: str,
        max_length: int = 100
    ) -> str:
        """
        Summarize conversation history for a user
        
        Args:
            user_id: User identifier
            max_length: Max words in summary
        
        Returns:
            Summary text
        """
        try:
            history = self.conversation_history.get(user_id, [])
            if not history:
                return "No conversation history"
            
            # Format history
            history_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in history
            ])
            
            prompt = f"""Summarize this conversation in {max_length} words or less:

{history_text}

Focus on: main topics discussed, user's goals, action items."""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a conversation summarization AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            summary = response.choices[0].message.content
            return summary
        
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "Unable to summarize conversation"
    
    def clear_history(self, user_id: str):
        """Clear conversation history for a user"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
            logger.info(f"Cleared history for user: {user_id}")
    
    def _build_intent_prompt(self, text: str, context: Optional[Dict]) -> str:
        """Build intent detection prompt with context"""
        prompt = f'User input: "{text}"\n\n'
        
        if context:
            prompt += "Context:\n"
            if context.get("current_time"):
                prompt += f"- Current time: {context['current_time']}\n"
            if context.get("user_name"):
                prompt += f"- User: {context['user_name']}\n"
            if context.get("recent_activities"):
                prompt += f"- Recent activities: {', '.join(context['recent_activities'])}\n"
            prompt += "\n"
        
        prompt += "Analyze and return JSON with intent, domain, confidence, entities, and response_suggestion."
        
        return prompt


def get_nlu_service() -> NLUService:
    """Get or create NLU service singleton"""
    global _nlu_service_instance
    
    if _nlu_service_instance is None:
        # Use OpenRouter with OpenAI SDK
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY or OPENROUTER_API_KEY not found in environment")
        
        # OpenRouter configuration
        base_url = "https://openrouter.ai/api/v1"
        model = "meta-llama/llama-3.3-70b-instruct"
        
        _nlu_service_instance = NLUService(api_key=api_key, base_url=base_url, model=model)
    
    return _nlu_service_instance

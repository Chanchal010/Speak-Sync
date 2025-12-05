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
    "exercise": ["log_exercise", "query_workout", "set_fitness_goal", "track_progress"],
    "finance": ["log_expense", "log_income", "query_budget", "financial_advice"],
    "sleep": ["log_sleep", "query_sleep_pattern", "sleep_advice"],
    "productivity": ["start_timer", "track_habit", "productivity_stats"],
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
                        "content": """You are an intent detection AI for a life management system (LifeOS).
Analyze user input and return a JSON response with:
- intent: specific action (e.g., create_task, log_exercise)
- domain: category (scheduling, exercise, finance, sleep, productivity, hydration, general)
- confidence: 0-1 score
- entities: extracted data (dates, amounts, names, etc.)
- response_suggestion: brief conversational response

Available intents by domain:
- scheduling: create_task, update_task, delete_task, query_schedule, find_free_time
- exercise: log_exercise, query_workout, set_fitness_goal, track_progress
- finance: log_expense, log_income, query_budget, financial_advice
- sleep: log_sleep, query_sleep_pattern, sleep_advice
- productivity: start_timer, track_habit, productivity_stats
- hydration: log_water, set_water_goal, hydration_reminder
- general: greeting, goodbye, help, thanks, chitchat

Be conversational, not interrogational. Respond naturally."""
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
            content = response.choices[0].message.content
            
            # Try to extract JSON if it's wrapped in markdown or text
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            result = json.loads(content)
            
            logger.info(f"Intent detected: {result.get('intent')} (domain: {result.get('domain')})")
            
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
                    "content": """You are a friendly AI assistant for LifeOS (Life Operating System).
Be conversational, empathetic, and helpful. Follow these principles:
1. Be conversational, not interrogational
2. Show understanding and empathy
3. Ask clarifying questions naturally when needed
4. Provide actionable suggestions
5. Keep responses concise (2-3 sentences)
6. Match the user's energy and tone

Domains you help with:
- Task scheduling and time management
- Exercise and fitness tracking
- Financial management
- Sleep quality monitoring
- Productivity and habit tracking
- Hydration reminders"""
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

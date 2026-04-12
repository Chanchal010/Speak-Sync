"""
Action Executor Service - Maps NLU intents to real backend API actions
Like Iron Man's JARVIS: understands natural language → executes actions

Strategy:
- Fill missing data with smart defaults (no interrogation)
- Infer mood, categories, amounts from context
- Only ask follow-up when absolutely critical info is missing
"""
import logging
import os
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

# Singleton
_action_executor_instance: Optional['ActionExecutorService'] = None

# Default values for missing data (low-friction strategy)
SMART_DEFAULTS = {
    "mood": "neutral",
    "priority": "medium",
    "currency": "INR",
    "water_amount_ml": 250,  # ~1 glass
    "exercise_duration_min": 30,
    "sleep_quality": "average",
    "necessity_score": 3,  # 1-5 scale, 3 = moderate
    "category": "general",
}


class ActionExecutorService:
    """
    Maps detected intents to real API actions on Scheduler & Lifestyle services.
    
    Flow:
    1. Receive NLU result (intent, domain, entities, confidence)
    2. Determine which service + endpoint to call
    3. Fill missing data with smart defaults
    4. Execute the API call
    5. Return action result + conversational response context
    """
    
    def __init__(self):
        # Service URLs (internal communication)
        self.scheduler_url = os.getenv("SCHEDULER_SERVICE_URL", "http://localhost:3001")
        self.lifestyle_url = os.getenv("LIFESTYLE_SERVICE_URL", "http://localhost:8001")
        self.gateway_url = os.getenv("GATEWAY_SERVICE_URL", "http://localhost:3000")
        
        # Internal API key for service-to-service auth
        self.internal_api_key = os.getenv("INTERNAL_API_KEY", "")
        
        # Confidence threshold — below this, ask for clarification
        self.min_confidence = 0.6
        
        # Intent-to-action mapping
        self.action_map = self._build_action_map()
        
        logger.info("✓ Action Executor Service initialized")
    
    def _build_action_map(self) -> Dict:
        """Build the complete intent → action mapping."""
        return {
            # ──── Scheduling Domain ────
            "create_task": {
                "service": "scheduler",
                "method": "POST",
                "endpoint": "/api/tasks",
                "required_fields": ["title"],
                "entity_mapping": {
                    "title": ["task_name", "title", "task", "name"],
                    "description": ["description", "details", "notes"],
                    "priority": ["priority", "urgency"],
                    "dueDate": ["dates", "due_date", "deadline"],
                    "dueTime": ["times", "due_time"],
                    "categoryId": ["category_id", "category"],
                },
                "defaults": {
                    "priority": "medium",
                    "status": "pending",
                },
            },
            "update_task": {
                "service": "scheduler",
                "method": "PUT",
                "endpoint": "/api/tasks/{id}",
                "required_fields": ["id"],
                "entity_mapping": {
                    "title": ["task_name", "title", "name"],
                    "priority": ["priority"],
                    "status": ["status"],
                    "dueDate": ["dates", "due_date"],
                },
            },
            "delete_task": {
                "service": "scheduler",
                "method": "DELETE",
                "endpoint": "/api/tasks/{id}",
                "required_fields": ["id"],
                "entity_mapping": {
                    "id": ["task_id", "id"],
                },
            },
            "query_schedule": {
                "service": "scheduler",
                "method": "GET",
                "endpoint": "/api/tasks",
                "required_fields": [],
                "entity_mapping": {
                    "status": ["status"],
                    "priority": ["priority"],
                    "date": ["dates"],
                },
            },
            "find_free_time": {
                "service": "scheduler",
                "method": "GET",
                "endpoint": "/api/tasks",
                "required_fields": [],
                "entity_mapping": {
                    "date": ["dates"],
                },
            },
            
            # ──── Calendar/Event Domain ────
            "create_event": {
                "service": "scheduler",
                "method": "POST",
                "endpoint": "/api/events",
                "required_fields": ["title"],
                "entity_mapping": {
                    "title": ["event_name", "title", "name"],
                    "description": ["description", "details"],
                    "startDate": ["dates", "start_date"],
                    "startTime": ["times", "start_time"],
                    "endTime": ["end_time"],
                    "location": ["locations", "location"],
                },
                "defaults": {
                    "allDay": False,
                },
            },
            "update_event": {
                "service": "scheduler",
                "method": "PUT",
                "endpoint": "/api/events/{id}",
                "required_fields": ["id"],
                "entity_mapping": {
                    "title": ["event_name", "title"],
                    "startDate": ["dates"],
                    "startTime": ["times"],
                },
            },
            "delete_event": {
                "service": "scheduler",
                "method": "DELETE",
                "endpoint": "/api/events/{id}",
                "required_fields": ["id"],
                "entity_mapping": {
                    "id": ["event_id", "id"],
                },
            },
            
            # ──── Exercise Domain ────
            "log_exercise": {
                "service": "lifestyle",
                "method": "POST",
                "endpoint": "/api/exercise",
                "required_fields": [],
                "entity_mapping": {
                    "exercise_type": ["activity", "exercise", "categories", "exercise_type"],
                    "duration_minutes": ["durations", "duration", "duration_minutes"],
                    "calories_burned": ["calories", "calories_burned"],
                    "intensity": ["intensity", "rpe"],
                    "notes": ["notes", "description"],
                },
                "defaults": {
                    "exercise_type": "general workout",
                    "duration_minutes": 30,
                    "intensity": "moderate",
                },
            },
            "query_workout": {
                "service": "lifestyle",
                "method": "GET",
                "endpoint": "/api/exercise",
                "required_fields": [],
                "entity_mapping": {
                    "start_date": ["dates"],
                },
            },
            
            # ──── Finance Domain ────
            "log_expense": {
                "service": "lifestyle",
                "method": "POST",
                "endpoint": "/api/finance",
                "required_fields": [],
                "entity_mapping": {
                    "amount": ["amounts", "amount"],
                    "category": ["categories", "category"],
                    "description": ["description", "notes", "item"],
                    "transaction_type": ["transaction_type"],
                    "currency": ["currency"],
                    "mood": ["mood", "emotion"],
                },
                "defaults": {
                    "transaction_type": "expense",
                    "currency": "INR",
                    "category": "general",
                    "mood": "neutral",
                },
            },
            "log_income": {
                "service": "lifestyle",
                "method": "POST",
                "endpoint": "/api/finance",
                "required_fields": [],
                "entity_mapping": {
                    "amount": ["amounts", "amount"],
                    "category": ["categories", "category"],
                    "description": ["description", "notes"],
                },
                "defaults": {
                    "transaction_type": "income",
                    "currency": "INR",
                    "category": "salary",
                },
            },
            
            # ──── Sleep Domain ────
            "log_sleep": {
                "service": "lifestyle",
                "method": "POST",
                "endpoint": "/api/sleep",
                "required_fields": [],
                "entity_mapping": {
                    "sleep_time": ["sleep_time", "bed_time"],
                    "wake_time": ["wake_time", "woke_up"],
                    "quality": ["quality", "sleep_quality"],
                    "duration_hours": ["durations", "duration", "hours"],
                    "notes": ["notes", "description"],
                },
                "defaults": {
                    "quality": "average",
                },
            },
            
            # ──── Hydration Domain ────
            "log_water": {
                "service": "lifestyle",
                "method": "POST",
                "endpoint": "/api/water",
                "required_fields": [],
                "entity_mapping": {
                    "amount_ml": ["amounts", "amount", "amount_ml"],
                    "container_type": ["container", "vessel"],
                },
                "defaults": {
                    "amount_ml": 250,  # 1 glass
                },
            },
            
            # ──── Food Domain ────
            "log_food": {
                "service": "lifestyle",
                "method": "POST",
                "endpoint": "/api/food",
                "required_fields": [],
                "entity_mapping": {
                    "food_items": ["food", "items", "meal"],
                    "meal_type": ["meal_type"],
                    "calories": ["calories"],
                    "notes": ["notes", "description"],
                },
                "defaults": {
                    "meal_type": "snack",
                },
            },
            
            # ──── Study Domain ────
            "log_study": {
                "service": "lifestyle",
                "method": "POST",
                "endpoint": "/api/study",
                "required_fields": [],
                "entity_mapping": {
                    "subject": ["subject", "topic", "categories"],
                    "duration_minutes": ["durations", "duration", "duration_minutes"],
                    "notes": ["notes", "description"],
                },
                "defaults": {
                    "duration_minutes": 30,
                    "subject": "general",
                },
            },
            
            # ──── Habit Domain ────
            "track_habit": {
                "service": "lifestyle",
                "method": "POST",
                "endpoint": "/api/habits/{id}/log",
                "required_fields": [],
                "entity_mapping": {
                    "habit_name": ["habit_name", "habit", "name"],
                    "value": ["value", "amount", "duration"],
                    "notes": ["notes"],
                },
            },
            "query_habits": {
                "service": "lifestyle",
                "method": "GET",
                "endpoint": "/api/habits",
                "required_fields": [],
                "entity_mapping": {},
            },
            
            # ──── Productivity Domain ────
            "start_timer": {
                "service": "none",
                "action_type": "client_side",
                "description": "Timer should be started on the client side",
            },
            "productivity_stats": {
                "service": "scheduler",
                "method": "GET",
                "endpoint": "/api/tasks/stats",
                "required_fields": [],
                "entity_mapping": {},
            },
            
            # ──── General Domain ────
            "greeting": {
                "service": "none",
                "action_type": "conversation_only",
            },
            "goodbye": {
                "service": "none",
                "action_type": "conversation_only",
            },
            "help": {
                "service": "none",
                "action_type": "conversation_only",
            },
            "thanks": {
                "service": "none",
                "action_type": "conversation_only",
            },
            "chitchat": {
                "service": "none",
                "action_type": "conversation_only",
            },
        }
    
    async def execute_action(
        self,
        intent: str,
        domain: str,
        entities: Dict,
        confidence: float,
        user_id: str,
        user_message: str = ""
    ) -> Dict[str, Any]:
        """
        Execute the action mapped to the detected intent.
        
        Args:
            intent: Detected intent (e.g., "create_task")
            domain: Intent domain (e.g., "scheduling")
            entities: Extracted entities from NLU
            confidence: Intent confidence score
            user_id: User identifier
            user_message: Original user message (for context)
        
        Returns:
            {
                "action_executed": True/False,
                "action_type": "api_call" | "conversation_only" | "needs_clarification",
                "service": "scheduler" | "lifestyle" | "none",
                "endpoint": "/api/tasks",
                "method": "POST",
                "payload": {...},
                "result": {...},  # API response
                "confirmation_text": "Task 'Buy groceries' created for tomorrow!",
                "error": None
            }
        """
        try:
            # Check confidence threshold
            if confidence < self.min_confidence:
                return {
                    "action_executed": False,
                    "action_type": "needs_clarification",
                    "confirmation_text": None,
                    "error": f"Low confidence ({confidence:.2f}). Need clarification."
                }
            
            # Look up the action mapping
            action_config = self.action_map.get(intent)
            
            if not action_config:
                logger.warning(f"No action mapping for intent: {intent}")
                return {
                    "action_executed": False,
                    "action_type": "unknown_intent",
                    "confirmation_text": None,
                    "error": f"No action mapping for intent: {intent}"
                }
            
            # Handle conversation-only intents (greeting, help, etc.)
            if action_config.get("action_type") == "conversation_only":
                return {
                    "action_executed": False,
                    "action_type": "conversation_only",
                    "service": "none",
                    "confirmation_text": None,
                    "error": None
                }
            
            # Handle client-side actions (timers, etc.)
            if action_config.get("action_type") == "client_side":
                return {
                    "action_executed": False,
                    "action_type": "client_side",
                    "service": "none",
                    "intent": intent,
                    "entities": entities,
                    "confirmation_text": action_config.get("description"),
                    "error": None
                }
            
            # Build the API payload from entities
            payload = self._build_payload(action_config, entities, user_id, user_message)
            
            # Check required fields
            missing = self._check_required_fields(action_config, payload)
            if missing:
                return {
                    "action_executed": False,
                    "action_type": "needs_clarification",
                    "missing_fields": missing,
                    "confirmation_text": None,
                    "error": f"Missing required info: {', '.join(missing)}"
                }
            
            # Resolve the endpoint (replace {id} placeholders)
            endpoint = self._resolve_endpoint(action_config["endpoint"], payload, entities)
            
            # Execute the API call
            service = action_config["service"]
            method = action_config["method"]
            
            result = await self._call_service(
                service=service,
                method=method,
                endpoint=endpoint,
                payload=payload if method in ["POST", "PUT", "PATCH"] else None,
                params=payload if method == "GET" else None,
                user_id=user_id
            )
            
            # Build confirmation text
            confirmation = self._build_confirmation(intent, payload, result)
            
            logger.info(f"✓ Action executed: {intent} → {service} {method} {endpoint}")
            
            return {
                "action_executed": True,
                "action_type": "api_call",
                "service": service,
                "endpoint": endpoint,
                "method": method,
                "payload": payload,
                "result": result,
                "confirmation_text": confirmation,
                "error": None
            }
        
        except Exception as e:
            logger.error(f"Action execution failed for intent '{intent}': {e}")
            return {
                "action_executed": False,
                "action_type": "error",
                "confirmation_text": None,
                "error": str(e)
            }
    
    def _build_payload(
        self,
        action_config: Dict,
        entities: Dict,
        user_id: str,
        user_message: str
    ) -> Dict:
        """
        Build API payload from extracted entities using the mapping.
        Fills smart defaults for missing data (low-friction strategy).
        """
        payload = {}
        entity_mapping = action_config.get("entity_mapping", {})
        defaults = action_config.get("defaults", {})
        
        # Map entities to payload fields
        for payload_field, entity_keys in entity_mapping.items():
            for entity_key in entity_keys:
                value = entities.get(entity_key)
                if value is not None:
                    # Handle list values — take the first item
                    if isinstance(value, list) and len(value) > 0:
                        value = value[0]
                    payload[payload_field] = value
                    break
        
        # Apply smart defaults for missing fields
        for field, default_value in defaults.items():
            if field not in payload:
                payload[field] = default_value
        
        # Always include user_id
        payload["user_id"] = user_id
        
        # Infer title from user message if not explicitly extracted
        if action_config.get("required_fields") and "title" in action_config["required_fields"]:
            if "title" not in payload or not payload["title"]:
                # Try to extract a meaningful title from the user message
                payload["title"] = self._infer_title(user_message)
        
        # Smart date handling — convert relative dates
        if "dueDate" in payload:
            payload["dueDate"] = self._resolve_date(payload["dueDate"])
        if "startDate" in payload:
            payload["startDate"] = self._resolve_date(payload["startDate"])
        if "date" in payload:
            payload["date"] = self._resolve_date(payload["date"])
        
        return payload
    
    def _check_required_fields(self, action_config: Dict, payload: Dict) -> List[str]:
        """Check which required fields are missing."""
        required = action_config.get("required_fields", [])
        missing = []
        for field in required:
            if field not in payload or not payload[field]:
                missing.append(field)
        return missing
    
    def _resolve_endpoint(self, endpoint: str, payload: Dict, entities: Dict) -> str:
        """Replace {id} placeholders in endpoint URLs."""
        if "{id}" in endpoint:
            # Try to find ID from entities or payload
            task_id = (
                entities.get("task_id") or 
                entities.get("event_id") or 
                entities.get("habit_id") or 
                entities.get("id") or 
                payload.get("id")
            )
            if task_id:
                if isinstance(task_id, list):
                    task_id = task_id[0]
                endpoint = endpoint.replace("{id}", str(task_id))
            else:
                # Can't resolve ID — endpoint stays with placeholder
                pass
        return endpoint
    
    def _resolve_date(self, date_value: Any) -> str:
        """Convert relative dates to ISO format."""
        if isinstance(date_value, str):
            today = datetime.now()
            lower = date_value.lower().strip()
            
            if lower in ["today", "aaj"]:
                return today.strftime("%Y-%m-%d")
            elif lower in ["tomorrow", "kal", "tmrw"]:
                return (today + timedelta(days=1)).strftime("%Y-%m-%d")
            elif lower in ["yesterday"]:
                return (today - timedelta(days=1)).strftime("%Y-%m-%d")
            elif lower in ["day after tomorrow", "parson"]:
                return (today + timedelta(days=2)).strftime("%Y-%m-%d")
            
            # If already in ISO format or other, return as-is
            return date_value
        return str(date_value) if date_value else datetime.now().strftime("%Y-%m-%d")
    
    def _infer_title(self, user_message: str) -> str:
        """Extract a meaningful title from the user's message."""
        # Remove common trigger phrases
        triggers = [
            "add a task", "create a task", "add task", "create task",
            "add a todo", "create a todo", "schedule", 
            "remind me to", "I need to", "I want to", "please",
            "add an event", "create an event", "set up",
            "can you", "could you", "will you",
        ]
        
        title = user_message
        for trigger in triggers:
            title = title.lower().replace(trigger.lower(), "").strip()
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()
        
        # Fallback
        return title if title else "New Task"
    
    def _build_confirmation(self, intent: str, payload: Dict, result: Dict) -> str:
        """Build a human-readable confirmation of what was done."""
        confirmations = {
            "create_task": f"✓ Task created: '{payload.get('title', 'Untitled')}'",
            "update_task": f"✓ Task updated successfully",
            "delete_task": f"✓ Task deleted",
            "query_schedule": f"Here are your tasks",
            "create_event": f"✓ Event scheduled: '{payload.get('title', 'Untitled')}'",
            "update_event": f"✓ Event updated",
            "delete_event": f"✓ Event removed",
            "log_exercise": f"✓ Workout logged: {payload.get('exercise_type', 'exercise')} for {payload.get('duration_minutes', '?')} min",
            "log_expense": f"✓ Expense logged: ₹{payload.get('amount', '?')} for {payload.get('category', 'general')}",
            "log_income": f"✓ Income logged: ₹{payload.get('amount', '?')}",
            "log_sleep": f"✓ Sleep logged",
            "log_water": f"✓ Water intake logged: {payload.get('amount_ml', 250)}ml",
            "log_food": f"✓ Meal logged",
            "log_study": f"✓ Study session logged: {payload.get('duration_minutes', '?')} min",
            "track_habit": f"✓ Habit logged",
            "query_workout": f"Here's your workout history",
            "query_habits": f"Here are your habits",
            "productivity_stats": f"Here are your productivity stats",
        }
        
        # Add date info if present
        base = confirmations.get(intent, f"✓ Action completed: {intent}")
        if payload.get("dueDate"):
            base += f" (due: {payload['dueDate']})"
        if payload.get("startDate"):
            base += f" (on: {payload['startDate']})"
        
        return base
    
    async def _call_service(
        self,
        service: str,
        method: str,
        endpoint: str,
        payload: Optional[Dict] = None,
        params: Optional[Dict] = None,
        user_id: str = ""
    ) -> Dict:
        """Make HTTP call to a backend service."""
        # Determine base URL
        if service == "scheduler":
            base_url = self.scheduler_url
        elif service == "lifestyle":
            base_url = self.lifestyle_url
        else:
            return {"message": "No service call needed"}
        
        url = f"{base_url}{endpoint}"
        
        headers = {
            "Content-Type": "application/json",
            "x-user-id": user_id,
            "x-internal-api-key": self.internal_api_key,
        }
        
        # Clean payload — remove user_id from body (it's in headers)
        if payload:
            clean_payload = {k: v for k, v in payload.items() if k != "user_id"}
        else:
            clean_payload = None
        
        # Clean params — remove user_id (add as query param instead)
        if params:
            clean_params = {k: v for k, v in params.items() if v is not None}
            clean_params["user_id"] = user_id
        else:
            clean_params = None
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=clean_params)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=clean_payload)
                elif method == "PUT":
                    response = await client.put(url, headers=headers, json=clean_payload)
                elif method == "DELETE":
                    response = await client.delete(url, headers=headers)
                elif method == "PATCH":
                    response = await client.patch(url, headers=headers, json=clean_payload)
                else:
                    return {"error": f"Unsupported method: {method}"}
                
                if response.status_code < 400:
                    try:
                        return response.json()
                    except Exception:
                        return {"status": "success", "status_code": response.status_code}
                else:
                    logger.warning(
                        f"Service call failed: {method} {url} → {response.status_code}: {response.text[:200]}"
                    )
                    return {
                        "error": f"Service returned {response.status_code}",
                        "details": response.text[:200]
                    }
        
        except httpx.ConnectError:
            logger.error(f"Cannot connect to {service} service at {base_url}")
            return {"error": f"{service} service unavailable"}
        except Exception as e:
            logger.error(f"Service call error: {e}")
            return {"error": str(e)}


def get_action_executor() -> ActionExecutorService:
    """Get or create ActionExecutorService singleton."""
    global _action_executor_instance
    
    if _action_executor_instance is None:
        _action_executor_instance = ActionExecutorService()
    
    return _action_executor_instance

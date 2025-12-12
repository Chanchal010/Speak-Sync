"""
Chat API Routes - NLU and conversational AI endpoints
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import logging

from src.services.nlu_service import get_nlu_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai/chat", tags=["Chat & NLU"])


# Request models
class IntentRequest(BaseModel):
    text: str = Field(..., description="User input text")
    user_id: Optional[str] = Field(None, description="User identifier for context")
    context: Optional[Dict] = Field(None, description="Additional context")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    user_id: Optional[str] = Field(None, description="User identifier")
    include_history: bool = Field(True, description="Include conversation history")
    context: Optional[Dict] = Field(None, description="Additional context")


class EntityRequest(BaseModel):
    text: str = Field(..., description="Text to extract entities from")
    entity_types: Optional[List[str]] = Field(None, description="Specific entity types to extract")


# ==================== Intent Detection ====================

@router.post("/intent")
async def detect_intent(request: IntentRequest):
    """
    Detect user intent from text
    
    **Example Request**:
    ```json
    {
        "text": "Schedule a workout for tomorrow at 6 PM",
        "user_id": "user123",
        "context": {
            "current_time": "2025-12-05T10:30:00",
            "user_name": "John"
        }
    }
    ```
    
    **Response**:
    ```json
    {
        "intent": "log_exercise",
        "domain": "exercise",
        "confidence": 0.95,
        "entities": {
            "dates": ["2025-12-06"],
            "times": ["18:00"],
            "activity": "workout"
        },
        "response_suggestion": "Got it! I'll schedule a workout for tomorrow at 6 PM."
    }
    ```
    """
    try:
        nlu_service = get_nlu_service()
        
        result = await nlu_service.detect_intent(
            text=request.text,
            user_id=request.user_id,
            context=request.context
        )
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Intent detection error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Intent detection failed: {str(e)}"
        )


@router.post("/entities")
async def extract_entities(request: EntityRequest):
    """
    Extract entities from text
    
    **Example**:
    ```json
    {
        "text": "I spent $50 on groceries yesterday at 3 PM",
        "entity_types": ["amounts", "dates", "times", "categories"]
    }
    ```
    
    **Response**:
    ```json
    {
        "amounts": [50.0],
        "dates": ["2025-12-04"],
        "times": ["15:00"],
        "categories": ["groceries"]
    }
    ```
    """
    try:
        nlu_service = get_nlu_service()
        
        entities = await nlu_service.extract_entities(
            text=request.text,
            entity_types=request.entity_types
        )
        
        return JSONResponse(content=entities)
    
    except Exception as e:
        logger.error(f"Entity extraction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Entity extraction failed: {str(e)}"
        )


# ==================== Conversational AI ====================

@router.post("/message")
async def chat_message(request: ChatRequest):
    """
    Process a chat message with full NLU pipeline
    
    This endpoint:
    1. Detects intent and extracts entities
    2. Generates a natural conversational response
    3. Maintains conversation history
    
    **Example**:
    ```json
    {
        "message": "I want to track my water intake",
        "user_id": "user123",
        "include_history": true
    }
    ```
    
    **Response**:
    ```json
    {
        "response": "Great! How much water have you had so far today?",
        "intent": "log_water",
        "domain": "hydration",
        "confidence": 0.92,
        "entities": {},
        "sentiment": {
            "sentiment": "neutral",
            "emotion": "calm",
            "intensity": 0.6
        }
    }
    ```
    """
    try:
        nlu_service = get_nlu_service()
        
        # Step 1: Detect intent
        intent_data = await nlu_service.detect_intent(
            text=request.message,
            user_id=request.user_id,
            context=request.context
        )
        
        # Step 2: Analyze sentiment
        sentiment = await nlu_service.analyze_sentiment(request.message)
        
        # Step 3: Generate response
        response_text = await nlu_service.generate_response(
            user_message=request.message,
            intent_data=intent_data,
            user_id=request.user_id,
            include_history=request.include_history
        )
        
        return JSONResponse(content={
            "response": response_text,
            "intent": intent_data.get("intent"),
            "domain": intent_data.get("domain"),
            "confidence": intent_data.get("confidence"),
            "entities": intent_data.get("entities", {}),
            "sentiment": sentiment
        })
    
    except Exception as e:
        logger.error(f"Chat message error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.post("/sentiment")
async def analyze_sentiment(text: str):
    """
    Analyze sentiment and emotion from text
    
    **Example**:
    ```bash
    curl -X POST "http://localhost:8000/api/ai/chat/sentiment?text=I'm so happy today!"
    ```
    
    **Response**:
    ```json
    {
        "sentiment": "positive",
        "emotion": "happy",
        "intensity": 0.9
    }
    ```
    """
    try:
        nlu_service = get_nlu_service()
        
        result = await nlu_service.analyze_sentiment(text)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Sentiment analysis failed: {str(e)}"
        )


# ==================== Conversation Management ====================

@router.get("/history/{user_id}/summary")
async def get_conversation_summary(user_id: str, max_length: int = 100):
    """
    Get a summary of user's conversation history
    
    **Example**:
    ```bash
    curl http://localhost:8000/api/ai/chat/history/user123/summary
    ```
    
    **Response**:
    ```json
    {
        "user_id": "user123",
        "summary": "User discussed workout scheduling and asked about fitness goals. Agreed to start with 3 workouts per week."
    }
    ```
    """
    try:
        nlu_service = get_nlu_service()
        
        summary = await nlu_service.summarize_conversation(
            user_id=user_id,
            max_length=max_length
        )
        
        return JSONResponse(content={
            "user_id": user_id,
            "summary": summary
        })
    
    except Exception as e:
        logger.error(f"Summary generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Summary generation failed: {str(e)}"
        )


@router.delete("/history/{user_id}")
async def clear_conversation_history(user_id: str):
    """
    Clear conversation history for a user
    
    **Example**:
    ```bash
    curl -X DELETE http://localhost:8000/api/ai/chat/history/user123
    ```
    """
    try:
        nlu_service = get_nlu_service()
        
        nlu_service.clear_history(user_id)
        
        return JSONResponse(content={
            "message": f"Conversation history cleared for user: {user_id}"
        })
    
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear history: {str(e)}"
        )


# ==================== Utility Endpoints ====================

@router.get("/intents")
async def list_intents():
    """
    List all available intents by domain
    
    **Response**:
    ```json
    {
        "domains": {
            "scheduling": ["create_task", "update_task", "delete_task"],
            "exercise": ["log_exercise", "query_workout"],
            ...
        },
        "total_intents": 32
    }
    ```
    """
    from services.nlu_service import INTENT_CATEGORIES
    
    total = sum(len(intents) for intents in INTENT_CATEGORIES.values())
    
    return JSONResponse(content={
        "domains": INTENT_CATEGORIES,
        "total_intents": total,
        "supported_domains": list(INTENT_CATEGORIES.keys())
    })


@router.get("/health")
async def nlu_health_check():
    """
    Check NLU service health
    """
    try:
        nlu_service = get_nlu_service()
        
        return JSONResponse(content={
            "status": "healthy",
            "model": nlu_service.model,
            "active_conversations": len(nlu_service.conversation_history)
        })
    
    except Exception as e:
        logger.error(f"NLU health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="NLU service unavailable"
        )

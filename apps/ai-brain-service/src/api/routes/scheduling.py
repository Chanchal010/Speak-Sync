"""
Scheduling API Routes
Endpoints for smart scheduling, conflict detection, and optimization
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

from ...services.scheduling_service import SchedulingService
from ...services.nlu_service import NLUService
from ...ml.scheduling_model import SchedulingModel


router = APIRouter(prefix="/api/scheduling", tags=["scheduling"])

# Dependency injection
scheduling_service = None
scheduling_model = None


async def get_db_pool():
    """Get database pool from main app"""
    from ...main import db
    if db and db.pool:
        return db.pool
    return None


async def get_scheduling_service():
    """Get or create scheduling service instance"""
    global scheduling_service
    if scheduling_service is None:
        db_pool = await get_db_pool()
        scheduling_service = SchedulingService(db_pool=db_pool)
        if db_pool:
            await scheduling_service.initialize(db_pool)
    return scheduling_service


async def get_scheduling_model():
    """Get or create scheduling model instance"""
    global scheduling_model
    if scheduling_model is None:
        scheduling_model = SchedulingModel()
    return scheduling_model


# ==================== Request/Response Models ====================

class ConflictAnalysisRequest(BaseModel):
    user_id: str
    start_date: datetime
    end_date: datetime


class ConflictAnalysisResponse(BaseModel):
    conflicts: List[Dict]
    overloaded_days: List[Dict]
    gaps: List[Dict]
    summary: Dict


class TimeSlotSuggestionRequest(BaseModel):
    user_id: str
    task_type: str = Field(..., description="deep_work, meeting, routine, review")
    duration_minutes: int
    deadline: Optional[datetime] = None
    preferred_days: Optional[List[int]] = Field(None, description="Weekday numbers 0-6")


class TimeSlotSuggestionResponse(BaseModel):
    suggestions: List[Dict]
    model_confidence: float


class OptimizeScheduleRequest(BaseModel):
    user_id: str
    task_ids: List[str]


class OptimizeScheduleResponse(BaseModel):
    optimized_schedule: List[Dict]
    improvements: Dict


class SmartSuggestionsRequest(BaseModel):
    user_id: str
    context: Optional[Dict] = Field(None, description="Additional context like location, time")


class SmartSuggestionsResponse(BaseModel):
    suggestions: List[str]
    timestamp: datetime


class TrainModelRequest(BaseModel):
    user_id: str
    days_of_history: int = Field(90, description="Days of historical data to use")


class PredictCompletionTimeRequest(BaseModel):
    user_id: str
    task: Dict


class PredictCompletionTimeResponse(BaseModel):
    predicted_minutes: int
    confidence: float
    explanation: str


class SchedulingScoreRequest(BaseModel):
    user_id: str
    task: Dict
    proposed_time: datetime
    current_schedule: List[Dict] = []


class SchedulingScoreResponse(BaseModel):
    score: float
    explanation: str
    recommendations: List[str]


# ==================== Endpoints ====================

@router.post(
    "/analyze-conflicts",
    response_model=ConflictAnalysisResponse,
    summary="Analyze Schedule Conflicts",
    description="Detect conflicts, overloaded days, and available time gaps in user's schedule"
)
async def analyze_conflicts(
    request: ConflictAnalysisRequest,
    service: SchedulingService = Depends(get_scheduling_service)
):
    """
    Analyze user's schedule for conflicts and optimization opportunities
    
    Example:
    ```json
    {
        "user_id": "user123",
        "start_date": "2025-12-15T00:00:00Z",
        "end_date": "2025-12-22T00:00:00Z"
    }
    ```
    """
    
    try:
        result = await service.analyze_schedule_conflicts(
            request.user_id,
            request.start_date,
            request.end_date
        )
        
        return ConflictAnalysisResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/suggest-time-slot",
    response_model=TimeSlotSuggestionResponse,
    summary="Suggest Optimal Time Slots",
    description="Get AI-powered suggestions for best times to schedule a task"
)
async def suggest_time_slot(
    request: TimeSlotSuggestionRequest,
    service: SchedulingService = Depends(get_scheduling_service)
):
    """
    Suggest optimal time slots based on:
    - User's productivity patterns
    - Current schedule
    - Task type requirements
    - Deadline constraints
    
    Example:
    ```json
    {
        "user_id": "user123",
        "task_type": "deep_work",
        "duration_minutes": 120,
        "deadline": "2025-12-20T17:00:00Z",
        "preferred_days": [1, 2, 3]
    }
    ```
    """
    
    try:
        suggestions = await service.suggest_optimal_time_slot(
            request.user_id,
            request.task_type,
            request.duration_minutes,
            request.deadline,
            request.preferred_days
        )
        
        # Calculate average confidence
        avg_confidence = sum(s['confidence'] for s in suggestions) / len(suggestions) if suggestions else 0
        
        return TimeSlotSuggestionResponse(
            suggestions=suggestions,
            model_confidence=avg_confidence
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/optimize-schedule",
    response_model=OptimizeScheduleResponse,
    summary="Optimize Task Schedule",
    description="Re-arrange multiple tasks for optimal scheduling"
)
async def optimize_schedule(
    request: OptimizeScheduleRequest,
    service: SchedulingService = Depends(get_scheduling_service)
):
    """
    Apply ML-based optimization to reschedule multiple tasks
    
    Example:
    ```json
    {
        "user_id": "user123",
        "task_ids": ["task1", "task2", "task3"]
    }
    ```
    """
    
    try:
        result = await service.optimize_task_schedule(
            request.user_id,
            request.task_ids
        )
        
        return OptimizeScheduleResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/smart-suggestions",
    response_model=SmartSuggestionsResponse,
    summary="Get Proactive Suggestions",
    description="Get context-aware scheduling suggestions"
)
async def smart_suggestions(
    request: SmartSuggestionsRequest,
    service: SchedulingService = Depends(get_scheduling_service)
):
    """
    Get proactive scheduling suggestions based on:
    - Current time and context
    - User's patterns
    - Upcoming deadlines
    - Schedule gaps
    
    Example:
    ```json
    {
        "user_id": "user123",
        "context": {
            "current_time": "2025-12-15T10:00:00Z",
            "location": "office"
        }
    }
    ```
    """
    
    try:
        suggestions = await service.get_smart_suggestions(
            request.user_id,
            request.context
        )
        
        return SmartSuggestionsResponse(
            suggestions=suggestions,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/train-model",
    summary="Train Scheduling Model",
    description="Train ML model on user's historical data"
)
async def train_model(
    request: TrainModelRequest,
    model: SchedulingModel = Depends(get_scheduling_model),
    service: SchedulingService = Depends(get_scheduling_service)
):
    """
    Train the scheduling model on user's historical data
    
    This should be called:
    - When user first starts using the system
    - Periodically (weekly) to update patterns
    - After significant changes in user behavior
    
    Example:
    ```json
    {
        "user_id": "user123",
        "days_of_history": 90
    }
    ```
    """
    
    try:
        # Fetch historical data
        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days_of_history)
        
        historical_tasks = await service._get_tasks(
            request.user_id, start_date, end_date
        )
        historical_events = await service._get_events(
            request.user_id, start_date, end_date
        )
        
        # Train model
        await model.train_on_user_data(
            request.user_id,
            historical_tasks,
            historical_events
        )
        
        return {
            "status": "success",
            "message": f"Model trained on {len(historical_tasks)} tasks and {len(historical_events)} events",
            "training_period": f"{request.days_of_history} days"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/predict-completion-time",
    response_model=PredictCompletionTimeResponse,
    summary="Predict Task Completion Time",
    description="Predict how long a task will actually take based on ML model"
)
async def predict_completion_time(
    request: PredictCompletionTimeRequest,
    model: SchedulingModel = Depends(get_scheduling_model)
):
    """
    Predict actual completion time vs. estimated time
    
    Example:
    ```json
    {
        "user_id": "user123",
        "task": {
            "title": "Write documentation",
            "estimated_duration": 60
        }
    }
    ```
    """
    
    try:
        predicted_minutes, confidence = model.predict_completion_time(
            request.task,
            request.user_id
        )
        
        estimated = request.task.get('estimated_duration', 60)
        difference = predicted_minutes - estimated
        
        explanation = f"Based on your history, this task will likely take {predicted_minutes} minutes "
        if abs(difference) > 10:
            explanation += f"({abs(difference)} minutes {'more' if difference > 0 else 'less'} than estimated)"
        else:
            explanation += "(close to your estimate)"
        
        return PredictCompletionTimeResponse(
            predicted_minutes=predicted_minutes,
            confidence=confidence,
            explanation=explanation
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/calculate-scheduling-score",
    response_model=SchedulingScoreResponse,
    summary="Calculate Scheduling Score",
    description="Score a proposed time slot for scheduling a task"
)
async def calculate_scheduling_score(
    request: SchedulingScoreRequest,
    model: SchedulingModel = Depends(get_scheduling_model)
):
    """
    Calculate a score (0-100) for scheduling a task at proposed time
    
    Example:
    ```json
    {
        "user_id": "user123",
        "task": {
            "title": "Deep work session",
            "priority": "HIGH",
            "due_date": "2025-12-20T17:00:00Z"
        },
        "proposed_time": "2025-12-15T10:00:00Z",
        "current_schedule": []
    }
    ```
    """
    
    try:
        score = model.calculate_scheduling_score(
            request.task,
            request.proposed_time,
            request.user_id,
            request.current_schedule
        )
        
        # Generate recommendations
        recommendations = []
        if score >= 80:
            recommendations.append("Excellent time slot - highly recommended")
        elif score >= 60:
            recommendations.append("Good time slot with minor considerations")
        else:
            recommendations.append("Consider alternative time slots")
        
        # Add specific recommendations
        hour = request.proposed_time.hour
        if hour < 9:
            recommendations.append("Early morning - ensure you're a morning person")
        elif hour > 17:
            recommendations.append("Evening slot - may impact work-life balance")
        
        explanation = f"Score: {score:.0f}/100. "
        if score >= 80:
            explanation += "Optimal time based on your patterns and current schedule."
        elif score >= 60:
            explanation += "Good time with some room for improvement."
        else:
            explanation += "Consider rescheduling for better productivity."
        
        return SchedulingScoreResponse(
            score=score,
            explanation=explanation,
            recommendations=recommendations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/patterns/{user_id}",
    summary="Get User Scheduling Patterns",
    description="Retrieve detected patterns in user's scheduling behavior"
)
async def get_scheduling_patterns(
    user_id: str,
    model: SchedulingModel = Depends(get_scheduling_model),
    service: SchedulingService = Depends(get_scheduling_service)
):
    """
    Get detected patterns:
    - Preferred days/hours
    - Task clustering
    - Average metrics
    
    Example: GET /api/scheduling/patterns/user123
    """
    
    try:
        # Fetch recent data
        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        tasks = await service._get_tasks(user_id, start_date, end_date)
        events = await service._get_events(user_id, start_date, end_date)
        
        patterns = model.detect_scheduling_patterns(tasks, events)
        
        return {
            "user_id": user_id,
            "patterns": patterns,
            "data_period": "90 days",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Scheduling Service Health",
    description="Check if scheduling service is operational"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "scheduling",
        "features": [
            "conflict_detection",
            "time_slot_suggestions",
            "schedule_optimization",
            "pattern_recognition",
            "ml_predictions"
        ],
        "timestamp": datetime.now().isoformat()
    }

"""
Habit Prediction API Routes
Endpoints for habit analysis, predictions, and personalized insights
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

from ...services.habit_prediction_service import HabitPredictionService
from ...ml.habit_model import HabitFormationModel


router = APIRouter(prefix="/api/habits", tags=["habits"])

# Dependency injection
habit_service = None
habit_model = None


async def get_habit_service():
    """Get or create habit prediction service instance"""
    global habit_service
    if habit_service is None:
        habit_service = HabitPredictionService()
    return habit_service


async def get_habit_model():
    """Get or create habit model instance"""
    global habit_model
    if habit_model is None:
        habit_model = HabitFormationModel()
    return habit_model


# ==================== Request/Response Models ====================

class AnalyzePatternsRequest(BaseModel):
    user_id: str
    habit_type: str = Field(..., description="food, exercise, meditation, sleep, water, study")
    days_history: int = Field(90, description="Days of historical data to analyze")


class AnalyzePatternsResponse(BaseModel):
    completion_rate: float
    streak_info: Dict
    time_patterns: Dict
    trends: Dict
    risk_factors: List[Dict]


class PredictStreakRequest(BaseModel):
    user_id: str
    habit_type: str
    current_streak: int


class PredictStreakResponse(BaseModel):
    survival_probability: Dict[str, float]
    risk_level: str
    critical_days: List[int]
    recommendations: List[str]


class PredictCompletionRequest(BaseModel):
    user_id: str
    habit_type: str


class PredictCompletionResponse(BaseModel):
    most_likely_time: str
    confidence: float
    alternative_times: List[Dict]
    reasoning: str


class PersonalizedInsightsRequest(BaseModel):
    user_id: str
    habit_type: Optional[str] = None


class PersonalizedInsightsResponse(BaseModel):
    insights: List[str]
    generated_at: datetime


class OptimalScheduleRequest(BaseModel):
    user_id: str
    habit_type: str


class OptimalScheduleResponse(BaseModel):
    recommended_times: List[Dict]
    frequency: str
    duration_recommendation: int
    environment_tips: List[str]


class HabitFormationRequest(BaseModel):
    user_id: str
    habit_type: str


class HabitFormationResponse(BaseModel):
    days_to_automation: int
    current_progress: float
    formation_stage: str
    estimated_completion_date: str
    strength_indicators: Dict
    next_milestone: Dict


class HabitStrengthRequest(BaseModel):
    user_id: str
    habit_type: str
    days_tracked: int = 90


class HabitStrengthResponse(BaseModel):
    strength_score: float
    automaticity: float
    lapse_risk: float
    risk_level: str
    success_probabilities: Dict[str, float]


class BehaviorChangeRequest(BaseModel):
    user_id: str
    habit_type: str


class BehaviorChangeResponse(BaseModel):
    current_stage: str
    behavior_plan: Dict
    intervention_timing: Dict


# ==================== Endpoints ====================

@router.post(
    "/analyze-patterns",
    response_model=AnalyzePatternsResponse,
    summary="Analyze Habit Patterns",
    description="Deep analysis of user's habit patterns, trends, and risk factors"
)
async def analyze_patterns(
    request: AnalyzePatternsRequest,
    service: HabitPredictionService = Depends(get_habit_service)
):
    """
    Analyze behavioral patterns for a specific habit
    
    Example:
    ```json
    {
        "user_id": "user123",
        "habit_type": "meditation",
        "days_history": 90
    }
    ```
    """
    
    try:
        result = await service.analyze_habit_patterns(
            request.user_id,
            request.habit_type,
            request.days_history
        )
        
        return AnalyzePatternsResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/predict-streak",
    response_model=PredictStreakResponse,
    summary="Predict Streak Survival",
    description="Predict probability of maintaining current habit streak"
)
async def predict_streak(
    request: PredictStreakRequest,
    service: HabitPredictionService = Depends(get_habit_service)
):
    """
    Predict likelihood of streak continuation
    
    Example:
    ```json
    {
        "user_id": "user123",
        "habit_type": "exercise",
        "current_streak": 14
    }
    ```
    """
    
    try:
        result = await service.predict_streak_survival(
            request.user_id,
            request.habit_type,
            request.current_streak
        )
        
        return PredictStreakResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/predict-next-completion",
    response_model=PredictCompletionResponse,
    summary="Predict Next Completion",
    description="Predict when user is most likely to complete habit next"
)
async def predict_next_completion(
    request: PredictCompletionRequest,
    service: HabitPredictionService = Depends(get_habit_service)
):
    """
    Predict optimal time for next habit completion
    
    Example:
    ```json
    {
        "user_id": "user123",
        "habit_type": "meditation"
    }
    ```
    """
    
    try:
        result = await service.predict_next_completion(
            request.user_id,
            request.habit_type
        )
        
        return PredictCompletionResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/personalized-insights",
    response_model=PersonalizedInsightsResponse,
    summary="Get Personalized Insights",
    description="Generate natural language insights about user's habits"
)
async def personalized_insights(
    request: PersonalizedInsightsRequest,
    service: HabitPredictionService = Depends(get_habit_service)
):
    """
    Get AI-generated insights about habit patterns
    
    Example:
    ```json
    {
        "user_id": "user123",
        "habit_type": "exercise"
    }
    ```
    
    Or for all habits:
    ```json
    {
        "user_id": "user123"
    }
    ```
    """
    
    try:
        insights = await service.generate_personalized_insights(
            request.user_id,
            request.habit_type
        )
        
        return PersonalizedInsightsResponse(
            insights=insights,
            generated_at=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/optimal-schedule",
    response_model=OptimalScheduleResponse,
    summary="Recommend Optimal Schedule",
    description="Get personalized schedule recommendations for a habit"
)
async def optimal_schedule(
    request: OptimalScheduleRequest,
    service: HabitPredictionService = Depends(get_habit_service)
):
    """
    Get optimal scheduling recommendations
    
    Example:
    ```json
    {
        "user_id": "user123",
        "habit_type": "study"
    }
    ```
    """
    
    try:
        result = await service.recommend_optimal_schedule(
            request.user_id,
            request.habit_type
        )
        
        return OptimalScheduleResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/formation-prediction",
    response_model=HabitFormationResponse,
    summary="Predict Habit Formation",
    description="Predict when habit will become automatic (66-day rule)"
)
async def formation_prediction(
    request: HabitFormationRequest,
    service: HabitPredictionService = Depends(get_habit_service)
):
    """
    Predict habit formation timeline and milestones
    
    Example:
    ```json
    {
        "user_id": "user123",
        "habit_type": "water"
    }
    ```
    """
    
    try:
        result = await service.predict_habit_formation(
            request.user_id,
            request.habit_type
        )
        
        return HabitFormationResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/habit-strength",
    response_model=HabitStrengthResponse,
    summary="Calculate Habit Strength",
    description="Calculate comprehensive habit strength metrics"
)
async def habit_strength(
    request: HabitStrengthRequest,
    service: HabitPredictionService = Depends(get_habit_service),
    model: HabitFormationModel = Depends(get_habit_model)
):
    """
    Calculate habit strength and related metrics
    
    Example:
    ```json
    {
        "user_id": "user123",
        "habit_type": "exercise",
        "days_tracked": 90
    }
    ```
    """
    
    try:
        # Fetch habit logs
        logs = await service._fetch_habit_logs(
            request.user_id,
            request.habit_type,
            request.days_tracked
        )
        
        # Calculate metrics
        strength_score = model.calculate_habit_strength(logs, request.days_tracked)
        
        streak_info = service._analyze_streaks(logs)
        current_streak = streak_info['current']
        
        automaticity = model.predict_automaticity(current_streak, strength_score)
        lapse_risk, risk_level = model.calculate_lapse_risk(
            logs, current_streak, request.days_tracked
        )
        
        success_probs = model.predict_success_probability(
            strength_score, automaticity, lapse_risk
        )
        
        return HabitStrengthResponse(
            strength_score=round(strength_score, 2),
            automaticity=round(automaticity, 2),
            lapse_risk=round(lapse_risk, 2),
            risk_level=risk_level,
            success_probabilities=success_probs
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/behavior-change-plan",
    response_model=BehaviorChangeResponse,
    summary="Generate Behavior Change Plan",
    description="Get personalized behavior change strategy"
)
async def behavior_change_plan(
    request: BehaviorChangeRequest,
    service: HabitPredictionService = Depends(get_habit_service),
    model: HabitFormationModel = Depends(get_habit_model)
):
    """
    Generate comprehensive behavior change plan
    
    Based on Transtheoretical Model and habit formation research
    
    Example:
    ```json
    {
        "user_id": "user123",
        "habit_type": "meditation"
    }
    ```
    """
    
    try:
        # Fetch data
        logs = await service._fetch_habit_logs(request.user_id, request.habit_type, 90)
        
        # Calculate metrics
        strength_score = model.calculate_habit_strength(logs, 90)
        streak_info = service._analyze_streaks(logs)
        current_streak = streak_info['current']
        
        # Identify stage
        current_stage = model.identify_behavior_stage(
            current_streak, strength_score, logs
        )
        
        # Generate plan
        behavior_plan = model.generate_behavior_change_plan(
            request.habit_type, current_stage, strength_score
        )
        
        # Calculate lapse risk
        lapse_risk, _ = model.calculate_lapse_risk(logs, current_streak, 90)
        
        # Optimal intervention timing
        intervention_timing = model.predict_optimal_intervention_time(
            logs, lapse_risk
        )
        
        return BehaviorChangeResponse(
            current_stage=current_stage,
            behavior_plan=behavior_plan,
            intervention_timing=intervention_timing
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/momentum/{user_id}/{habit_type}",
    summary="Get Habit Momentum",
    description="Calculate current habit momentum (improvement trend)"
)
async def get_momentum(
    user_id: str,
    habit_type: str,
    window_days: int = 14,
    service: HabitPredictionService = Depends(get_habit_service),
    model: HabitFormationModel = Depends(get_habit_model)
):
    """
    Calculate habit momentum over recent period
    
    Example: GET /api/habits/momentum/user123/exercise?window_days=14
    """
    
    try:
        logs = await service._fetch_habit_logs(user_id, habit_type, window_days * 2)
        
        momentum = model.calculate_habit_momentum(logs, window_days)
        
        # Interpret momentum
        if momentum > 0.1:
            interpretation = "Strong positive momentum - keep it up!"
        elif momentum > 0:
            interpretation = "Slight improvement trend"
        elif momentum > -0.1:
            interpretation = "Stable performance"
        else:
            interpretation = "Momentum declining - time to refocus"
        
        return {
            'momentum': momentum,
            'interpretation': interpretation,
            'window_days': window_days
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Habit Service Health",
    description="Check if habit prediction service is operational"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "habit_prediction",
        "features": [
            "pattern_analysis",
            "streak_prediction",
            "completion_prediction",
            "personalized_insights",
            "habit_strength_calculation",
            "behavior_change_plans",
            "momentum_tracking"
        ],
        "ml_models": [
            "habit_formation_model",
            "behavioral_prediction"
        ],
        "timestamp": datetime.now().isoformat()
    }

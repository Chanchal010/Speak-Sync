"""
Analytics API Routes
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from datetime import datetime

from ...database.mongodb import get_database
from ...services.analytics_service import AnalyticsService
from fastapi import Header


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


async def get_user_id(x_user_id: str = Header(...)):
    """Extract user ID from header"""
    return x_user_id


async def get_service():
    """Get analytics service instance"""
    return AnalyticsService(get_database())


@router.get("/correlations")
async def get_habit_correlations(
    habit_types: Optional[List[str]] = Query(
        None,
        description="Filter by habit types (food, exercise, financial, sleep, study, water)"
    ),
    start_date: Optional[datetime] = Query(
        None,
        description="Filter by date (>=). Format: YYYY-MM-DDTHH:MM:SS"
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Filter by date (<=). Format: YYYY-MM-DDTHH:MM:SS"
    ),
    user_id: str = Depends(get_user_id),
    service: AnalyticsService = Depends(get_service)
):
    """
    Analyze cross-habit correlations to discover behavioral patterns
    
    This endpoint performs comprehensive analysis across all habit types to identify:
    
    **1. Sleep Quality → Exercise Performance**
    - Correlation between sleep quality and next-day perceived exertion (RPE)
    - Pattern: Poor sleep (quality ≤4) often leads to higher RPE (≥7)
    - Actionable: Prioritize 7-8 hours sleep before intense workouts
    
    **2. Hydration → Cognitive Performance**
    - Armstrong Scale urine color vs cognitive fog and mental clarity
    - Pattern: Dehydration (urine_color ≥5) strongly correlates with cognitive fog
    - Actionable: Maintain urine color 1-3 for optimal mental performance
    
    **3. Food Satisfaction → Emotional State**
    - Meal satisfaction levels vs emotional state before eating
    - Pattern: Low satisfaction (≤4) correlates with negative emotions (stressed, sad, anxious, bored)
    - Actionable: Identify emotional eating triggers and plan meals accordingly
    
    **4. Financial Stress → Sleep Quality**
    - Impulse purchases vs same-day sleep quality
    - Pattern: Days with impulse spending often have poor sleep quality
    - Actionable: Address financial anxiety to improve sleep
    
    **5. Study Flow State → Conditions**
    - Optimal conditions for high flow states (≥8)
    - Factors: Sleep quality, hydration, caffeine intake, location, music
    - Actionable: Replicate successful study environment conditions
    
    **6. Daily Habit Patterns**
    - Overall tracking consistency and multi-habit days
    - Identifies days with comprehensive tracking across multiple habit types
    
    **Returns:**
    - Correlation data for each pattern
    - Strength indicators (weak/moderate/strong)
    - Specific examples from your data
    - AI-generated actionable insights
    """
    
    result = await service.get_correlations(
        user_id=user_id,
        habit_types=habit_types,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "success": True,
        "data": result
    }

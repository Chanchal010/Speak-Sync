"""
Food Log Routes
API endpoints for meal tracking and food logging
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header

from ...database.mongodb import get_database
from ...models.food_log import FoodLogCreate, FoodLogUpdate, FoodLogResponse
from ...services.food_log_service import FoodLogService, get_food_log_service


router = APIRouter(prefix="/api/food-logs", tags=["Food Logs"])


async def get_user_id(x_user_id: str = Header(..., description="User ID from auth")) -> str:
    """Extract user ID from header"""
    return x_user_id


async def get_service() -> FoodLogService:
    """Dependency to get food log service"""
    db = get_database()
    return get_food_log_service(db)


@router.post("", response_model=FoodLogResponse, status_code=201)
async def create_food_log(
    habit_id: str,
    log_data: FoodLogCreate,
    user_id: str = Depends(get_user_id),
    service: FoodLogService = Depends(get_service)
):
    """
    Create a new food log entry
    
    **Meal Types**: breakfast, lunch, dinner, snack
    
    **AI Training Fields**:
    - hunger_level: 1-10 (1=Not hungry, 10=Starving)
    - satisfaction_level: 1-10 (1=Unsatisfied, 10=Very satisfied)
    - eating_speed: slow | moderate | fast
    - emotional_state: happy | stressed | bored | sad | neutral | excited
    - location: home | work | restaurant | outdoor
    - social_context: alone | family | friends | colleagues
    - distraction_level: 1-10 (1=Mindful, 10=Very distracted)
    """
    try:
        log = await service.create_food_log(user_id, habit_id, log_data)
        return FoodLogResponse(
            _id=str(log.id),
            user_id=log.user_id,
            habit_id=log.habit_id,
            meal_type=log.meal_type,
            timestamp=log.timestamp,
            food_items=log.food_items,
            portion_size=log.portion_size,
            calories=log.calories,
            hunger_level=log.hunger_level,
            satisfaction_level=log.satisfaction_level,
            eating_speed=log.eating_speed,
            emotional_state=log.emotional_state,
            location=log.location,
            social_context=log.social_context,
            distraction_level=log.distraction_level,
            notes=log.notes,
            photos=log.photos,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[FoodLogResponse])
async def get_food_logs(
    habit_id: Optional[str] = None,
    meal_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
    user_id: str = Depends(get_user_id),
    service: FoodLogService = Depends(get_service)
):
    """
    Get food logs with optional filters
    
    **Query Parameters**:
    - habit_id: Filter by specific habit
    - meal_type: Filter by meal type (breakfast, lunch, dinner, snack)
    - start_date: Filter logs from this date onwards
    - end_date: Filter logs up to this date
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (max 100)
    """
    if limit > 100:
        limit = 100
    
    logs = await service.get_food_logs(
        user_id=user_id,
        habit_id=habit_id,
        meal_type=meal_type,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return [
        FoodLogResponse(
            _id=str(log.id),
            user_id=log.user_id,
            habit_id=log.habit_id,
            meal_type=log.meal_type,
            timestamp=log.timestamp,
            food_items=log.food_items,
            portion_size=log.portion_size,
            calories=log.calories,
            hunger_level=log.hunger_level,
            satisfaction_level=log.satisfaction_level,
            eating_speed=log.eating_speed,
            emotional_state=log.emotional_state,
            location=log.location,
            social_context=log.social_context,
            distraction_level=log.distraction_level,
            notes=log.notes,
            photos=log.photos,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
        for log in logs
    ]


@router.get("/{log_id}", response_model=FoodLogResponse)
async def get_food_log(
    log_id: str,
    user_id: str = Depends(get_user_id),
    service: FoodLogService = Depends(get_service)
):
    """Get a specific food log by ID"""
    log = await service.get_food_log_by_id(user_id, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Food log not found")
    
    return FoodLogResponse(
        _id=str(log.id),
        user_id=log.user_id,
        habit_id=log.habit_id,
        meal_type=log.meal_type,
        timestamp=log.timestamp,
        food_items=log.food_items,
        portion_size=log.portion_size,
        calories=log.calories,
        hunger_level=log.hunger_level,
        satisfaction_level=log.satisfaction_level,
        eating_speed=log.eating_speed,
        emotional_state=log.emotional_state,
        location=log.location,
        social_context=log.social_context,
        distraction_level=log.distraction_level,
        notes=log.notes,
        photos=log.photos,
        created_at=log.created_at,
        updated_at=log.updated_at
    )


@router.put("/{log_id}", response_model=FoodLogResponse)
async def update_food_log(
    log_id: str,
    log_update: FoodLogUpdate,
    user_id: str = Depends(get_user_id),
    service: FoodLogService = Depends(get_service)
):
    """Update a food log"""
    log = await service.update_food_log(user_id, log_id, log_update)
    if not log:
        raise HTTPException(status_code=404, detail="Food log not found")
    
    return FoodLogResponse(
        _id=str(log.id),
        user_id=log.user_id,
        habit_id=log.habit_id,
        meal_type=log.meal_type,
        timestamp=log.timestamp,
        food_items=log.food_items,
        portion_size=log.portion_size,
        calories=log.calories,
        hunger_level=log.hunger_level,
        satisfaction_level=log.satisfaction_level,
        eating_speed=log.eating_speed,
        emotional_state=log.emotional_state,
        location=log.location,
        social_context=log.social_context,
        distraction_level=log.distraction_level,
        notes=log.notes,
        photos=log.photos,
        created_at=log.created_at,
        updated_at=log.updated_at
    )


@router.delete("/{log_id}")
async def delete_food_log(
    log_id: str,
    user_id: str = Depends(get_user_id),
    service: FoodLogService = Depends(get_service)
):
    """Soft delete a food log"""
    success = await service.delete_food_log(user_id, log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Food log not found")
    
    return {"success": True, "message": "Food log deleted successfully"}


@router.get("/stats/overview")
async def get_food_log_stats(
    habit_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: str = Depends(get_user_id),
    service: FoodLogService = Depends(get_service)
):
    """
    Get food logging statistics
    
    Returns aggregated data including:
    - Total logs
    - Average calories, hunger, satisfaction, distraction levels
    - Meal type distribution
    - Location distribution
    - Emotional state patterns
    """
    stats = await service.get_food_log_stats(
        user_id=user_id,
        habit_id=habit_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {"success": True, "data": stats}

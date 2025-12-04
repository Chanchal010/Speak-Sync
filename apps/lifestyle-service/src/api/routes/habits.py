"""
Habit API routes
"""
from fastapi import APIRouter, HTTPException, Header, Depends, Query
from typing import List, Optional
from datetime import datetime

from ...models.habit import HabitCreate, HabitUpdate, HabitResponse
from ...services.habit_service import get_habit_service, HabitService
from ...database.mongodb import get_database

router = APIRouter(prefix="/api/habits", tags=["habits"])

async def get_user_id(x_user_id: str = Header(..., description="User ID from auth")) -> str:
    """Extract user ID from header"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID required")
    return x_user_id

async def get_service() -> HabitService:
    """Dependency to get habit service"""
    db = get_database()
    return get_habit_service(db)

@router.post("", response_model=HabitResponse, status_code=201)
async def create_habit(
    habit_data: HabitCreate,
    user_id: str = Depends(get_user_id),
    service: HabitService = Depends(get_service)
):
    """
    Create a new habit
    
    **Supported habit types**: food, exercise, financial, sleep, study, water
    """
    try:
        habit = await service.create_habit(user_id, habit_data)
        return HabitResponse(
            _id=str(habit.id),
            user_id=habit.user_id,
            habit_type=habit.habit_type,
            name=habit.name,
            description=habit.description,
            color=habit.color,
            icon=habit.icon,
            is_active=habit.is_active,
            current_streak=habit.current_streak,
            longest_streak=habit.longest_streak,
            total_logs=habit.total_logs,
            config=habit.config,
            ai_insights=habit.ai_insights,
            last_analyzed=habit.last_analyzed,
            created_at=habit.created_at,
            updated_at=habit.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create habit: {str(e)}")

@router.get("", response_model=List[HabitResponse])
async def get_habits(
    user_id: str = Depends(get_user_id),
    service: HabitService = Depends(get_service),
    habit_type: Optional[str] = Query(None, description="Filter by habit type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of items to return")
):
    """
    Get all habits for the authenticated user
    
    **Query Parameters:**
    - `habit_type`: Filter by type (food, exercise, financial, sleep, study, water)
    - `is_active`: Filter by active status
    - `skip`: Pagination offset
    - `limit`: Page size
    """
    try:
        habits = await service.get_user_habits(
            user_id=user_id,
            habit_type=habit_type,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
        
        return [
            HabitResponse(
                _id=str(habit.id),
                user_id=habit.user_id,
                habit_type=habit.habit_type,
                name=habit.name,
                description=habit.description,
                color=habit.color,
                icon=habit.icon,
                is_active=habit.is_active,
                current_streak=habit.current_streak,
                longest_streak=habit.longest_streak,
                total_logs=habit.total_logs,
                config=habit.config,
                ai_insights=habit.ai_insights,
                last_analyzed=habit.last_analyzed,
                created_at=habit.created_at,
                updated_at=habit.updated_at
            )
            for habit in habits
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch habits: {str(e)}")

@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: str,
    user_id: str = Depends(get_user_id),
    service: HabitService = Depends(get_service)
):
    """Get a specific habit by ID"""
    habit = await service.get_habit_by_id(user_id, habit_id)
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    return HabitResponse(
        _id=str(habit.id),
        user_id=habit.user_id,
        habit_type=habit.habit_type,
        name=habit.name,
        description=habit.description,
        color=habit.color,
        icon=habit.icon,
        is_active=habit.is_active,
        current_streak=habit.current_streak,
        longest_streak=habit.longest_streak,
        total_logs=habit.total_logs,
        config=habit.config,
        ai_insights=habit.ai_insights,
        last_analyzed=habit.last_analyzed,
        created_at=habit.created_at,
        updated_at=habit.updated_at
    )

@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: str,
    habit_update: HabitUpdate,
    user_id: str = Depends(get_user_id),
    service: HabitService = Depends(get_service)
):
    """Update a habit"""
    habit = await service.update_habit(user_id, habit_id, habit_update)
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    return HabitResponse(
        _id=str(habit.id),
        user_id=habit.user_id,
        habit_type=habit.habit_type,
        name=habit.name,
        description=habit.description,
        color=habit.color,
        icon=habit.icon,
        is_active=habit.is_active,
        current_streak=habit.current_streak,
        longest_streak=habit.longest_streak,
        total_logs=habit.total_logs,
        config=habit.config,
        ai_insights=habit.ai_insights,
        last_analyzed=habit.last_analyzed,
        created_at=habit.created_at,
        updated_at=habit.updated_at
    )

@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: str,
    user_id: str = Depends(get_user_id),
    service: HabitService = Depends(get_service)
):
    """Soft delete a habit (preserves data for AI training)"""
    success = await service.delete_habit(user_id, habit_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    return {"success": True, "message": "Habit deleted successfully"}

@router.get("/stats/overview")
async def get_habit_stats(
    user_id: str = Depends(get_user_id),
    service: HabitService = Depends(get_service)
):
    """Get habit statistics overview"""
    try:
        stats = await service.get_habit_stats(user_id)
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch stats: {str(e)}")

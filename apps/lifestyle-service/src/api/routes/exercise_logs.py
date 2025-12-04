"""
Exercise Log Routes
API endpoints for workout tracking and exercise logging
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header

from ...database.mongodb import get_database
from ...models.exercise_log import ExerciseLogCreate, ExerciseLogUpdate, ExerciseLogResponse
from ...services.exercise_log_service import ExerciseLogService, get_exercise_log_service


router = APIRouter(prefix="/api/exercise-logs", tags=["Exercise Logs"])


async def get_user_id(x_user_id: str = Header(..., description="User ID from auth")) -> str:
    """Extract user ID from header"""
    return x_user_id


async def get_service() -> ExerciseLogService:
    """Dependency to get exercise log service"""
    db = get_database()
    return get_exercise_log_service(db)


@router.post("", response_model=ExerciseLogResponse, status_code=201)
async def create_exercise_log(
    log_data: ExerciseLogCreate,
    user_id: str = Depends(get_user_id),
    service: ExerciseLogService = Depends(get_service)
):
    """
    Create a new exercise log entry
    
    **AI Training Fields**:
    - rpe: Rate of Perceived Exertion 1-10 (1=Very Easy, 10=Maximal Effort)
    - post_activity_energy: 1-10 (1=Exhausted, 10=Energized)
    - motivation_level: 1-10 (1=Forced, 10=Highly motivated)
    - soreness_level: 1-10 (1=None, 10=Severe)
    - sleep_quality_previous_night: 1-10
    - mood_before: anxious | stressed | neutral | energetic | happy
    - mood_after: tired | satisfied | energized | accomplished | frustrated
    - location: gym | home | outdoor | studio
    - workout_type: solo | group | trainer | virtual
    """
    try:
        log = await service.create_exercise_log(user_id, log_data.habit_id, log_data)
        return ExerciseLogResponse(
            _id=str(log.id),
            user_id=log.user_id,
            habit_id=log.habit_id,
            activity_type=log.activity_type,
            timestamp=log.timestamp,
            duration=log.duration,
            intensity=log.intensity,
            rpe=log.rpe,
            post_activity_energy=log.post_activity_energy,
            heart_rate_avg=log.heart_rate_avg,
            heart_rate_max=log.heart_rate_max,
            calories_burned=log.calories_burned,
            distance=log.distance,
            focus_areas=log.focus_areas,
            soreness_level=log.soreness_level,
            sleep_quality_previous_night=log.sleep_quality_previous_night,
            location=log.location,
            workout_type=log.workout_type,
            motivation_level=log.motivation_level,
            mood_before=log.mood_before,
            mood_after=log.mood_after,
            notes=log.notes,
            photos=log.photos,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[ExerciseLogResponse])
async def get_exercise_logs(
    habit_id: Optional[str] = None,
    activity_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
    user_id: str = Depends(get_user_id),
    service: ExerciseLogService = Depends(get_service)
):
    """
    Get exercise logs with optional filters
    
    **Query Parameters**:
    - habit_id: Filter by specific habit
    - activity_type: Filter by activity type
    - start_date: Filter logs from this date onwards
    - end_date: Filter logs up to this date
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (max 100)
    """
    if limit > 100:
        limit = 100
    
    logs = await service.get_exercise_logs(
        user_id=user_id,
        habit_id=habit_id,
        activity_type=activity_type,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return [
        ExerciseLogResponse(
            _id=str(log.id),
            user_id=log.user_id,
            habit_id=log.habit_id,
            activity_type=log.activity_type,
            timestamp=log.timestamp,
            duration=log.duration,
            intensity=log.intensity,
            rpe=log.rpe,
            post_activity_energy=log.post_activity_energy,
            heart_rate_avg=log.heart_rate_avg,
            heart_rate_max=log.heart_rate_max,
            calories_burned=log.calories_burned,
            distance=log.distance,
            focus_areas=log.focus_areas,
            soreness_level=log.soreness_level,
            sleep_quality_previous_night=log.sleep_quality_previous_night,
            location=log.location,
            workout_type=log.workout_type,
            motivation_level=log.motivation_level,
            mood_before=log.mood_before,
            mood_after=log.mood_after,
            notes=log.notes,
            photos=log.photos,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
        for log in logs
    ]


@router.get("/{log_id}", response_model=ExerciseLogResponse)
async def get_exercise_log(
    log_id: str,
    user_id: str = Depends(get_user_id),
    service: ExerciseLogService = Depends(get_service)
):
    """Get a specific exercise log by ID"""
    log = await service.get_exercise_log_by_id(user_id, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Exercise log not found")
    
    return ExerciseLogResponse(
        _id=str(log.id),
        user_id=log.user_id,
        habit_id=log.habit_id,
        activity_type=log.activity_type,
        timestamp=log.timestamp,
        duration=log.duration,
        intensity=log.intensity,
        rpe=log.rpe,
        post_activity_energy=log.post_activity_energy,
        heart_rate_avg=log.heart_rate_avg,
        heart_rate_max=log.heart_rate_max,
        calories_burned=log.calories_burned,
        distance=log.distance,
        focus_areas=log.focus_areas,
        soreness_level=log.soreness_level,
        sleep_quality_previous_night=log.sleep_quality_previous_night,
        location=log.location,
        workout_type=log.workout_type,
        motivation_level=log.motivation_level,
        mood_before=log.mood_before,
        mood_after=log.mood_after,
        notes=log.notes,
        photos=log.photos,
        created_at=log.created_at,
        updated_at=log.updated_at
    )


@router.put("/{log_id}", response_model=ExerciseLogResponse)
async def update_exercise_log(
    log_id: str,
    log_update: ExerciseLogUpdate,
    user_id: str = Depends(get_user_id),
    service: ExerciseLogService = Depends(get_service)
):
    """Update an exercise log"""
    log = await service.update_exercise_log(user_id, log_id, log_update)
    if not log:
        raise HTTPException(status_code=404, detail="Exercise log not found")
    
    return ExerciseLogResponse(
        _id=str(log.id),
        user_id=log.user_id,
        habit_id=log.habit_id,
        activity_type=log.activity_type,
        timestamp=log.timestamp,
        duration=log.duration,
        intensity=log.intensity,
        rpe=log.rpe,
        post_activity_energy=log.post_activity_energy,
        heart_rate_avg=log.heart_rate_avg,
        heart_rate_max=log.heart_rate_max,
        calories_burned=log.calories_burned,
        distance=log.distance,
        focus_areas=log.focus_areas,
        soreness_level=log.soreness_level,
        sleep_quality_previous_night=log.sleep_quality_previous_night,
        location=log.location,
        workout_type=log.workout_type,
        motivation_level=log.motivation_level,
        mood_before=log.mood_before,
        mood_after=log.mood_after,
        notes=log.notes,
        photos=log.photos,
        created_at=log.created_at,
        updated_at=log.updated_at
    )


@router.delete("/{log_id}")
async def delete_exercise_log(
    log_id: str,
    user_id: str = Depends(get_user_id),
    service: ExerciseLogService = Depends(get_service)
):
    """Soft delete an exercise log"""
    success = await service.delete_exercise_log(user_id, log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Exercise log not found")
    
    return {"success": True, "message": "Exercise log deleted successfully"}


@router.get("/stats/overview")
async def get_exercise_log_stats(
    habit_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: str = Depends(get_user_id),
    service: ExerciseLogService = Depends(get_service)
):
    """
    Get exercise logging statistics
    
    Returns aggregated data including:
    - Total logs, duration, calories, distance
    - Average RPE, post-activity energy, motivation
    - Activity type distribution
    - Location and workout type patterns
    - Mood changes (before/after)
    """
    stats = await service.get_exercise_log_stats(
        user_id=user_id,
        habit_id=habit_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {"success": True, "data": stats}

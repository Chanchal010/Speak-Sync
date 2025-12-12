"""
Sleep Log Routes
API endpoints for sleep tracking, chronotype detection, and sleep debt monitoring
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header

from ...database.mongodb import get_database
from ...models.sleep_log import SleepLogCreate, SleepLogUpdate, SleepLogResponse
from ...services.sleep_log_service import SleepLogService, get_sleep_log_service


router = APIRouter(prefix="/api/sleep-logs", tags=["Sleep Logs"])


async def get_user_id(x_user_id: str = Header(..., description="User ID from auth")) -> str:
    """Extract user ID from header"""
    return x_user_id


async def get_service() -> SleepLogService:
    """Dependency to get sleep log service"""
    db = get_database()
    return get_sleep_log_service(db)


@router.post("", response_model=SleepLogResponse, status_code=201)
async def create_sleep_log(
    log_data: SleepLogCreate,
    user_id: str = Depends(get_user_id),
    service: SleepLogService = Depends(get_service)
):
    """
    Create a new sleep log entry
    
    **AI Training Fields**:
    - sleep_quality: 1-10 overall quality
    - grogginess_level: 1=Alert, 10=Zombie (morning alertness)
    - sleep_latency: Minutes to fall asleep (insomnia indicator)
    - felt_rested: Boolean for actual restfulness
    - sleep_debt: Calculated from target_sleep_hours vs actual
    - chronotype detection: Bedtime/wake_time patterns
    - pre_sleep_activity: reading | tv | phone | exercise | meditation | work
    - screen_time_before_bed: Minutes (blue light impact)
    - caffeine_intake: Hours since last caffeine
    - stress_level: 1-10 (correlation with sleep quality)
    """
    try:
        log = await service.create_sleep_log(user_id, log_data.habit_id, log_data)
        return SleepLogResponse(
            id=str(log.id),
            user_id=log.user_id,
            habit_id=log.habit_id,
            bedtime=log.bedtime,
            wake_time=log.wake_time,
            sleep_duration=log.sleep_duration,
            sleep_quality=log.sleep_quality,
            sleep_latency=log.sleep_latency,
            times_awakened=log.times_awakened,
            grogginess_level=log.grogginess_level,
            natural_wake_time=log.natural_wake_time,
            used_alarm=log.used_alarm,
            felt_rested=log.felt_rested,
            target_sleep_hours=log.target_sleep_hours,
            sleep_debt=log.sleep_debt,
            pre_sleep_activity=log.pre_sleep_activity,
            screen_time_before_bed=log.screen_time_before_bed,
            caffeine_intake=log.caffeine_intake,
            alcohol_intake=log.alcohol_intake,
            exercise_today=log.exercise_today,
            stress_level=log.stress_level,
            room_temperature=log.room_temperature,
            noise_level=log.noise_level,
            had_dreams=log.had_dreams,
            dream_type=log.dream_type,
            mood_on_waking=log.mood_on_waking,
            notes=log.notes,
            timestamp=log.timestamp,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[SleepLogResponse])
async def get_sleep_logs(
    habit_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
    user_id: str = Depends(get_user_id),
    service: SleepLogService = Depends(get_service)
):
    """
    Get sleep logs with optional filters
    
    **Query Parameters**:
    - habit_id: Filter by specific habit
    - start_date: Filter logs from this date onwards
    - end_date: Filter logs up to this date
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (max 100)
    """
    if limit > 100:
        limit = 100
    
    logs = await service.get_sleep_logs(
        user_id=user_id,
        habit_id=habit_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return [
        SleepLogResponse(
            id=str(log.id),
            user_id=log.user_id,
            habit_id=log.habit_id,
            bedtime=log.bedtime,
            wake_time=log.wake_time,
            sleep_duration=log.sleep_duration,
            sleep_quality=log.sleep_quality,
            sleep_latency=log.sleep_latency,
            times_awakened=log.times_awakened,
            grogginess_level=log.grogginess_level,
            natural_wake_time=log.natural_wake_time,
            used_alarm=log.used_alarm,
            felt_rested=log.felt_rested,
            target_sleep_hours=log.target_sleep_hours,
            sleep_debt=log.sleep_debt,
            pre_sleep_activity=log.pre_sleep_activity,
            screen_time_before_bed=log.screen_time_before_bed,
            caffeine_intake=log.caffeine_intake,
            alcohol_intake=log.alcohol_intake,
            exercise_today=log.exercise_today,
            stress_level=log.stress_level,
            room_temperature=log.room_temperature,
            noise_level=log.noise_level,
            had_dreams=log.had_dreams,
            dream_type=log.dream_type,
            mood_on_waking=log.mood_on_waking,
            notes=log.notes,
            timestamp=log.timestamp,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
        for log in logs
    ]


@router.get("/{log_id}", response_model=SleepLogResponse)
async def get_sleep_log(
    log_id: str,
    user_id: str = Depends(get_user_id),
    service: SleepLogService = Depends(get_service)
):
    """Get a specific sleep log by ID"""
    log = await service.get_sleep_log_by_id(user_id, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    
    return SleepLogResponse(
        id=str(log.id),
        user_id=log.user_id,
        habit_id=log.habit_id,
        bedtime=log.bedtime,
        wake_time=log.wake_time,
        sleep_duration=log.sleep_duration,
        sleep_quality=log.sleep_quality,
        sleep_latency=log.sleep_latency,
        times_awakened=log.times_awakened,
        grogginess_level=log.grogginess_level,
        natural_wake_time=log.natural_wake_time,
        used_alarm=log.used_alarm,
        felt_rested=log.felt_rested,
        target_sleep_hours=log.target_sleep_hours,
        sleep_debt=log.sleep_debt,
        pre_sleep_activity=log.pre_sleep_activity,
        screen_time_before_bed=log.screen_time_before_bed,
        caffeine_intake=log.caffeine_intake,
        alcohol_intake=log.alcohol_intake,
        exercise_today=log.exercise_today,
        stress_level=log.stress_level,
        room_temperature=log.room_temperature,
        noise_level=log.noise_level,
        had_dreams=log.had_dreams,
        dream_type=log.dream_type,
        mood_on_waking=log.mood_on_waking,
        notes=log.notes,
        timestamp=log.timestamp,
        created_at=log.created_at,
        updated_at=log.updated_at
    )


@router.put("/{log_id}", response_model=SleepLogResponse)
async def update_sleep_log(
    log_id: str,
    update_data: SleepLogUpdate,
    user_id: str = Depends(get_user_id),
    service: SleepLogService = Depends(get_service)
):
    """Update a sleep log"""
    log = await service.update_sleep_log(user_id, log_id, update_data)
    if not log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    
    return SleepLogResponse(
        id=str(log.id),
        user_id=log.user_id,
        habit_id=log.habit_id,
        bedtime=log.bedtime,
        wake_time=log.wake_time,
        sleep_duration=log.sleep_duration,
        sleep_quality=log.sleep_quality,
        sleep_latency=log.sleep_latency,
        times_awakened=log.times_awakened,
        grogginess_level=log.grogginess_level,
        natural_wake_time=log.natural_wake_time,
        used_alarm=log.used_alarm,
        felt_rested=log.felt_rested,
        target_sleep_hours=log.target_sleep_hours,
        sleep_debt=log.sleep_debt,
        pre_sleep_activity=log.pre_sleep_activity,
        screen_time_before_bed=log.screen_time_before_bed,
        caffeine_intake=log.caffeine_intake,
        alcohol_intake=log.alcohol_intake,
        exercise_today=log.exercise_today,
        stress_level=log.stress_level,
        room_temperature=log.room_temperature,
        noise_level=log.noise_level,
        had_dreams=log.had_dreams,
        dream_type=log.dream_type,
        mood_on_waking=log.mood_on_waking,
        notes=log.notes,
        timestamp=log.timestamp,
        created_at=log.created_at,
        updated_at=log.updated_at
    )


@router.delete("/{log_id}", status_code=204)
async def delete_sleep_log(
    log_id: str,
    user_id: str = Depends(get_user_id),
    service: SleepLogService = Depends(get_service)
):
    """Soft delete a sleep log"""
    deleted = await service.delete_sleep_log(user_id, log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    return None


@router.get("/stats/overview", response_model=dict)
async def get_sleep_stats(
    habit_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: str = Depends(get_user_id),
    service: SleepLogService = Depends(get_service)
):
    """
    Get sleep statistics with chronotype detection
    
    **Returns**:
    - avg_sleep_duration: Average hours slept
    - avg_sleep_quality: Average quality score
    - avg_grogginess: Morning alertness level
    - total_sleep_debt: Accumulated debt
    - rested_percentage: % of nights felt rested
    - alarm_usage_percentage: % of mornings used alarm
    - avg_bedtime_hour: Average bedtime (chronotype)
    - avg_wake_time_hour: Average wake time (chronotype)
    - chronotype_hint: early_bird | night_owl | intermediate
    - pre_sleep_activity_distribution: Activity patterns
    - mood_distribution: Waking mood patterns
    """
    stats = await service.get_sleep_log_stats(
        user_id=user_id,
        habit_id=habit_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "success": True,
        "data": stats
    }

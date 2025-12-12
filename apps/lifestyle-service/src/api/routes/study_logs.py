"""
Study Log API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from typing import Optional, List
from datetime import datetime

from ...database.mongodb import get_database
from ...models.study_log import StudyLogCreate, StudyLogUpdate, StudyLogResponse
from ...services.study_log_service import StudyLogService

router = APIRouter(prefix="/api/study-logs", tags=["study-logs"])


async def get_user_id(x_user_id: str = Header(..., description="User ID from auth")) -> str:
    """Extract user ID from header"""
    return x_user_id


async def get_service() -> StudyLogService:
    """Dependency to get study log service"""
    db = get_database()
    return StudyLogService(db)


@router.post("", response_model=StudyLogResponse)
async def create_study_log(
    log_data: StudyLogCreate,
    user_id: str = Depends(get_user_id),
    service: StudyLogService = Depends(get_service)
):
    """
    Create a new study log with stickiness factor tracking
    
    **Stickiness Factor**: Measures adherence to scheduled study times
    - deviation_duration: Auto-calculated from scheduled vs actual times
    - High stickiness = starting/ending close to planned times
    - Low stickiness = significant procrastination or overrun
    
    **AI Learning Fields**:
    - flow_state_score (1-10): Deep focus vs distraction
    - interruption_count: External disruptions during session
    - distraction_sources: phone, social_media, notifications, people, thoughts
    - energy_level_start/end: Track energy depletion patterns
    - mental_clarity: Correlate with sleep quality, caffeine, meal timing
    - task_completed: Integration with Phase 2 scheduler-service
    - study_method: reading, practice_problems, video_lectures, flashcards
    - location: library, home, cafe - find optimal study environment
    - used_music: Background music impact on focus
    - caffeine_before_study: Caffeine's effect on flow state
    - sleep_quality_last_night: Previous night's sleep impact on retention
    - retention_confidence: Self-assessment of learning effectiveness
    """
    try:
        log = await service.create_study_log(user_id, log_data)
        return StudyLogResponse(
            id=str(log.id),
            user_id=log.user_id,
            habit_id=log.habit_id,
            scheduled_start=log.scheduled_start,
            scheduled_end=log.scheduled_end,
            actual_start=log.actual_start,
            actual_end=log.actual_end,
            deviation_duration=log.deviation_duration,
            task_id=log.task_id,
            task_completed=log.task_completed,
            completion_quality=log.completion_quality,
            flow_state_score=log.flow_state_score,
            interruption_count=log.interruption_count,
            distraction_sources=log.distraction_sources,
            energy_level_start=log.energy_level_start,
            energy_level_end=log.energy_level_end,
            mental_clarity=log.mental_clarity,
            motivation_level=log.motivation_level,
            subject=log.subject,
            study_method=log.study_method,
            break_count=log.break_count,
            break_duration=log.break_duration,
            location=log.location,
            noise_level=log.noise_level,
            used_music=log.used_music,
            music_type=log.music_type,
            caffeine_before_study=log.caffeine_before_study,
            meal_timing=log.meal_timing,
            sleep_quality_last_night=log.sleep_quality_last_night,
            stress_level=log.stress_level,
            retention_confidence=log.retention_confidence,
            satisfaction_level=log.satisfaction_level,
            would_repeat_conditions=log.would_repeat_conditions,
            notes=log.notes,
            timestamp=log.timestamp,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[StudyLogResponse])
async def get_study_logs(
    habit_id: Optional[str] = Query(None, description="Filter by habit ID"),
    task_id: Optional[str] = Query(None, description="Filter by task ID from scheduler-service"),
    start_date: Optional[datetime] = Query(None, description="Filter by actual start date (>=)"),
    end_date: Optional[datetime] = Query(None, description="Filter by actual start date (<=)"),
    skip: int = Query(0, ge=0, description="Number of logs to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of logs to return"),
    user_id: str = Depends(get_user_id),
    service: StudyLogService = Depends(get_service)
):
    """Get study logs with optional filters"""
    logs = await service.get_study_logs(
        user_id=user_id,
        habit_id=habit_id,
        task_id=task_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return [
        StudyLogResponse(
            id=str(log.id),
            user_id=log.user_id,
            habit_id=log.habit_id,
            scheduled_start=log.scheduled_start,
            scheduled_end=log.scheduled_end,
            actual_start=log.actual_start,
            actual_end=log.actual_end,
            deviation_duration=log.deviation_duration,
            task_id=log.task_id,
            task_completed=log.task_completed,
            completion_quality=log.completion_quality,
            flow_state_score=log.flow_state_score,
            interruption_count=log.interruption_count,
            distraction_sources=log.distraction_sources,
            energy_level_start=log.energy_level_start,
            energy_level_end=log.energy_level_end,
            mental_clarity=log.mental_clarity,
            motivation_level=log.motivation_level,
            subject=log.subject,
            study_method=log.study_method,
            break_count=log.break_count,
            break_duration=log.break_duration,
            location=log.location,
            noise_level=log.noise_level,
            used_music=log.used_music,
            music_type=log.music_type,
            caffeine_before_study=log.caffeine_before_study,
            meal_timing=log.meal_timing,
            sleep_quality_last_night=log.sleep_quality_last_night,
            stress_level=log.stress_level,
            retention_confidence=log.retention_confidence,
            satisfaction_level=log.satisfaction_level,
            would_repeat_conditions=log.would_repeat_conditions,
            notes=log.notes,
            timestamp=log.timestamp,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
        for log in logs
    ]


@router.get("/{log_id}", response_model=StudyLogResponse)
async def get_study_log(
    log_id: str,
    user_id: str = Depends(get_user_id),
    service: StudyLogService = Depends(get_service)
):
    """Get a specific study log by ID"""
    log = await service.get_study_log_by_id(user_id, log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Study log not found")
    
    return StudyLogResponse(
        id=str(log.id),
        user_id=log.user_id,
        habit_id=log.habit_id,
        scheduled_start=log.scheduled_start,
        scheduled_end=log.scheduled_end,
        actual_start=log.actual_start,
        actual_end=log.actual_end,
        deviation_duration=log.deviation_duration,
        task_id=log.task_id,
        task_completed=log.task_completed,
        completion_quality=log.completion_quality,
        flow_state_score=log.flow_state_score,
        interruption_count=log.interruption_count,
        distraction_sources=log.distraction_sources,
        energy_level_start=log.energy_level_start,
        energy_level_end=log.energy_level_end,
        mental_clarity=log.mental_clarity,
        motivation_level=log.motivation_level,
        subject=log.subject,
        study_method=log.study_method,
        break_count=log.break_count,
        break_duration=log.break_duration,
        location=log.location,
        noise_level=log.noise_level,
        used_music=log.used_music,
        music_type=log.music_type,
        caffeine_before_study=log.caffeine_before_study,
        meal_timing=log.meal_timing,
        sleep_quality_last_night=log.sleep_quality_last_night,
        stress_level=log.stress_level,
        retention_confidence=log.retention_confidence,
        satisfaction_level=log.satisfaction_level,
        would_repeat_conditions=log.would_repeat_conditions,
        notes=log.notes,
        timestamp=log.timestamp,
        created_at=log.created_at,
        updated_at=log.updated_at
    )


@router.put("/{log_id}", response_model=StudyLogResponse)
async def update_study_log(
    log_id: str,
    update_data: StudyLogUpdate,
    user_id: str = Depends(get_user_id),
    service: StudyLogService = Depends(get_service)
):
    """Update a study log (recalculates deviation if times changed)"""
    log = await service.update_study_log(user_id, log_id, update_data)
    
    if not log:
        raise HTTPException(status_code=404, detail="Study log not found")
    
    return StudyLogResponse(
        id=str(log.id),
        user_id=log.user_id,
        habit_id=log.habit_id,
        scheduled_start=log.scheduled_start,
        scheduled_end=log.scheduled_end,
        actual_start=log.actual_start,
        actual_end=log.actual_end,
        deviation_duration=log.deviation_duration,
        task_id=log.task_id,
        task_completed=log.task_completed,
        completion_quality=log.completion_quality,
        flow_state_score=log.flow_state_score,
        interruption_count=log.interruption_count,
        distraction_sources=log.distraction_sources,
        energy_level_start=log.energy_level_start,
        energy_level_end=log.energy_level_end,
        mental_clarity=log.mental_clarity,
        motivation_level=log.motivation_level,
        subject=log.subject,
        study_method=log.study_method,
        break_count=log.break_count,
        break_duration=log.break_duration,
        location=log.location,
        noise_level=log.noise_level,
        used_music=log.used_music,
        music_type=log.music_type,
        caffeine_before_study=log.caffeine_before_study,
        meal_timing=log.meal_timing,
        sleep_quality_last_night=log.sleep_quality_last_night,
        stress_level=log.stress_level,
        retention_confidence=log.retention_confidence,
        satisfaction_level=log.satisfaction_level,
        would_repeat_conditions=log.would_repeat_conditions,
        notes=log.notes,
        timestamp=log.timestamp,
        created_at=log.created_at,
        updated_at=log.updated_at
    )


@router.delete("/{log_id}")
async def delete_study_log(
    log_id: str,
    user_id: str = Depends(get_user_id),
    service: StudyLogService = Depends(get_service)
):
    """Soft delete a study log"""
    success = await service.delete_study_log(user_id, log_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Study log not found")
    
    return {"message": "Study log deleted successfully"}


@router.get("/stats/overview")
async def get_study_stats(
    habit_id: Optional[str] = Query(None, description="Filter by habit ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by date (>=)"),
    end_date: Optional[datetime] = Query(None, description="Filter by date (<=)"),
    user_id: str = Depends(get_user_id),
    service: StudyLogService = Depends(get_service)
):
    """
    Get study log statistics with stickiness metrics
    
    Returns:
    - total_logs: Number of study sessions
    - total_study_time: Total minutes spent studying
    - avg_study_duration: Average session length
    - avg_deviation: Average minutes deviated from schedule
    - avg_stickiness_percentage: 100% = perfect adherence, 0% = completely off schedule
    - avg_flow_state: Average focus level (1-10)
    - avg_interruptions: Average interruptions per session
    - task_completion_rate: Percentage of linked tasks completed
    - high_flow_sessions: Sessions with flow_state >= 8
    - low_flow_sessions: Sessions with flow_state <= 3
    - distraction_distribution: Most common distractions
    - study_method_distribution: Most effective study methods
    - location_distribution: Best study locations
    """
    stats = await service.get_study_log_stats(
        user_id=user_id,
        habit_id=habit_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {"success": True, "data": stats}

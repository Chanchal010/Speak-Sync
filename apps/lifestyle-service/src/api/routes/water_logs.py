"""
Water Log API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from typing import Optional, List
from datetime import datetime

from ...database.mongodb import get_database
from ...models.water_log import WaterLogCreate, WaterLogUpdate, WaterLogResponse
from ...services.water_log_service import WaterLogService

router = APIRouter(prefix="/api/water-logs", tags=["water-logs"])


async def get_user_id(x_user_id: str = Header(..., description="User ID from auth")) -> str:
    """Extract user ID from header"""
    return x_user_id


async def get_service() -> WaterLogService:
    """Dependency to get water log service"""
    db = get_database()
    return WaterLogService(db)


@router.post("", response_model=WaterLogResponse)
async def create_water_log(
    log_data: WaterLogCreate,
    user_id: str = Depends(get_user_id),
    service: WaterLogService = Depends(get_service)
):
    """
    Create a new water intake log with cognitive fog detection
    
    **Armstrong Scale (Urine Color Hydration Chart)**:
    - 1-3: Optimal hydration (pale yellow to light yellow)
    - 4: Adequate hydration (yellow)
    - 5-6: Mild dehydration (dark yellow to amber)
    - 7: Moderate dehydration (orange)
    - 8: Severe dehydration (brown) - seek medical attention
    
    **AI Learning Fields**:
    - cognitive_fog: Mental fog, difficulty concentrating (key indicator of dehydration)
    - thirst_intensity (1-10): Body's natural hydration signal
    - urine_color (Armstrong Scale): Objective hydration measurement
    - headache_present: Common dehydration symptom
    - energy_level: Hydration's impact on energy
    - mental_clarity: Cognitive performance correlation with hydration
    - caffeine_intake: Diuretic effect increases fluid loss
    - alcohol_intake: Diuretic effect, accelerates dehydration
    - activity_level: Exercise increases hydration needs
    - sweat_level: Fluid loss through perspiration
    - temperature/humidity: Environmental factors affecting hydration
    - body_weight: For calculating personalized daily hydration goals (30-35ml/kg)
    """
    try:
        log = await service.create_water_log(user_id, log_data)
        return WaterLogResponse(
            id=str(log.id),
            user_id=log.user_id,
            habit_id=log.habit_id,
            intake_volume=log.intake_volume,
            intake_source=log.intake_source,
            urine_color=log.urine_color,
            thirst_intensity=log.thirst_intensity,
            cognitive_fog=log.cognitive_fog,
            headache_present=log.headache_present,
            dry_mouth=log.dry_mouth,
            fatigue_level=log.fatigue_level,
            dizziness=log.dizziness,
            energy_level=log.energy_level,
            physical_performance=log.physical_performance,
            mental_clarity=log.mental_clarity,
            caffeine_intake=log.caffeine_intake,
            alcohol_intake=log.alcohol_intake,
            activity_level=log.activity_level,
            exercise_duration=log.exercise_duration,
            sweat_level=log.sweat_level,
            temperature=log.temperature,
            humidity=log.humidity,
            altitude=log.altitude,
            body_weight=log.body_weight,
            time_since_last_intake=log.time_since_last_intake,
            notes=log.notes,
            timestamp=log.timestamp,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[WaterLogResponse])
async def get_water_logs(
    habit_id: Optional[str] = Query(None, description="Filter by habit ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by date (>=)"),
    end_date: Optional[datetime] = Query(None, description="Filter by date (<=)"),
    skip: int = Query(0, ge=0, description="Number of logs to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of logs to return"),
    user_id: str = Depends(get_user_id),
    service: WaterLogService = Depends(get_service)
):
    """Get water logs with optional filters"""
    logs = await service.get_water_logs(
        user_id=user_id,
        habit_id=habit_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return [
        WaterLogResponse(
            id=str(log.id),
            user_id=log.user_id,
            habit_id=log.habit_id,
            intake_volume=log.intake_volume,
            intake_source=log.intake_source,
            urine_color=log.urine_color,
            thirst_intensity=log.thirst_intensity,
            cognitive_fog=log.cognitive_fog,
            headache_present=log.headache_present,
            dry_mouth=log.dry_mouth,
            fatigue_level=log.fatigue_level,
            dizziness=log.dizziness,
            energy_level=log.energy_level,
            physical_performance=log.physical_performance,
            mental_clarity=log.mental_clarity,
            caffeine_intake=log.caffeine_intake,
            alcohol_intake=log.alcohol_intake,
            activity_level=log.activity_level,
            exercise_duration=log.exercise_duration,
            sweat_level=log.sweat_level,
            temperature=log.temperature,
            humidity=log.humidity,
            altitude=log.altitude,
            body_weight=log.body_weight,
            time_since_last_intake=log.time_since_last_intake,
            notes=log.notes,
            timestamp=log.timestamp,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
        for log in logs
    ]


@router.get("/{log_id}", response_model=WaterLogResponse)
async def get_water_log(
    log_id: str,
    user_id: str = Depends(get_user_id),
    service: WaterLogService = Depends(get_service)
):
    """Get a specific water log by ID"""
    log = await service.get_water_log_by_id(user_id, log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Water log not found")
    
    return WaterLogResponse(
        id=str(log.id),
        user_id=log.user_id,
        habit_id=log.habit_id,
        intake_volume=log.intake_volume,
        intake_source=log.intake_source,
        urine_color=log.urine_color,
        thirst_intensity=log.thirst_intensity,
        cognitive_fog=log.cognitive_fog,
        headache_present=log.headache_present,
        dry_mouth=log.dry_mouth,
        fatigue_level=log.fatigue_level,
        dizziness=log.dizziness,
        energy_level=log.energy_level,
        physical_performance=log.physical_performance,
        mental_clarity=log.mental_clarity,
        caffeine_intake=log.caffeine_intake,
        alcohol_intake=log.alcohol_intake,
        activity_level=log.activity_level,
        exercise_duration=log.exercise_duration,
        sweat_level=log.sweat_level,
        temperature=log.temperature,
        humidity=log.humidity,
        altitude=log.altitude,
        body_weight=log.body_weight,
        time_since_last_intake=log.time_since_last_intake,
        notes=log.notes,
        timestamp=log.timestamp,
        created_at=log.created_at,
        updated_at=log.updated_at
    )


@router.put("/{log_id}", response_model=WaterLogResponse)
async def update_water_log(
    log_id: str,
    update_data: WaterLogUpdate,
    user_id: str = Depends(get_user_id),
    service: WaterLogService = Depends(get_service)
):
    """Update a water log"""
    log = await service.update_water_log(user_id, log_id, update_data)
    
    if not log:
        raise HTTPException(status_code=404, detail="Water log not found")
    
    return WaterLogResponse(
        id=str(log.id),
        user_id=log.user_id,
        habit_id=log.habit_id,
        intake_volume=log.intake_volume,
        intake_source=log.intake_source,
        urine_color=log.urine_color,
        thirst_intensity=log.thirst_intensity,
        cognitive_fog=log.cognitive_fog,
        headache_present=log.headache_present,
        dry_mouth=log.dry_mouth,
        fatigue_level=log.fatigue_level,
        dizziness=log.dizziness,
        energy_level=log.energy_level,
        physical_performance=log.physical_performance,
        mental_clarity=log.mental_clarity,
        caffeine_intake=log.caffeine_intake,
        alcohol_intake=log.alcohol_intake,
        activity_level=log.activity_level,
        exercise_duration=log.exercise_duration,
        sweat_level=log.sweat_level,
        temperature=log.temperature,
        humidity=log.humidity,
        altitude=log.altitude,
        body_weight=log.body_weight,
        time_since_last_intake=log.time_since_last_intake,
        notes=log.notes,
        timestamp=log.timestamp,
        created_at=log.created_at,
        updated_at=log.updated_at
    )


@router.delete("/{log_id}")
async def delete_water_log(
    log_id: str,
    user_id: str = Depends(get_user_id),
    service: WaterLogService = Depends(get_service)
):
    """Soft delete a water log"""
    success = await service.delete_water_log(user_id, log_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Water log not found")
    
    return {"message": "Water log deleted successfully"}


@router.get("/stats/overview")
async def get_water_stats(
    habit_id: Optional[str] = Query(None, description="Filter by habit ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by date (>=)"),
    end_date: Optional[datetime] = Query(None, description="Filter by date (<=)"),
    user_id: str = Depends(get_user_id),
    service: WaterLogService = Depends(get_service)
):
    """
    Get water intake statistics with hydration analysis
    
    Returns:
    - total_logs: Number of water intake entries
    - total_intake: Total milliliters consumed
    - avg_intake_per_log: Average intake per entry
    - avg_daily_intake: Average daily consumption
    - days_tracked: Number of unique days logged
    - avg_urine_color: Average Armstrong Scale reading
    - hydration_status_hint: Overall hydration status (optimal/adequate/mild_dehydration/moderate/severe)
    - hydration_status_distribution: Breakdown of hydration levels
    - cognitive_fog_instances: Times experiencing mental fog
    - cognitive_fog_percentage: % of logs with cognitive fog
    - headache_instances: Dehydration headaches reported
    - avg_energy_level: Average energy (1-10)
    - avg_mental_clarity: Average mental clarity (1-10)
    - intake_source_distribution: Water sources (water, juice, tea, etc.)
    - activity_level_distribution: Hydration during different activity levels
    """
    stats = await service.get_water_log_stats(
        user_id=user_id,
        habit_id=habit_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {"success": True, "data": stats}

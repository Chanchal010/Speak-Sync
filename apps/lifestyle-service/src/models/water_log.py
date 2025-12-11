"""
Water Log model for MongoDB with cognitive fog detection
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class WaterLogBase(BaseModel):
    """Base water log fields with hydration tracking"""
    habit_id: str = Field(..., description="Reference to habit")
    
    # Hydration intake
    intake_volume: int = Field(..., ge=0, description="Water intake in milliliters (ml)")
    intake_source: Optional[str] = Field(None, description="water, juice, tea, coffee, smoothie, soup, fruits")
    
    # Armstrong Scale (urine color hydration indicator)
    urine_color: Optional[int] = Field(None, ge=1, le=8, description="Armstrong Scale: 1-3=Optimal, 4-6=Dehydrated, 7-8=Severely Dehydrated")
    
    # Dehydration symptoms
    thirst_intensity: Optional[int] = Field(None, ge=1, le=10, description="1=Not thirsty, 10=Extremely thirsty")
    cognitive_fog: Optional[bool] = Field(None, description="Experiencing mental fog, difficulty concentrating")
    headache_present: Optional[bool] = Field(None, description="Dehydration-related headache")
    dry_mouth: Optional[bool] = Field(None, description="Mouth feels dry")
    fatigue_level: Optional[int] = Field(None, ge=1, le=10, description="1=Energized, 10=Exhausted")
    dizziness: Optional[bool] = Field(None, description="Feeling dizzy or lightheaded")
    
    # Energy and performance
    energy_level: Optional[int] = Field(None, ge=1, le=10, description="1=Sluggish, 10=Highly energetic")
    physical_performance: Optional[int] = Field(None, ge=1, le=10, description="Physical capability (for athletes)")
    mental_clarity: Optional[int] = Field(None, ge=1, le=10, description="1=Foggy, 10=Sharp")
    
    # Diuretic factors (increase urination)
    caffeine_intake: Optional[int] = Field(None, ge=0, description="Caffeine consumed in mg (coffee ~95mg, tea ~47mg)")
    alcohol_intake: Optional[bool] = Field(None, description="Consumed alcohol (diuretic effect)")
    
    # Activity level (affects hydration needs)
    activity_level: Optional[str] = Field(None, description="sedentary, light_activity, moderate_exercise, intense_exercise")
    exercise_duration: Optional[int] = Field(None, ge=0, description="Minutes of exercise")
    sweat_level: Optional[str] = Field(None, description="none, light, moderate, heavy")
    
    # Environment (affects hydration needs)
    temperature: Optional[str] = Field(None, description="cold, cool, comfortable, warm, hot")
    humidity: Optional[str] = Field(None, description="dry, normal, humid")
    altitude: Optional[str] = Field(None, description="sea_level, moderate_altitude, high_altitude")
    
    # Body measurements
    body_weight: Optional[float] = Field(None, ge=0, description="Weight in kg (for calculating hydration needs)")
    
    # Time tracking
    time_since_last_intake: Optional[int] = Field(None, ge=0, description="Minutes since last water intake")
    
    notes: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "habit_id": "507f1f77bcf86cd799439011",
                "intake_volume": 500,
                "intake_source": "water",
                "urine_color": 3,
                "thirst_intensity": 4,
                "cognitive_fog": False,
                "energy_level": 8,
                "mental_clarity": 8,
                "caffeine_intake": 95,
                "activity_level": "moderate_exercise"
            }
        }

class WaterLogCreate(WaterLogBase):
    """Water log creation model"""
    pass

class WaterLogUpdate(BaseModel):
    """Water log update model - all fields optional"""
    intake_volume: Optional[int] = Field(None, ge=0)
    intake_source: Optional[str] = None
    urine_color: Optional[int] = Field(None, ge=1, le=8)
    thirst_intensity: Optional[int] = Field(None, ge=1, le=10)
    cognitive_fog: Optional[bool] = None
    headache_present: Optional[bool] = None
    dry_mouth: Optional[bool] = None
    fatigue_level: Optional[int] = Field(None, ge=1, le=10)
    dizziness: Optional[bool] = None
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    physical_performance: Optional[int] = Field(None, ge=1, le=10)
    mental_clarity: Optional[int] = Field(None, ge=1, le=10)
    caffeine_intake: Optional[int] = Field(None, ge=0)
    alcohol_intake: Optional[bool] = None
    activity_level: Optional[str] = None
    exercise_duration: Optional[int] = Field(None, ge=0)
    sweat_level: Optional[str] = None
    temperature: Optional[str] = None
    humidity: Optional[str] = None
    altitude: Optional[str] = None
    body_weight: Optional[float] = Field(None, ge=0)
    time_since_last_intake: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)

class WaterLogInDB(WaterLogBase):
    """Water log as stored in database"""
    id: ObjectId = Field(alias="_id")
    user_id: str
    timestamp: datetime
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True

class WaterLogResponse(BaseModel):
    """Water log response model"""
    id: str
    user_id: str
    habit_id: str
    intake_volume: int
    intake_source: Optional[str]
    urine_color: Optional[int]
    thirst_intensity: Optional[int]
    cognitive_fog: Optional[bool]
    headache_present: Optional[bool]
    dry_mouth: Optional[bool]
    fatigue_level: Optional[int]
    dizziness: Optional[bool]
    energy_level: Optional[int]
    physical_performance: Optional[int]
    mental_clarity: Optional[int]
    caffeine_intake: Optional[int]
    alcohol_intake: Optional[bool]
    activity_level: Optional[str]
    exercise_duration: Optional[int]
    sweat_level: Optional[str]
    temperature: Optional[str]
    humidity: Optional[str]
    altitude: Optional[str]
    body_weight: Optional[float]
    time_since_last_intake: Optional[int]
    notes: Optional[str]
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "user123",
                "habit_id": "507f1f77bcf86cd799439012",
                "intake_volume": 500,
                "urine_color": 3,
                "cognitive_fog": False,
                "energy_level": 8
            }
        }

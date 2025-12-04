"""
Exercise Log Models
Tracks workout sessions with RPE and recovery data for AI analysis
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

from .habit import PyObjectId


class ExerciseLogBase(BaseModel):
    """Base exercise log fields"""
    habit_id: str = Field(..., description="Reference to the exercise habit")
    activity_type: str = Field(..., description="Type of exercise performed")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Core workout data
    duration: int = Field(..., ge=1, description="Duration in minutes")
    intensity: Optional[str] = Field(None, description="low | moderate | high | very_high")
    
    # AI Training Fields - RPE & Recovery
    rpe: int = Field(..., ge=1, le=10, description="Rate of Perceived Exertion: 1=Very Easy, 10=Maximal Effort")
    post_activity_energy: int = Field(..., ge=1, le=10, description="Energy level after workout: 1=Exhausted, 10=Energized")
    
    # Physical metrics
    heart_rate_avg: Optional[int] = Field(None, ge=40, le=220, description="Average heart rate (bpm)")
    heart_rate_max: Optional[int] = Field(None, ge=40, le=220, description="Maximum heart rate (bpm)")
    calories_burned: Optional[int] = Field(None, ge=0)
    distance: Optional[float] = Field(None, ge=0, description="Distance in kilometers")
    
    # Body focus & recovery
    focus_areas: List[str] = Field(default_factory=list, description="Body parts targeted")
    soreness_level: Optional[int] = Field(None, ge=1, le=10, description="Muscle soreness: 1=None, 10=Severe")
    sleep_quality_previous_night: Optional[int] = Field(None, ge=1, le=10, description="Sleep quality before workout")
    
    # Environmental & psychological
    location: Optional[str] = Field(None, description="gym | home | outdoor | studio")
    workout_type: Optional[str] = Field(None, description="solo | group | trainer | virtual")
    motivation_level: Optional[int] = Field(None, ge=1, le=10, description="1=Forced, 10=Highly motivated")
    mood_before: Optional[str] = Field(None, description="anxious | stressed | neutral | energetic | happy")
    mood_after: Optional[str] = Field(None, description="tired | satisfied | energized | accomplished | frustrated")
    
    # Additional metadata
    notes: Optional[str] = Field(None, max_length=500)
    photos: List[str] = Field(default_factory=list, description="Photo URLs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "habit_id": "507f1f77bcf86cd799439011",
                "activity_type": "HIIT",
                "duration": 30,
                "intensity": "high",
                "rpe": 8,
                "post_activity_energy": 7,
                "heart_rate_avg": 145,
                "heart_rate_max": 175,
                "calories_burned": 350,
                "focus_areas": ["Full Body", "Cardio"],
                "location": "home",
                "workout_type": "solo",
                "motivation_level": 8,
                "mood_before": "neutral",
                "mood_after": "energized"
            }
        }


class ExerciseLogInDB(ExerciseLogBase):
    """Exercise log as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ExerciseLogCreate(ExerciseLogBase):
    """Schema for creating an exercise log"""
    pass


class ExerciseLogUpdate(BaseModel):
    """Schema for updating an exercise log"""
    activity_type: Optional[str] = None
    duration: Optional[int] = Field(None, ge=1)
    intensity: Optional[str] = None
    rpe: Optional[int] = Field(None, ge=1, le=10)
    post_activity_energy: Optional[int] = Field(None, ge=1, le=10)
    heart_rate_avg: Optional[int] = Field(None, ge=40, le=220)
    heart_rate_max: Optional[int] = Field(None, ge=40, le=220)
    calories_burned: Optional[int] = Field(None, ge=0)
    distance: Optional[float] = Field(None, ge=0)
    focus_areas: Optional[List[str]] = None
    soreness_level: Optional[int] = Field(None, ge=1, le=10)
    sleep_quality_previous_night: Optional[int] = Field(None, ge=1, le=10)
    location: Optional[str] = None
    workout_type: Optional[str] = None
    motivation_level: Optional[int] = Field(None, ge=1, le=10)
    mood_before: Optional[str] = None
    mood_after: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)
    photos: Optional[List[str]] = None


class ExerciseLogResponse(BaseModel):
    """Response model for exercise log"""
    id: str = Field(..., alias="_id")
    user_id: str
    habit_id: str
    activity_type: str
    timestamp: datetime
    duration: int
    intensity: Optional[str]
    rpe: int
    post_activity_energy: int
    heart_rate_avg: Optional[int]
    heart_rate_max: Optional[int]
    calories_burned: Optional[int]
    distance: Optional[float]
    focus_areas: List[str]
    soreness_level: Optional[int]
    sleep_quality_previous_night: Optional[int]
    location: Optional[str]
    workout_type: Optional[str]
    motivation_level: Optional[int]
    mood_before: Optional[str]
    mood_after: Optional[str]
    notes: Optional[str]
    photos: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "user123",
                "habit_id": "507f1f77bcf86cd799439012",
                "activity_type": "Running",
                "duration": 45,
                "rpe": 7,
                "post_activity_energy": 8,
                "created_at": "2025-12-04T08:30:00Z"
            }
        }

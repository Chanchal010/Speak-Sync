"""
Study Log model for MongoDB with stickiness factor tracking
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

class StudyLogBase(BaseModel):
    """Base study log fields with stickiness tracking"""
    habit_id: str = Field(..., description="Reference to habit")
    
    # Schedule adherence (stickiness factor)
    scheduled_start: datetime = Field(..., description="When user planned to start studying")
    scheduled_end: datetime = Field(..., description="When user planned to finish studying")
    actual_start: datetime = Field(..., description="When user actually started studying")
    actual_end: datetime = Field(..., description="When user actually finished studying")
    deviation_duration: Optional[float] = Field(None, description="Minutes deviated from schedule (auto-calculated)")
    
    # Task integration (Phase 2 scheduler-service)
    task_id: Optional[str] = Field(None, description="Reference to task in scheduler-service")
    task_completed: Optional[bool] = Field(None, description="Whether the scheduled task was completed")
    completion_quality: Optional[int] = Field(None, ge=1, le=10, description="1=Rushed, 10=Thorough")
    
    # Focus and flow state
    flow_state_score: int = Field(..., ge=1, le=10, description="1=Constant distraction, 10=Deep focus")
    interruption_count: int = Field(default=0, ge=0, description="Number of times interrupted during session")
    distraction_sources: List[str] = Field(default=[], description="phone, social_media, notifications, people, thoughts, fatigue, hunger")
    
    # Study quality indicators
    energy_level_start: Optional[int] = Field(None, ge=1, le=10, description="Energy at start: 1=Exhausted, 10=Energized")
    energy_level_end: Optional[int] = Field(None, ge=1, le=10, description="Energy at end")
    mental_clarity: Optional[int] = Field(None, ge=1, le=10, description="1=Foggy, 10=Sharp")
    motivation_level: Optional[int] = Field(None, ge=1, le=10, description="1=Forced, 10=Eager")
    
    # Study session details
    subject: Optional[str] = Field(None, max_length=100, description="Subject or topic studied")
    study_method: Optional[str] = Field(None, description="reading, practice_problems, video_lectures, note_taking, group_study, flashcards, teaching_others")
    break_count: Optional[int] = Field(None, ge=0, description="Number of planned breaks taken")
    break_duration: Optional[int] = Field(None, ge=0, description="Total break time in minutes")
    
    # Environment
    location: Optional[str] = Field(None, description="library, home, cafe, classroom, office")
    noise_level: Optional[str] = Field(None, description="silent, quiet, moderate, loud")
    used_music: Optional[bool] = Field(None, description="Studied with background music")
    music_type: Optional[str] = Field(None, description="classical, lo-fi, ambient, binaural_beats, none")
    
    # Pre-study factors
    caffeine_before_study: Optional[bool] = Field(None, description="Had caffeine within 30min before starting")
    meal_timing: Optional[str] = Field(None, description="just_ate, 1-2_hours_ago, 3-4_hours_ago, hungry")
    sleep_quality_last_night: Optional[int] = Field(None, ge=1, le=10, description="Quality of previous night's sleep")
    stress_level: Optional[int] = Field(None, ge=1, le=10, description="Stress level before starting")
    
    # Post-study reflection
    retention_confidence: Optional[int] = Field(None, ge=1, le=10, description="1=Forgot already, 10=Will remember")
    satisfaction_level: Optional[int] = Field(None, ge=1, le=10, description="How satisfied with the session")
    would_repeat_conditions: Optional[bool] = Field(None, description="Would study under same conditions again")
    
    notes: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "habit_id": "507f1f77bcf86cd799439011",
                "scheduled_start": "2025-12-04T14:00:00Z",
                "scheduled_end": "2025-12-04T16:00:00Z",
                "actual_start": "2025-12-04T14:15:00Z",
                "actual_end": "2025-12-04T16:10:00Z",
                "flow_state_score": 8,
                "interruption_count": 2,
                "distraction_sources": ["phone", "notifications"],
                "subject": "Machine Learning",
                "study_method": "practice_problems"
            }
        }

class StudyLogCreate(StudyLogBase):
    """Study log creation model"""
    pass

class StudyLogUpdate(BaseModel):
    """Study log update model - all fields optional"""
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    task_id: Optional[str] = None
    task_completed: Optional[bool] = None
    completion_quality: Optional[int] = Field(None, ge=1, le=10)
    flow_state_score: Optional[int] = Field(None, ge=1, le=10)
    interruption_count: Optional[int] = Field(None, ge=0)
    distraction_sources: Optional[List[str]] = None
    energy_level_start: Optional[int] = Field(None, ge=1, le=10)
    energy_level_end: Optional[int] = Field(None, ge=1, le=10)
    mental_clarity: Optional[int] = Field(None, ge=1, le=10)
    motivation_level: Optional[int] = Field(None, ge=1, le=10)
    subject: Optional[str] = Field(None, max_length=100)
    study_method: Optional[str] = None
    break_count: Optional[int] = Field(None, ge=0)
    break_duration: Optional[int] = Field(None, ge=0)
    location: Optional[str] = None
    noise_level: Optional[str] = None
    used_music: Optional[bool] = None
    music_type: Optional[str] = None
    caffeine_before_study: Optional[bool] = None
    meal_timing: Optional[str] = None
    sleep_quality_last_night: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    retention_confidence: Optional[int] = Field(None, ge=1, le=10)
    satisfaction_level: Optional[int] = Field(None, ge=1, le=10)
    would_repeat_conditions: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)

class StudyLogInDB(StudyLogBase):
    """Study log as stored in database"""
    id: ObjectId = Field(alias="_id")
    user_id: str
    timestamp: datetime
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True

class StudyLogResponse(BaseModel):
    """Study log response model"""
    id: str
    user_id: str
    habit_id: str
    scheduled_start: datetime
    scheduled_end: datetime
    actual_start: datetime
    actual_end: datetime
    deviation_duration: Optional[float]
    task_id: Optional[str]
    task_completed: Optional[bool]
    completion_quality: Optional[int]
    flow_state_score: int
    interruption_count: int
    distraction_sources: List[str]
    energy_level_start: Optional[int]
    energy_level_end: Optional[int]
    mental_clarity: Optional[int]
    motivation_level: Optional[int]
    subject: Optional[str]
    study_method: Optional[str]
    break_count: Optional[int]
    break_duration: Optional[int]
    location: Optional[str]
    noise_level: Optional[str]
    used_music: Optional[bool]
    music_type: Optional[str]
    caffeine_before_study: Optional[bool]
    meal_timing: Optional[str]
    sleep_quality_last_night: Optional[int]
    stress_level: Optional[int]
    retention_confidence: Optional[int]
    satisfaction_level: Optional[int]
    would_repeat_conditions: Optional[bool]
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
                "scheduled_start": "2025-12-04T14:00:00Z",
                "scheduled_end": "2025-12-04T16:00:00Z",
                "actual_start": "2025-12-04T14:15:00Z",
                "actual_end": "2025-12-04T16:10:00Z",
                "deviation_duration": 25.0,
                "flow_state_score": 8,
                "interruption_count": 2
            }
        }

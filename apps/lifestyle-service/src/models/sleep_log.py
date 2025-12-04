"""
Sleep Log Models
Track sleep patterns with chronotype detection and sleep debt calculation
"""
from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

from .habit import PyObjectId


class SleepLogBase(BaseModel):
    """Base sleep log with AI training fields"""
    habit_id: str = Field(..., description="Associated sleep habit ID")
    bedtime: datetime = Field(..., description="When went to bed")
    wake_time: datetime = Field(..., description="When woke up")
    sleep_duration: Optional[float] = Field(None, description="Total hours slept (calculated)")
    
    # Sleep quality metrics
    sleep_quality: int = Field(..., ge=1, le=10, description="Overall sleep quality 1-10")
    sleep_latency: Optional[int] = Field(None, description="Minutes to fall asleep")
    times_awakened: Optional[int] = Field(None, ge=0, description="Number of times woke up during night")
    grogginess_level: int = Field(..., ge=1, le=10, description="Morning grogginess 1=Alert, 10=Zombie")
    
    # Chronotype detection fields
    natural_wake_time: Optional[datetime] = Field(None, description="When naturally woke (no alarm)")
    used_alarm: bool = Field(True, description="Did you use an alarm?")
    felt_rested: bool = Field(..., description="Felt rested upon waking?")
    
    # Sleep debt tracking
    target_sleep_hours: Optional[float] = Field(None, description="Personal target hours")
    sleep_debt: Optional[float] = Field(None, description="Accumulated sleep debt (calculated)")
    
    # Pre-sleep behavior (AI training)
    pre_sleep_activity: Optional[str] = Field(None, description="Activity before bed: reading | tv | phone | exercise | meditation | work | other")
    screen_time_before_bed: Optional[int] = Field(None, description="Minutes of screen time before bed")
    caffeine_intake: Optional[int] = Field(None, description="Hours since last caffeine")
    alcohol_intake: Optional[bool] = Field(None, description="Consumed alcohol before bed?")
    exercise_today: Optional[bool] = Field(None, description="Exercised today?")
    stress_level: Optional[int] = Field(None, ge=1, le=10, description="Stress level today")
    
    # Environment
    room_temperature: Optional[str] = Field(None, description="Room temp: cold | cool | comfortable | warm | hot")
    noise_level: Optional[str] = Field(None, description="Noise: silent | quiet | moderate | loud")
    
    # Dreams and mood
    had_dreams: Optional[bool] = Field(None, description="Remember dreams?")
    dream_type: Optional[str] = Field(None, description="Dream type: pleasant | neutral | nightmare | none")
    mood_on_waking: Optional[str] = Field(None, description="Waking mood: refreshed | neutral | groggy | irritable | anxious")
    
    notes: Optional[str] = Field(None, description="Additional sleep notes")
    
    class Config:
        populate_by_name = True


class SleepLogInDB(SleepLogBase):
    """Sleep log as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class SleepLogCreate(SleepLogBase):
    """Schema for creating sleep log"""
    pass


class SleepLogUpdate(BaseModel):
    """Schema for updating sleep log"""
    bedtime: Optional[datetime] = None
    wake_time: Optional[datetime] = None
    sleep_duration: Optional[float] = None
    sleep_quality: Optional[int] = Field(None, ge=1, le=10)
    sleep_latency: Optional[int] = None
    times_awakened: Optional[int] = None
    grogginess_level: Optional[int] = Field(None, ge=1, le=10)
    natural_wake_time: Optional[datetime] = None
    used_alarm: Optional[bool] = None
    felt_rested: Optional[bool] = None
    target_sleep_hours: Optional[float] = None
    sleep_debt: Optional[float] = None
    pre_sleep_activity: Optional[str] = None
    screen_time_before_bed: Optional[int] = None
    caffeine_intake: Optional[int] = None
    alcohol_intake: Optional[bool] = None
    exercise_today: Optional[bool] = None
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    room_temperature: Optional[str] = None
    noise_level: Optional[str] = None
    had_dreams: Optional[bool] = None
    dream_type: Optional[str] = None
    mood_on_waking: Optional[str] = None
    notes: Optional[str] = None


class SleepLogResponse(BaseModel):
    """Schema for sleep log response"""
    id: str = Field(..., alias="_id")
    user_id: str
    habit_id: str
    bedtime: datetime
    wake_time: datetime
    sleep_duration: Optional[float]
    sleep_quality: int
    sleep_latency: Optional[int]
    times_awakened: Optional[int]
    grogginess_level: int
    natural_wake_time: Optional[datetime]
    used_alarm: bool
    felt_rested: bool
    target_sleep_hours: Optional[float]
    sleep_debt: Optional[float]
    pre_sleep_activity: Optional[str]
    screen_time_before_bed: Optional[int]
    caffeine_intake: Optional[int]
    alcohol_intake: Optional[bool]
    exercise_today: Optional[bool]
    stress_level: Optional[int]
    room_temperature: Optional[str]
    noise_level: Optional[str]
    had_dreams: Optional[bool]
    dream_type: Optional[str]
    mood_on_waking: Optional[str]
    notes: Optional[str]
    timestamp: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

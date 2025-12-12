"""
Base Habit model for MongoDB
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(str):
    """Custom ObjectId type for Pydantic v2"""
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.with_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v, info):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return v
            raise ValueError("Invalid ObjectId")
        raise ValueError("Invalid ObjectId type")

class HabitConfig(BaseModel):
    """Type-specific configuration for each habit type"""
    # Food-specific
    target_meals: Optional[int] = None
    track_macros: Optional[bool] = False
    
    # Exercise-specific
    target_workouts: Optional[int] = None
    preferred_types: Optional[List[str]] = []
    
    # Financial-specific
    monthly_budget: Optional[float] = None
    savings_goal: Optional[float] = None
    
    # Sleep-specific
    target_sleep_hours: Optional[float] = None
    ideal_bedtime: Optional[str] = None
    
    # Study-specific
    target_hours: Optional[int] = None
    focus_goal: Optional[int] = None
    
    # Water-specific
    target_intake: Optional[int] = None  # ml
    body_weight: Optional[float] = None  # kg

    class Config:
        json_schema_extra = {
            "example": {
                "target_workouts": 4,
                "preferred_types": ["Yoga", "HIIT"]
            }
        }

class HabitBase(BaseModel):
    """Base habit fields"""
    user_id: str = Field(..., description="User ID from auth service")
    habit_type: str = Field(..., description="food | exercise | financial | sleep | study | water")
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: str = Field(default="#3B82F6", pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None
    is_active: bool = Field(default=True)
    
    # Tracking fields
    current_streak: int = Field(default=0, ge=0)
    longest_streak: int = Field(default=0, ge=0)
    total_logs: int = Field(default=0, ge=0)
    
    # Configuration
    config: HabitConfig = Field(default_factory=HabitConfig)
    
    # AI metadata
    ai_insights: List[str] = Field(default_factory=list)
    last_analyzed: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "habit_type": "exercise",
                "name": "Morning Workout",
                "description": "Daily exercise routine",
                "color": "#10B981",
                "config": {
                    "target_workouts": 5,
                    "preferred_types": ["Yoga", "Running"]
                }
            }
        }

class HabitInDB(HabitBase):
    """Habit model with MongoDB fields"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "user123",
                "habit_type": "exercise",
                "name": "Morning Workout",
                "created_at": "2025-12-04T10:00:00Z"
            }
        }

class HabitCreate(BaseModel):
    """Schema for creating a new habit (user_id comes from auth header)"""
    habit_type: str = Field(..., description="food | exercise | financial | sleep | study | water")
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: str = Field(default="#3B82F6", pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None
    is_active: bool = Field(default=True)
    config: HabitConfig = Field(default_factory=HabitConfig)
    
    class Config:
        json_schema_extra = {
            "example": {
                "habit_type": "food",
                "name": "Healthy Eating",
                "description": "Track my daily meals",
                "color": "#4CAF50",
                "icon": "🍎",
                "config": {
                    "target_meals": 3
                }
            }
        }

class HabitUpdate(BaseModel):
    """Schema for updating a habit"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None
    is_active: Optional[bool] = None
    config: Optional[HabitConfig] = None

class HabitResponse(BaseModel):
    """Response model for habit"""
    id: str = Field(..., alias="_id")
    user_id: str
    habit_type: str
    name: str
    description: Optional[str]
    color: str
    icon: Optional[str]
    is_active: bool
    current_streak: int
    longest_streak: int
    total_logs: int
    config: HabitConfig
    ai_insights: List[str]
    last_analyzed: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True
        json_encoders = {ObjectId: str}

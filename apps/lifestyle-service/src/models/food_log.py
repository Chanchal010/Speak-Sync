"""
Food Log Models
Tracks meal entries with detailed metadata for AI analysis
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

from .habit import PyObjectId


class FoodLogBase(BaseModel):
    """Base food log fields"""
    habit_id: str = Field(..., description="Reference to the food habit")
    meal_type: str = Field(..., description="breakfast | lunch | dinner | snack")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Core meal data
    food_items: List[str] = Field(default_factory=list, description="List of food items consumed")
    portion_size: Optional[str] = Field(None, description="small | medium | large")
    calories: Optional[int] = Field(None, ge=0)
    
    # AI Training Fields - Eating Behavior Analysis
    hunger_level: Optional[int] = Field(None, ge=1, le=10, description="1=Not hungry, 10=Starving")
    satisfaction_level: Optional[int] = Field(None, ge=1, le=10, description="1=Unsatisfied, 10=Very satisfied")
    eating_speed: Optional[str] = Field(None, description="slow | moderate | fast")
    
    # Emotional & Environmental Context
    emotional_state: Optional[str] = Field(None, description="happy | stressed | bored | sad | neutral | excited")
    location: Optional[str] = Field(None, description="home | work | restaurant | outdoor")
    social_context: Optional[str] = Field(None, description="alone | family | friends | colleagues")
    distraction_level: Optional[int] = Field(None, ge=1, le=10, description="1=Mindful, 10=Very distracted")
    
    # Additional metadata
    notes: Optional[str] = Field(None, max_length=500)
    photos: List[str] = Field(default_factory=list, description="Photo URLs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "habit_id": "507f1f77bcf86cd799439011",
                "meal_type": "breakfast",
                "food_items": ["Oatmeal", "Banana", "Almonds"],
                "portion_size": "medium",
                "calories": 350,
                "hunger_level": 7,
                "satisfaction_level": 8,
                "eating_speed": "moderate",
                "emotional_state": "neutral",
                "location": "home",
                "social_context": "alone",
                "distraction_level": 3,
                "notes": "Felt energized after eating"
            }
        }


class FoodLogInDB(FoodLogBase):
    """Food log as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class FoodLogCreate(FoodLogBase):
    """Schema for creating a food log"""
    pass


class FoodLogUpdate(BaseModel):
    """Schema for updating a food log"""
    meal_type: Optional[str] = None
    food_items: Optional[List[str]] = None
    portion_size: Optional[str] = None
    calories: Optional[int] = Field(None, ge=0)
    hunger_level: Optional[int] = Field(None, ge=1, le=10)
    satisfaction_level: Optional[int] = Field(None, ge=1, le=10)
    eating_speed: Optional[str] = None
    emotional_state: Optional[str] = None
    location: Optional[str] = None
    social_context: Optional[str] = None
    distraction_level: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = Field(None, max_length=500)
    photos: Optional[List[str]] = None


class FoodLogResponse(BaseModel):
    """Response model for food log"""
    id: str = Field(..., alias="_id")
    user_id: str
    habit_id: str
    meal_type: str
    timestamp: datetime
    food_items: List[str]
    portion_size: Optional[str]
    calories: Optional[int]
    hunger_level: Optional[int]
    satisfaction_level: Optional[int]
    eating_speed: Optional[str]
    emotional_state: Optional[str]
    location: Optional[str]
    social_context: Optional[str]
    distraction_level: Optional[int]
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
                "meal_type": "breakfast",
                "timestamp": "2025-12-04T08:30:00Z",
                "food_items": ["Oatmeal", "Banana"],
                "hunger_level": 7,
                "satisfaction_level": 8,
                "created_at": "2025-12-04T08:30:00Z"
            }
        }

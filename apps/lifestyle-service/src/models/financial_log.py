"""
Financial Log Models
Track spending habits with AI-ready behavioral data
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

from .habit import PyObjectId


class FinancialLogBase(BaseModel):
    """Base financial log with AI training fields"""
    habit_id: str = Field(..., description="Associated financial habit ID")
    amount: float = Field(..., description="Transaction amount")
    category: str = Field(..., description="Spending category: groceries | dining | entertainment | transport | shopping | bills | healthcare | education | investment | other")
    description: Optional[str] = Field(None, description="What was purchased")
    necessity_score: int = Field(..., ge=1, le=10, description="1=Impulse luxury, 10=Critical necessity")
    
    # Behavioral AI fields
    associated_mood: Optional[str] = Field(None, description="Mood during purchase: happy | sad | stressed | bored | excited | anxious | neutral")
    time_of_purchase: Optional[datetime] = Field(None, description="When the purchase was made")
    location: Optional[str] = Field(None, description="Where purchased: online | store | restaurant | gas_station | other")
    payment_method: Optional[str] = Field(None, description="Payment type: cash | debit | credit | digital_wallet")
    impulse_buy: bool = Field(False, description="Was this unplanned?")
    budget_category: Optional[str] = Field(None, description="User's budget category")
    savings_allocation: Optional[float] = Field(None, description="Amount saved/invested")
    
    # Context for triggers
    social_context: Optional[str] = Field(None, description="Spending trigger: alone | with_friends | with_family | peer_pressure")
    emotional_trigger: Optional[str] = Field(None, description="Why bought: reward | stress_relief | boredom | celebration | fear_of_missing_out | need")
    regret_level: Optional[int] = Field(None, ge=1, le=10, description="Post-purchase regret 1-10")
    
    notes: Optional[str] = Field(None, description="Additional context")
    receipt_photo: Optional[str] = Field(None, description="Receipt image URL")
    
    class Config:
        populate_by_name = True


class FinancialLogInDB(FinancialLogBase):
    """Financial log as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class FinancialLogCreate(FinancialLogBase):
    """Schema for creating financial log"""
    pass


class FinancialLogUpdate(BaseModel):
    """Schema for updating financial log"""
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    necessity_score: Optional[int] = Field(None, ge=1, le=10)
    associated_mood: Optional[str] = None
    time_of_purchase: Optional[datetime] = None
    location: Optional[str] = None
    payment_method: Optional[str] = None
    impulse_buy: Optional[bool] = None
    budget_category: Optional[str] = None
    savings_allocation: Optional[float] = None
    social_context: Optional[str] = None
    emotional_trigger: Optional[str] = None
    regret_level: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    receipt_photo: Optional[str] = None


class FinancialLogResponse(BaseModel):
    """Schema for financial log response"""
    id: str = Field(..., alias="_id")
    user_id: str
    habit_id: str
    amount: float
    category: str
    description: Optional[str]
    necessity_score: int
    associated_mood: Optional[str]
    time_of_purchase: datetime
    location: Optional[str]
    payment_method: Optional[str]
    impulse_buy: bool
    budget_category: Optional[str]
    savings_allocation: Optional[float]
    social_context: Optional[str]
    emotional_trigger: Optional[str]
    regret_level: Optional[int]
    notes: Optional[str]
    receipt_photo: Optional[str]
    timestamp: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

"""
Financial Log Routes
API endpoints for spending tracking and financial habit analysis
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header

from ...database.mongodb import get_database
from ...models.financial_log import FinancialLogCreate, FinancialLogUpdate, FinancialLogResponse
from ...services.financial_log_service import FinancialLogService, get_financial_log_service


router = APIRouter(prefix="/api/financial-logs", tags=["Financial Logs"])


async def get_user_id(x_user_id: str = Header(..., description="User ID from auth")) -> str:
    """Extract user ID from header"""
    return x_user_id


async def get_service() -> FinancialLogService:
    """Dependency to get financial log service"""
    db = get_database()
    return get_financial_log_service(db)


@router.post("", response_model=FinancialLogResponse, status_code=201)
async def create_financial_log(
    log_data: FinancialLogCreate,
    user_id: str = Depends(get_user_id),
    service: FinancialLogService = Depends(get_service)
):
    """
    Create a new financial log entry
    
    **AI Training Fields**:
    - necessity_score: 1-10 (1=Impulse luxury, 10=Critical necessity)
    - associated_mood: Emotional state during purchase
    - impulse_buy: Was this unplanned?
    - emotional_trigger: Why bought (reward, stress_relief, boredom, etc.)
    - regret_level: 1-10 post-purchase regret
    - social_context: Who influenced the purchase
    - time_of_purchase: When the purchase was made
    - location: online | store | restaurant | gas_station | other
    - payment_method: cash | debit | credit | digital_wallet
    """
    try:
        log = await service.create_financial_log(user_id, log_data.habit_id, log_data)
        return FinancialLogResponse(
            id=str(log.id),
            user_id=log.user_id,
            habit_id=log.habit_id,
            amount=log.amount,
            category=log.category,
            description=log.description,
            necessity_score=log.necessity_score,
            associated_mood=log.associated_mood,
            time_of_purchase=log.time_of_purchase,
            location=log.location,
            payment_method=log.payment_method,
            impulse_buy=log.impulse_buy,
            budget_category=log.budget_category,
            savings_allocation=log.savings_allocation,
            social_context=log.social_context,
            emotional_trigger=log.emotional_trigger,
            regret_level=log.regret_level,
            notes=log.notes,
            receipt_photo=log.receipt_photo,
            timestamp=log.timestamp,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[FinancialLogResponse])
async def get_financial_logs(
    habit_id: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
    user_id: str = Depends(get_user_id),
    service: FinancialLogService = Depends(get_service)
):
    """
    Get financial logs with optional filters
    
    **Query Parameters**:
    - habit_id: Filter by specific habit
    - category: Filter by spending category
    - start_date: Filter logs from this date onwards
    - end_date: Filter logs up to this date
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (max 100)
    """
    if limit > 100:
        limit = 100
    
    logs = await service.get_financial_logs(
        user_id=user_id,
        habit_id=habit_id,
        category=category,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return [
        FinancialLogResponse(
            id=str(log.id),
            user_id=log.user_id,
            habit_id=log.habit_id,
            amount=log.amount,
            category=log.category,
            description=log.description,
            necessity_score=log.necessity_score,
            associated_mood=log.associated_mood,
            time_of_purchase=log.time_of_purchase,
            location=log.location,
            payment_method=log.payment_method,
            impulse_buy=log.impulse_buy,
            budget_category=log.budget_category,
            savings_allocation=log.savings_allocation,
            social_context=log.social_context,
            emotional_trigger=log.emotional_trigger,
            regret_level=log.regret_level,
            notes=log.notes,
            receipt_photo=log.receipt_photo,
            timestamp=log.timestamp,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
        for log in logs
    ]


@router.get("/{log_id}", response_model=FinancialLogResponse)
async def get_financial_log(
    log_id: str,
    user_id: str = Depends(get_user_id),
    service: FinancialLogService = Depends(get_service)
):
    """Get a specific financial log by ID"""
    log = await service.get_financial_log_by_id(user_id, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Financial log not found")
    
    return FinancialLogResponse(
        id=str(log.id),
        user_id=log.user_id,
        habit_id=log.habit_id,
        amount=log.amount,
        category=log.category,
        description=log.description,
        necessity_score=log.necessity_score,
        associated_mood=log.associated_mood,
        time_of_purchase=log.time_of_purchase,
        location=log.location,
        payment_method=log.payment_method,
        impulse_buy=log.impulse_buy,
        budget_category=log.budget_category,
        savings_allocation=log.savings_allocation,
        social_context=log.social_context,
        emotional_trigger=log.emotional_trigger,
        regret_level=log.regret_level,
        notes=log.notes,
        receipt_photo=log.receipt_photo,
        timestamp=log.timestamp,
        created_at=log.created_at,
        updated_at=log.updated_at
    )


@router.put("/{log_id}", response_model=FinancialLogResponse)
async def update_financial_log(
    log_id: str,
    update_data: FinancialLogUpdate,
    user_id: str = Depends(get_user_id),
    service: FinancialLogService = Depends(get_service)
):
    """Update a financial log"""
    log = await service.update_financial_log(user_id, log_id, update_data)
    if not log:
        raise HTTPException(status_code=404, detail="Financial log not found")
    
    return FinancialLogResponse(
        id=str(log.id),
        user_id=log.user_id,
        habit_id=log.habit_id,
        amount=log.amount,
        category=log.category,
        description=log.description,
        necessity_score=log.necessity_score,
        associated_mood=log.associated_mood,
        time_of_purchase=log.time_of_purchase,
        location=log.location,
        payment_method=log.payment_method,
        impulse_buy=log.impulse_buy,
        budget_category=log.budget_category,
        savings_allocation=log.savings_allocation,
        social_context=log.social_context,
        emotional_trigger=log.emotional_trigger,
        regret_level=log.regret_level,
        notes=log.notes,
        receipt_photo=log.receipt_photo,
        timestamp=log.timestamp,
        created_at=log.created_at,
        updated_at=log.updated_at
    )


@router.delete("/{log_id}", status_code=204)
async def delete_financial_log(
    log_id: str,
    user_id: str = Depends(get_user_id),
    service: FinancialLogService = Depends(get_service)
):
    """Soft delete a financial log"""
    deleted = await service.delete_financial_log(user_id, log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Financial log not found")
    return None


@router.get("/stats/overview", response_model=dict)
async def get_financial_stats(
    habit_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: str = Depends(get_user_id),
    service: FinancialLogService = Depends(get_service)
):
    """
    Get financial spending statistics
    
    **Returns**:
    - total_spent: Total amount spent
    - avg_amount: Average transaction amount
    - avg_necessity: Average necessity score
    - avg_regret: Average regret level
    - impulse_count: Number of impulse purchases
    - impulse_percentage: % of purchases that were impulse
    - total_savings: Total amount saved/invested
    - category_distribution: Spending by category
    - mood_distribution: Purchases by mood
    - trigger_distribution: Emotional triggers
    - location_distribution: Where purchases were made
    """
    stats = await service.get_financial_log_stats(
        user_id=user_id,
        habit_id=habit_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "success": True,
        "data": stats
    }

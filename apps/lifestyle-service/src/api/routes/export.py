"""
Export API Routes
"""
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from typing import Optional, List
from datetime import datetime
from io import BytesIO
import json

from ...database.mongodb import get_database
from ...services.export_service import ExportService
from fastapi import Header


router = APIRouter(prefix="/api/export", tags=["export"])


async def get_user_id(x_user_id: str = Header(...)):
    """Extract user ID from header"""
    return x_user_id


async def get_service():
    """Get export service instance"""
    return ExportService(get_database())


@router.get("/csv")
async def export_csv(
    habit_types: Optional[List[str]] = Query(
        None,
        description="Filter by habit types (food, exercise, financial, sleep, study, water). If not specified, exports all types."
    ),
    start_date: Optional[datetime] = Query(
        None,
        description="Filter by date (>=). Format: YYYY-MM-DDTHH:MM:SS"
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Filter by date (<=). Format: YYYY-MM-DDTHH:MM:SS"
    ),
    user_id: str = Depends(get_user_id),
    service: ExportService = Depends(get_service)
):
    """
    Export habit data as CSV files
    
    Creates separate CSV files for each habit type with all fields including calculated metrics:
    
    **Sleep Logs CSV includes:**
    - All base fields (bedtime, wake_time, duration, sleep_quality, etc.)
    - `chronotype_hint`: early_bird, night_owl, or intermediate
    - `sleep_debt`: Difference between target_hours and actual duration
    
    **Study Logs CSV includes:**
    - All base fields (scheduled times, actual times, flow_state_score, etc.)
    - `stickiness_percentage`: Schedule adherence (100% - deviation/planned * 100)
    - `deviation_duration`: Total minutes deviated from schedule
    
    **Water Logs CSV includes:**
    - All base fields (intake_volume, urine_color, cognitive_fog, etc.)
    - `hydration_status`: optimal, adequate, mild_dehydration, moderate_dehydration, severe_dehydration
    
    **Exercise Logs CSV includes:**
    - All base fields (exercise_type, duration, perceived_exertion, etc.)
    - `over_training_risk`: high, moderate, or low based on RPE, post-energy, soreness
    
    **Financial Logs CSV includes:**
    - All base fields (amount, category, necessity_score, impulse_buy, etc.)
    - `spending_pattern`: impulse, necessary, or discretionary
    
    **Food Logs CSV includes:**
    - All base fields (meal_type, calories, satisfaction_level, emotional_state, etc.)
    
    **Returns:** ZIP file containing separate CSV files for each habit type
    
    **Note:** Due to FastAPI limitations, this endpoint returns JSON with CSV content.
    Use the JSON format endpoint or implement a proper file download in frontend.
    """
    
    result = await service.export_data(
        user_id=user_id,
        format="csv",
        habit_types=habit_types,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "success": True,
        "data": result
    }


@router.get("/json")
async def export_json(
    habit_types: Optional[List[str]] = Query(
        None,
        description="Filter by habit types (food, exercise, financial, sleep, study, water). If not specified, exports all types."
    ),
    start_date: Optional[datetime] = Query(
        None,
        description="Filter by date (>=). Format: YYYY-MM-DDTHH:MM:SS"
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Filter by date (<=). Format: YYYY-MM-DDTHH:MM:SS"
    ),
    user_id: str = Depends(get_user_id),
    service: ExportService = Depends(get_service)
):
    """
    Export habit data as JSON
    
    Returns all habit logs in a structured JSON format with calculated fields:
    
    **Structure:**
    ```json
    {
      "format": "json",
      "data": {
        "food": [...],
        "exercise": [...],
        "financial": [...],
        "sleep": [...],
        "study": [...],
        "water": [...]
      },
      "total_logs": 123,
      "habit_types": ["food", "exercise", "sleep"],
      "exported_at": "2025-12-04T15:30:00"
    }
    ```
    
    **Calculated Fields Included:**
    - Sleep: `chronotype_hint`, `sleep_debt`
    - Study: `stickiness_percentage` (already stored), `deviation_duration`
    - Water: `hydration_status` based on Armstrong Scale
    - Exercise: `over_training_risk` indicator
    - Financial: `spending_pattern` classification
    
    **Use Cases:**
    - Data backup
    - Import into other applications
    - Data analysis in Python/R
    - Machine learning model training
    """
    
    result = await service.export_data(
        user_id=user_id,
        format="json",
        habit_types=habit_types,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "success": True,
        "data": result
    }

"""
Water Log Service for business logic
"""
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from ..models.water_log import WaterLogCreate, WaterLogUpdate, WaterLogInDB, WaterLogResponse
from .habit_service import HabitService
from ..utils.rabbitmq.publisher import get_event_publisher
import logging

logger = logging.getLogger(__name__)


class WaterLogService:
    """Service for managing water logs with hydration status tracking"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.water_logs
        self.habit_service = HabitService(db)
    
    def _detect_hydration_status(self, urine_color: Optional[int]) -> str:
        """Detect hydration status from Armstrong Scale urine color"""
        if not urine_color:
            return "unknown"
        
        if urine_color <= 3:
            return "optimal"
        elif urine_color <= 4:
            return "adequate"
        elif urine_color <= 6:
            return "mild_dehydration"
        elif urine_color == 7:
            return "moderate_dehydration"
        else:  # 8
            return "severe_dehydration"
    
    def _calculate_daily_goal(self, body_weight: Optional[float] = None) -> int:
        """Calculate daily water intake goal in ml"""
        if body_weight:
            # General guideline: 30-35ml per kg body weight
            return int(body_weight * 33)
        else:
            # Default recommendation: 2000ml (2 liters)
            return 2000
    
    async def create_water_log(
        self,
        user_id: str,
        log_data: WaterLogCreate
    ) -> WaterLogInDB:
        """Create a new water log entry"""
        # Validate habit
        habit_id = log_data.habit_id
        if not ObjectId.is_valid(habit_id):
            raise ValueError("Invalid habit ID")
        
        habit = await self.habit_service.get_habit_by_id(user_id, habit_id)
        if not habit:
            raise ValueError("Habit not found")
        if habit.habit_type != "water":
            raise ValueError("Habit must be of type 'water'")
        
        # Create log
        log_dict = log_data.model_dump()
        log_dict["user_id"] = user_id
        log_dict["timestamp"] = datetime.utcnow()
        log_dict["created_at"] = datetime.utcnow()
        log_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(log_dict)
        log_dict["_id"] = result.inserted_id
        
        water_log = WaterLogInDB(**log_dict)
        
        # Update habit streak and count
        log_date = log_dict["timestamp"].date()
        await self.habit_service.update_streak(user_id, habit_id, log_date)
        
        # Publish WATER_LOGGED event
        try:
            publisher = get_event_publisher()
            publisher.publish_water_logged(
                user_id=user_id,
                habit_id=habit_id,
                log_id=str(water_log.id),
                amount=water_log.amount_ml,
                urine_color=water_log.urine_color or 4,
                caffeine=water_log.caffeine_intake or False,
                cognitive_fog=water_log.cognitive_fog or False,
                logged_at=water_log.timestamp
            )
        except Exception as e:
            logger.error(f"Failed to publish WATER_LOGGED event: {e}")
        
        return water_log
    
    async def get_water_log_by_id(
        self,
        user_id: str,
        log_id: str
    ) -> Optional[WaterLogInDB]:
        """Get a specific water log"""
        if not ObjectId.is_valid(log_id):
            return None
        
        log = await self.collection.find_one({
            "_id": ObjectId(log_id),
            "user_id": user_id,
            "deleted_at": None
        })
        
        if log:
            return WaterLogInDB(**log)
        return None
    
    async def get_water_logs(
        self,
        user_id: str,
        habit_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[WaterLogInDB]:
        """Get water logs with optional filters"""
        query: Dict[str, Any] = {
            "user_id": user_id,
            "deleted_at": None
        }
        
        if habit_id:
            if not ObjectId.is_valid(habit_id):
                return []
            query["habit_id"] = habit_id
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        cursor = self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        return [WaterLogInDB(**log) for log in logs]
    
    async def update_water_log(
        self,
        user_id: str,
        log_id: str,
        update_data: WaterLogUpdate
    ) -> Optional[WaterLogInDB]:
        """Update a water log"""
        if not ObjectId.is_valid(log_id):
            return None
        
        existing_log = await self.get_water_log_by_id(user_id, log_id)
        if not existing_log:
            return None
        
        update_dict = {k: v for k, v in update_data.model_dump(exclude_unset=True).items() if v is not None}
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(log_id), "user_id": user_id, "deleted_at": None},
            {"$set": update_dict},
            return_document=True
        )
        
        if result:
            return WaterLogInDB(**result)
        return None
    
    async def delete_water_log(
        self,
        user_id: str,
        log_id: str
    ) -> bool:
        """Soft delete a water log"""
        if not ObjectId.is_valid(log_id):
            return False
        
        result = await self.collection.update_one(
            {"_id": ObjectId(log_id), "user_id": user_id, "deleted_at": None},
            {"$set": {"deleted_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    async def get_water_log_stats(
        self,
        user_id: str,
        habit_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get water log statistics with hydration analysis"""
        query: Dict[str, Any] = {
            "user_id": user_id,
            "deleted_at": None
        }
        
        if habit_id:
            if not ObjectId.is_valid(habit_id):
                return {}
            query["habit_id"] = habit_id
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        logs = await self.collection.find(query).to_list(length=None)
        
        if not logs:
            return {
                "total_logs": 0,
                "total_intake": 0,
                "avg_daily_intake": 0,
                "avg_urine_color": 0.0,
                "hydration_status_hint": "insufficient_data",
                "cognitive_fog_instances": 0,
                "cognitive_fog_percentage": 0.0,
                "headache_instances": 0,
                "avg_energy_level": 0.0,
                "avg_mental_clarity": 0.0
            }
        
        total_logs = len(logs)
        total_intake = 0
        urine_color_count = 0
        urine_color_sum = 0
        cognitive_fog_count = 0
        headache_count = 0
        energy_sum = 0
        energy_count = 0
        clarity_sum = 0
        clarity_count = 0
        
        # Track daily totals
        daily_intakes: Dict[str, int] = {}
        
        # Hydration status distribution
        hydration_status_counts: Dict[str, int] = {}
        
        # Source and activity distributions
        source_counts: Dict[str, int] = {}
        activity_counts: Dict[str, int] = {}
        
        for log in logs:
            # Intake tracking
            intake = log.get("intake_volume", 0)
            total_intake += intake
            
            # Daily totals
            log_date = log.get("timestamp", datetime.utcnow()).strftime("%Y-%m-%d")
            daily_intakes[log_date] = daily_intakes.get(log_date, 0) + intake
            
            # Urine color (Armstrong Scale)
            urine_color = log.get("urine_color")
            if urine_color:
                urine_color_sum += urine_color
                urine_color_count += 1
                status = self._detect_hydration_status(urine_color)
                hydration_status_counts[status] = hydration_status_counts.get(status, 0) + 1
            
            # Cognitive symptoms
            if log.get("cognitive_fog"):
                cognitive_fog_count += 1
            if log.get("headache_present"):
                headache_count += 1
            
            # Energy and clarity
            energy = log.get("energy_level")
            if energy:
                energy_sum += energy
                energy_count += 1
            
            clarity = log.get("mental_clarity")
            if clarity:
                clarity_sum += clarity
                clarity_count += 1
            
            # Distributions
            source = log.get("intake_source")
            if source:
                source_counts[source] = source_counts.get(source, 0) + 1
            
            activity = log.get("activity_level")
            if activity:
                activity_counts[activity] = activity_counts.get(activity, 0) + 1
        
        # Calculate averages
        avg_urine_color = round(urine_color_sum / urine_color_count, 2) if urine_color_count > 0 else 0.0
        hydration_status_hint = self._detect_hydration_status(int(avg_urine_color)) if avg_urine_color > 0 else "unknown"
        
        # Daily intake average
        avg_daily_intake = round(sum(daily_intakes.values()) / len(daily_intakes)) if daily_intakes else 0
        
        return {
            "total_logs": total_logs,
            "total_intake": total_intake,
            "avg_intake_per_log": round(total_intake / total_logs, 2),
            "avg_daily_intake": avg_daily_intake,
            "days_tracked": len(daily_intakes),
            "avg_urine_color": avg_urine_color,
            "hydration_status_hint": hydration_status_hint,
            "hydration_status_distribution": hydration_status_counts,
            "cognitive_fog_instances": cognitive_fog_count,
            "cognitive_fog_percentage": round((cognitive_fog_count / total_logs * 100), 2),
            "headache_instances": headache_count,
            "headache_percentage": round((headache_count / total_logs * 100), 2),
            "avg_energy_level": round(energy_sum / energy_count, 2) if energy_count > 0 else 0.0,
            "avg_mental_clarity": round(clarity_sum / clarity_count, 2) if clarity_count > 0 else 0.0,
            "intake_source_distribution": source_counts,
            "activity_level_distribution": activity_counts
        }


def get_water_log_service(db: AsyncIOMotorDatabase) -> WaterLogService:
    """Factory function to get water log service"""
    return WaterLogService(db)

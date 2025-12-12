"""
Food Log Service
Business logic for food logging and meal tracking
"""
from datetime import datetime, date
from typing import Optional, List, Dict
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.food_log import FoodLogInDB, FoodLogCreate, FoodLogUpdate
from ..services.habit_service import get_habit_service
from ..utils.rabbitmq.publisher import get_event_publisher
import logging

logger = logging.getLogger(__name__)


class FoodLogService:
    """Service for managing food logs"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.food_logs
        self.habit_service = get_habit_service(database)
    
    async def create_food_log(
        self,
        user_id: str,
        habit_id: str,
        log_data: FoodLogCreate
    ) -> FoodLogInDB:
        """Create a new food log entry"""
        # Verify habit exists and belongs to user
        habit = await self.habit_service.get_habit_by_id(user_id, habit_id)
        if not habit:
            raise ValueError("Habit not found")
        
        if habit.habit_type != "food":
            raise ValueError("Habit must be of type 'food'")
        
        # Create log entry
        log_dict = log_data.model_dump()
        log_dict["user_id"] = user_id
        log_dict["habit_id"] = habit_id
        log_dict["created_at"] = datetime.utcnow()
        log_dict["updated_at"] = datetime.utcnow()
        log_dict["deleted_at"] = None
        
        result = await self.collection.insert_one(log_dict)
        log_dict["_id"] = result.inserted_id
        
        food_log = FoodLogInDB(**log_dict)
        
        # Update habit streak and total_logs
        log_date = log_data.timestamp.date() if log_data.timestamp else date.today()
        await self.habit_service.update_streak(user_id, habit_id, log_date)
        
        # Publish FOOD_LOGGED event
        try:
            publisher = get_event_publisher()
            publisher.publish_food_logged(
                user_id=user_id,
                habit_id=habit_id,
                log_id=str(food_log.id),
                meal_type=food_log.meal_type,
                satisfaction=food_log.satisfaction,
                emotional_state=food_log.emotional_state,
                macros=food_log.macros,
                logged_at=food_log.timestamp
            )
        except Exception as e:
            logger.error(f"Failed to publish FOOD_LOGGED event: {e}")
        
        return food_log
    
    async def get_food_log_by_id(
        self,
        user_id: str,
        log_id: str
    ) -> Optional[FoodLogInDB]:
        """Get a specific food log by ID"""
        try:
            log_data = await self.collection.find_one({
                "_id": ObjectId(log_id),
                "user_id": user_id,
                "deleted_at": None
            })
            return FoodLogInDB(**log_data) if log_data else None
        except Exception:
            return None
    
    async def get_food_logs(
        self,
        user_id: str,
        habit_id: Optional[str] = None,
        meal_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[FoodLogInDB]:
        """Get food logs with optional filters"""
        query = {
            "user_id": user_id,
            "deleted_at": None
        }
        
        if habit_id:
            query["habit_id"] = habit_id
        
        if meal_type:
            query["meal_type"] = meal_type
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        cursor = self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        logs = await cursor.to_list(length=limit)
        return [FoodLogInDB(**log) for log in logs]
    
    async def update_food_log(
        self,
        user_id: str,
        log_id: str,
        log_update: FoodLogUpdate
    ) -> Optional[FoodLogInDB]:
        """Update a food log"""
        update_data = {
            k: v for k, v in log_update.model_dump(exclude_unset=True).items()
            if v is not None
        }
        
        if not update_data:
            return await self.get_food_log_by_id(user_id, log_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            result = await self.collection.find_one_and_update(
                {
                    "_id": ObjectId(log_id),
                    "user_id": user_id,
                    "deleted_at": None
                },
                {"$set": update_data},
                return_document=True
            )
            return FoodLogInDB(**result) if result else None
        except Exception:
            return None
    
    async def delete_food_log(
        self,
        user_id: str,
        log_id: str
    ) -> bool:
        """Soft delete a food log"""
        try:
            result = await self.collection.update_one(
                {
                    "_id": ObjectId(log_id),
                    "user_id": user_id,
                    "deleted_at": None
                },
                {
                    "$set": {
                        "deleted_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def get_food_log_stats(
        self,
        user_id: str,
        habit_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get statistics for food logs"""
        match_query = {
            "user_id": user_id,
            "deleted_at": None
        }
        
        if habit_id:
            match_query["habit_id"] = habit_id
        
        if start_date or end_date:
            match_query["timestamp"] = {}
            if start_date:
                match_query["timestamp"]["$gte"] = start_date
            if end_date:
                match_query["timestamp"]["$lte"] = end_date
        
        pipeline = [
            {"$match": match_query},
            {
                "$group": {
                    "_id": None,
                    "total_logs": {"$sum": 1},
                    "avg_calories": {"$avg": "$calories"},
                    "avg_hunger": {"$avg": "$hunger_level"},
                    "avg_satisfaction": {"$avg": "$satisfaction_level"},
                    "avg_distraction": {"$avg": "$distraction_level"},
                    "meal_type_breakdown": {
                        "$push": "$meal_type"
                    },
                    "common_locations": {
                        "$push": "$location"
                    },
                    "emotional_states": {
                        "$push": "$emotional_state"
                    }
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        
        if not result:
            return {
                "total_logs": 0,
                "avg_calories": None,
                "avg_hunger": None,
                "avg_satisfaction": None,
                "avg_distraction": None,
                "meal_type_distribution": {},
                "location_distribution": {},
                "emotional_state_distribution": {}
            }
        
        stats = result[0]
        
        # Calculate distributions
        from collections import Counter
        meal_types = Counter([m for m in stats.get("meal_type_breakdown", []) if m])
        locations = Counter([l for l in stats.get("common_locations", []) if l])
        emotions = Counter([e for e in stats.get("emotional_states", []) if e])
        
        return {
            "total_logs": stats.get("total_logs", 0),
            "avg_calories": round(stats.get("avg_calories", 0), 1) if stats.get("avg_calories") else None,
            "avg_hunger": round(stats.get("avg_hunger", 1), 1) if stats.get("avg_hunger") else None,
            "avg_satisfaction": round(stats.get("avg_satisfaction", 1), 1) if stats.get("avg_satisfaction") else None,
            "avg_distraction": round(stats.get("avg_distraction", 1), 1) if stats.get("avg_distraction") else None,
            "meal_type_distribution": dict(meal_types),
            "location_distribution": dict(locations),
            "emotional_state_distribution": dict(emotions)
        }


def get_food_log_service(database: AsyncIOMotorDatabase) -> FoodLogService:
    """Get or create food log service instance"""
    return FoodLogService(database)

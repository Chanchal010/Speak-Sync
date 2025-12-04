"""
Habit service - Business logic for habit management
"""
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.habit import HabitCreate, HabitUpdate, HabitInDB, HabitResponse
from ..database.mongodb import COLLECTIONS
from ..utils.rabbitmq.publisher import get_event_publisher
import logging

logger = logging.getLogger(__name__)

class HabitService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database[COLLECTIONS["habits"]]
    
    async def create_habit(self, user_id: str, habit_data: HabitCreate) -> HabitInDB:
        """Create a new habit"""
        habit_dict = habit_data.model_dump()
        habit_dict["user_id"] = user_id
        habit_dict["created_at"] = datetime.utcnow()
        habit_dict["updated_at"] = datetime.utcnow()
        habit_dict["deleted_at"] = None
        
        result = await self.collection.insert_one(habit_dict)
        habit_dict["_id"] = result.inserted_id
        
        habit = HabitInDB(**habit_dict)
        
        # Publish HABIT_CREATED event
        try:
            publisher = get_event_publisher()
            publisher.publish_habit_created(
                user_id=user_id,
                habit_id=str(habit.id),
                habit_type=habit.habit_type,
                name=habit.name,
                frequency=habit.frequency,
                target_value=habit.target_value,
                target_unit=habit.target_unit
            )
        except Exception as e:
            logger.error(f"Failed to publish HABIT_CREATED event: {e}")
        
        return habit
    
    async def get_habit_by_id(self, user_id: str, habit_id: str) -> Optional[HabitInDB]:
        """Get a single habit by ID"""
        if not ObjectId.is_valid(habit_id):
            return None
        
        habit = await self.collection.find_one({
            "_id": ObjectId(habit_id),
            "user_id": user_id,
            "deleted_at": None
        })
        
        if habit:
            return HabitInDB(**habit)
        return None
    
    async def get_user_habits(
        self, 
        user_id: str, 
        habit_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[HabitInDB]:
        """Get all habits for a user with optional filters"""
        query: Dict[str, Any] = {
            "user_id": user_id,
            "deleted_at": None
        }
        
        if habit_type:
            query["habit_type"] = habit_type
        
        if is_active is not None:
            query["is_active"] = is_active
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        habits = await cursor.to_list(length=limit)
        
        return [HabitInDB(**habit) for habit in habits]
    
    async def update_habit(
        self, 
        user_id: str, 
        habit_id: str, 
        habit_update: HabitUpdate
    ) -> Optional[HabitInDB]:
        """Update a habit"""
        if not ObjectId.is_valid(habit_id):
            return None
        
        update_data = habit_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_habit_by_id(user_id, habit_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {
                "_id": ObjectId(habit_id),
                "user_id": user_id,
                "deleted_at": None
            },
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            return HabitInDB(**result)
        return None
    
    async def delete_habit(self, user_id: str, habit_id: str) -> bool:
        """Soft delete a habit"""
        if not ObjectId.is_valid(habit_id):
            return False
        
        result = await self.collection.update_one(
            {
                "_id": ObjectId(habit_id),
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
    
    async def update_streak(
        self,
        user_id: str,
        habit_id: str,
        last_log_date: date
    ) -> Optional[HabitInDB]:
        """Update habit streak after logging"""
        if not ObjectId.is_valid(habit_id):
            return None
        
        habit = await self.get_habit_by_id(user_id, habit_id)
        if not habit:
            return None
        
        # Calculate streak
        today = datetime.utcnow().date()
        last_log = last_log_date if isinstance(last_log_date, date) else last_log_date.date()
        
        days_diff = (today - last_log).days
        
        if days_diff == 0:
            # Same day log, maintain streak
            new_streak = habit.current_streak
        elif days_diff == 1:
            # Consecutive day, increment streak
            new_streak = habit.current_streak + 1
        else:
            # Streak broken, reset to 1
            new_streak = 1
        
        # Update longest streak if needed
        new_longest = max(habit.longest_streak, new_streak)
        
        result = await self.collection.find_one_and_update(
            {
                "_id": ObjectId(habit_id),
                "user_id": user_id,
                "deleted_at": None
            },
            {
                "$set": {
                    "current_streak": new_streak,
                    "longest_streak": new_longest,
                    "updated_at": datetime.utcnow()
                },
                "$inc": {"total_logs": 1}
            },
            return_document=True
        )
        
        if result:
            return HabitInDB(**result)
        return None
    
    async def get_habit_stats(self, user_id: str) -> Dict[str, Any]:
        """Get habit statistics for a user"""
        pipeline = [
            {"$match": {"user_id": user_id, "deleted_at": None}},
            {"$group": {
                "_id": "$habit_type",
                "count": {"$sum": 1},
                "total_logs": {"$sum": "$total_logs"},
                "avg_streak": {"$avg": "$current_streak"},
                "max_streak": {"$max": "$longest_streak"}
            }}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        stats = await cursor.to_list(length=None)
        
        total_habits = await self.collection.count_documents({
            "user_id": user_id,
            "deleted_at": None
        })
        
        active_habits = await self.collection.count_documents({
            "user_id": user_id,
            "is_active": True,
            "deleted_at": None
        })
        
        return {
            "total_habits": total_habits,
            "active_habits": active_habits,
            "by_type": stats
        }

# Singleton instance
_habit_service: Optional[HabitService] = None

def get_habit_service(database: AsyncIOMotorDatabase) -> HabitService:
    """Get or create habit service instance"""
    global _habit_service
    if _habit_service is None:
        _habit_service = HabitService(database)
    return _habit_service

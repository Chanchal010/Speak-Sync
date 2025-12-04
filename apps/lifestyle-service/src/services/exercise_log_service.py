"""
Exercise Log Service
Business logic for exercise logging and workout tracking
"""
from datetime import datetime, date
from typing import Optional, List, Dict
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.exercise_log import ExerciseLogInDB, ExerciseLogCreate, ExerciseLogUpdate
from ..services.habit_service import get_habit_service


class ExerciseLogService:
    """Service for managing exercise logs"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.exercise_logs
        self.habit_service = get_habit_service(database)
    
    async def create_exercise_log(
        self,
        user_id: str,
        habit_id: str,
        log_data: ExerciseLogCreate
    ) -> ExerciseLogInDB:
        """Create a new exercise log entry"""
        # Verify habit exists and belongs to user
        habit = await self.habit_service.get_habit_by_id(user_id, habit_id)
        if not habit:
            raise ValueError("Habit not found")
        
        if habit.habit_type != "exercise":
            raise ValueError("Habit must be of type 'exercise'")
        
        # Create log entry
        log_dict = log_data.model_dump()
        log_dict["user_id"] = user_id
        log_dict["habit_id"] = habit_id
        log_dict["created_at"] = datetime.utcnow()
        log_dict["updated_at"] = datetime.utcnow()
        log_dict["deleted_at"] = None
        
        result = await self.collection.insert_one(log_dict)
        log_dict["_id"] = result.inserted_id
        
        # Update habit streak and total_logs
        log_date = log_data.timestamp.date() if log_data.timestamp else date.today()
        await self.habit_service.update_streak(user_id, habit_id, log_date)
        
        return ExerciseLogInDB(**log_dict)
    
    async def get_exercise_log_by_id(
        self,
        user_id: str,
        log_id: str
    ) -> Optional[ExerciseLogInDB]:
        """Get a specific exercise log by ID"""
        try:
            log_data = await self.collection.find_one({
                "_id": ObjectId(log_id),
                "user_id": user_id,
                "deleted_at": None
            })
            return ExerciseLogInDB(**log_data) if log_data else None
        except Exception:
            return None
    
    async def get_exercise_logs(
        self,
        user_id: str,
        habit_id: Optional[str] = None,
        activity_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ExerciseLogInDB]:
        """Get exercise logs with optional filters"""
        query = {
            "user_id": user_id,
            "deleted_at": None
        }
        
        if habit_id:
            query["habit_id"] = habit_id
        
        if activity_type:
            query["activity_type"] = activity_type
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        cursor = self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        logs = await cursor.to_list(length=limit)
        return [ExerciseLogInDB(**log) for log in logs]
    
    async def update_exercise_log(
        self,
        user_id: str,
        log_id: str,
        log_update: ExerciseLogUpdate
    ) -> Optional[ExerciseLogInDB]:
        """Update an exercise log"""
        update_data = {
            k: v for k, v in log_update.model_dump(exclude_unset=True).items()
            if v is not None
        }
        
        if not update_data:
            return await self.get_exercise_log_by_id(user_id, log_id)
        
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
            return ExerciseLogInDB(**result) if result else None
        except Exception:
            return None
    
    async def delete_exercise_log(
        self,
        user_id: str,
        log_id: str
    ) -> bool:
        """Soft delete an exercise log"""
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
    
    async def get_exercise_log_stats(
        self,
        user_id: str,
        habit_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get statistics for exercise logs"""
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
                    "total_duration": {"$sum": "$duration"},
                    "avg_duration": {"$avg": "$duration"},
                    "avg_rpe": {"$avg": "$rpe"},
                    "avg_post_energy": {"$avg": "$post_activity_energy"},
                    "avg_motivation": {"$avg": "$motivation_level"},
                    "total_calories": {"$sum": "$calories_burned"},
                    "total_distance": {"$sum": "$distance"},
                    "activity_types": {"$push": "$activity_type"},
                    "locations": {"$push": "$location"},
                    "workout_types": {"$push": "$workout_type"},
                    "moods_before": {"$push": "$mood_before"},
                    "moods_after": {"$push": "$mood_after"}
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        
        if not result:
            return {
                "total_logs": 0,
                "total_duration": 0,
                "avg_duration": None,
                "avg_rpe": None,
                "avg_post_energy": None,
                "avg_motivation": None,
                "total_calories": None,
                "total_distance": None,
                "activity_distribution": {},
                "location_distribution": {},
                "workout_type_distribution": {},
                "mood_before_distribution": {},
                "mood_after_distribution": {}
            }
        
        stats = result[0]
        
        # Calculate distributions
        from collections import Counter
        activities = Counter([a for a in stats.get("activity_types", []) if a])
        locations = Counter([l for l in stats.get("locations", []) if l])
        workout_types = Counter([w for w in stats.get("workout_types", []) if w])
        moods_before = Counter([m for m in stats.get("moods_before", []) if m])
        moods_after = Counter([m for m in stats.get("moods_after", []) if m])
        
        return {
            "total_logs": stats.get("total_logs", 0),
            "total_duration": stats.get("total_duration", 0),
            "avg_duration": round(stats.get("avg_duration", 0), 1) if stats.get("avg_duration") else None,
            "avg_rpe": round(stats.get("avg_rpe", 0), 1) if stats.get("avg_rpe") else None,
            "avg_post_energy": round(stats.get("avg_post_energy", 0), 1) if stats.get("avg_post_energy") else None,
            "avg_motivation": round(stats.get("avg_motivation", 0), 1) if stats.get("avg_motivation") else None,
            "total_calories": stats.get("total_calories"),
            "total_distance": round(stats.get("total_distance", 0), 2) if stats.get("total_distance") else None,
            "activity_distribution": dict(activities),
            "location_distribution": dict(locations),
            "workout_type_distribution": dict(workout_types),
            "mood_before_distribution": dict(moods_before),
            "mood_after_distribution": dict(moods_after)
        }


def get_exercise_log_service(database: AsyncIOMotorDatabase) -> ExerciseLogService:
    """Get or create exercise log service instance"""
    return ExerciseLogService(database)

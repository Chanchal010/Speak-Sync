"""
Sleep Log Service
Business logic for sleep tracking, chronotype detection, and sleep debt calculation
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.sleep_log import SleepLogInDB, SleepLogCreate, SleepLogUpdate
from .habit_service import HabitService, get_habit_service
from ..utils.rabbitmq.publisher import get_event_publisher
import logging

logger = logging.getLogger(__name__)


class SleepLogService:
    """Service for sleep log operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["sleep_logs"]
        self.habit_service = get_habit_service(db)
    
    def _calculate_sleep_duration(self, bedtime: datetime, wake_time: datetime) -> float:
        """Calculate sleep duration in hours"""
        duration = wake_time - bedtime
        return round(duration.total_seconds() / 3600, 2)
    
    async def create_sleep_log(
        self,
        user_id: str,
        habit_id: str,
        log_data: SleepLogCreate
    ) -> SleepLogInDB:
        """Create a new sleep log entry"""
        # Verify habit exists and is sleep type
        habit = await self.habit_service.get_habit_by_id(user_id, habit_id)
        if not habit:
            raise ValueError("Habit not found")
        if habit.habit_type != "sleep":
            raise ValueError("Habit must be of type 'sleep'")
        
        # Create log
        log_dict = log_data.model_dump()
        log_dict["user_id"] = user_id
        
        # Calculate sleep duration
        if not log_dict.get("sleep_duration"):
            log_dict["sleep_duration"] = self._calculate_sleep_duration(
                log_dict["bedtime"], 
                log_dict["wake_time"]
            )
        
        # Calculate sleep debt (if target hours provided)
        if log_dict.get("target_sleep_hours"):
            actual_sleep = log_dict["sleep_duration"]
            target_sleep = log_dict["target_sleep_hours"]
            log_dict["sleep_debt"] = round(target_sleep - actual_sleep, 2)
        
        log_dict["timestamp"] = datetime.utcnow()
        log_dict["created_at"] = datetime.utcnow()
        log_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(log_dict)
        log_dict["_id"] = result.inserted_id
        
        sleep_log = SleepLogInDB(**log_dict)
        
        # Update habit streak and count
        log_date = log_dict["wake_time"].date() if isinstance(log_dict["wake_time"], datetime) else log_dict["wake_time"]
        await self.habit_service.update_streak(user_id, habit_id, log_date)
        
        # Publish SLEEP_LOGGED event
        try:
            publisher = get_event_publisher()
            publisher.publish_sleep_logged(
                user_id=user_id,
                habit_id=habit_id,
                log_id=str(sleep_log.id),
                bedtime=sleep_log.bedtime,
                wake_time=sleep_log.wake_time,
                duration=int(sleep_log.sleep_duration * 60),  # Convert hours to minutes
                quality=sleep_log.sleep_quality,
                interruptions=sleep_log.interruptions or 0,
                logged_at=sleep_log.timestamp
            )
        except Exception as e:
            logger.error(f"Failed to publish SLEEP_LOGGED event: {e}")
        
        return sleep_log
    
    async def get_sleep_log_by_id(
        self,
        user_id: str,
        log_id: str
    ) -> Optional[SleepLogInDB]:
        """Get a specific sleep log"""
        from bson import ObjectId
        
        log_dict = await self.collection.find_one({
            "_id": ObjectId(log_id),
            "user_id": user_id,
            "deleted_at": None
        })
        
        if log_dict:
            return SleepLogInDB(**log_dict)
        return None
    
    async def get_sleep_logs(
        self,
        user_id: str,
        habit_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[SleepLogInDB]:
        """Get sleep logs with filters"""
        query: Dict[str, Any] = {
            "user_id": user_id,
            "deleted_at": None
        }
        
        if habit_id:
            query["habit_id"] = habit_id
        if start_date or end_date:
            query["wake_time"] = {}
            if start_date:
                query["wake_time"]["$gte"] = start_date
            if end_date:
                query["wake_time"]["$lte"] = end_date
        
        cursor = self.collection.find(query).sort("wake_time", -1).skip(skip).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        return [SleepLogInDB(**log) for log in logs]
    
    async def update_sleep_log(
        self,
        user_id: str,
        log_id: str,
        update_data: SleepLogUpdate
    ) -> Optional[SleepLogInDB]:
        """Update a sleep log"""
        from bson import ObjectId
        
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        if not update_dict:
            return await self.get_sleep_log_by_id(user_id, log_id)
        
        # Recalculate sleep duration if bedtime or wake_time changed
        current_log = await self.get_sleep_log_by_id(user_id, log_id)
        if current_log:
            bedtime = update_dict.get("bedtime", current_log.bedtime)
            wake_time = update_dict.get("wake_time", current_log.wake_time)
            update_dict["sleep_duration"] = self._calculate_sleep_duration(bedtime, wake_time)
            
            # Recalculate sleep debt if target changed
            if update_dict.get("target_sleep_hours"):
                update_dict["sleep_debt"] = round(
                    update_dict["target_sleep_hours"] - update_dict["sleep_duration"], 2
                )
        
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(log_id), "user_id": user_id, "deleted_at": None},
            {"$set": update_dict},
            return_document=True
        )
        
        if result:
            return SleepLogInDB(**result)
        return None
    
    async def delete_sleep_log(
        self,
        user_id: str,
        log_id: str
    ) -> bool:
        """Soft delete a sleep log"""
        from bson import ObjectId
        
        result = await self.collection.update_one(
            {"_id": ObjectId(log_id), "user_id": user_id, "deleted_at": None},
            {"$set": {"deleted_at": datetime.utcnow(), "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    async def get_sleep_log_stats(
        self,
        user_id: str,
        habit_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get sleep statistics with chronotype analysis"""
        match_stage: Dict[str, Any] = {
            "user_id": user_id,
            "deleted_at": None
        }
        
        if habit_id:
            match_stage["habit_id"] = habit_id
        if start_date or end_date:
            match_stage["wake_time"] = {}
            if start_date:
                match_stage["wake_time"]["$gte"] = start_date
            if end_date:
                match_stage["wake_time"]["$lte"] = end_date
        
        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": None,
                    "total_logs": {"$sum": 1},
                    "avg_sleep_duration": {"$avg": "$sleep_duration"},
                    "avg_sleep_quality": {"$avg": "$sleep_quality"},
                    "avg_grogginess": {"$avg": "$grogginess_level"},
                    "avg_sleep_latency": {"$avg": "$sleep_latency"},
                    "avg_times_awakened": {"$avg": "$times_awakened"},
                    "total_sleep_debt": {"$sum": "$sleep_debt"},
                    "nights_felt_rested": {
                        "$sum": {"$cond": ["$felt_rested", 1, 0]}
                    },
                    "nights_used_alarm": {
                        "$sum": {"$cond": ["$used_alarm", 1, 0]}
                    },
                    "pre_sleep_activities": {"$push": "$pre_sleep_activity"},
                    "moods_on_waking": {"$push": "$mood_on_waking"},
                    "room_temps": {"$push": "$room_temperature"},
                    "bedtimes": {"$push": "$bedtime"},
                    "wake_times": {"$push": "$wake_time"}
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        
        if not result:
            return {
                "total_logs": 0,
                "avg_sleep_duration": 0,
                "avg_sleep_quality": 0,
                "avg_grogginess": 0,
                "avg_sleep_latency": 0,
                "avg_times_awakened": 0,
                "total_sleep_debt": 0,
                "rested_percentage": 0,
                "alarm_usage_percentage": 0,
                "pre_sleep_activity_distribution": {},
                "mood_distribution": {},
                "room_temperature_distribution": {},
                "avg_bedtime": None,
                "avg_wake_time": None
            }
        
        stats = result[0]
        total_logs = stats["total_logs"]
        
        # Calculate distributions
        activity_dist = {}
        for activity in stats["pre_sleep_activities"]:
            if activity:
                activity_dist[activity] = activity_dist.get(activity, 0) + 1
        
        mood_dist = {}
        for mood in stats["moods_on_waking"]:
            if mood:
                mood_dist[mood] = mood_dist.get(mood, 0) + 1
        
        temp_dist = {}
        for temp in stats["room_temps"]:
            if temp:
                temp_dist[temp] = temp_dist.get(temp, 0) + 1
        
        # Calculate average bedtime and wake time (for chronotype detection)
        avg_bedtime_hour = None
        avg_wake_time_hour = None
        if stats["bedtimes"]:
            bedtime_hours = [bt.hour + bt.minute/60 for bt in stats["bedtimes"] if bt]
            avg_bedtime_hour = round(sum(bedtime_hours) / len(bedtime_hours), 1) if bedtime_hours else None
        if stats["wake_times"]:
            wake_time_hours = [wt.hour + wt.minute/60 for wt in stats["wake_times"] if wt]
            avg_wake_time_hour = round(sum(wake_time_hours) / len(wake_time_hours), 1) if wake_time_hours else None
        
        return {
            "total_logs": total_logs,
            "avg_sleep_duration": round(stats["avg_sleep_duration"], 2) if stats["avg_sleep_duration"] else 0,
            "avg_sleep_quality": round(stats["avg_sleep_quality"], 2) if stats["avg_sleep_quality"] else 0,
            "avg_grogginess": round(stats["avg_grogginess"], 2) if stats["avg_grogginess"] else 0,
            "avg_sleep_latency": round(stats["avg_sleep_latency"], 2) if stats["avg_sleep_latency"] else 0,
            "avg_times_awakened": round(stats["avg_times_awakened"], 2) if stats["avg_times_awakened"] else 0,
            "total_sleep_debt": round(stats["total_sleep_debt"] or 0, 2),
            "rested_percentage": round((stats["nights_felt_rested"] / total_logs * 100), 2) if total_logs > 0 else 0,
            "alarm_usage_percentage": round((stats["nights_used_alarm"] / total_logs * 100), 2) if total_logs > 0 else 0,
            "pre_sleep_activity_distribution": activity_dist,
            "mood_distribution": mood_dist,
            "room_temperature_distribution": temp_dist,
            "avg_bedtime_hour": avg_bedtime_hour,
            "avg_wake_time_hour": avg_wake_time_hour,
            "chronotype_hint": self._detect_chronotype(avg_bedtime_hour, avg_wake_time_hour)
        }
    
    def _detect_chronotype(self, avg_bedtime: Optional[float], avg_wake: Optional[float]) -> str:
        """Detect chronotype based on sleep patterns"""
        if not avg_bedtime or not avg_wake:
            return "insufficient_data"
        
        # Early bird: bedtime before 22:00 (22.0), wake before 6:00 (6.0)
        if avg_bedtime < 22.0 and avg_wake < 6.0:
            return "early_bird"
        # Night owl: bedtime after 00:00 (24.0), wake after 8:00 (8.0)
        elif avg_bedtime > 24.0 or (avg_bedtime < 2.0 and avg_wake > 8.0):
            return "night_owl"
        # Intermediate
        else:
            return "intermediate"


def get_sleep_log_service(db: AsyncIOMotorDatabase) -> SleepLogService:
    """Factory function to get sleep log service"""
    return SleepLogService(db)

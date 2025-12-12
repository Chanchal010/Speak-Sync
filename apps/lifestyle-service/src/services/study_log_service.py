"""
Study Log Service for business logic
"""
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from ..models.study_log import StudyLogCreate, StudyLogUpdate, StudyLogInDB, StudyLogResponse
from .habit_service import HabitService
from ..utils.rabbitmq.publisher import get_event_publisher
import logging

logger = logging.getLogger(__name__)


class StudyLogService:
    """Service for managing study logs with stickiness factor"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.study_logs
        self.habit_service = HabitService(db)
    
    def _calculate_deviation(
        self,
        scheduled_start: datetime,
        scheduled_end: datetime,
        actual_start: datetime,
        actual_end: datetime
    ) -> float:
        """Calculate total deviation from schedule in minutes"""
        start_deviation = abs((actual_start - scheduled_start).total_seconds() / 60)
        end_deviation = abs((actual_end - scheduled_end).total_seconds() / 60)
        return round(start_deviation + end_deviation, 2)
    
    def _calculate_stickiness_percentage(self, deviation_minutes: float, planned_duration_minutes: float) -> float:
        """Calculate stickiness as percentage adherence to schedule"""
        if planned_duration_minutes == 0:
            return 0.0
        # Stickiness = 100% - (deviation as percentage of planned duration)
        deviation_percentage = (deviation_minutes / planned_duration_minutes) * 100
        stickiness = max(0.0, 100.0 - deviation_percentage)
        return round(stickiness, 2)
    
    async def create_study_log(
        self,
        user_id: str,
        log_data: StudyLogCreate
    ) -> StudyLogInDB:
        """Create a new study log with automatic deviation calculation"""
        # Validate habit
        habit_id = log_data.habit_id
        if not ObjectId.is_valid(habit_id):
            raise ValueError("Invalid habit ID")
        
        habit = await self.habit_service.get_habit_by_id(user_id, habit_id)
        if not habit:
            raise ValueError("Habit not found")
        if habit.habit_type != "study":
            raise ValueError("Habit must be of type 'study'")
        
        # Create log
        log_dict = log_data.model_dump()
        log_dict["user_id"] = user_id
        
        # Calculate deviation from schedule
        if not log_dict.get("deviation_duration"):
            log_dict["deviation_duration"] = self._calculate_deviation(
                log_dict["scheduled_start"],
                log_dict["scheduled_end"],
                log_dict["actual_start"],
                log_dict["actual_end"]
            )
        
        log_dict["timestamp"] = datetime.utcnow()
        log_dict["created_at"] = datetime.utcnow()
        log_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(log_dict)
        log_dict["_id"] = result.inserted_id
        
        study_log = StudyLogInDB(**log_dict)
        
        # Update habit streak and count
        log_date = log_dict["actual_start"].date() if isinstance(log_dict["actual_start"], datetime) else log_dict["actual_start"]
        await self.habit_service.update_streak(user_id, habit_id, log_date)
        
        # Publish STUDY_LOGGED event
        try:
            publisher = get_event_publisher()
            duration = int((study_log.actual_end - study_log.actual_start).total_seconds() / 60)
            publisher.publish_study_logged(
                user_id=user_id,
                habit_id=habit_id,
                log_id=str(study_log.id),
                task_id=study_log.task_id,
                duration=duration,
                flow_state=study_log.flow_state or False,
                stickiness_percentage=study_log.stickiness_percentage or 0,
                logged_at=study_log.timestamp
            )
        except Exception as e:
            logger.error(f"Failed to publish STUDY_LOGGED event: {e}")
        
        return study_log
    
    async def get_study_log_by_id(
        self,
        user_id: str,
        log_id: str
    ) -> Optional[StudyLogInDB]:
        """Get a specific study log"""
        if not ObjectId.is_valid(log_id):
            return None
        
        log = await self.collection.find_one({
            "_id": ObjectId(log_id),
            "user_id": user_id,
            "deleted_at": None
        })
        
        if log:
            return StudyLogInDB(**log)
        return None
    
    async def get_study_logs(
        self,
        user_id: str,
        habit_id: Optional[str] = None,
        task_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[StudyLogInDB]:
        """Get study logs with optional filters"""
        query: Dict[str, Any] = {
            "user_id": user_id,
            "deleted_at": None
        }
        
        if habit_id:
            if not ObjectId.is_valid(habit_id):
                return []
            query["habit_id"] = habit_id
        
        if task_id:
            query["task_id"] = task_id
        
        if start_date or end_date:
            query["actual_start"] = {}
            if start_date:
                query["actual_start"]["$gte"] = start_date
            if end_date:
                query["actual_start"]["$lte"] = end_date
        
        cursor = self.collection.find(query).sort("actual_start", -1).skip(skip).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        return [StudyLogInDB(**log) for log in logs]
    
    async def update_study_log(
        self,
        user_id: str,
        log_id: str,
        update_data: StudyLogUpdate
    ) -> Optional[StudyLogInDB]:
        """Update a study log and recalculate deviation if times changed"""
        if not ObjectId.is_valid(log_id):
            return None
        
        existing_log = await self.get_study_log_by_id(user_id, log_id)
        if not existing_log:
            return None
        
        update_dict = {k: v for k, v in update_data.model_dump(exclude_unset=True).items() if v is not None}
        
        # Recalculate deviation if any time fields changed
        time_fields = ["scheduled_start", "scheduled_end", "actual_start", "actual_end"]
        if any(field in update_dict for field in time_fields):
            # Get all time values (updated or existing)
            scheduled_start = update_dict.get("scheduled_start", existing_log.scheduled_start)
            scheduled_end = update_dict.get("scheduled_end", existing_log.scheduled_end)
            actual_start = update_dict.get("actual_start", existing_log.actual_start)
            actual_end = update_dict.get("actual_end", existing_log.actual_end)
            
            update_dict["deviation_duration"] = self._calculate_deviation(
                scheduled_start, scheduled_end, actual_start, actual_end
            )
        
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(log_id), "user_id": user_id, "deleted_at": None},
            {"$set": update_dict},
            return_document=True
        )
        
        if result:
            return StudyLogInDB(**result)
        return None
    
    async def delete_study_log(
        self,
        user_id: str,
        log_id: str
    ) -> bool:
        """Soft delete a study log"""
        if not ObjectId.is_valid(log_id):
            return False
        
        result = await self.collection.update_one(
            {"_id": ObjectId(log_id), "user_id": user_id, "deleted_at": None},
            {"$set": {"deleted_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    async def get_study_log_stats(
        self,
        user_id: str,
        habit_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get study log statistics with stickiness metrics"""
        query: Dict[str, Any] = {
            "user_id": user_id,
            "deleted_at": None
        }
        
        if habit_id:
            if not ObjectId.is_valid(habit_id):
                return {}
            query["habit_id"] = habit_id
        
        if start_date or end_date:
            query["actual_start"] = {}
            if start_date:
                query["actual_start"]["$gte"] = start_date
            if end_date:
                query["actual_start"]["$lte"] = end_date
        
        logs = await self.collection.find(query).to_list(length=None)
        
        if not logs:
            return {
                "total_logs": 0,
                "total_study_time": 0.0,
                "avg_deviation": 0.0,
                "avg_stickiness_percentage": 0.0,
                "avg_flow_state": 0.0,
                "avg_interruptions": 0.0,
                "task_completion_rate": 0.0,
                "high_flow_sessions": 0,
                "low_flow_sessions": 0
            }
        
        total_logs = len(logs)
        total_study_minutes = 0.0
        total_deviation = 0.0
        total_stickiness = 0.0
        total_flow_state = 0.0
        total_interruptions = 0.0
        tasks_with_completion = 0
        tasks_completed = 0
        high_flow_count = 0  # flow_state >= 8
        low_flow_count = 0   # flow_state <= 3
        
        # Distributions
        distraction_counts: Dict[str, int] = {}
        method_counts: Dict[str, int] = {}
        location_counts: Dict[str, int] = {}
        
        for log in logs:
            # Study time (actual duration in minutes)
            actual_start = log.get("actual_start")
            actual_end = log.get("actual_end")
            if actual_start and actual_end:
                duration = (actual_end - actual_start).total_seconds() / 60
                total_study_minutes += duration
                
                # Calculate stickiness for this session
                scheduled_start = log.get("scheduled_start")
                scheduled_end = log.get("scheduled_end")
                if scheduled_start and scheduled_end:
                    planned_duration = (scheduled_end - scheduled_start).total_seconds() / 60
                    deviation = log.get("deviation_duration", 0)
                    stickiness = self._calculate_stickiness_percentage(deviation, planned_duration)
                    total_stickiness += stickiness
            
            # Deviation
            total_deviation += log.get("deviation_duration", 0)
            
            # Flow state
            flow_score = log.get("flow_state_score", 0)
            total_flow_state += flow_score
            if flow_score >= 8:
                high_flow_count += 1
            elif flow_score <= 3:
                low_flow_count += 1
            
            # Interruptions
            total_interruptions += log.get("interruption_count", 0)
            
            # Task completion
            if log.get("task_id"):
                tasks_with_completion += 1
                if log.get("task_completed"):
                    tasks_completed += 1
            
            # Distraction sources
            for distraction in log.get("distraction_sources", []):
                distraction_counts[distraction] = distraction_counts.get(distraction, 0) + 1
            
            # Study methods
            method = log.get("study_method")
            if method:
                method_counts[method] = method_counts.get(method, 0) + 1
            
            # Locations
            location = log.get("location")
            if location:
                location_counts[location] = location_counts.get(location, 0) + 1
        
        return {
            "total_logs": total_logs,
            "total_study_time": round(total_study_minutes, 2),
            "avg_study_duration": round(total_study_minutes / total_logs, 2),
            "avg_deviation": round(total_deviation / total_logs, 2),
            "avg_stickiness_percentage": round(total_stickiness / total_logs, 2),
            "avg_flow_state": round(total_flow_state / total_logs, 2),
            "avg_interruptions": round(total_interruptions / total_logs, 2),
            "task_completion_rate": round((tasks_completed / tasks_with_completion * 100), 2) if tasks_with_completion > 0 else 0.0,
            "high_flow_sessions": high_flow_count,
            "high_flow_percentage": round((high_flow_count / total_logs * 100), 2),
            "low_flow_sessions": low_flow_count,
            "low_flow_percentage": round((low_flow_count / total_logs * 100), 2),
            "distraction_distribution": distraction_counts,
            "study_method_distribution": method_counts,
            "location_distribution": location_counts
        }


def get_study_log_service(db: AsyncIOMotorDatabase) -> StudyLogService:
    """Factory function to get study log service"""
    return StudyLogService(db)

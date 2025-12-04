"""
Financial Log Service
Business logic for spending tracking and financial habit analysis
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.financial_log import FinancialLogInDB, FinancialLogCreate, FinancialLogUpdate
from .habit_service import HabitService, get_habit_service


class FinancialLogService:
    """Service for financial log operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["financial_logs"]
        self.habit_service = get_habit_service(db)
    
    async def create_financial_log(
        self,
        user_id: str,
        habit_id: str,
        log_data: FinancialLogCreate
    ) -> FinancialLogInDB:
        """Create a new financial log entry"""
        # Verify habit exists and is financial type
        habit = await self.habit_service.get_habit_by_id(user_id, habit_id)
        if not habit:
            raise ValueError("Habit not found")
        if habit.habit_type != "financial":
            raise ValueError("Habit must be of type 'financial'")
        
        # Create log
        log_dict = log_data.model_dump()
        log_dict["user_id"] = user_id
        log_dict["timestamp"] = datetime.utcnow()
        if not log_dict.get("time_of_purchase"):
            log_dict["time_of_purchase"] = datetime.utcnow()
        log_dict["created_at"] = datetime.utcnow()
        log_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(log_dict)
        log_dict["_id"] = result.inserted_id
        
        # Update habit streak and count
        log_date = log_dict["time_of_purchase"].date() if isinstance(log_dict["time_of_purchase"], datetime) else log_dict["time_of_purchase"]
        await self.habit_service.update_streak(habit_id, user_id, log_date)
        
        return FinancialLogInDB(**log_dict)
    
    async def get_financial_log_by_id(
        self,
        user_id: str,
        log_id: str
    ) -> Optional[FinancialLogInDB]:
        """Get a specific financial log"""
        from bson import ObjectId
        
        log_dict = await self.collection.find_one({
            "_id": ObjectId(log_id),
            "user_id": user_id,
            "deleted_at": None
        })
        
        if log_dict:
            return FinancialLogInDB(**log_dict)
        return None
    
    async def get_financial_logs(
        self,
        user_id: str,
        habit_id: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[FinancialLogInDB]:
        """Get financial logs with filters"""
        query: Dict[str, Any] = {
            "user_id": user_id,
            "deleted_at": None
        }
        
        if habit_id:
            query["habit_id"] = habit_id
        if category:
            query["category"] = category
        if start_date or end_date:
            query["time_of_purchase"] = {}
            if start_date:
                query["time_of_purchase"]["$gte"] = start_date
            if end_date:
                query["time_of_purchase"]["$lte"] = end_date
        
        cursor = self.collection.find(query).sort("time_of_purchase", -1).skip(skip).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        return [FinancialLogInDB(**log) for log in logs]
    
    async def update_financial_log(
        self,
        user_id: str,
        log_id: str,
        update_data: FinancialLogUpdate
    ) -> Optional[FinancialLogInDB]:
        """Update a financial log"""
        from bson import ObjectId
        
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        if not update_dict:
            return await self.get_financial_log_by_id(user_id, log_id)
        
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(log_id), "user_id": user_id, "deleted_at": None},
            {"$set": update_dict},
            return_document=True
        )
        
        if result:
            return FinancialLogInDB(**result)
        return None
    
    async def delete_financial_log(
        self,
        user_id: str,
        log_id: str
    ) -> bool:
        """Soft delete a financial log"""
        from bson import ObjectId
        
        result = await self.collection.update_one(
            {"_id": ObjectId(log_id), "user_id": user_id, "deleted_at": None},
            {"$set": {"deleted_at": datetime.utcnow(), "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    async def get_financial_log_stats(
        self,
        user_id: str,
        habit_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get financial statistics with spending insights"""
        match_stage: Dict[str, Any] = {
            "user_id": user_id,
            "deleted_at": None
        }
        
        if habit_id:
            match_stage["habit_id"] = habit_id
        if start_date or end_date:
            match_stage["time_of_purchase"] = {}
            if start_date:
                match_stage["time_of_purchase"]["$gte"] = start_date
            if end_date:
                match_stage["time_of_purchase"]["$lte"] = end_date
        
        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": None,
                    "total_logs": {"$sum": 1},
                    "total_spent": {"$sum": "$amount"},
                    "avg_amount": {"$avg": "$amount"},
                    "avg_necessity": {"$avg": "$necessity_score"},
                    "avg_regret": {"$avg": "$regret_level"},
                    "impulse_count": {
                        "$sum": {"$cond": ["$impulse_buy", 1, 0]}
                    },
                    "total_savings": {"$sum": "$savings_allocation"},
                    "categories": {"$push": "$category"},
                    "moods": {"$push": "$associated_mood"},
                    "triggers": {"$push": "$emotional_trigger"},
                    "locations": {"$push": "$location"}
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        
        if not result:
            return {
                "total_logs": 0,
                "total_spent": 0,
                "avg_amount": 0,
                "avg_necessity": 0,
                "avg_regret": 0,
                "impulse_count": 0,
                "impulse_percentage": 0,
                "total_savings": 0,
                "category_distribution": {},
                "mood_distribution": {},
                "trigger_distribution": {},
                "location_distribution": {}
            }
        
        stats = result[0]
        total_logs = stats["total_logs"]
        
        # Calculate distributions
        category_dist = {}
        for cat in stats["categories"]:
            if cat:
                category_dist[cat] = category_dist.get(cat, 0) + 1
        
        mood_dist = {}
        for mood in stats["moods"]:
            if mood:
                mood_dist[mood] = mood_dist.get(mood, 0) + 1
        
        trigger_dist = {}
        for trigger in stats["triggers"]:
            if trigger:
                trigger_dist[trigger] = trigger_dist.get(trigger, 0) + 1
        
        location_dist = {}
        for loc in stats["locations"]:
            if loc:
                location_dist[loc] = location_dist.get(loc, 0) + 1
        
        return {
            "total_logs": total_logs,
            "total_spent": round(stats["total_spent"], 2),
            "avg_amount": round(stats["avg_amount"], 2),
            "avg_necessity": round(stats["avg_necessity"], 2) if stats["avg_necessity"] else 0,
            "avg_regret": round(stats["avg_regret"], 2) if stats["avg_regret"] else 0,
            "impulse_count": stats["impulse_count"],
            "impulse_percentage": round((stats["impulse_count"] / total_logs * 100), 2) if total_logs > 0 else 0,
            "total_savings": round(stats["total_savings"] or 0, 2),
            "category_distribution": category_dist,
            "mood_distribution": mood_dist,
            "trigger_distribution": trigger_dist,
            "location_distribution": location_dist
        }


def get_financial_log_service(db: AsyncIOMotorDatabase) -> FinancialLogService:
    """Factory function to get financial log service"""
    return FinancialLogService(db)

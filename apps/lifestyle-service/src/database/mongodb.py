"""
MongoDB database configuration and connection management
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_database = os.getenv("MONGODB_DATABASE", "speak_sync_lifestyle")
    
    if not mongodb_uri:
        raise ValueError("MONGODB_URI environment variable is not set")
    
    print(f"[INFO] Connecting to MongoDB: {mongodb_database}")
    
    mongodb.client = AsyncIOMotorClient(mongodb_uri)
    mongodb.database = mongodb.client[mongodb_database]
    
    # Test connection
    try:
        await mongodb.client.admin.command('ping')
        print(f"[SUCCESS] MongoDB connected successfully to database: {mongodb_database}")
    except Exception as e:
        print(f"[ERROR] MongoDB connection failed: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        print("[INFO] MongoDB connection closed")

def get_database():
    """Get database instance"""
    return mongodb.database

# Collection names
COLLECTIONS = {
    "habits": "habits",
    "food_logs": "food_logs",
    "exercise_logs": "exercise_logs",
    "financial_logs": "financial_logs",
    "sleep_logs": "sleep_logs",
    "study_logs": "study_logs",
    "water_logs": "water_logs",
    "habit_insights": "habit_insights"
}

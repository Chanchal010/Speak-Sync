from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .database.mongodb import connect_to_mongo, close_mongo_connection, get_database
from .api.routes import habits, food_logs, exercise_logs, financial_logs, sleep_logs, study_logs, water_logs, analytics, export
from .utils.rabbitmq import init_rabbitmq, get_rabbitmq

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown"""
    # Startup
    await connect_to_mongo()
    
    # Initialize RabbitMQ in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        await loop.run_in_executor(executor, init_rabbitmq)
    
    # Create indexes
    db = get_database()
    # Habit indexes
    await db["habits"].create_index([("user_id", 1), ("deleted_at", 1)])
    await db["habits"].create_index([("user_id", 1), ("habit_type", 1)])
    await db["habits"].create_index([("user_id", 1), ("is_active", 1)])
    
    # Food log indexes
    await db["food_logs"].create_index([("user_id", 1), ("deleted_at", 1)])
    await db["food_logs"].create_index([("user_id", 1), ("habit_id", 1)])
    await db["food_logs"].create_index([("user_id", 1), ("timestamp", -1)])
    await db["food_logs"].create_index([("user_id", 1), ("meal_type", 1)])
    
    # Exercise log indexes
    await db["exercise_logs"].create_index([("user_id", 1), ("deleted_at", 1)])
    await db["exercise_logs"].create_index([("user_id", 1), ("habit_id", 1)])
    await db["exercise_logs"].create_index([("user_id", 1), ("timestamp", -1)])
    await db["exercise_logs"].create_index([("user_id", 1), ("activity_type", 1)])
    
    # Financial log indexes
    await db["financial_logs"].create_index([("user_id", 1), ("deleted_at", 1)])
    await db["financial_logs"].create_index([("user_id", 1), ("habit_id", 1)])
    await db["financial_logs"].create_index([("user_id", 1), ("time_of_purchase", -1)])
    await db["financial_logs"].create_index([("user_id", 1), ("category", 1)])
    
    # Sleep log indexes
    await db["sleep_logs"].create_index([("user_id", 1), ("deleted_at", 1)])
    await db["sleep_logs"].create_index([("user_id", 1), ("habit_id", 1)])
    await db["sleep_logs"].create_index([("user_id", 1), ("wake_time", -1)])
    await db["sleep_logs"].create_index([("user_id", 1), ("bedtime", -1)])
    
    # Study log indexes
    await db["study_logs"].create_index([("user_id", 1), ("deleted_at", 1)])
    await db["study_logs"].create_index([("user_id", 1), ("habit_id", 1)])
    await db["study_logs"].create_index([("user_id", 1), ("scheduled_start", -1)])
    await db["study_logs"].create_index([("user_id", 1), ("task_id", 1)])
    
    # Water log indexes
    await db["water_logs"].create_index([("user_id", 1), ("deleted_at", 1)])
    await db["water_logs"].create_index([("user_id", 1), ("habit_id", 1)])
    await db["water_logs"].create_index([("user_id", 1), ("timestamp", -1)])
    await db["water_logs"].create_index([("user_id", 1), ("urine_color", 1)])
    
    print("[SUCCESS] MongoDB indexes created")
    
    yield
    
    # Shutdown
    rabbitmq = get_rabbitmq()
    rabbitmq.close()
    await close_mongo_connection()

app = FastAPI(
    title="Lifestyle Service",
    description="Habit tracking and lifestyle management with AI-ready data collection",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(habits.router)
app.include_router(food_logs.router)
app.include_router(exercise_logs.router)
app.include_router(financial_logs.router)
app.include_router(sleep_logs.router)
app.include_router(study_logs.router)
app.include_router(water_logs.router)
app.include_router(analytics.router)
app.include_router(export.router)

@app.get("/health")
async def health():
    """Health check endpoint"""
    db = get_database()
    try:
        await db.command("ping")
        return {
            "status": "healthy",
            "service": "lifestyle",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "lifestyle",
            "database": "disconnected",
            "error": str(e)
        }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Lifestyle & Habit Service - LifeOS",
        "version": "1.0.0",
        "endpoints": {
            "habits": "/api/habits",
            "health": "/health",
            "docs": "/docs"
        }
    }
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

from src.api.routes import voice, chat, conversation, scheduling, habits, memory
from src.database.connection import Database, RedisClient
from src.database.vector_operations import VectorOperations
from src.services.vector_memory_service import VectorMemoryService
from src.services.supabase_realtime_service import SupabaseRealtimeService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connections
db: Database = None
redis: RedisClient = None
vector_ops: VectorOperations = None
vector_memory_service: VectorMemoryService = None
realtime_service: SupabaseRealtimeService = None  # Supabase Realtime + Storage

# gRPC server task
_grpc_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    global db, redis, vector_ops, vector_memory_service, realtime_service, _grpc_task

    # Startup
    logger.info("Starting AI Brain Service...")

    try:
        # Initialize database connections (optional for STT-only mode)
        database_url = os.getenv("DATABASE_URL")
        redis_url = os.getenv("REDIS_URL")

        if database_url and "localhost" not in database_url and "127.0.0.1" not in database_url:
            db = Database()
            await db.connect(
                database_url=database_url,
                min_size=5,
                max_size=15
            )
            logger.info("✓ PostgreSQL connected")

            # Initialize vector operations
            vector_ops = VectorOperations(db.pool)
            await vector_ops.initialize_vector_tables()
            logger.info("✓ Vector tables initialized")

            # Initialize vector memory service
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                vector_memory_service = VectorMemoryService(
                    vector_ops=vector_ops,
                    openai_api_key=openai_api_key
                )
                logger.info("✓ Vector memory service ready")
            else:
                logger.warning("⚠ OpenAI API key not configured - vector memory disabled")
        else:
            logger.warning("⚠ PostgreSQL not configured - running in STT-only mode")

        if redis_url and "localhost" not in redis_url and "127.0.0.1" not in redis_url:
            redis = RedisClient()
            await redis.connect(redis_url=redis_url)
            logger.info("✓ Redis connected")
        else:
            logger.warning("⚠ Redis not configured - caching disabled")

        # ─────────────────────────────────────────────
        # START gRPC SERVER (port 50051) alongside REST
        # ─────────────────────────────────────────────
        try:
            from src.grpc_server import serve as grpc_serve
            grpc_port = int(os.getenv("GRPC_PORT", 50051))
            _grpc_task = asyncio.create_task(
                grpc_serve(host="0.0.0.0", port=grpc_port)
            )
            logger.info(f"✓ gRPC server started on port {grpc_port}")
        except Exception as grpc_err:
            logger.warning(f"⚠ gRPC server failed to start: {grpc_err} — REST API still running")

        # ─────────────────────────────────────────────
        # SUPABASE REALTIME + STORAGE
        # ─────────────────────────────────────────────
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if supabase_url and supabase_key:
            realtime_service = SupabaseRealtimeService(
                supabase_url=supabase_url,
                supabase_service_key=supabase_key
            )
            if realtime_service.available:
                logger.info("✓ Supabase Realtime + Storage ready")
            else:
                logger.warning("⚠ Supabase client unavailable (install supabase package)")
        else:
            logger.warning("⚠ SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set — Realtime disabled")

        logger.info("✓ AI Brain Service ready! REST:8000 | gRPC:50051")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        logger.warning("⚠ Running with limited functionality")

    yield

    # Shutdown
    logger.info("Shutting down AI Brain Service...")

    if _grpc_task and not _grpc_task.done():
        _grpc_task.cancel()
        try:
            await _grpc_task
        except asyncio.CancelledError:
            pass
        logger.info("✓ gRPC server stopped")

    if db:
        await db.close()
        logger.info("✓ PostgreSQL disconnected")

    if redis:
        await redis.close()
        logger.info("✓ Redis disconnected")



# Create FastAPI app
app = FastAPI(
    title="AI Brain Service",
    description="Voice AI System with STT, LLM, and TTS capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(voice.router)
app.include_router(chat.router)
app.include_router(conversation.router)
app.include_router(scheduling.router)
app.include_router(habits.router)
app.include_router(memory.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Brain Service",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "Speech-to-Text (OpenAI Whisper)",
            "Text-to-Speech (OpenAI TTS)",
            "Natural Language Understanding (OpenRouter LLM)",
            "Complete Voice Conversation (STT → NLU → TTS)",
            "Smart Scheduling AI (ML-powered)",
            "Habit Prediction Engine (Behavioral Analytics)",
            "Vector Memory System (Semantic Search & Context Retrieval)"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    # Check database
    try:
        if db and db.pool:
            async with db.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            health_status["services"]["database"] = "healthy"
        else:
            health_status["services"]["database"] = "not_connected"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        if redis and redis.client:
            await redis.client.ping()
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["services"]["redis"] = "not_connected"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check Supabase Realtime
    if realtime_service and realtime_service.available:
        health_status["services"]["supabase_realtime"] = "healthy"
    elif os.getenv("SUPABASE_URL"):
        health_status["services"]["supabase_realtime"] = "configured_but_unavailable"
    else:
        health_status["services"]["supabase_realtime"] = "not_configured"

    # Check OpenAI API key
    if os.getenv("OPENAI_API_KEY"):
        health_status["services"]["openai"] = "configured"
    else:
        health_status["services"]["openai"] = "not_configured"
        health_status["status"] = "degraded"

    # Check Groq/OpenRouter API key
    if os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY"):
        health_status["services"]["llm"] = "configured"
    else:
        health_status["services"]["llm"] = "not_configured"
        health_status["status"] = "degraded"

    # Check BehavioralObserver (Gemini FREE model)
    if os.getenv("OPENROUTER_API_KEY") or os.getenv("GROQ_API_KEY"):
        health_status["services"]["behavioral_observer"] = "ready"
    else:
        health_status["services"]["behavioral_observer"] = "no_api_key"

    # Check gRPC
    health_status["services"]["grpc"] = (
        "running" if _grpc_task and not _grpc_task.done() else "stopped"
    )

    return health_status


@app.get("/api/info")
async def service_info():
    """Service information"""
    return {
        "service": "AI Brain Service",
        "version": "1.0.0",
        "endpoints": {
            "stt": "/api/ai/voice/transcribe",
            "tts": "/api/ai/voice/synthesize",
            "tts_emotion": "/api/ai/voice/synthesize-emotion",
            "voices": "/api/ai/voice/voices",
            "chat": "/api/ai/chat (coming soon)"
        },
        "grpc": {
            "port": 50051,
            "services": ["VoiceService", "HealthService"]
        },
        "capabilities": {
            "audio_formats": ["wav", "mp3", "m4a", "webm", "ogg", "flac"],
            "languages": ["en", "hi", "es", "fr", "de", "auto"],
            "max_audio_size_mb": 25
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
"""
Database connection and initialization for AI Brain Service
Handles PostgreSQL with pgvector and Redis connections
"""
import asyncpg
from redis import asyncio as aioredis
from typing import Optional
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class Database:
    """PostgreSQL connection pool with pgvector support"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self, database_url: str, min_size: int = 10, max_size: int = 20):
        """
        Create connection pool with optimized settings
        
        Args:
            database_url: PostgreSQL connection string
            min_size: Minimum pool size (default: 10)
            max_size: Maximum pool size (default: 20)
        """
        try:
            self.pool = await asyncpg.create_pool(
                database_url,
                min_size=min_size,
                max_size=max_size,
                command_timeout=60,  # 60 seconds timeout for queries
                server_settings={
                    'jit': 'off',  # Disable JIT for faster connection
                    'application_name': 'ai-brain-service'
                }
            )
            
            # Test connection and pgvector
            async with self.pool.acquire() as conn:
                # Check pgvector extension
                result = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
                )
                if not result:
                    logger.warning("pgvector extension not found. Run migration first!")
                else:
                    logger.info("✓ pgvector extension is available")
                
                # Test query
                await conn.fetchval("SELECT 1")
                logger.info(f"✓ PostgreSQL connected (pool: {min_size}-{max_size})")
        
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed")
    
    @asynccontextmanager
    async def acquire(self):
        """Get connection from pool (context manager)"""
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute(self, query: str, *args):
        """Execute query without returning results"""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Fetch multiple rows"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Fetch single row"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Fetch single value"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)


class RedisClient:
    """Redis connection for caching and session storage"""
    
    def __init__(self):
        self.client: Optional[aioredis.Redis] = None
    
    async def connect(self, redis_url: str):
        """
        Connect to Redis with retry logic
        
        Args:
            redis_url: Redis connection string (redis:// or rediss://)
        """
        try:
            self.client = await aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,  # Connection pool size
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.client.ping()
            logger.info("✓ Redis connected")
        
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")
    
    async def set(self, key: str, value: str, expire: int = 3600):
        """
        Set key with expiration
        
        Args:
            key: Cache key
            value: Cache value
            expire: TTL in seconds (default: 1 hour)
        """
        await self.client.set(key, value, ex=expire)
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        return await self.client.get(key)
    
    async def delete(self, key: str):
        """Delete key"""
        await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.client.exists(key) > 0
    
    async def setex(self, key: str, seconds: int, value: str):
        """Set key with expiration in one call"""
        await self.client.setex(key, seconds, value)
    
    async def incr(self, key: str) -> int:
        """Increment counter"""
        return await self.client.incr(key)
    
    async def expire(self, key: str, seconds: int):
        """Set expiration on existing key"""
        await self.client.expire(key, seconds)


# Global instances
db = Database()
redis = RedisClient()


async def init_db(database_url: str, redis_url: str):
    """Initialize database connections"""
    await db.connect(database_url)
    await redis.connect(redis_url)
    logger.info("All database connections initialized")


async def close_db():
    """Close all database connections"""
    await db.close()
    await redis.close()
    logger.info("All database connections closed")

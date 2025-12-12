"""
Vector Database Operations - pgvector integration for semantic search
Handles embedding storage, similarity search, and memory management
"""

import asyncpg
from typing import List, Dict, Optional, Tuple
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class VectorOperations:
    """
    PostgreSQL pgvector operations for semantic memory
    """
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.pool = db_pool
        self.embedding_dimension = 1536  # OpenAI text-embedding-3-small
    
    async def initialize_vector_tables(self):
        """
        Create vector memory tables if they don't exist
        
        Tables:
        - conversation_memory: Stores conversation embeddings
        - context_memory: Stores contextual information
        - semantic_cache: Caches similar queries
        """
        
        async with self.pool.acquire() as conn:
            # Create extension if not exists
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # Conversation memory table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    session_id VARCHAR(255),
                    conversation_text TEXT NOT NULL,
                    embedding vector(1536),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes for conversation_memory
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id 
                ON conversation_memory(user_id)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_id 
                ON conversation_memory(session_id)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON conversation_memory(created_at)
            """)
            
            # Create vector index for similarity search (HNSW - fast approximate)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS conversation_memory_embedding_idx 
                ON conversation_memory 
                USING hnsw (embedding vector_cosine_ops)
            """)
            
            # Context memory table (for important facts/preferences)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS context_memory (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    context_type VARCHAR(50),
                    context_key VARCHAR(255),
                    context_value TEXT,
                    embedding vector(1536),
                    importance_score FLOAT DEFAULT 0.5,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT NOW(),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes for context_memory
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_context 
                ON context_memory(user_id, context_type)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_importance 
                ON context_memory(importance_score)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS context_memory_embedding_idx 
                ON context_memory 
                USING hnsw (embedding vector_cosine_ops)
            """)
            
            # Semantic cache table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS semantic_cache (
                    id SERIAL PRIMARY KEY,
                    query_text TEXT NOT NULL,
                    query_embedding vector(1536),
                    response TEXT NOT NULL,
                    metadata JSONB,
                    hit_count INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT NOW(),
                    last_used TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS semantic_cache_embedding_idx 
                ON semantic_cache 
                USING hnsw (query_embedding vector_cosine_ops)
            """)
            
            logger.info("✓ Vector memory tables initialized")
    
    async def store_conversation(
        self,
        user_id: str,
        session_id: str,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Store conversation with embedding
        
        Returns: conversation_id
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO conversation_memory 
                (user_id, session_id, conversation_text, embedding, metadata)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """, user_id, session_id, text, embedding, metadata or {})
            
            return row['id']
    
    async def semantic_search_conversations(
        self,
        user_id: str,
        query_embedding: List[float],
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Find similar conversations using cosine similarity
        
        Args:
            user_id: User ID to search within
            query_embedding: Query vector
            limit: Max results to return
            similarity_threshold: Minimum similarity (0-1)
        
        Returns:
            List of similar conversations with similarity scores
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    id,
                    conversation_text,
                    metadata,
                    session_id,
                    created_at,
                    1 - (embedding <=> $1::vector) as similarity
                FROM conversation_memory
                WHERE user_id = $2
                    AND 1 - (embedding <=> $1::vector) >= $3
                ORDER BY embedding <=> $1::vector
                LIMIT $4
            """, query_embedding, user_id, similarity_threshold, limit)
            
            return [
                {
                    'id': row['id'],
                    'text': row['conversation_text'],
                    'metadata': row['metadata'],
                    'session_id': row['session_id'],
                    'created_at': row['created_at'].isoformat(),
                    'similarity': float(row['similarity'])
                }
                for row in rows
            ]
    
    async def store_context(
        self,
        user_id: str,
        context_type: str,
        context_key: str,
        context_value: str,
        embedding: List[float],
        importance_score: float = 0.5
    ) -> int:
        """
        Store contextual information (preferences, facts, etc.)
        
        Returns: context_id
        """
        
        async with self.pool.acquire() as conn:
            # Check if context already exists
            existing = await conn.fetchrow("""
                SELECT id FROM context_memory
                WHERE user_id = $1 AND context_type = $2 AND context_key = $3
            """, user_id, context_type, context_key)
            
            if existing:
                # Update existing
                await conn.execute("""
                    UPDATE context_memory
                    SET context_value = $1,
                        embedding = $2,
                        importance_score = $3,
                        last_accessed = NOW()
                    WHERE id = $4
                """, context_value, embedding, importance_score, existing['id'])
                
                return existing['id']
            else:
                # Insert new
                row = await conn.fetchrow("""
                    INSERT INTO context_memory
                    (user_id, context_type, context_key, context_value, embedding, importance_score)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                """, user_id, context_type, context_key, context_value, embedding, importance_score)
                
                return row['id']
    
    async def retrieve_context(
        self,
        user_id: str,
        query_embedding: List[float],
        context_type: Optional[str] = None,
        limit: int = 3
    ) -> List[Dict]:
        """
        Retrieve relevant context based on semantic similarity
        """
        
        async with self.pool.acquire() as conn:
            if context_type:
                rows = await conn.fetch("""
                    SELECT 
                        id, context_type, context_key, context_value,
                        importance_score, access_count,
                        1 - (embedding <=> $1::vector) as similarity
                    FROM context_memory
                    WHERE user_id = $2 AND context_type = $3
                    ORDER BY 
                        (1 - (embedding <=> $1::vector)) * importance_score DESC
                    LIMIT $4
                """, query_embedding, user_id, context_type, limit)
            else:
                rows = await conn.fetch("""
                    SELECT 
                        id, context_type, context_key, context_value,
                        importance_score, access_count,
                        1 - (embedding <=> $1::vector) as similarity
                    FROM context_memory
                    WHERE user_id = $2
                    ORDER BY 
                        (1 - (embedding <=> $1::vector)) * importance_score DESC
                    LIMIT $3
                """, query_embedding, user_id, limit)
            
            # Update access count
            for row in rows:
                await conn.execute("""
                    UPDATE context_memory
                    SET access_count = access_count + 1,
                        last_accessed = NOW()
                    WHERE id = $1
                """, row['id'])
            
            return [
                {
                    'id': row['id'],
                    'type': row['context_type'],
                    'key': row['context_key'],
                    'value': row['context_value'],
                    'importance': float(row['importance_score']),
                    'access_count': row['access_count'],
                    'similarity': float(row['similarity'])
                }
                for row in rows
            ]
    
    async def check_semantic_cache(
        self,
        query_embedding: List[float],
        similarity_threshold: float = 0.95
    ) -> Optional[Dict]:
        """
        Check if similar query exists in cache
        
        High threshold (0.95) for cache hits
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    id, query_text, response, metadata,
                    1 - (query_embedding <=> $1::vector) as similarity
                FROM semantic_cache
                WHERE 1 - (query_embedding <=> $1::vector) >= $2
                ORDER BY query_embedding <=> $1::vector
                LIMIT 1
            """, query_embedding, similarity_threshold)
            
            if row:
                # Update cache stats
                await conn.execute("""
                    UPDATE semantic_cache
                    SET hit_count = hit_count + 1,
                        last_used = NOW()
                    WHERE id = $1
                """, row['id'])
                
                return {
                    'query': row['query_text'],
                    'response': row['response'],
                    'metadata': row['metadata'],
                    'similarity': float(row['similarity']),
                    'cache_hit': True
                }
            
            return None
    
    async def store_in_cache(
        self,
        query_text: str,
        query_embedding: List[float],
        response: str,
        metadata: Optional[Dict] = None
    ):
        """Store query-response pair in semantic cache"""
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO semantic_cache
                (query_text, query_embedding, response, metadata)
                VALUES ($1, $2, $3, $4)
            """, query_text, query_embedding, response, metadata or {})
    
    async def get_conversation_history(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent conversation history
        """
        
        async with self.pool.acquire() as conn:
            if session_id:
                rows = await conn.fetch("""
                    SELECT id, conversation_text, metadata, created_at
                    FROM conversation_memory
                    WHERE user_id = $1 AND session_id = $2
                    ORDER BY created_at DESC
                    LIMIT $3
                """, user_id, session_id, limit)
            else:
                rows = await conn.fetch("""
                    SELECT id, conversation_text, metadata, created_at
                    FROM conversation_memory
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                """, user_id, limit)
            
            return [
                {
                    'id': row['id'],
                    'text': row['conversation_text'],
                    'metadata': row['metadata'],
                    'created_at': row['created_at'].isoformat()
                }
                for row in rows
            ][::-1]  # Reverse to chronological order
    
    async def delete_old_memories(
        self,
        user_id: str,
        days_old: int = 90
    ) -> int:
        """
        Delete conversations older than N days
        
        Returns: number of deleted records
        """
        
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM conversation_memory
                WHERE user_id = $1
                    AND created_at < NOW() - INTERVAL '$2 days'
            """, user_id, days_old)
            
            # Extract count from result string like "DELETE 42"
            count = int(result.split()[-1]) if result else 0
            return count
    
    async def get_memory_stats(self, user_id: str) -> Dict:
        """Get statistics about stored memories"""
        
        async with self.pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_conversations,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    MIN(created_at) as first_conversation,
                    MAX(created_at) as last_conversation
                FROM conversation_memory
                WHERE user_id = $1
            """, user_id)
            
            context_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_contexts,
                    COUNT(DISTINCT context_type) as unique_types,
                    AVG(importance_score) as avg_importance,
                    SUM(access_count) as total_accesses
                FROM context_memory
                WHERE user_id = $1
            """, user_id)
            
            return {
                'conversations': {
                    'total': stats['total_conversations'],
                    'sessions': stats['unique_sessions'],
                    'first': stats['first_conversation'].isoformat() if stats['first_conversation'] else None,
                    'last': stats['last_conversation'].isoformat() if stats['last_conversation'] else None
                },
                'context': {
                    'total': context_stats['total_contexts'],
                    'types': context_stats['unique_types'],
                    'avg_importance': float(context_stats['avg_importance']) if context_stats['avg_importance'] else 0,
                    'total_accesses': context_stats['total_accesses'] or 0
                }
            }
    
    async def find_similar_contexts(
        self,
        user_id: str,
        context_value: str,
        embedding: List[float],
        limit: int = 5
    ) -> List[Dict]:
        """
        Find similar stored contexts
        Useful for deduplication and finding related information
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    id, context_type, context_key, context_value,
                    importance_score,
                    1 - (embedding <=> $1::vector) as similarity
                FROM context_memory
                WHERE user_id = $2
                    AND context_value != $3
                ORDER BY embedding <=> $1::vector
                LIMIT $4
            """, embedding, user_id, context_value, limit)
            
            return [
                {
                    'id': row['id'],
                    'type': row['context_type'],
                    'key': row['context_key'],
                    'value': row['context_value'],
                    'importance': float(row['importance_score']),
                    'similarity': float(row['similarity'])
                }
                for row in rows
            ]
    
    async def update_context_importance(
        self,
        context_id: int,
        new_importance: float
    ):
        """Update importance score of a context"""
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE context_memory
                SET importance_score = $1
                WHERE id = $2
            """, new_importance, context_id)
    
    async def delete_context(self, context_id: int):
        """Delete a specific context"""
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                DELETE FROM context_memory
                WHERE id = $1
            """, context_id)

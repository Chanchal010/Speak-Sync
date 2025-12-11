"""
Vector Memory Service - Semantic memory and context retrieval
Handles embeddings generation, similarity search, and intelligent memory management
"""

from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import openai
from openai import AsyncOpenAI
import asyncio
import hashlib

from src.database.vector_operations import VectorOperations

logger = logging.getLogger(__name__)


class VectorMemoryService:
    """
    Manages semantic memory using embeddings and vector similarity
    """
    
    def __init__(
        self,
        vector_ops: VectorOperations,
        openai_api_key: str
    ):
        self.vector_ops = vector_ops
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.embedding_model = "text-embedding-3-small"  # 1536 dimensions
        self.embedding_cache = {}  # In-memory cache for frequent queries
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using OpenAI
        
        Args:
            text: Input text to embed
        
        Returns:
            1536-dimensional embedding vector
        """
        
        # Check cache first
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.embedding_cache:
            logger.debug(f"Embedding cache hit for text hash: {text_hash[:8]}")
            return self.embedding_cache[text_hash]
        
        try:
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            # Cache the embedding (limit cache size)
            if len(self.embedding_cache) > 1000:
                # Remove oldest entries (simple FIFO)
                self.embedding_cache.pop(next(iter(self.embedding_cache)))
            
            self.embedding_cache[text_hash] = embedding
            
            logger.debug(f"Generated embedding for text length: {len(text)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def store_conversation_memory(
        self,
        user_id: str,
        session_id: str,
        conversation_text: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Store conversation with semantic embedding
        
        Returns:
            {
                'memory_id': int,
                'stored_at': str,
                'embedding_dimensions': int
            }
        """
        
        try:
            # Generate embedding
            embedding = await self.generate_embedding(conversation_text)
            
            # Store in vector database
            memory_id = await self.vector_ops.store_conversation(
                user_id=user_id,
                session_id=session_id,
                text=conversation_text,
                embedding=embedding,
                metadata=metadata or {}
            )
            
            logger.info(f"Stored conversation memory {memory_id} for user {user_id}")
            
            return {
                'memory_id': memory_id,
                'stored_at': datetime.utcnow().isoformat(),
                'embedding_dimensions': len(embedding)
            }
            
        except Exception as e:
            logger.error(f"Failed to store conversation memory: {e}")
            raise
    
    async def recall_similar_conversations(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> Dict:
        """
        Find similar past conversations using semantic search
        
        Args:
            user_id: User to search for
            query: Natural language query
            limit: Max results
            similarity_threshold: Min similarity (0-1)
        
        Returns:
            {
                'query': str,
                'results': List[conversation],
                'count': int,
                'search_time_ms': float
            }
        """
        
        start_time = datetime.utcnow()
        
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            
            # Search similar conversations
            results = await self.vector_ops.semantic_search_conversations(
                user_id=user_id,
                query_embedding=query_embedding,
                limit=limit,
                similarity_threshold=similarity_threshold
            )
            
            search_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(f"Found {len(results)} similar conversations for query: {query[:50]}...")
            
            return {
                'query': query,
                'results': results,
                'count': len(results),
                'search_time_ms': round(search_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to recall conversations: {e}")
            raise
    
    async def store_user_context(
        self,
        user_id: str,
        context_type: str,
        context_key: str,
        context_value: str,
        importance: float = 0.5
    ) -> Dict:
        """
        Store important context/facts about user
        
        Context types:
        - preference: User preferences (theme, language, etc.)
        - fact: Personal facts (name, location, etc.)
        - goal: User goals and aspirations
        - habit: Habit-related information
        - schedule: Scheduling preferences
        
        Args:
            importance: 0.0-1.0, higher = more important
        
        Returns:
            {
                'context_id': int,
                'stored_at': str,
                'importance': float
            }
        """
        
        try:
            # Generate embedding for the context value
            embedding = await self.generate_embedding(context_value)
            
            # Store in context memory
            context_id = await self.vector_ops.store_context(
                user_id=user_id,
                context_type=context_type,
                context_key=context_key,
                context_value=context_value,
                embedding=embedding,
                importance_score=importance
            )
            
            logger.info(f"Stored context {context_key} for user {user_id} (importance: {importance})")
            
            return {
                'context_id': context_id,
                'stored_at': datetime.utcnow().isoformat(),
                'importance': importance
            }
            
        except Exception as e:
            logger.error(f"Failed to store context: {e}")
            raise
    
    async def retrieve_relevant_context(
        self,
        user_id: str,
        query: str,
        context_type: Optional[str] = None,
        limit: int = 3
    ) -> Dict:
        """
        Retrieve relevant context based on current query
        
        This powers context-aware responses by finding relevant
        user information based on semantic similarity
        
        Returns:
            {
                'query': str,
                'contexts': List[context],
                'count': int
            }
        """
        
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            
            # Retrieve similar contexts
            contexts = await self.vector_ops.retrieve_context(
                user_id=user_id,
                query_embedding=query_embedding,
                context_type=context_type,
                limit=limit
            )
            
            logger.info(f"Retrieved {len(contexts)} relevant contexts for query")
            
            return {
                'query': query,
                'contexts': contexts,
                'count': len(contexts)
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            raise
    
    async def get_contextual_summary(
        self,
        user_id: str,
        current_query: str
    ) -> Dict:
        """
        Get comprehensive contextual summary for a query
        
        Combines:
        - Similar past conversations
        - Relevant stored context
        - User preferences
        
        Returns:
            {
                'summary': str,
                'relevant_conversations': List,
                'relevant_contexts': List,
                'confidence': float
            }
        """
        
        try:
            # Parallel retrieval of conversations and contexts
            conversations_task = self.recall_similar_conversations(
                user_id=user_id,
                query=current_query,
                limit=3,
                similarity_threshold=0.75
            )
            
            contexts_task = self.retrieve_relevant_context(
                user_id=user_id,
                query=current_query,
                limit=5
            )
            
            conversations_result, contexts_result = await asyncio.gather(
                conversations_task,
                contexts_task
            )
            
            # Build summary
            summary_parts = []
            
            if conversations_result['results']:
                summary_parts.append(
                    f"Found {len(conversations_result['results'])} similar past conversations"
                )
            
            if contexts_result['contexts']:
                context_types = set(c['type'] for c in contexts_result['contexts'])
                summary_parts.append(
                    f"Retrieved {len(contexts_result['contexts'])} relevant contexts "
                    f"({', '.join(context_types)})"
                )
            
            # Calculate confidence based on similarity scores
            all_similarities = (
                [c['similarity'] for c in conversations_result['results']] +
                [c['similarity'] for c in contexts_result['contexts']]
            )
            
            confidence = sum(all_similarities) / len(all_similarities) if all_similarities else 0.0
            
            summary = ". ".join(summary_parts) if summary_parts else "No relevant context found"
            
            return {
                'summary': summary,
                'relevant_conversations': conversations_result['results'],
                'relevant_contexts': contexts_result['contexts'],
                'confidence': round(confidence, 3)
            }
            
        except Exception as e:
            logger.error(f"Failed to get contextual summary: {e}")
            raise
    
    async def check_cache_or_compute(
        self,
        query: str,
        compute_func,
        cache_response: bool = True
    ) -> Tuple[Dict, bool]:
        """
        Check semantic cache before computing response
        
        Args:
            query: User query
            compute_func: Async function to compute response if not cached
            cache_response: Whether to cache the computed response
        
        Returns:
            (response, is_cache_hit)
        """
        
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            
            # Check cache
            cached = await self.vector_ops.check_semantic_cache(
                query_embedding=query_embedding,
                similarity_threshold=0.95  # High threshold for cache
            )
            
            if cached:
                logger.info(f"Cache hit for query: {query[:50]}...")
                return cached, True
            
            # Cache miss - compute response
            logger.info(f"Cache miss - computing response for: {query[:50]}...")
            response = await compute_func()
            
            # Store in cache if requested
            if cache_response:
                await self.vector_ops.store_in_cache(
                    query_text=query,
                    query_embedding=query_embedding,
                    response=str(response),
                    metadata={'computed_at': datetime.utcnow().isoformat()}
                )
            
            return response, False
            
        except Exception as e:
            logger.error(f"Failed cache check: {e}")
            # On error, just compute without cache
            response = await compute_func()
            return response, False
    
    async def get_conversation_history(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> Dict:
        """
        Get chronological conversation history
        
        Returns:
            {
                'conversations': List[conversation],
                'count': int,
                'session_id': Optional[str]
            }
        """
        
        try:
            conversations = await self.vector_ops.get_conversation_history(
                user_id=user_id,
                session_id=session_id,
                limit=limit
            )
            
            return {
                'conversations': conversations,
                'count': len(conversations),
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            raise
    
    async def cleanup_old_memories(
        self,
        user_id: str,
        days_old: int = 90
    ) -> Dict:
        """
        Remove old conversation memories to manage storage
        
        Returns:
            {
                'deleted_count': int,
                'days_old': int
            }
        """
        
        try:
            deleted_count = await self.vector_ops.delete_old_memories(
                user_id=user_id,
                days_old=days_old
            )
            
            logger.info(f"Deleted {deleted_count} memories older than {days_old} days for user {user_id}")
            
            return {
                'deleted_count': deleted_count,
                'days_old': days_old
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup memories: {e}")
            raise
    
    async def get_memory_statistics(self, user_id: str) -> Dict:
        """
        Get comprehensive memory statistics
        
        Returns:
            {
                'user_id': str,
                'conversations': {...},
                'contexts': {...},
                'cache_size': int
            }
        """
        
        try:
            stats = await self.vector_ops.get_memory_stats(user_id)
            
            stats['user_id'] = user_id
            stats['cache_size'] = len(self.embedding_cache)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            raise
    
    async def find_related_contexts(
        self,
        user_id: str,
        context_value: str,
        limit: int = 5
    ) -> Dict:
        """
        Find contexts related to a given context value
        Useful for discovering connections
        
        Returns:
            {
                'query_context': str,
                'related': List[context],
                'count': int
            }
        """
        
        try:
            # Generate embedding
            embedding = await self.generate_embedding(context_value)
            
            # Find similar
            related = await self.vector_ops.find_similar_contexts(
                user_id=user_id,
                context_value=context_value,
                embedding=embedding,
                limit=limit
            )
            
            return {
                'query_context': context_value,
                'related': related,
                'count': len(related)
            }
            
        except Exception as e:
            logger.error(f"Failed to find related contexts: {e}")
            raise
    
    async def update_context_importance(
        self,
        context_id: int,
        new_importance: float
    ) -> Dict:
        """
        Adjust importance of a stored context
        
        Use this to promote frequently used/relevant contexts
        or demote less important ones
        """
        
        try:
            await self.vector_ops.update_context_importance(
                context_id=context_id,
                new_importance=new_importance
            )
            
            logger.info(f"Updated importance of context {context_id} to {new_importance}")
            
            return {
                'context_id': context_id,
                'new_importance': new_importance,
                'updated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update context importance: {e}")
            raise
    
    async def batch_store_conversations(
        self,
        user_id: str,
        session_id: str,
        conversations: List[Dict]
    ) -> Dict:
        """
        Store multiple conversations efficiently
        
        Args:
            conversations: List of {'text': str, 'metadata': dict}
        
        Returns:
            {
                'stored_count': int,
                'memory_ids': List[int]
            }
        """
        
        try:
            memory_ids = []
            
            # Generate embeddings in batch (more efficient)
            texts = [conv['text'] for conv in conversations]
            
            # OpenAI supports batch embeddings
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            # Store each conversation
            for conv, embedding in zip(conversations, embeddings):
                memory_id = await self.vector_ops.store_conversation(
                    user_id=user_id,
                    session_id=session_id,
                    text=conv['text'],
                    embedding=embedding,
                    metadata=conv.get('metadata', {})
                )
                memory_ids.append(memory_id)
            
            logger.info(f"Batch stored {len(memory_ids)} conversations for user {user_id}")
            
            return {
                'stored_count': len(memory_ids),
                'memory_ids': memory_ids
            }
            
        except Exception as e:
            logger.error(f"Failed to batch store conversations: {e}")
            raise
    
    async def extract_and_store_contexts(
        self,
        user_id: str,
        conversation_text: str,
        context_hints: Optional[List[str]] = None
    ) -> Dict:
        """
        Extract important contexts from conversation using LLM
        and store them
        
        Args:
            conversation_text: Full conversation to analyze
            context_hints: Optional hints about what to look for
        
        Returns:
            {
                'extracted_contexts': List[context],
                'stored_count': int
            }
        """
        
        try:
            # Use OpenAI to extract contexts
            system_prompt = """You are a context extraction assistant. 
Analyze the conversation and extract important information about the user:
- Personal facts (name, location, job, etc.)
- Preferences (likes, dislikes, habits)
- Goals and aspirations
- Important relationships or events

Return JSON array of contexts with format:
[
    {
        "type": "fact|preference|goal",
        "key": "brief_key",
        "value": "detailed_value",
        "importance": 0.0-1.0
    }
]"""
            
            if context_hints:
                system_prompt += f"\n\nFocus on: {', '.join(context_hints)}"
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": conversation_text}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            contexts = result.get('contexts', [])
            
            # Store each extracted context
            stored_ids = []
            for ctx in contexts:
                result = await self.store_user_context(
                    user_id=user_id,
                    context_type=ctx['type'],
                    context_key=ctx['key'],
                    context_value=ctx['value'],
                    importance=ctx.get('importance', 0.5)
                )
                stored_ids.append(result['context_id'])
            
            logger.info(f"Extracted and stored {len(contexts)} contexts from conversation")
            
            return {
                'extracted_contexts': contexts,
                'stored_count': len(stored_ids)
            }
            
        except Exception as e:
            logger.error(f"Failed to extract contexts: {e}")
            # Return empty on error rather than failing
            return {
                'extracted_contexts': [],
                'stored_count': 0
            }

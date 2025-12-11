"""
Memory API Routes - Vector memory and context management endpoints
Provides semantic search, context storage, and memory retrieval
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

from src.services.vector_memory_service import VectorMemoryService
from src.database.vector_operations import VectorOperations
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/memory", tags=["Vector Memory"])


# ============= Request/Response Models =============

class StoreConversationRequest(BaseModel):
    """Request to store a conversation with semantic embedding"""
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Conversation session ID")
    conversation_text: str = Field(..., description="Conversation content")
    metadata: Optional[Dict] = Field(default={}, description="Additional metadata")


class StoreConversationResponse(BaseModel):
    """Response after storing conversation"""
    memory_id: int
    stored_at: str
    embedding_dimensions: int


class RecallConversationsRequest(BaseModel):
    """Request to recall similar conversations"""
    user_id: str = Field(..., description="User identifier")
    query: str = Field(..., description="Search query")
    limit: int = Field(default=5, ge=1, le=20, description="Max results")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Min similarity")


class ConversationResult(BaseModel):
    """Single conversation result"""
    id: int
    text: str
    metadata: Dict
    session_id: str
    created_at: str
    similarity: float


class RecallConversationsResponse(BaseModel):
    """Response with similar conversations"""
    query: str
    results: List[ConversationResult]
    count: int
    search_time_ms: float


class StoreContextRequest(BaseModel):
    """Request to store user context"""
    user_id: str = Field(..., description="User identifier")
    context_type: str = Field(..., description="Type: fact, preference, goal, habit, schedule")
    context_key: str = Field(..., description="Brief identifier")
    context_value: str = Field(..., description="Detailed value")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance score")


class StoreContextResponse(BaseModel):
    """Response after storing context"""
    context_id: int
    stored_at: str
    importance: float


class RetrieveContextRequest(BaseModel):
    """Request to retrieve relevant context"""
    user_id: str = Field(..., description="User identifier")
    query: str = Field(..., description="Query to find relevant context for")
    context_type: Optional[str] = Field(default=None, description="Filter by type")
    limit: int = Field(default=3, ge=1, le=10, description="Max results")


class ContextResult(BaseModel):
    """Single context result"""
    id: int
    type: str
    key: str
    value: str
    importance: float
    access_count: int
    similarity: float


class RetrieveContextResponse(BaseModel):
    """Response with relevant contexts"""
    query: str
    contexts: List[ContextResult]
    count: int


class ContextualSummaryRequest(BaseModel):
    """Request for contextual summary"""
    user_id: str = Field(..., description="User identifier")
    current_query: str = Field(..., description="Current user query")


class ContextualSummaryResponse(BaseModel):
    """Comprehensive contextual summary"""
    summary: str
    relevant_conversations: List[ConversationResult]
    relevant_contexts: List[ContextResult]
    confidence: float


class ConversationHistoryRequest(BaseModel):
    """Request for conversation history"""
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Filter by session")
    limit: int = Field(default=10, ge=1, le=50, description="Max results")


class ConversationHistoryItem(BaseModel):
    """Single history item"""
    id: int
    text: str
    metadata: Dict
    created_at: str


class ConversationHistoryResponse(BaseModel):
    """Response with conversation history"""
    conversations: List[ConversationHistoryItem]
    count: int
    session_id: Optional[str]


class CleanupMemoriesRequest(BaseModel):
    """Request to cleanup old memories"""
    user_id: str = Field(..., description="User identifier")
    days_old: int = Field(default=90, ge=1, description="Delete memories older than N days")


class CleanupMemoriesResponse(BaseModel):
    """Response after cleanup"""
    deleted_count: int
    days_old: int


class MemoryStatsResponse(BaseModel):
    """Memory statistics"""
    user_id: str
    conversations: Dict
    context: Dict
    cache_size: int


class UpdateImportanceRequest(BaseModel):
    """Request to update context importance"""
    context_id: int = Field(..., description="Context ID")
    new_importance: float = Field(..., ge=0.0, le=1.0, description="New importance")


class UpdateImportanceResponse(BaseModel):
    """Response after updating importance"""
    context_id: int
    new_importance: float
    updated_at: str


class FindRelatedRequest(BaseModel):
    """Request to find related contexts"""
    user_id: str = Field(..., description="User identifier")
    context_value: str = Field(..., description="Context to find related items for")
    limit: int = Field(default=5, ge=1, le=10, description="Max results")


class FindRelatedResponse(BaseModel):
    """Response with related contexts"""
    query_context: str
    related: List[ContextResult]
    count: int


class BatchStoreRequest(BaseModel):
    """Request to batch store conversations"""
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session ID")
    conversations: List[Dict] = Field(..., description="List of {text, metadata}")


class BatchStoreResponse(BaseModel):
    """Response after batch storage"""
    stored_count: int
    memory_ids: List[int]


class ExtractContextsRequest(BaseModel):
    """Request to extract and store contexts from conversation"""
    user_id: str = Field(..., description="User identifier")
    conversation_text: str = Field(..., description="Conversation to analyze")
    context_hints: Optional[List[str]] = Field(default=None, description="What to look for")


class ExtractedContext(BaseModel):
    """Extracted context item"""
    type: str
    key: str
    value: str
    importance: float


class ExtractContextsResponse(BaseModel):
    """Response with extracted contexts"""
    extracted_contexts: List[ExtractedContext]
    stored_count: int


# ============= Dependency Injection =============

async def get_vector_memory_service() -> VectorMemoryService:
    """Dependency to get vector memory service instance"""
    from src.main import vector_memory_service
    if not vector_memory_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector memory service not initialized"
        )
    return vector_memory_service


# ============= API Endpoints =============

@router.post(
    "/store-conversation",
    response_model=StoreConversationResponse,
    summary="Store Conversation with Semantic Embedding"
)
async def store_conversation(
    request: StoreConversationRequest,
    service: VectorMemoryService = Depends(get_vector_memory_service)
):
    """
    Store a conversation with its semantic embedding for later retrieval.
    
    The conversation will be indexed for semantic similarity search.
    """
    try:
        result = await service.store_conversation_memory(
            user_id=request.user_id,
            session_id=request.session_id,
            conversation_text=request.conversation_text,
            metadata=request.metadata
        )
        return result
    except Exception as e:
        logger.error(f"Failed to store conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store conversation: {str(e)}"
        )


@router.post(
    "/recall-conversations",
    response_model=RecallConversationsResponse,
    summary="Recall Similar Conversations"
)
async def recall_conversations(
    request: RecallConversationsRequest,
    service: VectorMemoryService = Depends(get_vector_memory_service)
):
    """
    Find similar past conversations using semantic search.
    
    Returns conversations ranked by similarity to the query.
    """
    try:
        result = await service.recall_similar_conversations(
            user_id=request.user_id,
            query=request.query,
            limit=request.limit,
            similarity_threshold=request.similarity_threshold
        )
        return result
    except Exception as e:
        logger.error(f"Failed to recall conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to recall conversations: {str(e)}"
        )


@router.post(
    "/store-context",
    response_model=StoreContextResponse,
    summary="Store User Context"
)
async def store_context(
    request: StoreContextRequest,
    service: VectorMemoryService = Depends(get_vector_memory_service)
):
    """
    Store important context/facts about a user.
    
    Context types:
    - fact: Personal information
    - preference: User preferences
    - goal: Goals and aspirations
    - habit: Habit-related info
    - schedule: Scheduling preferences
    """
    try:
        result = await service.store_user_context(
            user_id=request.user_id,
            context_type=request.context_type,
            context_key=request.context_key,
            context_value=request.context_value,
            importance=request.importance
        )
        return result
    except Exception as e:
        logger.error(f"Failed to store context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store context: {str(e)}"
        )


@router.post(
    "/retrieve-context",
    response_model=RetrieveContextResponse,
    summary="Retrieve Relevant Context"
)
async def retrieve_context(
    request: RetrieveContextRequest,
    service: VectorMemoryService = Depends(get_vector_memory_service)
):
    """
    Retrieve relevant user context based on semantic similarity to query.
    
    Returns contexts ranked by relevance and importance.
    """
    try:
        result = await service.retrieve_relevant_context(
            user_id=request.user_id,
            query=request.query,
            context_type=request.context_type,
            limit=request.limit
        )
        return result
    except Exception as e:
        logger.error(f"Failed to retrieve context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve context: {str(e)}"
        )


@router.post(
    "/contextual-summary",
    response_model=ContextualSummaryResponse,
    summary="Get Contextual Summary"
)
async def get_contextual_summary(
    request: ContextualSummaryRequest,
    service: VectorMemoryService = Depends(get_vector_memory_service)
):
    """
    Get comprehensive contextual summary combining:
    - Similar past conversations
    - Relevant stored contexts
    - User preferences
    
    Use this for context-aware AI responses.
    """
    try:
        result = await service.get_contextual_summary(
            user_id=request.user_id,
            current_query=request.current_query
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get contextual summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contextual summary: {str(e)}"
        )


@router.post(
    "/conversation-history",
    response_model=ConversationHistoryResponse,
    summary="Get Conversation History"
)
async def get_conversation_history(
    request: ConversationHistoryRequest,
    service: VectorMemoryService = Depends(get_vector_memory_service)
):
    """
    Get chronological conversation history.
    
    Can filter by session_id for specific conversation threads.
    """
    try:
        result = await service.get_conversation_history(
            user_id=request.user_id,
            session_id=request.session_id,
            limit=request.limit
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}"
        )


@router.post(
    "/cleanup-memories",
    response_model=CleanupMemoriesResponse,
    summary="Cleanup Old Memories"
)
async def cleanup_memories(
    request: CleanupMemoriesRequest,
    service: VectorMemoryService = Depends(get_vector_memory_service)
):
    """
    Delete conversations older than N days to manage storage.
    
    Context memories are preserved as they're typically more permanent.
    """
    try:
        result = await service.cleanup_old_memories(
            user_id=request.user_id,
            days_old=request.days_old
        )
        return result
    except Exception as e:
        logger.error(f"Failed to cleanup memories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup memories: {str(e)}"
        )


@router.get(
    "/stats/{user_id}",
    response_model=MemoryStatsResponse,
    summary="Get Memory Statistics"
)
async def get_memory_stats(
    user_id: str,
    service: VectorMemoryService = Depends(get_vector_memory_service)
):
    """
    Get comprehensive memory statistics for a user.
    
    Includes conversation counts, context info, and cache statistics.
    """
    try:
        result = await service.get_memory_statistics(user_id)
        return result
    except Exception as e:
        logger.error(f"Failed to get memory stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memory stats: {str(e)}"
        )


@router.post(
    "/find-related",
    response_model=FindRelatedResponse,
    summary="Find Related Contexts"
)
async def find_related(
    request: FindRelatedRequest,
    service: VectorMemoryService = Depends(get_vector_memory_service)
):
    """
    Find contexts semantically related to a given context.
    
    Useful for discovering connections and related information.
    """
    try:
        result = await service.find_related_contexts(
            user_id=request.user_id,
            context_value=request.context_value,
            limit=request.limit
        )
        return result
    except Exception as e:
        logger.error(f"Failed to find related contexts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find related contexts: {str(e)}"
        )


@router.post(
    "/update-importance",
    response_model=UpdateImportanceResponse,
    summary="Update Context Importance"
)
async def update_importance(
    request: UpdateImportanceRequest,
    service: VectorMemoryService = Depends(get_vector_memory_service)
):
    """
    Update importance score of a stored context.
    
    Use this to promote frequently used contexts or demote less important ones.
    """
    try:
        result = await service.update_context_importance(
            context_id=request.context_id,
            new_importance=request.new_importance
        )
        return result
    except Exception as e:
        logger.error(f"Failed to update importance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update importance: {str(e)}"
        )


@router.post(
    "/batch-store",
    response_model=BatchStoreResponse,
    summary="Batch Store Conversations"
)
async def batch_store(
    request: BatchStoreRequest,
    service: VectorMemoryService = Depends(get_vector_memory_service)
):
    """
    Store multiple conversations efficiently in a batch.
    
    More efficient than individual stores as embeddings are generated in parallel.
    """
    try:
        result = await service.batch_store_conversations(
            user_id=request.user_id,
            session_id=request.session_id,
            conversations=request.conversations
        )
        return result
    except Exception as e:
        logger.error(f"Failed to batch store: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to batch store: {str(e)}"
        )


@router.post(
    "/extract-contexts",
    response_model=ExtractContextsResponse,
    summary="Extract and Store Contexts"
)
async def extract_contexts(
    request: ExtractContextsRequest,
    service: VectorMemoryService = Depends(get_vector_memory_service)
):
    """
    Extract important contexts from conversation using AI and store them.
    
    Automatically identifies:
    - Personal facts
    - Preferences
    - Goals
    - Important relationships
    
    Provide context_hints to guide extraction (e.g., ["preferences", "goals"]).
    """
    try:
        result = await service.extract_and_store_contexts(
            user_id=request.user_id,
            conversation_text=request.conversation_text,
            context_hints=request.context_hints
        )
        return result
    except Exception as e:
        logger.error(f"Failed to extract contexts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract contexts: {str(e)}"
        )


@router.get(
    "/health",
    summary="Memory Service Health Check"
)
async def health_check(
    service: VectorMemoryService = Depends(get_vector_memory_service)
):
    """Check if memory service is operational"""
    return {
        "status": "healthy",
        "service": "vector_memory",
        "features": [
            "Semantic conversation search",
            "Context storage and retrieval",
            "Contextual summaries",
            "Memory management",
            "Batch operations",
            "AI-powered context extraction"
        ],
        "embedding_model": service.embedding_model,
        "cache_size": len(service.embedding_cache)
    }

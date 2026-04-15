-- ============================================================
-- Speak-Sync Supabase Setup Script
-- Run this in Supabase → SQL Editor after creating your project
-- ============================================================

-- Step 1: Enable pgvector extension (required for AI memory)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- Step 2: Verify pgvector is working
-- ============================================================
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- ============================================================
-- Step 3: Create vector memory table (from vector_operations.py)
-- ============================================================
CREATE TABLE IF NOT EXISTS user_context_vectors (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    context_type VARCHAR(100) NOT NULL,
    context_key VARCHAR(500) NOT NULL,
    context_value TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-small dimensions
    importance FLOAT DEFAULT 0.5,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast user lookups
CREATE INDEX IF NOT EXISTS idx_user_context_user_id
    ON user_context_vectors(user_id);

-- Index for context type filtering
CREATE INDEX IF NOT EXISTS idx_user_context_type
    ON user_context_vectors(user_id, context_type);

-- Vector similarity search index (HNSW — fastest for your scale)
CREATE INDEX IF NOT EXISTS idx_user_context_embedding
    ON user_context_vectors
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ============================================================
-- Step 4: Conversation history table
-- ============================================================
CREATE TABLE IF NOT EXISTS conversation_history (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(500) NOT NULL,
    role VARCHAR(50) NOT NULL,  -- 'user' | 'assistant'
    content TEXT NOT NULL,
    intent VARCHAR(100),
    domain VARCHAR(100),
    entities JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversation_user_session
    ON conversation_history(user_id, session_id);

CREATE INDEX IF NOT EXISTS idx_conversation_created
    ON conversation_history(user_id, created_at DESC);

-- ============================================================
-- Step 5: Behavioral observations table (for BehavioralObserver)
-- ============================================================
CREATE TABLE IF NOT EXISTS behavioral_observations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    insight TEXT NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    embedding vector(1536),  -- for semantic retrieval
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_behavioral_user_id
    ON behavioral_observations(user_id);

CREATE INDEX IF NOT EXISTS idx_behavioral_created
    ON behavioral_observations(user_id, created_at DESC);

-- Vector index for semantic search on behavioral patterns
CREATE INDEX IF NOT EXISTS idx_behavioral_embedding
    ON behavioral_observations
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ============================================================
-- Step 6: Realtime events table (used by SupabaseRealtimeService)
-- Flutter subscribes to this table per-user for live updates
-- ============================================================
CREATE TABLE IF NOT EXISTS realtime_events (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    channel VARCHAR(255) NOT NULL,
    event VARCHAR(100) NOT NULL,
    payload JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_realtime_events_user_id
    ON realtime_events(user_id, created_at DESC);

-- Auto-delete old events (keep only last 24 hours)
-- Set up via Supabase Dashboard → Database → Functions, or run periodically

-- ============================================================
-- Step 7: Enable Realtime on tables (for live notifications)
-- ============================================================
ALTER TABLE conversation_history REPLICA IDENTITY FULL;
ALTER TABLE behavioral_observations REPLICA IDENTITY FULL;
ALTER TABLE realtime_events REPLICA IDENTITY FULL;

-- Supabase Realtime — add tables to the publication
ALTER PUBLICATION supabase_realtime ADD TABLE conversation_history;
ALTER PUBLICATION supabase_realtime ADD TABLE behavioral_observations;
ALTER PUBLICATION supabase_realtime ADD TABLE realtime_events;

-- ============================================================
-- Step 7: Storage buckets (run in Supabase Dashboard → Storage)
-- OR via SQL:
-- ============================================================
-- NOTE: Storage buckets are usually created via Dashboard.
-- Go to Storage → New Bucket → Create these:
--   • tts-cache    (private, 50MB limit per file)
--   • voice-recordings (private, 25MB limit per file)
--   • user-avatars (public, 5MB limit per file)

-- ============================================================
-- Step 8: Row Level Security (RLS) — protect user data
-- ============================================================
ALTER TABLE user_context_vectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE behavioral_observations ENABLE ROW LEVEL SECURITY;

-- For now: allow service role full access (your backend uses service role key)
-- The Gateway JWT handles auth — Supabase here is purely a DB layer.
CREATE POLICY "Service role full access - user_context" ON user_context_vectors
    FOR ALL USING (true);  -- Restricted by your Gateway JWT layer

CREATE POLICY "Service role full access - conversation" ON conversation_history
    FOR ALL USING (true);

CREATE POLICY "Service role full access - behavioral" ON behavioral_observations
    FOR ALL USING (true);

-- ============================================================
-- DONE! Your Supabase DB is ready.
-- Next: Copy your connection string from:
-- Supabase Dashboard → Settings → Database → Connection string → URI
-- ============================================================

-- Quick test — insert and retrieve a vector:
-- INSERT INTO user_context_vectors (user_id, context_type, context_key, context_value, embedding)
-- VALUES ('test_user', 'test', 'test_key', 'test value', '[0.1, 0.2, ...]'::vector);

SELECT 'Supabase setup complete! pgvector + Realtime + Tables all ready.' AS status;

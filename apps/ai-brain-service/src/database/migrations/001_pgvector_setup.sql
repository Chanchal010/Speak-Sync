-- Phase 6: AI Brain Service - Database Setup
-- pgvector extension for embeddings and semantic search
-- Run this migration on your PostgreSQL database

-- Step 1: Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Task embeddings for ML-based task classification and similarity
CREATE TABLE IF NOT EXISTS task_embeddings (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  task_id VARCHAR(36),
  embedding vector(1536),  -- OpenAI text-embedding-3-small dimension
  priority VARCHAR(2),      -- VI, MI, NI
  category VARCHAR(50),
  completion_time_minutes INT,
  task_title TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_task_embeddings_user ON task_embeddings(user_id);
CREATE INDEX IF NOT EXISTS idx_task_embeddings_task ON task_embeddings(task_id);

-- Vector similarity index (IVFFlat - fast approximate nearest neighbor)
CREATE INDEX IF NOT EXISTS idx_task_embeddings_vector 
ON task_embeddings USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Step 3: User behavior embeddings for pattern recognition
CREATE TABLE IF NOT EXISTS user_behavior_embeddings (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  behavior_type VARCHAR(50) NOT NULL,  -- 'task_completion', 'habit_log', 'schedule_pattern', 'voice_interaction'
  embedding vector(1536),
  metadata JSONB,  -- {day_of_week: 1, hour: 10, success: true, context: {...}}
  frequency INT DEFAULT 1,
  last_occurred_at TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for behavior analysis
CREATE INDEX IF NOT EXISTS idx_behavior_embeddings_user ON user_behavior_embeddings(user_id);
CREATE INDEX IF NOT EXISTS idx_behavior_embeddings_type ON user_behavior_embeddings(behavior_type);
CREATE INDEX IF NOT EXISTS idx_behavior_embeddings_occurred ON user_behavior_embeddings(last_occurred_at DESC);

-- Vector similarity index
CREATE INDEX IF NOT EXISTS idx_behavior_embeddings_vector 
ON user_behavior_embeddings USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Step 4: Conversation context for chat memory
CREATE TABLE IF NOT EXISTS conversation_context (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  session_id VARCHAR(50) NOT NULL,
  message_role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system'
  message_content TEXT NOT NULL,
  embedding vector(1536),
  intent VARCHAR(50),  -- 'create_task', 'log_habit', 'ask_question', etc.
  entities JSONB,      -- Extracted entities from the message
  emotion VARCHAR(20), -- 'calm', 'stressed', 'excited', etc.
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for conversation history
CREATE INDEX IF NOT EXISTS idx_conversation_user_session ON conversation_context(user_id, session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_created ON conversation_context(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversation_intent ON conversation_context(intent);

-- Vector similarity index for semantic search in chat history
CREATE INDEX IF NOT EXISTS idx_conversation_vector 
ON conversation_context USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 50);

-- Step 5: Voice interaction logs (for quality monitoring)
CREATE TABLE IF NOT EXISTS voice_interactions (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  session_id VARCHAR(50) NOT NULL,
  audio_duration_ms INT,
  transcription_text TEXT,
  transcription_confidence FLOAT,
  intent VARCHAR(50),
  response_text TEXT,
  response_audio_generated BOOLEAN DEFAULT FALSE,
  total_latency_ms INT,  -- Total time from audio upload to response
  stt_latency_ms INT,    -- Speech-to-text time
  llm_latency_ms INT,    -- LLM processing time
  tts_latency_ms INT,    -- Text-to-speech time
  success BOOLEAN DEFAULT TRUE,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for analytics
CREATE INDEX IF NOT EXISTS idx_voice_interactions_user ON voice_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_voice_interactions_session ON voice_interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_voice_interactions_created ON voice_interactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_voice_interactions_success ON voice_interactions(success);

-- Step 6: User AI preferences (voice, learning patterns)
CREATE TABLE IF NOT EXISTS user_ai_preferences (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL UNIQUE,
  preferred_voice VARCHAR(50) DEFAULT 'en-us-female-calm',  -- TTS voice preference
  preferred_language VARCHAR(10) DEFAULT 'en',              -- STT language
  tts_speaking_rate FLOAT DEFAULT 1.0,                      -- Speed: 0.5 to 2.0
  enable_proactive_suggestions BOOLEAN DEFAULT TRUE,
  suggestion_frequency VARCHAR(20) DEFAULT 'moderate',      -- 'low', 'moderate', 'high'
  quiet_hours_start TIME,                                   -- No suggestions during quiet hours
  quiet_hours_end TIME,
  learning_enabled BOOLEAN DEFAULT TRUE,                    -- Allow AI to learn from behavior
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for user preferences
CREATE INDEX IF NOT EXISTS idx_user_ai_preferences_user ON user_ai_preferences(user_id);

-- Step 7: Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Step 8: Add triggers for updated_at
CREATE TRIGGER update_task_embeddings_updated_at BEFORE UPDATE ON task_embeddings
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_behavior_embeddings_updated_at BEFORE UPDATE ON user_behavior_embeddings
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_ai_preferences_updated_at BEFORE UPDATE ON user_ai_preferences
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Step 9: Add helpful comments
COMMENT ON TABLE task_embeddings IS 'Stores task embeddings for ML-based similarity search and priority prediction';
COMMENT ON TABLE user_behavior_embeddings IS 'Stores user behavior patterns as embeddings for proactive suggestions';
COMMENT ON TABLE conversation_context IS 'Stores conversation history with embeddings for context-aware responses';
COMMENT ON TABLE voice_interactions IS 'Logs voice interactions for quality monitoring and performance optimization';
COMMENT ON TABLE user_ai_preferences IS 'Stores user preferences for voice AI features';

COMMENT ON COLUMN task_embeddings.embedding IS 'OpenAI text-embedding-3-small (1536 dimensions)';
COMMENT ON COLUMN user_behavior_embeddings.metadata IS 'Structured behavior context: {day_of_week, hour, success, task_type, etc}';
COMMENT ON COLUMN conversation_context.intent IS 'Classified intent: create_task, log_habit, schedule_event, ask_question, etc';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'pgvector setup complete! Tables created:';
    RAISE NOTICE '  - task_embeddings (for task similarity & priority prediction)';
    RAISE NOTICE '  - user_behavior_embeddings (for pattern recognition)';
    RAISE NOTICE '  - conversation_context (for chat memory)';
    RAISE NOTICE '  - voice_interactions (for quality monitoring)';
    RAISE NOTICE '  - user_ai_preferences (for personalization)';
    RAISE NOTICE '';
    RAISE NOTICE 'Vector indexes created with IVFFlat for fast similarity search';
    RAISE NOTICE 'Ready for Phase 6 implementation!';
END $$;

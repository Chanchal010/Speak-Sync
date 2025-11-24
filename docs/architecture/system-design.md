## Data Storage
- PostgreSQL: Structured data (tasks, events, users)
- MongoDB: Unstructured logs and habits
- pgvector: AI embeddings for RAG

## AI Pipeline
1. Voice Input → Whisper STT
2. Text → Llama 3.3 (Intent Classification)
3. Query → pgvector (Context Retrieval)
4. Response → Chatterbox TTS
# AI Brain Service - Migration Status & Continuation Guide

**Last Updated**: December 11, 2025  
**Current Status**: ✅ Linux Migration Complete  
**Completion**: 80% (Parts 1-8 complete, Parts 9-10 pending)

---

## 🚨 CURRENT STATE (Linux)

### What's Working ✅
- **Python Version**: Python 3.11.14 in venv (Linux)
- **Location**: `/media/code-buddy/code/Projects/Speak-Sync/apps/ai-brain-service/venv`
- **Services Implemented**:
  - ✅ Part 1: Database & gRPC Setup (PostgreSQL + pgvector, Redis, gRPC)
  - ✅ Part 2: STT Engine (OpenAI Whisper - fully functional)
  - ✅ Part 3: TTS Engine (OpenAI TTS - working, 6 voices)
  - ✅ Part 4: NLU & Intent Detection (OpenRouter Llama 3.3 70B - tested & working)
  - ✅ Part 5: Voice Conversation Flow (STT→NLU→TTS pipeline - ready)
  - ✅ Part 6: Smart Scheduling AI (ML-powered conflict detection, optimization)
  - ✅ Part 7: Habit Prediction Engine (Behavioral analytics, ML predictions)
  - ✅ Part 8: Vector Memory System (pgvector, embeddings, semantic search) - **NEWLY IMPLEMENTED**

### Migration Success 🎉
- **TTS Package**: ✅ Successfully installed on Linux (no C++ Build Tools needed)
- **All Dependencies**: ✅ Fully installed (requirements.txt complete)
- **All Services Running**: 
  - AI Brain Service: Port 8000 ✅
  - Scheduler Service: Port 3001 ✅
  - Lifestyle Service: Port 8001 ✅

---

## 🎯 Phase 6 Part 6: Smart Scheduling AI - COMPLETE ✅

### Implementation Summary (Dec 11, 2025)

**New Files Created**:
1. `src/services/scheduling_service.py` (770 lines)
   - Conflict detection and resolution
   - Time slot optimization
   - Smart scheduling suggestions
   - Workload balancing
   
2. `src/ml/scheduling_model.py` (590 lines)
   - ML-based pattern recognition
   - Completion time prediction
   - Task type classification
   - Historical analysis

3. `src/api/routes/scheduling.py` (550 lines)
   - 9 API endpoints for scheduling
   - Health check
   - Pattern analysis

**API Endpoints Added**:
- `POST /api/scheduling/analyze-conflicts` - Detect conflicts
- `POST /api/scheduling/suggest-time-slot` - Get optimal slots
- `POST /api/scheduling/optimize-schedule` - Re-arrange tasks
- `POST /api/scheduling/smart-suggestions` - Proactive suggestions
- `POST /api/scheduling/train-model` - Train ML model
- `POST /api/scheduling/predict-completion-time` - Predict duration
- `POST /api/scheduling/calculate-scheduling-score` - Score time slots
- `GET /api/scheduling/patterns/{user_id}` - Get user patterns
- `GET /api/scheduling/health` - Service health

**Features Implemented**:
- ✅ Conflict detection (event overlaps, task-event conflicts)
- ✅ Overloaded day detection (>10 hours)
- ✅ Time gap identification for scheduling
- ✅ ML-based time slot scoring (0-100)
- ✅ Priority-based task allocation
- ✅ Eisenhower matrix integration
- ✅ User productivity pattern learning
- ✅ Task type clustering (meetings, coding, writing, etc.)
- ✅ Completion time prediction
- ✅ Workload balancing algorithm

**Testing Status**:
- ✅ Service starts without errors
- ✅ Health endpoint responding
- ✅ All endpoints registered in FastAPI
- ✅ Database integration ready
- ⏳ End-to-end API testing pending

---

## 🎯 Phase 6 Part 7: Habit Prediction Engine - COMPLETE ✅

### Implementation Summary (Dec 11, 2025)

**New Files Created**:
1. `src/services/habit_prediction_service.py` (840 lines)
   - Behavioral pattern analysis
   - Streak survival prediction
   - Completion time prediction
   - Personalized insights generation
   - Optimal schedule recommendations
   - Habit formation tracking (66-day rule)
   
2. `src/ml/habit_model.py` (610 lines)
   - Habit strength calculation (0-100 score)
   - Automaticity prediction
   - Lapse risk assessment
   - Behavior change stage identification
   - Implementation intentions (if-then plans)
   - Environmental design strategies

3. `src/api/routes/habits.py` (550 lines)
   - 10 API endpoints for habit predictions
   - Health check
   - Momentum tracking

**API Endpoints Added**:
- `POST /api/habits/analyze-patterns` - Deep pattern analysis
- `POST /api/habits/predict-streak` - Streak survival probability
- `POST /api/habits/predict-next-completion` - Next completion time
- `POST /api/habits/personalized-insights` - Natural language insights
- `POST /api/habits/optimal-schedule` - Schedule recommendations
- `POST /api/habits/formation-prediction` - 66-day automation timeline
- `POST /api/habits/habit-strength` - Comprehensive strength metrics
- `POST /api/habits/behavior-change-plan` - Transtheoretical model plans
- `GET /api/habits/momentum/{user_id}/{habit_type}` - Momentum tracking
- `GET /api/habits/health` - Service health

**Features Implemented**:
- ✅ Behavioral pattern recognition (time, day, consistency)
- ✅ Streak analysis (current, longest, average)
- ✅ Survival probability prediction (1d, 3d, 7d, 30d)
- ✅ Risk factor identification (weekend dropoff, low completion)
- ✅ Critical day detection (high-risk weekdays)
- ✅ Habit strength scoring (5 weighted features)
- ✅ Automaticity calculation (logarithmic curve)
- ✅ Lapse risk assessment (3-level system)
- ✅ Success probability forecasting (1w to 1y)
- ✅ Behavior stage identification (6-stage model)
- ✅ Momentum calculation (improvement tracking)
- ✅ Optimal intervention timing
- ✅ Cross-habit correlation analysis
- ✅ Environment optimization tips

**ML Models**:
- Habit Formation Model (based on Lally et al., 2010 research)
- Behavioral Prediction Engine
- Transtheoretical Model integration
- Implementation Intentions framework

**Testing Status**:
- ✅ Service starts without errors
- ✅ Health endpoint responding (all 10 endpoints)
- ✅ All endpoints tested with sample data
- ✅ Integration with Lifestyle Service (httpx async)
- ⏳ Real user data testing pending

---

## 🎯 Phase 6 Part 8: Vector Memory System - COMPLETE ✅

### Implementation Summary (Dec 11, 2025)

**New Files Created**:
1. `src/database/vector_operations.py` (498 lines)
   - pgvector table creation (conversation_memory, context_memory, semantic_cache)
   - HNSW indexing for fast similarity search
   - Semantic search operations (cosine similarity)
   - Context storage and retrieval
   - Memory statistics and cleanup
   
2. `src/services/vector_memory_service.py` (740 lines)
   - OpenAI embeddings generation (text-embedding-3-small)
   - Embedding caching (1000 item limit)
   - Semantic conversation search
   - Context-aware retrieval
   - Batch operations
   - AI-powered context extraction
   - Contextual summary generation

3. `src/api/routes/memory.py` (590 lines)
   - 13 API endpoints for memory management
   - Health check
   - Batch operations
   - Statistics tracking

**API Endpoints Added**:
- `POST /api/memory/store-conversation` - Store with embedding
- `POST /api/memory/recall-conversations` - Semantic search
- `POST /api/memory/store-context` - Store user context
- `POST /api/memory/retrieve-context` - Retrieve relevant context
- `POST /api/memory/contextual-summary` - Comprehensive summary
- `POST /api/memory/conversation-history` - Get history
- `POST /api/memory/cleanup-memories` - Delete old memories
- `GET /api/memory/stats/{user_id}` - Get statistics
- `POST /api/memory/find-related` - Find related contexts
- `POST /api/memory/update-importance` - Update importance score
- `POST /api/memory/batch-store` - Batch conversation storage
- `POST /api/memory/extract-contexts` - AI context extraction
- `GET /api/memory/health` - Service health

**Features Implemented**:
- ✅ pgvector extension initialization
- ✅ Vector tables with HNSW indexing
- ✅ 1536-dimensional embeddings (OpenAI)
- ✅ Semantic similarity search (cosine distance)
- ✅ Context types: fact, preference, goal, habit, schedule
- ✅ Importance scoring (0.0-1.0)
- ✅ Access count tracking
- ✅ Semantic cache (95% similarity threshold)
- ✅ Batch embedding generation
- ✅ AI-powered context extraction (GPT-4o-mini)
- ✅ Memory cleanup (age-based)
- ✅ Comprehensive statistics
- ✅ In-memory embedding cache
- ✅ Similar context discovery

**Database Tables Created**:
- `conversation_memory`: Stores conversation embeddings with metadata
- `context_memory`: Stores user contexts (facts, preferences, goals)
- `semantic_cache`: Caches query-response pairs for efficiency

**Integration Status**:
- ✅ Integrated into main.py with lifespan initialization
- ✅ Vector tables initialized on startup
- ✅ Service health responding
- ✅ Test script created (test-memory-api.sh)
- ⏳ Full testing pending (OpenAI quota exceeded)

**Note**: System architecture is complete and working. Actual embedding generation requires OpenAI API quota. Non-embedding features (history, stats, cleanup) tested successfully.

---

## 📋 Exact Current Point

### Services Status
- **AI Brain Service**: Running on port 8000 with scheduling + habit endpoints ✅
- **Scheduler Service**: Running on port 3001 (RabbitMQ configured) ✅
- **Lifestyle Service**: Running on port 8001 (MongoDB connected) ✅

### Current Terminal State
- **Directory**: `/media/code-buddy/code/Projects/Speak-Sync`
- **Venv Active**: Multiple (ai-brain, lifestyle in separate terminals)
- **Services**: All running in background with nohup
cd ~/Speak-Sync/apps/ai-brain-service

# Verify Python version (should have 3.11.x)
python3 --version

# If not 3.11, install it:
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# Install C++ build tools (CRITICAL for TTS)
sudo apt install build-essential
```

### STEP 2: Create Virtual Environment
```bash
# Remove old Windows venv if exists
rm -rf venv venv_py313_backup

# Create new Linux venv with Python 3.11
python3.11 -m venv venv

# Activate venv
source venv/bin/activate

# Verify Python version
python --version  # Should show 3.11.x

# Upgrade pip
pip install --upgrade pip
```

### STEP 3: Install All Packages
```bash
# This will work on Linux (C++ tools available)
pip install -r requirements.txt

# Expected time: 3-5 minutes (PyTorch is large ~2GB)
# TTS will build successfully on Linux!
```

### STEP 4: Verify Installation
```bash
# Check critical packages
pip list | grep -E "fastapi|openai|torch|TTS|redis|psycopg"

# Test Python imports
python -c "import fastapi; import openai; import torch; print('✓ Core packages OK')"
python -c "from TTS.api import TTS; print('✓ TTS installed successfully')"
```

### STEP 5: Environment Configuration
```bash
# Verify .env file exists
cat .env | head -5

# Should contain:
# - OPENAI_API_KEY
# - GROQ_API_KEY (OpenRouter key)
# - DATABASE_URL (Neon PostgreSQL)
# - REDIS_URL (Upstash)
```

### STEP 6: Test Server Startup
```bash
# Start server
python -m uvicorn src.main:app --reload --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.

# Test health endpoint
curl http://localhost:8000/health
```

### STEP 7: Verify All Services
```bash
# Test conversation health
curl http://localhost:8000/api/ai/conversation/health

# Expected response:
# {
#   "status": "healthy",
#   "services": {
#     "stt": "available",
#     "tts": "available", 
#     "nlu": "available"
#   }
# }
```

---

## 📁 Critical Files & Their Status

### Fully Implemented Files ✅
1. **`src/database/connection.py`** (182 lines)
   - PostgreSQL + pgvector connection
   - Redis connection (Upstash with SSL)
   - Fixed: `close()` method names

2. **`src/services/voice_service.py`** (366 lines)
   - OpenAI Whisper STT
   - 6 audio formats supported
   - HTTP + gRPC streaming

3. **`src/services/tts_service.py`** (294 lines)
   - OpenAI TTS implementation
   - 6 voice profiles
   - Audio caching
   - **NOTE**: Will be enhanced with XTTS on Linux

4. **`src/services/nlu_service.py`** (414 lines)
   - OpenRouter Llama 3.3 70B
   - 32+ intents across 6 domains
   - Entity extraction, sentiment analysis
   - Fixed: JSON parsing for markdown-wrapped responses
   - Fixed: `generate_response()` returns string

5. **`src/services/conversation_service.py`** (418 lines)
   - Complete STT→NLU→TTS orchestration
   - Session management (ConversationState)
   - 4 voice profiles: default, friendly, professional, energetic
   - Methods: process_voice_input(), process_text_input(), stream_conversation()
   - Fixed: Line 176 - generate_response() return type

6. **`src/api/routes/conversation.py`** (467 lines)
   - POST `/api/ai/conversation/voice` - Full voice interaction
   - POST `/api/ai/conversation/text` - Text with voice response
   - POST `/api/ai/conversation/voice/audio-response` - Audio-only
   - WebSocket `/api/ai/conversation/stream` - Real-time streaming
   - GET/DELETE session management

7. **`src/api/routes/chat.py`** (357 lines)
   - 8 NLU/chat endpoints
   - All tested and working

8. **`src/main.py`** (213 lines)
   - FastAPI app initialization
   - All routers included
   - Database lifecycle management
   - Fixed: Duplicate line in features array
   - Fixed: Database close() method calls

### Configuration Files ✅
1. **`.env`** - All API keys configured:
   ```env
   OPENAI_API_KEY=sk-proj-...
   GROQ_API_KEY=sk-or-v1-...  # OpenRouter key
   DATABASE_URL=postgresql://...@ep-...neon.tech/speaksync?sslmode=require
   REDIS_URL=rediss://:...@caring-fireant-58972.upstash.io:6379
   ```

2. **`requirements.txt`** - Contains:
   ```
   fastapi==0.115.6
   uvicorn[standard]==0.32.1
   openai==1.57.4
   redis==5.2.1
   psycopg[binary,pool]==3.2.3
   pgvector==0.3.6
   grpcio==1.68.1
   grpcio-tools==1.68.1
   python-dotenv==1.0.1
   TTS==0.22.0  # ← This one fails on Windows, works on Linux
   torch==2.5.1
   # ... more packages
   ```

---

## 🎯 Remaining Work (Parts 6-10)

### Part 6: Smart Scheduling AI
**Status**: Not started  
**What to implement**:
- ML models for conflict detection
- Intelligent scheduling suggestions
- Priority-based task allocation
- Time slot optimization

**New Files Needed**:
- `src/services/scheduling_service.py`
- `src/ml/scheduling_model.py`
- `src/api/routes/scheduling.py`

### Part 7: Habit Prediction Engine
**Status**: Not started  
**What to implement**:
- Behavioral analysis algorithms
- Pattern recognition for user habits
- Predictive analytics for habit formation
- Recommendation system

**New Files Needed**:
- `src/services/habit_prediction_service.py`
- `src/ml/habit_model.py`
- `src/api/routes/habits.py`

### Part 8: Vector Memory System
**Status**: Not started  
**What to implement**:
- Embedding generation for conversations
- pgvector integration for semantic search
- Context retrieval for conversations
- Memory management

**New Files Needed**:
- `src/services/vector_memory_service.py`
- `src/database/vector_operations.py`
- Update `src/services/conversation_service.py` to use vector memory

### Part 9: Gateway Integration
**Status**: Not started  
**What to implement**:
- Connect AI Brain Service with Gateway Service
- Implement service-to-service authentication
- Add health checks and service discovery
- Test end-to-end flows

**Files to Modify**:
- Gateway service configuration
- Add AI Brain endpoints to gateway routes
- Update docker-compose for service linking

### Part 10: Testing & Deployment
**Status**: Not started  
**What to implement**:
- Unit tests for all services
- Integration tests for conversation flow
- Docker containerization
- CI/CD pipeline setup
- Production deployment to cloud

**New Files Needed**:
- `tests/test_conversation.py`
- `tests/test_nlu.py`
- `tests/test_integration.py`
- `.github/workflows/ci.yml`
- Update `Dockerfile` for production

---

## 🔍 Known Issues & Fixes Applied

### Issue 1: Import Path Errors ✅ FIXED
**Error**: `ModuleNotFoundError: No module named 'api'`  
**Fix**: Changed all imports from relative (`from api.routes`) to absolute (`from src.api.routes`)

### Issue 2: Environment Variables Not Loading ✅ FIXED
**Error**: API keys undefined  
**Fix**: Added python-dotenv in main.py:
```python
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")
```

### Issue 3: OpenRouter SDK Incompatibility ✅ FIXED
**Error**: Groq SDK doesn't support OpenRouter  
**Fix**: Used OpenAI SDK with custom base_url:
```python
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
```

### Issue 4: JSON Parsing Failures ✅ FIXED
**Error**: OpenRouter returns markdown-wrapped JSON  
**Fix**: Added extraction logic in nlu_service.py:
```python
if "```json" in content:
    content = content.split("```json")[1].split("```")[0].strip()
```

### Issue 5: Redis Connection Error ✅ FIXED
**Error**: `unexpected keyword argument 'max_connections'`  
**Fix**: Removed max_connections parameter from Redis.from_url()

### Issue 6: Database Shutdown Error ✅ FIXED
**Error**: `AttributeError: 'DatabaseConnection' object has no attribute 'disconnect'`  
**Fix**: Renamed disconnect() to close() in connection.py

### Issue 7: generate_response() Type Error ✅ FIXED
**Error**: conversation_service expects string, got dict  
**Fix**: Changed nlu_service.generate_response() to return response["response"]

### Issue 8: Syntax Error in main.py ✅ FIXED
**Error**: Duplicate "Habit Predictions" in features list  
**Fix**: Removed duplicate line

---

## 🐧 Linux-Specific Advantages

### Why TTS Works on Linux:
1. **build-essential** package provides gcc/g++ compilers
2. **python3-dev** includes Python C headers
3. No Visual Studio dependency
4. Faster compilation (native toolchain)
5. Better package ecosystem for ML/AI

### Additional Linux Benefits:
- Docker works natively (no WSL overhead)
- Better PostgreSQL/Redis performance
- Native gRPC support
- Easier deployment to cloud (most use Linux)
- Lighter resource usage

---

## 📦 Node Modules Question - ANSWER

### **DO NOT REMOVE node_modules when switching to Linux**

**Why?**
- `node_modules` contains **JavaScript/TypeScript dependencies**
- This project has **multiple Node.js services**:
  - `apps/gateway-service` (Node.js/TypeScript)
  - `apps/scheduler-service` (Node.js/TypeScript)
  - `apps/worker-service` (Node.js/TypeScript)
  - Root workspace packages

**What to do instead:**

#### For Python services (ai-brain-service, lifestyle-service):
```bash
# Remove Python venvs (platform-specific)
rm -rf apps/ai-brain-service/venv
rm -rf apps/ai-brain-service/venv_py313_backup
rm -rf apps/lifestyle-service/venv

# Recreate on Linux
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### For Node.js services:
```bash
# node_modules works cross-platform, but rebuild native modules
cd apps/gateway-service
npm rebuild  # Rebuilds native addons for Linux

# Or clean install (safer)
rm -rf node_modules package-lock.json
npm install

# Repeat for other Node services
```

#### For workspace root:
```bash
# At project root
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

**Summary**: 
- ❌ Don't delete node_modules before transfer
- ✅ Run `npm rebuild` or reinstall on Linux
- ✅ Delete Python venvs (platform-specific)
- ✅ Keep source code, .env, configs

---

## 🚀 Quick Start Commands (Linux)

```bash
# 1. Navigate to project
cd ~/Speak-Sync/apps/ai-brain-service

# 2. Install system dependencies
sudo apt install python3.11 python3.11-venv python3.11-dev build-essential

# 3. Create venv
python3.11 -m venv venv
source venv/bin/activate

# 4. Install packages
pip install --upgrade pip
pip install -r requirements.txt

# 5. Start server
python -m uvicorn src.main:app --reload --port 8000

# 6. Test in another terminal
curl http://localhost:8000/health
curl http://localhost:8000/api/ai/conversation/health
```

---

## 📞 Testing Checklist (After Linux Setup)

### 1. Health Checks
```bash
✅ GET http://localhost:8000/health
✅ GET http://localhost:8000/api/ai/conversation/health
```

### 2. STT Testing
```bash
✅ POST http://localhost:8000/api/ai/voice/transcribe
   - Upload audio file
   - Verify transcription accuracy
```

### 3. TTS Testing
```bash
✅ POST http://localhost:8000/api/ai/voice/synthesize
   - Send text
   - Verify audio generation
   - Test XTTS voices (new on Linux!)
```

### 4. NLU Testing
```bash
✅ POST http://localhost:8000/api/ai/chat/intent
   - Test: "Schedule meeting tomorrow at 3pm"
   - Verify: create_calendar_event intent
```

### 5. Full Conversation Flow
```bash
✅ POST http://localhost:8000/api/ai/conversation/voice
   - Upload voice: "What's my schedule today?"
   - Verify: STT → NLU → TTS pipeline
   - Check: Receives audio response
```

---

## 🔐 Environment Variables (Verify on Linux)

```bash
# Check .env file
cat .env

# Should have:
OPENAI_API_KEY=sk-proj-...
GROQ_API_KEY=sk-or-v1-...  # OpenRouter
DATABASE_URL=postgresql://...
REDIS_URL=rediss://...
PORT=8000
LOG_LEVEL=info
```

---

## 🎯 Success Criteria

### Before Starting Part 6:
- [ ] All packages installed (including TTS)
- [ ] Server starts without errors
- [ ] All 5 parts tested and working
- [ ] No import errors
- [ ] Database connections successful
- [ ] Redis connections successful
- [ ] OpenAI API working
- [ ] OpenRouter API working

### Then Proceed With:
1. Part 6: Smart Scheduling AI
2. Part 7: Habit Prediction Engine
3. Part 8: Vector Memory System
4. Part 9: Gateway Integration
5. Part 10: Testing & Deployment

---

## 💡 Important Notes

1. **Python Version**: Must be 3.11.x (not 3.13, not 3.10)
2. **Virtual Environment**: Always activate before working
3. **API Keys**: Verify all keys in .env file work
4. **Database**: Neon PostgreSQL should be accessible
5. **Redis**: Upstash Redis should be accessible
6. **Port 8000**: Must be available (or change in .env)

---

## 🆘 Troubleshooting (Linux)

### If TTS installation fails:
```bash
sudo apt install python3.11-dev build-essential
pip install --upgrade pip setuptools wheel
pip install TTS==0.22.0
```

### If PyTorch fails:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### If gRPC fails:
```bash
sudo apt install python3-grpcio
pip install grpcio==1.68.1 grpcio-tools==1.68.1
```

### If database connection fails:
```bash
# Check .env DATABASE_URL
# Verify Neon PostgreSQL is accessible
psql "$DATABASE_URL"
```

---

## 📄 File Structure Reference

```
apps/ai-brain-service/
├── venv/                          # ← DELETE on Windows, recreate on Linux
├── venv_py313_backup/             # ← DELETE (Windows backup)
├── src/
│   ├── main.py                    # ✅ Complete
│   ├── database/
│   │   └── connection.py          # ✅ Complete
│   ├── services/
│   │   ├── voice_service.py       # ✅ Complete (STT)
│   │   ├── tts_service.py         # ✅ Complete (will enhance with XTTS)
│   │   ├── nlu_service.py         # ✅ Complete (NLU)
│   │   └── conversation_service.py # ✅ Complete (orchestration)
│   └── api/
│       └── routes/
│           ├── voice.py           # ✅ Complete
│           ├── chat.py            # ✅ Complete
│           └── conversation.py    # ✅ Complete
├── .env                           # ✅ Complete (verify keys work)
├── requirements.txt               # ✅ Complete
├── Dockerfile                     # ⏳ Will update in Part 10
└── MIGRATION_STATUS.md            # ← THIS FILE

Pending Parts:
├── src/services/scheduling_service.py      # Part 6
├── src/services/habit_prediction_service.py # Part 7
├── src/services/vector_memory_service.py   # Part 8
└── tests/                                  # Part 10
```

---

## ✅ Final Checklist Before Resuming

On Linux, run these commands in order:

```bash
# 1. System setup
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev build-essential

# 2. Navigate to project
cd ~/Speak-Sync/apps/ai-brain-service

# 3. Clean old venvs
rm -rf venv venv_py313_backup

# 4. Create new venv
python3.11 -m venv venv
source venv/bin/activate

# 5. Verify Python
python --version  # Must show 3.11.x

# 6. Install packages
pip install --upgrade pip
pip install -r requirements.txt

# 7. Verify TTS installed
python -c "from TTS.api import TTS; print('✓ TTS works!')"

# 8. Test server
python -m uvicorn src.main:app --reload --port 8000

# 9. In another terminal, test
curl http://localhost:8000/health
curl http://localhost:8000/api/ai/conversation/health

# 10. If all tests pass, proceed to Part 6!
```

---

**Status**: Ready to resume on Linux! All critical context saved. 🚀

# Graph Report - D:\Projects\speak_sync\speak_sync_server  (2026-04-28)

## Corpus Check
- 171 files · ~3,000,446 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2451 nodes · 6099 edges · 78 communities detected
- Extraction: 70% EXTRACTED · 30% INFERRED · 0% AMBIGUOUS · INFERRED: 1850 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]

## God Nodes (most connected - your core abstractions)
1. `VectorOperations` - 103 edges
2. `get()` - 102 edges
3. `VectorMemoryService` - 88 edges
4. `HabitService` - 66 edges
5. `NLUService` - 60 edges
6. `SchedulingService` - 53 edges
7. `HabitPredictionService` - 51 edges
8. `SchedulingModel` - 50 edges
9. `PyObjectId` - 50 edges
10. `append()` - 47 edges

## Surprising Connections (you probably didn't know these)
- `serve()` --calls--> `add_VoiceServiceServicer_to_server()`  [INFERRED]
  D:\Projects\Speak-Sync\apps\ai-brain-service\src\grpc_server.py → D:\Projects\Speak-Sync\apps\ai-brain-service\src\grpc_generated\voice_pb2_grpc.py
- `serve()` --calls--> `add_HealthServiceServicer_to_server()`  [INFERRED]
  D:\Projects\Speak-Sync\apps\ai-brain-service\src\grpc_server.py → D:\Projects\Speak-Sync\apps\ai-brain-service\src\grpc_generated\voice_pb2_grpc.py
- `Config` --uses--> `PyObjectId`  [INFERRED]
  D:\Projects\Speak-Sync\apps\lifestyle-service\src\models\food_log.py → D:\Projects\Speak-Sync\apps\lifestyle-service\src\models\habit.py
- `Food Log Models Tracks meal entries with detailed metadata for AI analysis` --uses--> `PyObjectId`  [INFERRED]
  D:\Projects\Speak-Sync\apps\lifestyle-service\src\models\food_log.py → D:\Projects\Speak-Sync\apps\lifestyle-service\src\models\habit.py
- `Food log as stored in database` --uses--> `PyObjectId`  [INFERRED]
  D:\Projects\Speak-Sync\apps\lifestyle-service\src\models\food_log.py → D:\Projects\Speak-Sync\apps\lifestyle-service\src\models\habit.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.01
Nodes (372): getRetryCount(), handleMessage(), retryMessage(), sendToDeadLetterQueue(), stopConsuming(), CategoryController, #a(), ae() (+364 more)

### Community 1 - "Community 1"
Cohesion: 0.01
Nodes (319): ac(), ad(), addErrorMessage(), addField(), addItem(), addMarginSymbol(), addSuggestion(), afterNextNewline() (+311 more)

### Community 2 - "Community 2"
Cohesion: 0.02
Nodes (180): ActionExecutorService, get_action_executor(), Action Executor Service - Maps NLU intents to real backend API actions Like Iron, Maps detected intents to real API actions on Scheduler & Lifestyle services., Execute the action mapped to the detected intent.                  Args:, Build API payload from extracted entities using the mapping.         Fills smart, Check which required fields are missing., Replace {id} placeholders in endpoint URLs. (+172 more)

### Community 3 - "Community 3"
Cohesion: 0.02
Nodes (154): startConsuming(), BaseModel, acquire(), Database, get_rabbitmq(), init_rabbitmq(), RabbitMQConnection, RabbitMQ Connection Manager - Singleton Pattern Handles connection lifecycle wi (+146 more)

### Community 4 - "Community 4"
Cohesion: 0.02
Nodes (45): AuthController, AuthService, constructor(), CategoryService, errorHandler(), EventService, export_csv(), export_json() (+37 more)

### Community 5 - "Community 5"
Cohesion: 0.03
Nodes (136): DataLoader, MergedExtensionsList, RequestHandler, Skip, TypedSql, RabbitMQ Configuration, Config, __get_pydantic_core_schema__() (+128 more)

### Community 6 - "Community 6"
Cohesion: 0.02
Nodes (91): read(), close_db(), init_db(), Close Redis connection, Set key with expiration                  Args:             key: Cache key, Set key with expiration in one call, Set expiration on existing key, Initialize database connections (+83 more)

### Community 7 - "Community 7"
Cohesion: 0.04
Nodes (74): HabitFormationModel, ML Model for Habit Formation and Prediction Uses behavioral science and machine, Predict how automatic the habit feels (0-1)                  Based on research:, Machine Learning model for habit formation prediction     Based on behavioral ps, Calculate risk of breaking habit (0-1) and risk level                  Returns:, Predict probability of long-term success                  Returns probabilities, Identify current stage in behavior change model, Identify patterns in failed attempts                  Returns triggers that corr (+66 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (82): Config, ExerciseLogBase, ExerciseLogCreate, ExerciseLogInDB, ExerciseLogResponse, ExerciseLogUpdate, Exercise Log Models Tracks workout sessions with RPE and recovery data for AI a, Response model for exercise log (+74 more)

### Community 9 - "Community 9"
Cohesion: 0.04
Nodes (3): AIBrainService, LifestyleService, ServiceRegistry

### Community 10 - "Community 10"
Cohesion: 0.11
Nodes (41): Config, Study Log model for MongoDB with stickiness factor tracking, Base study log fields with stickiness tracking, Study log as stored in database, Study log response model, Study log creation model, Study log update model - all fields optional, get_study_log_service() (+33 more)

### Community 11 - "Community 11"
Cohesion: 0.06
Nodes (25): $(), a(), de(), F, fe(), G(), ge(), I() (+17 more)

### Community 12 - "Community 12"
Cohesion: 0.11
Nodes (37): Config, FoodLogBase, FoodLogCreate, FoodLogInDB, FoodLogResponse, FoodLogUpdate, Food Log Models Tracks meal entries with detailed metadata for AI analysis, Food log as stored in database (+29 more)

### Community 13 - "Community 13"
Cohesion: 0.06
Nodes (23): object, add_HealthServiceServicer_to_server(), add_VoiceServiceServicer_to_server(), HealthService, HealthServiceServicer, HealthServiceStub, ===== Complete Conversation Flow =====          Full conversation: User speaks →, Voice AI Service - Complete STT, TTS, and Conversation handling     ===== STT (S (+15 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (12): get_realtime_service(), Supabase Realtime Client ──────────────────────── Wraps Supabase's Realtime WebS, Push AI-generated proactive nudge to Flutter.         Called by BehavioralObserv, Push conversation turn to Flutter for real-time transcript display, Upload TTS audio to Supabase Storage (instead of local filesystem).         Retu, Retrieve cached TTS audio from Supabase Storage, Broadcast an event via Supabase Realtime channel, Get or create SupabaseRealtimeService singleton (+4 more)

### Community 15 - "Community 15"
Cohesion: 0.17
Nodes (9): BehavioralObserver, get_behavioral_observer(), Behavioral Observer Service ────────────────────────── Continuously learns from, Build a dynamic user profile from all stored observations.         Called before, Generate a proactive nudge based on behavioral patterns.         Called by the b, Called BEFORE every LLM response to inject behavioral context.         Makes the, Retrieve observations from memory, 24/7 Humanly Behavioral Learning System      Uses google/gemini-2.0-flash-exp:fr (+1 more)

### Community 16 - "Community 16"
Cohesion: 0.32
Nodes (1): HabitStreakConsumer

### Community 17 - "Community 17"
Cohesion: 0.33
Nodes (1): EmailNotificationConsumer

### Community 18 - "Community 18"
Cohesion: 0.33
Nodes (2): TaskReminderConsumer, toLocaleString()

### Community 19 - "Community 19"
Cohesion: 0.4
Nodes (4): AnyNull, DbNull, JsonNull, PrismaClient

### Community 20 - "Community 20"
Cohesion: 0.5
Nodes (2): c(), k()

### Community 21 - "Community 21"
Cohesion: 0.4
Nodes (0): 

### Community 22 - "Community 22"
Cohesion: 0.5
Nodes (1): GroqClient

### Community 23 - "Community 23"
Cohesion: 0.67
Nodes (1): PrismaClient

### Community 24 - "Community 24"
Cohesion: 0.67
Nodes (1): WhisperClient

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (0): 

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): Generate Python gRPC code from proto files Run this after modifying voice.proto

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (0): 

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (0): 

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): Get connection from pool (context manager)

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): Check if two time ranges overlap

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (0): 

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (0): 

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (0): 

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (0): 

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (0): 

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (0): 

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (0): 

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (0): 

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (0): 

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (0): 

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (0): 

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (0): 

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (0): 

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (0): 

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (0): 

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (0): 

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (0): 

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (0): 

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (0): 

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (0): 

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (0): 

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (0): 

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (0): 

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (0): 

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (0): 

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (0): 

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (0): 

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (0): 

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (0): 

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (0): 

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (0): 

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (0): 

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (0): 

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (0): 

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (0): 

### Community 77 - "Community 77"
Cohesion: 1.0
Nodes (1): Intercept NOTIFY_DEBUGGER_ABOUT_RX_PAGES and touch the pages.

## Knowledge Gaps
- **289 isolated node(s):** `Generate Python gRPC code from proto files Run this after modifying voice.proto`, `Start gRPC server          Args:         host: Server host (default: 0.0.0.0)`, `Run database migration for pgvector setup`, `Execute pgvector setup migration`, `Chat API Routes - NLU and conversational AI endpoints` (+284 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 25`** (2 nodes): `walk()`, `bundle_codebase.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (2 nodes): `generate_grpc.py`, `Generate Python gRPC code from proto files Run this after modifying voice.proto`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (2 nodes): `role.middleware.ts`, `requireRole()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (2 nodes): `setup-python-services.ps1`, `Setup-PythonService()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `test-scheduler-api.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `Get connection from pool (context manager)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `voice_pb2.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `Check if two time ranges overlap`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `prisma.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `client.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `client.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `default.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `default.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `edge.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `edge.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `index.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `query_compiler_bg.wasm-base64.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `wasm-edge-light-loader.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `wasm-worker-loader.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `index-browser.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `worker.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `index.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `index.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `index.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `index.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `habit.events.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `notification.events.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `schedule.events.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `user.events.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `migrate-to-free-stack.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `run-ai-brain.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `run-lifestyle.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `setup-env.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `verify-env.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `Intercept NOTIFY_DEBUGGER_ABOUT_RX_PAGES and touch the pages.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get()` connect `Community 2` to `Community 0`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 14`, `Community 15`?**
  _High betweenness centrality (0.211) - this node is a cross-community bridge._
- **Why does `Gl()` connect `Community 1` to `Community 3`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `request()` connect `Community 0` to `Community 9`, `Community 2`, `Community 3`, `Community 1`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 104 inferred relationships involving `str` (e.g. with `health_check()` and `run_migration()`) actually correct?**
  _`str` has 104 INFERRED edges - model-reasoned connections that need verification._
- **Are the 87 inferred relationships involving `VectorOperations` (e.g. with `lifespan()` and `Startup and shutdown events`) actually correct?**
  _`VectorOperations` has 87 INFERRED edges - model-reasoned connections that need verification._
- **Are the 89 inferred relationships involving `get()` (e.g. with `.StreamTranscribe()` and `.TranscribeAudio()`) actually correct?**
  _`get()` has 89 INFERRED edges - model-reasoned connections that need verification._
- **Are the 71 inferred relationships involving `VectorMemoryService` (e.g. with `lifespan()` and `Startup and shutdown events`) actually correct?**
  _`VectorMemoryService` has 71 INFERRED edges - model-reasoned connections that need verification._
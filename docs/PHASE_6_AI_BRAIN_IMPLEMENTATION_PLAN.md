# 🧠 Phase 6: AI Brain Service - Complete Implementation Plan

**Timeline**: 10-14 Days | **Status**: Planning Phase
**Real-time Communication**: gRPC for voice streaming & live suggestions

---

## 📋 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Voice Interaction Principles](#voice-interaction-principles)
3. [Implementation Roadmap](#implementation-roadmap)
4. [Technical Stack](#technical-stack)
5. [Detailed Feature Breakdown](#detailed-feature-breakdown)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       Gateway Service                            │
│                  (HTTP REST + gRPC Client)                       │
└──────────────┬──────────────────────────────────────────────────┘
               │
               │ HTTP REST (Non-real-time)
               │ gRPC Stream (Voice + Real-time)
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI Brain Service (Python)                     │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Voice Engine │  │  NLU Engine  │  │ Context Mgr  │          │
│  │  (Whisper)   │  │   (Groq)     │  │  (pgvector)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │Smart Suggest │  │ Pattern Rec. │  │  Embeddings  │          │
│  │   Engine     │  │   (ML)       │  │   Storage    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└──────────────┬────────────────────────────────────┬─────────────┘
               │                                    │
               │                                    │
               ▼                                    ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│  Scheduler Service (PG)  │      │  Lifestyle Service (Mongo)│
│  - Tasks, Events         │      │  - Habits, Logs          │
└──────────────────────────┘      └──────────────────────────┘
```

---

## 🎙️ Complete Voice AI Flow (STT → LLM → TTS)

### Real-World Example: Hydration Logging

```
┌─────────────────────────────────────────────────────────────────┐
│  USER SPEAKS: "Just finished my coffee, switching to my green   │
│                water bottle now."                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STT (Whisper): Transcribes audio → text                         │
│  Output: "Just finished my coffee, switching to my green water  │
│           bottle now."                                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  LLM (Groq): Understands intent + extracts entities              │
│                                                                   │
│  Context: User's water container definitions:                    │
│   - "Green Bottle" = 750ml                                       │
│   - "Coffee" = caffeine tracker                                  │
│                                                                   │
│  Output: {                                                        │
│    intent: "log_hydration",                                      │
│    intake_type: "coffee",                                        │
│    next_source: "green_bottle",                                  │
│    volume: 750,                                                   │
│    response: "Got it! Logged your coffee. I'll remind you       │
│               about the green bottle in 2 hours.",              │
│    emotion: "calm"                                               │
│  }                                                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  TTS (Coqui): Synthesizes natural voice response                 │
│                                                                   │
│  Text: "Got it! Logged your coffee. I'll remind you about the   │
│         green bottle in 2 hours."                                │
│  Voice: en-us-female-calm                                        │
│  Emotion: calm                                                   │
│                                                                   │
│  Output: 🔊 Audio stream (WAV/MP3)                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  USER HEARS: Natural voice response                              │
│  🎧 "Got it! Logged your coffee. I'll remind you about the      │
│      green bottle in 2 hours."                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Total Latency Target**: <3 seconds (STT: 500ms, LLM: 1s, TTS: 1s, Network: 500ms)

---

## 🎙️ Voice Interaction Principles

### Core Philosophy: **Conversational, Not Interrogational**

#### ❌ BAD PATTERNS (Survey Mode)
```
AI: "What was your RPE? What was your duration? How do you feel?"
User: Gets frustrated and abandons app
```

#### ✅ GOOD PATTERNS (Conversation Mode)
```
AI: "Welcome back! You crushed that gym session. How did it feel compared to last time?"
User: "Honestly, leg day killed me today. I was in there for an hour but had zero energy at the end."
AI: [Extracts: Activity=Gym, Focus=Legs, Duration=60, RPE=9/10, Energy=Low]
```

### Extraction Strategy

Each domain has specific extraction rules:

| Domain | Context Trigger | Conversational Prompt | Extracted Fields |
|--------|----------------|----------------------|------------------|
| **Exercise** | Post-workout check-in | "How did the session go compared to last time?" | Activity_Type, Focus_Area, Duration, RPE, Post_Activity_Energy |
| **Financial** | Immediate after purchase | User vents naturally | Amount, Currency, Category, Necessity_Score, Associated_Mood |
| **Sleep** | Morning greeting | "I see you're up earlier. How did you sleep?" | Wake_Time, Sleep_Latency, Grogginess_Level, Sleep_Quality |
| **Productivity** | Post deep-work block | "That was your 2-hour block. How did it go?" | Task_Status, Actual_Duration, Deviation, Interruption_Source, Flow_State_Score |
| **Hydration** | Container context | "Just finished coffee, switching to green bottle." | Intake_Type, Next_Source, Auto_Schedule_Reminder |

---

## 🗓️ Implementation Roadmap

### **Week 1: Foundation (Days 1-7)**

#### **Part 1: Database & Infrastructure Setup** (Days 1-2)
- [ ] Set up pgvector extension in PostgreSQL
- [ ] Create embeddings tables (task_embeddings, habit_embeddings, user_context)
- [ ] Set up Redis for real-time context caching
- [ ] Configure Groq API credentials
- [ ] Configure OpenAI Whisper API credentials
- [ ] Set up gRPC server in AI Brain Service
- [ ] Set up gRPC client in Gateway Service

**Deliverables:**
- Migration files for pgvector schema
- Working gRPC bidirectional streaming
- Environment configuration validated

---

#### **Part 2: Voice Engine (STT + TTS)** (Days 3-5)

##### **2A: Speech-to-Text (Whisper)** (Day 3)
- [ ] Implement OpenAI Whisper STT endpoint
- [ ] Add audio file upload (WAV, MP3, M4A support)
- [ ] Implement streaming audio via gRPC
- [ ] Add multi-language support (English, Hindi, etc.)
- [ ] Error handling for poor audio quality
- [ ] Unit tests for transcription service

**Endpoints:**
```python
POST /api/ai/transcribe         # HTTP upload (file)
gRPC VoiceStream.Transcribe     # Real-time streaming
```

**Testing:**
```bash
curl -X POST http://localhost:8003/api/ai/transcribe \
  -F "audio=@test-voice.wav" \
  -F "language=en"
```

#### **Part 3: Natural Language Understanding Core** (Days 6-7)
- [ ] Install and configure Coqui TTS (Chatterbots)
- [ ] Download pre-trained models (VITS, Tacotron2)
- [ ] Implement TTS service with voice customization
- [ ] Add emotion/tone control (calm, energetic, empathetic)
- [ ] Implement audio streaming via gRPC
- [ ] Cache frequently used phrases
- [ ] Multi-language voice support
- [ ] Unit tests for TTS service

**Endpoints:**
```python
POST /api/ai/synthesize         # HTTP text-to-speech
gRPC VoiceStream.Synthesize     # Real-time TTS streaming
POST /api/ai/voices             # List available voices
```

**Testing:**
```bash
curl -X POST http://localhost:8003/api/ai/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Welcome back! Ready to log your meditation?", "voice": "en-us-female", "emotion": "calm"}' \
  --output response.wav
```

---

#### **Part 3: Natural Language Understanding Core** (Days 5-7)
- [ ] Implement Groq LLM integration (Llama 3.3 70B)
- [ ] Create domain-specific prompt templates:
  - Exercise logging prompt
  - Financial tracking prompt
  - Sleep tracking prompt
  - Task creation prompt
  - Habit logging prompt
- [ ] Implement intent classification
- [ ] Implement entity extraction (dates, amounts, categories, etc.)
- [ ] Add JSON response validation
- [ ] Add conversational memory (last 5 interactions)

**Key Service:**
```python
# apps/ai-brain-service/src/services/nlu_service.py
class NLUService:
    async def parse_intent(user_input: str, user_context: dict) -> IntentResult
    async def extract_entities(text: str, domain: str) -> dict
    async def classify_priority(task_description: str) -> str  # VI/MI/NI
```

---

### **Week 2: Smart Features & Conversational AI (Days 8-14)**

#### **Part 4: Conversational Voice AI Flow** (Day 8)
- [ ] Implement complete STT → LLM → TTS pipeline
- [ ] Add conversation state management
- [ ] Implement context retention (last 5 exchanges)
- [ ] Add emotion detection from user voice
- [ ] Dynamic TTS emotion matching
- [ ] Implement interruption handling
- [ ] Add "thinking" audio cues
- [ ] Test full voice conversation flow

**Complete Voice Flow:**
```
User speaks → STT (Whisper) → Context + LLM (Groq) → TTS (Coqui) → User hears
```

---

#### **Part 5: Smart Task Suggestions** (Days 9-10)
- [ ] Implement task intent parsing with Groq
- [ ] Auto-classification of priority (VI/MI/NI) based on keywords
- [ ] Intelligent due date parsing ("tomorrow", "next Monday", etc.)
- [ ] Integration with scheduler service (create task via API)
- [ ] Suggested time blocking on calendar
- [ ] Few-shot learning from user's historical tasks

**Example Flow:**
#### **Part 6: Context-Aware Suggestions** (Days 11-12)
User: "I need to prepare for tomorrow's client meeting"

AI Processing:
1. Intent: Create task
2. Priority: VI (keyword: "meeting" + "tomorrow")
3. Due date: 2025-12-05 09:00 AM (context: meetings usually at 9am)
4. Suggested time block: 2025-12-04 15:00-17:00 (2 hours prep)

Output:
- Create task "Prepare for client meeting" (VI, due: tomorrow 9am)
- Create task "Review agenda" (MI, due: today)
- Suggest calendar block: Today 3-5pm
```

---

#### **Part 5: Context-Aware Suggestions** (Days 10-11)
- [ ] Implement user behavior pattern recognition
- [ ] Time-based suggestion engine (morning/evening routines)
- [ ] Habit streak prediction
- [ ] Proactive reminders based on patterns
- [ ] Store behavior embeddings in pgvector
- [ ] Query similar past behaviors for suggestions

**Pattern Recognition:**
```python
# Example: Friday evening pattern
if current_time.weekday() == 4 and current_time.hour >= 17:
    if user_usually_plans_weekend():
        suggest("Review your tasks for next week?")

# Example: Morning meditation habit
if current_time.hour < 10 and user.meditation_habit.completion_rate > 0.8:
    if not logged_today("meditation"):
        suggest("Ready to log your meditation?")
```

#### **Part 7: Smart Scheduling Assistant** (Day 13)
```sql
CREATE TABLE user_behavior_embeddings (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(36),
  behavior_type VARCHAR(50),  -- 'task_completion', 'habit_log', 'schedule_pattern'
  embedding vector(1536),
  metadata JSONB,              -- {day_of_week, time_of_day, success, context}
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON user_behavior_embeddings 
USING ivfflat (embedding vector_cosine_ops);
```

---

#### **Part 6: Smart Scheduling Assistant** (Days 12-13)
- [ ] Implement calendar conflict checking
- [ ] Contact/attendee extraction from past events
- [ ] Time preference learning (morning person vs night owl)
- [ ] Location suggestions based on history
- [ ] Meeting duration prediction
- [ ] Best time slot recommendation

**Example:**
```
User: "Schedule coffee with John next week"

AI Analysis:
1. Extract contact: "John" → Found in past events (john@example.com)
2. User preference: 85% of meetings scheduled 9-11am
3. Calendar check: Tuesday 10am free, no conflicts
4. Location history: 70% meetings at "Cafe Downtown"

Suggestion:
"How about Tuesday 10am at Cafe Downtown? That's when you both 
usually have coffee meetings."
```

---

#### **Part 8: Habit Insights & Analytics** (Day 14)
- [ ] Implement MongoDB aggregation for habit patterns
- [ ] Statistical analysis (completion rates, streaks, time patterns)
- [ ] Natural language insight generation
- [ ] Visualization data endpoints (charts/graphs)
- [ ] Weekly/monthly summary reports

**Insights Examples:**
```
- "You complete workouts 90% more on Mondays than Fridays"
- "Your meditation streak breaks most often on weekends"
- "Tasks marked VI are completed 2 days earlier on average"
- "You're most productive between 9-11am"
- "Your sleep quality drops below 6/10 when you work past 11pm"
```

---

## 🛠️ Technical Stack

### Core Technologies
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **AI/ML** | Groq (Llama 3.3 70B) | Intent parsing, entity extraction |
| **Speech-to-Text** | OpenAI Whisper | Voice transcription |
| **Text-to-Speech** | Coqui TTS (Chatterbots) | Natural voice responses |
| **Embeddings** | OpenAI text-embedding-3-small | Semantic search |
| **Vector DB** | pgvector (PostgreSQL) | Store & query embeddings |
| **Real-time** | gRPC | Voice streaming, live suggestions |
| **Caching** | Redis | User context, recent interactions |
| **Message Queue** | RabbitMQ | Async processing (insights generation) |

### New Dependencies to Add
```txt
# AI & ML
groq==0.13.0
openai==1.58.1
sentence-transformers==2.2.2

# Text-to-Speech (Coqui TTS)
TTS==0.22.0
torch==2.1.2
torchaudio==2.1.2
pydub==0.25.1

# Real-time Communication
grpcio==1.60.0
grpcio-tools==1.60.0

# Vector Operations
pgvector==0.3.6
numpy==1.26.3

# Audio Processing
soundfile==0.12.1
librosa==0.10.1

# Async & Performance
asyncio==3.4.3
aioredis==2.0.1
```

---

## 🔧 Detailed Feature Breakdown

### Feature 1: Smart Task Suggestions

#### Backend Service
**File:** `apps/ai-brain-service/src/services/task_assistant.py`

```python
from groq import Groq
from typing import Dict, List
import datetime

class TaskAssistant:
    def __init__(self, groq_client: Groq, pgvector_service):
        self.groq = groq_client
        self.pgvector = pgvector_service
    
    async def parse_task_intent(
        self, 
        user_input: str, 
        user_context: Dict
    ) -> Dict:
        """
        Parse natural language into structured task data
        
        Args:
            user_input: "I need to prepare for meeting tomorrow"
            user_context: {
                'user_id': 'uuid',
                'timezone': 'Asia/Kolkata',
                'past_tasks': [...],
                'current_time': datetime
            }
        
        Returns:
            {
                'tasks': [
                    {
                        'title': 'Prepare for client meeting',
                        'priority': 'VI',
                        'due_date': '2025-12-05T09:00:00Z',
                        'category': 'Work'
                    }
                ],
                'suggested_blocks': [
                    {
                        'title': 'Meeting prep time',
                        'start': '2025-12-04T15:00:00Z',
                        'end': '2025-12-04T17:00:00Z'
                    }
                ]
            }
        """
        
        # Build context-aware system prompt
        system_prompt = self._build_system_prompt(user_context)
        
        # Call Groq with structured output
        completion = await self.groq.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(completion.choices[0].message.content)
        
        # Enhance with ML predictions
        result = await self._enhance_with_ml(result, user_context)
        
        return result
    
    def _build_system_prompt(self, context: Dict) -> str:
        """Generate context-aware system prompt"""
        return f"""You are a task management AI assistant for LifeOS.

User Context:
- Timezone: {context['timezone']}
- Current time: {context['current_time']}
- Recent task patterns: {context.get('past_tasks_summary', 'None')}

Rules:
1. Parse user input into structured task data
2. Classify priority: VI (urgent/important), MI (moderate), NI (nice-to-have)
3. Extract due dates (support: "tomorrow", "next Monday", "in 3 days")
4. Suggest related subtasks if complex
5. Recommend time blocks for task completion

Priority Classification:
- VI: meetings, deadlines, "urgent", "important", "asap"
- MI: regular work, "should", "need to"
- NI: "maybe", "someday", "want to"

Respond in JSON:
{{
  "tasks": [
    {{
      "title": "string",
      "description": "string (optional)",
      "priority": "VI|MI|NI",
      "due_date": "ISO 8601",
      "category": "Work|Personal|Learning|etc",
      "estimated_minutes": number
    }}
  ],
  "suggested_blocks": [
    {{
      "title": "string",
      "start": "ISO 8601",
      "end": "ISO 8601"
    }}
  ]
}}
"""
    
    async def _enhance_with_ml(self, result: Dict, context: Dict) -> Dict:
        """Use ML to enhance predictions"""
        
        for task in result['tasks']:
            # Query similar past tasks from pgvector
            embedding = await self._get_embedding(task['title'])
            similar_tasks = await self.pgvector.query_similar(
                user_id=context['user_id'],
                embedding=embedding,
                limit=5
            )
            
            # Adjust priority based on historical patterns
            if similar_tasks:
                priority_votes = [t['priority'] for t in similar_tasks]
                predicted_priority = max(set(priority_votes), key=priority_votes.count)
                
                # Override if ML is confident
                if priority_votes.count(predicted_priority) >= 4:
                    task['priority_ml_suggested'] = predicted_priority
            
            # Predict time estimate
            if similar_tasks:
                avg_time = sum(t['actual_time_minutes'] for t in similar_tasks if t['actual_time_minutes']) / len(similar_tasks)
                task['estimated_minutes'] = int(avg_time)
        
        return result
```

#### API Endpoint
**File:** `apps/ai-brain-service/src/api/routes/tasks.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/ai/tasks", tags=["Task AI"])

class TaskIntentRequest(BaseModel):
    user_input: str
    user_id: str

class TaskIntentResponse(BaseModel):
    tasks: List[Dict]
    suggested_blocks: List[Dict]
    confidence: float

@router.post("/parse-intent", response_model=TaskIntentResponse)
async def parse_task_intent(
    request: TaskIntentRequest,
    task_assistant: TaskAssistant = Depends()
):
    """
    Parse natural language into structured task data
    
    Example:
        POST /api/ai/tasks/parse-intent
        {
            "user_input": "I need to prepare for meeting tomorrow",
            "user_id": "user-123"
        }
    """
    try:
        # Get user context
        user_context = await get_user_context(request.user_id)
        
        # Parse intent
        result = await task_assistant.parse_task_intent(
            user_input=request.user_input,
            user_context=user_context
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Feature 2: Voice Input with Whisper

#### Whisper Service
**File:** `apps/ai-brain-service/src/services/voice_service.py`

```python
import openai
from typing import Optional
import aiofiles
import os

class VoiceService:
    def __init__(self, openai_client: openai.AsyncOpenAI):
        self.client = openai_client
    
    async def transcribe_audio(
        self,
        audio_file_path: str,
        language: Optional[str] = None
    ) -> Dict:
        """
        Transcribe audio using OpenAI Whisper
        
        Args:
            audio_file_path: Path to audio file (WAV, MP3, M4A)
            language: Optional language code (en, hi, etc.)
        
        Returns:
            {
                'text': 'Transcribed text',
                'language': 'en',
                'confidence': 0.95
            }
        """
        
        async with aiofiles.open(audio_file_path, 'rb') as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json"
            )
        
        return {
            'text': transcript.text,
            'language': transcript.language,
            'confidence': self._calculate_confidence(transcript)
        }
    
    async def transcribe_stream(self, audio_stream):
        """
        Real-time transcription via gRPC stream
        """
        # Implementation for streaming transcription
        pass
```

---

## 🔊 Text-to-Speech (TTS) Implementation

### TTS Service with Coqui (Chatterbots)
**File:** `apps/ai-brain-service/src/services/tts_service.py`

```python
import torch
from TTS.api import TTS
from typing import Optional, Dict
import io
import aiofiles
from pydub import AudioSegment
import hashlib
import asyncio
from pathlib import Path

class TTSService:
    """
    Text-to-Speech service using Coqui TTS (Chatterbots)
    Supports multiple voices, emotions, and streaming output
    """
    
    def __init__(self, cache_dir: str = "./tts_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize TTS models
        self.models = {}
        self._load_models()
        
        # Voice configurations
        self.voices = {
            "en-us-female-calm": {
                "model": "tts_models/en/ljspeech/tacotron2-DDC",
                "emotion": "calm",
                "speaking_rate": 1.0
            },
            "en-us-female-energetic": {
                "model": "tts_models/en/ljspeech/vits",
                "emotion": "energetic",
                "speaking_rate": 1.1
            },
            "en-us-female-empathetic": {
                "model": "tts_models/en/ljspeech/tacotron2-DDC",
                "emotion": "empathetic",
                "speaking_rate": 0.95
            },
            "en-us-male": {
                "model": "tts_models/en/ljspeech/tacotron2-DDC",
                "emotion": "neutral",
                "speaking_rate": 1.0
            },
            "hi-in-female": {
                "model": "tts_models/hi/cv/vits",  # Hindi support
                "emotion": "neutral",
                "speaking_rate": 1.0
            }
        }
    
    def _load_models(self):
        """Load TTS models into memory"""
        
        # Load English model (VITS - high quality, fast)
        self.models['en-vits'] = TTS(
            model_name="tts_models/en/ljspeech/vits",
            gpu=torch.cuda.is_available()
        )
        
        # Load Tacotron2 for emotion control
        self.models['en-tacotron2'] = TTS(
            model_name="tts_models/en/ljspeech/tacotron2-DDC",
            gpu=torch.cuda.is_available()
        )
        
        # Load Hindi model
        self.models['hi-vits'] = TTS(
            model_name="tts_models/hi/cv/vits",
            gpu=torch.cuda.is_available()
        )
    
    async def synthesize(
        self,
        text: str,
        voice: str = "en-us-female-calm",
        emotion: Optional[str] = None,
        output_format: str = "wav",
        use_cache: bool = True
    ) -> bytes:
        """
        Convert text to speech
        
        Args:
            text: Text to synthesize
            voice: Voice ID from self.voices
            emotion: Override emotion (calm/energetic/empathetic)
            output_format: Output format (wav/mp3)
            use_cache: Use cached audio if available
        
        Returns:
            Audio bytes
        """
        
        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(text, voice, emotion)
            cached_audio = await self._get_from_cache(cache_key, output_format)
            if cached_audio:
                return cached_audio
        
        # Get voice config
        voice_config = self.voices.get(voice, self.voices["en-us-female-calm"])
        if emotion:
            voice_config = {**voice_config, "emotion": emotion}
        
        # Select model
        if "tacotron2" in voice_config["model"]:
            model = self.models['en-tacotron2']
        elif "hi" in voice_config["model"]:
            model = self.models['hi-vits']
        else:
            model = self.models['en-vits']
        
        # Preprocess text for natural speech
        text = self._preprocess_text(text, voice_config["emotion"])
        
        # Generate audio
        wav_path = self.cache_dir / f"temp_{cache_key}.wav"
        
        # Run TTS in thread pool (CPU intensive)
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: model.tts_to_file(
                text=text,
                file_path=str(wav_path),
                speaker_wav=None,
                language="en" if "en" in voice else "hi"
            )
        )
        
        # Convert format if needed
        audio_bytes = await self._convert_audio_format(wav_path, output_format)
        
        # Cache result
        if use_cache:
            await self._save_to_cache(cache_key, audio_bytes, output_format)
        
        # Cleanup temp file
        wav_path.unlink(missing_ok=True)
        
        return audio_bytes
    
    def _preprocess_text(self, text: str, emotion: str) -> str:
        """Add prosody markers based on emotion"""
        
        if emotion == "energetic":
            # Add excitement
            text = text.replace("!", "!!")
            text = text.replace(".", "!")
        elif emotion == "empathetic":
            # Softer tone
            text = text.replace(".", "...")
        elif emotion == "calm":
            # Neutral, clear
            pass
        
        return text
    
    async def _convert_audio_format(
        self, 
        input_path: Path, 
        output_format: str
    ) -> bytes:
        """Convert audio to desired format"""
        
        audio = AudioSegment.from_wav(str(input_path))
        
        # Optimize for voice
        audio = audio.set_channels(1)  # Mono
        audio = audio.set_frame_rate(16000)  # 16kHz
        
        # Export to bytes
        buffer = io.BytesIO()
        audio.export(buffer, format=output_format, bitrate="64k")
        buffer.seek(0)
        
        return buffer.read()
    
    def _get_cache_key(self, text: str, voice: str, emotion: Optional[str]) -> str:
        """Generate cache key"""
        key_str = f"{text}_{voice}_{emotion or 'none'}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def _get_from_cache(
        self, 
        cache_key: str, 
        format: str
    ) -> Optional[bytes]:
        """Retrieve cached audio"""
        cache_path = self.cache_dir / f"{cache_key}.{format}"
        
        if cache_path.exists():
            async with aiofiles.open(cache_path, 'rb') as f:
                return await f.read()
        
        return None
    
    async def _save_to_cache(
        self, 
        cache_key: str, 
        audio_bytes: bytes, 
        format: str
    ):
        """Save audio to cache"""
        cache_path = self.cache_dir / f"{cache_key}.{format}"
        
        async with aiofiles.open(cache_path, 'wb') as f:
            await f.write(audio_bytes)
    
    async def stream_synthesize(self, text: str, voice: str):
        """
        Stream TTS output for low-latency responses
        Yields audio chunks as they're generated
        """
        
        # Split text into sentences for streaming
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            audio_chunk = await self.synthesize(
                text=sentence,
                voice=voice,
                use_cache=True
            )
            yield audio_chunk
    
    def _split_into_sentences(self, text: str) -> list:
        """Split text into sentences for streaming"""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def get_available_voices(self) -> Dict:
        """Return list of available voices"""
        return {
            voice_id: {
                "name": voice_id,
                "language": "en" if "en" in voice_id else "hi",
                "gender": "female" if "female" in voice_id else "male",
                "emotion": config["emotion"]
            }
            for voice_id, config in self.voices.items()
        }
```

### TTS API Endpoints
**File:** `apps/ai-brain-service/src/api/routes/tts.py`

```python
from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/ai", tags=["Text-to-Speech"])

class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "en-us-female-calm"
    emotion: Optional[str] = None
    format: str = "wav"

@router.post("/synthesize")
async def synthesize_speech(
    request: SynthesizeRequest,
    tts_service: TTSService = Depends()
):
    """
    Convert text to speech
    
    Example:
        POST /api/ai/synthesize
        {
            "text": "Welcome back! Ready to log your meditation?",
            "voice": "en-us-female-calm",
            "emotion": "calm",
            "format": "wav"
        }
    
    Response:
        Audio file (WAV/MP3)
    """
    try:
        audio_bytes = await tts_service.synthesize(
            text=request.text,
            voice=request.voice,
            emotion=request.emotion,
            output_format=request.format
        )
        
        return Response(
            content=audio_bytes,
            media_type=f"audio/{request.format}",
            headers={
                "Content-Disposition": f'attachment; filename="response.{request.format}"'
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/synthesize-stream")
async def synthesize_speech_stream(
    request: SynthesizeRequest,
    tts_service: TTSService = Depends()
):
    """
    Stream TTS output for low-latency (sentence by sentence)
    """
    async def audio_generator():
        async for audio_chunk in tts_service.stream_synthesize(
            text=request.text,
            voice=request.voice
        ):
            yield audio_chunk
    
    return StreamingResponse(
        audio_generator(),
        media_type=f"audio/{request.format}"
    )

@router.get("/voices")
async def list_voices(tts_service: TTSService = Depends()):
    """
    Get available TTS voices
    
    Response:
        {
            "en-us-female-calm": {
                "name": "en-us-female-calm",
                "language": "en",
                "gender": "female",
                "emotion": "calm"
            },
            "en-us-female-energetic": {...},
            ...
        }
    """
    return tts_service.get_available_voices()
```

### Complete Voice Conversation Flow
**File:** `apps/ai-brain-service/src/services/conversation_service.py`

```python
class ConversationService:
    """
    Orchestrates complete voice conversation:
    User speaks → STT → Context + LLM → TTS → User hears
    """
    
    def __init__(
        self,
        voice_service: VoiceService,
        nlu_service: NLUService,
        tts_service: TTSService,
        context_manager: ContextManager
    ):
        self.voice = voice_service
        self.nlu = nlu_service
        self.tts = tts_service
        self.context = context_manager
    
    async def handle_conversation(
        self,
        audio_stream,
        user_id: str,
        session_id: str
    ):
        """
        Complete voice conversation flow
        
        Flow:
        1. User speaks (audio stream)
        2. STT transcribes
        3. Get user context
        4. LLM processes with conversational style
        5. TTS synthesizes response
        6. Stream audio back to user
        """
        
        # Step 1 & 2: Transcribe user input
        transcript = await self.voice.transcribe_stream(audio_stream)
        
        yield {
            'type': 'transcript',
            'text': transcript['text'],
            'is_final': True
        }
        
        # Step 3: Get user context
        user_context = await self.context.get_context(user_id, session_id)
        
        # Step 4: Process with LLM (conversational style)
        llm_response = await self.nlu.process_conversational(
            user_input=transcript['text'],
            user_context=user_context,
            conversation_history=user_context['recent_messages']
        )
        
        yield {
            'type': 'llm_response',
            'text': llm_response['response_text'],
            'intent': llm_response['intent'],
            'entities': llm_response['entities']
        }
        
        # Step 5 & 6: Synthesize and stream response
        selected_voice = self._select_voice(llm_response.get('emotion', 'calm'))
        
        async for audio_chunk in self.tts.stream_synthesize(
            text=llm_response['response_text'],
            voice=selected_voice
        ):
            yield {
                'type': 'audio',
                'audio_data': audio_chunk,
                'is_final': False
            }
        
        # Final marker
        yield {
            'type': 'audio',
            'audio_data': b'',
            'is_final': True
        }
        
        # Update context
        await self.context.add_exchange(
            user_id=user_id,
            session_id=session_id,
            user_message=transcript['text'],
            assistant_message=llm_response['response_text']
        )
    
    def _select_voice(self, emotion: str) -> str:
        """Select appropriate TTS voice based on emotion"""
        
        emotion_voice_map = {
            "calm": "en-us-female-calm",
            "energetic": "en-us-female-energetic",
            "empathetic": "en-us-female-empathetic",
            "excited": "en-us-female-energetic",
            "neutral": "en-us-female-calm"
        }
        
        return emotion_voice_map.get(emotion, "en-us-female-calm")
```

---

#### gRPC Service Definition (Complete: STT + TTS)
**File:** `apps/ai-brain-service/protos/voice.proto`

```protobuf
syntax = "proto3";

package voice;

service VoiceService {
  // STT: Bidirectional streaming for real-time transcription
  rpc StreamTranscribe(stream AudioChunk) returns (stream TranscriptChunk);
  
  // STT: Process full audio file
  rpc TranscribeAudio(AudioRequest) returns (TranscriptResponse);
  
  // TTS: Synthesize text to speech
  rpc Synthesize(SynthesizeRequest) returns (AudioResponse);
  
  // TTS: Stream synthesized speech (sentence by sentence)
  rpc StreamSynthesize(SynthesizeRequest) returns (stream AudioChunk);
  
  // Full conversation: STT → LLM → TTS (bidirectional)
  rpc Converse(stream AudioChunk) returns (stream ConversationResponse);
}

// STT Messages
message AudioChunk {
  bytes audio_data = 1;
  string session_id = 2;
  int32 chunk_index = 3;
}

message TranscriptChunk {
  string text = 1;
  bool is_final = 2;
  float confidence = 3;
}

message AudioRequest {
  bytes audio_data = 1;
  string user_id = 2;
  string language = 3;
}

message TranscriptResponse {
  string text = 1;
  string language = 2;
  float confidence = 3;
}

// TTS Messages
message SynthesizeRequest {
  string text = 1;
  string voice = 2;       // "en-us-female-calm", etc.
  string emotion = 3;     // "calm", "energetic", "empathetic"
  string user_id = 4;
  string format = 5;      // "wav", "mp3"
}

message AudioResponse {
  bytes audio_data = 1;
  string format = 2;
  int32 duration_ms = 3;
}

// Conversation Messages
message ConversationResponse {
  oneof response_type {
    TranscriptChunk transcript = 1;    // What user said
    string llm_text = 2;                // AI response (text)
    AudioChunk audio = 3;               // AI response (audio)
    string status = 4;                  // "processing", "complete"
  }
  bool is_final = 5;
}
```

#### gRPC Server Implementation
**File:** `apps/ai-brain-service/src/grpc_server.py`

```python
import grpc
from concurrent import futures
import voice_pb2
import voice_pb2_grpc

class VoiceServicer(voice_pb2_grpc.VoiceServiceServicer):
    def __init__(self, voice_service: VoiceService):
        self.voice_service = voice_service
    
    async def StreamTranscribe(self, request_iterator, context):
        """Handle real-time audio streaming"""
        
        audio_buffer = bytearray()
        
        async for audio_chunk in request_iterator:
            audio_buffer.extend(audio_chunk.audio_data)
            
            # Process every 3 seconds of audio
            if len(audio_buffer) >= 48000 * 3:  # 3 sec at 16kHz
                transcript = await self.voice_service.transcribe_chunk(
                    bytes(audio_buffer)
                )
                
                yield voice_pb2.TranscriptChunk(
                    text=transcript['text'],
                    is_final=False,
                    confidence=transcript['confidence']
                )
                
                audio_buffer.clear()
        
        # Final transcription
        if audio_buffer:
            transcript = await self.voice_service.transcribe_chunk(
                bytes(audio_buffer)
            )
            
            yield voice_pb2.TranscriptChunk(
                text=transcript['text'],
                is_final=True,
                confidence=transcript['confidence']
            )

async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    voice_pb2_grpc.add_VoiceServiceServicer_to_server(
        VoiceServicer(voice_service),
        server
    )
    
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()
```

---

### Feature 3: Context-Aware Suggestions

#### Pattern Recognition Service
**File:** `apps/ai-brain-service/src/services/pattern_service.py`

```python
from datetime import datetime, timedelta
from typing import List, Dict
import asyncpg

class PatternRecognitionService:
    def __init__(self, db_pool: asyncpg.Pool, pgvector_service):
        self.db = db_pool
        self.pgvector = pgvector_service
    
    async def analyze_user_patterns(self, user_id: str) -> Dict:
        """
        Analyze user behavior patterns for proactive suggestions
        
        Returns:
            {
                'time_patterns': {...},
                'habit_patterns': {...},
                'productivity_windows': [...],
                'streak_risks': [...]
            }
        """
        
        patterns = {
            'time_patterns': await self._analyze_time_patterns(user_id),
            'habit_patterns': await self._analyze_habit_patterns(user_id),
            'productivity_windows': await self._find_productivity_windows(user_id),
            'streak_risks': await self._identify_streak_risks(user_id)
        }
        
        return patterns
    
    async def _analyze_time_patterns(self, user_id: str) -> Dict:
        """Analyze when user typically performs activities"""
        
        query = """
        SELECT 
            EXTRACT(DOW FROM created_at) as day_of_week,
            EXTRACT(HOUR FROM created_at) as hour_of_day,
            status,
            COUNT(*) as frequency
        FROM tasks
        WHERE user_id = $1 
          AND deleted_at IS NULL
          AND created_at > NOW() - INTERVAL '60 days'
        GROUP BY day_of_week, hour_of_day, status
        ORDER BY frequency DESC
        """
        
        results = await self.db.fetch(query, user_id)
        
        return {
            'most_active_days': self._get_top_days(results),
            'most_active_hours': self._get_top_hours(results),
            'completion_patterns': self._analyze_completion_times(results)
        }
    
    async def generate_proactive_suggestion(
        self, 
        user_id: str, 
        current_context: Dict
    ) -> Optional[str]:
        """
        Generate context-aware suggestion based on patterns
        
        Args:
            current_context: {
                'current_time': datetime,
                'last_activity': datetime,
                'location': 'home|work|gym',
                'recent_tasks': [...]
            }
        """
        
        patterns = await self.analyze_user_patterns(user_id)
        current_time = current_context['current_time']
        
        # Friday evening - suggest weekly review
        if current_time.weekday() == 4 and current_time.hour >= 17:
            if self._user_usually_reviews_weekend(patterns):
                return "It's Friday evening. Want to review your tasks for next week?"
        
        # Morning - check meditation habit
        if current_time.hour < 10:
            meditation_habit = await self._get_habit(user_id, 'meditation')
            if meditation_habit and meditation_habit['completion_rate'] > 0.8:
                logged_today = await self._habit_logged_today(user_id, 'meditation')
                if not logged_today:
                    return "Good morning! Ready to log your meditation?"
        
        # Before typical workout time
        workout_time = patterns['time_patterns'].get('typical_workout_time')
        if workout_time and abs((current_time.hour - workout_time).total_seconds()) < 1800:
            return "It's almost your usual workout time. Ready to crush it?"
        
        # No activity for 3+ hours - check in
        if (current_time - current_context['last_activity']).total_seconds() > 10800:
            return "I haven't heard from you in a while. How's your day going?"
        
        return None
```

---

### Feature 4: Smart Scheduling Assistant

#### Scheduling Assistant Service
**File:** `apps/ai-brain-service/src/services/scheduling_assistant.py`

```python
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

class SchedulingAssistant:
    def __init__(self, groq_client, scheduler_api_client):
        self.groq = groq_client
        self.scheduler_api = scheduler_api_client
    
    async def parse_meeting_request(
        self,
        user_input: str,
        user_id: str
    ) -> Dict:
        """
        Parse: "Schedule coffee with John next week"
        
        Returns:
            {
                'intent': 'create_event',
                'title': 'Coffee with John',
                'attendees': ['john@example.com'],
                'suggested_slots': [
                    {
                        'start': '2025-12-10T10:00:00Z',
                        'end': '2025-12-10T11:00:00Z',
                        'confidence': 0.9,
                        'reason': 'Your usual coffee time, John is free'
                    }
                ],
                'location_suggestion': 'Cafe Downtown'
            }
        """
        
        # Extract entities
        entities = await self._extract_entities(user_input)
        
        # Find attendee contact info
        attendees = await self._resolve_attendees(
            entities['attendees'], 
            user_id
        )
        
        # Get user's calendar
        calendar_events = await self.scheduler_api.get_events(
            user_id=user_id,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=14)
        )
        
        # Analyze time preferences
        time_prefs = await self._analyze_time_preferences(user_id)
        
        # Find best slots
        suggested_slots = await self._find_best_slots(
            calendar_events,
            time_prefs,
            entities['time_range']
        )
        
        # Suggest location
        location = await self._suggest_location(user_id, attendees)
        
        return {
            'intent': 'create_event',
            'title': entities['title'],
            'attendees': attendees,
            'suggested_slots': suggested_slots,
            'location_suggestion': location
        }
    
    async def _analyze_time_preferences(self, user_id: str) -> Dict:
        """Learn when user prefers meetings"""
        
        query = """
        SELECT 
            EXTRACT(HOUR FROM start_time) as hour,
            EXTRACT(DOW FROM start_time) as day_of_week,
            COUNT(*) as frequency
        FROM events
        WHERE user_id = $1
          AND start_time > NOW() - INTERVAL '90 days'
          AND title ILIKE '%meeting%' OR title ILIKE '%call%'
        GROUP BY hour, day_of_week
        ORDER BY frequency DESC
        LIMIT 10
        """
        
        results = await self.db.fetch(query, user_id)
        
        return {
            'preferred_hours': [r['hour'] for r in results[:3]],
            'preferred_days': [r['day_of_week'] for r in results[:3]],
            'peak_meeting_time': results[0]['hour'] if results else 10
        }
    
    async def _find_best_slots(
        self,
        calendar_events: List[Dict],
        time_prefs: Dict,
        time_range: Dict
    ) -> List[Dict]:
        """Find optimal meeting slots"""
        
        slots = []
        current_date = time_range['start']
        
        while current_date <= time_range['end']:
            # Check preferred hours
            for hour in time_prefs['preferred_hours']:
                slot_start = current_date.replace(hour=hour, minute=0)
                slot_end = slot_start + timedelta(hours=1)
                
                # Check for conflicts
                has_conflict = any(
                    self._times_overlap(event, slot_start, slot_end)
                    for event in calendar_events
                )
                
                if not has_conflict:
                    slots.append({
                        'start': slot_start.isoformat(),
                        'end': slot_end.isoformat(),
                        'confidence': 0.9,
                        'reason': f'Your usual meeting time ({hour}:00)'
                    })
            
            current_date += timedelta(days=1)
        
        return sorted(slots, key=lambda x: x['confidence'], reverse=True)[:3]
```

---

### Feature 5: Habit Insights & Analytics

#### Insights Generation Service
**File:** `apps/ai-brain-service/src/services/insights_service.py`

```python
from typing import List, Dict
import statistics

class InsightsService:
    def __init__(self, lifestyle_api_client, scheduler_api_client):
        self.lifestyle_api = lifestyle_api_client
        self.scheduler_api = scheduler_api_client
    
    async def generate_weekly_insights(self, user_id: str) -> List[str]:
        """
        Generate natural language insights from user data
        
        Returns:
            [
                "You complete workouts 90% more on Mondays than Fridays",
                "Your meditation streak breaks most often on weekends",
                "Tasks marked VI are completed 2 days earlier on average"
            ]
        """
        
        insights = []
        
        # Habit insights
        habits = await self.lifestyle_api.get_habits(user_id)
        for habit in habits:
            habit_insight = await self._analyze_habit(user_id, habit)
            if habit_insight:
                insights.append(habit_insight)
        
        # Task insights
        task_insight = await self._analyze_task_patterns(user_id)
        insights.extend(task_insight)
        
        # Productivity insights
        productivity_insight = await self._analyze_productivity(user_id)
        insights.extend(productivity_insight)
        
        return insights
    
    async def _analyze_habit(self, user_id: str, habit: Dict) -> Optional[str]:
        """Analyze single habit for patterns"""
        
        logs = await self.lifestyle_api.get_habit_logs(
            user_id=user_id,
            habit_id=habit['id'],
            days=90
        )
        
        if len(logs) < 10:
            return None
        
        # Group by day of week
        by_weekday = {}
        for log in logs:
            weekday = log['logged_at'].weekday()
            by_weekday.setdefault(weekday, []).append(log)
        
        # Find best/worst days
        completion_rates = {
            day: len(logs) / 13  # ~13 weeks
            for day, logs in by_weekday.items()
        }
        
        best_day = max(completion_rates, key=completion_rates.get)
        worst_day = min(completion_rates, key=completion_rates.get)
        
        best_day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][best_day]
        worst_day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][worst_day]
        
        if completion_rates[best_day] > completion_rates[worst_day] * 1.5:
            return f"You complete {habit['name']} {int((completion_rates[best_day] / completion_rates[worst_day] - 1) * 100)}% more on {best_day_name}s than {worst_day_name}s"
        
        # Streak break analysis
        streaks = self._calculate_streaks(logs)
        if streaks:
            avg_streak = statistics.mean(streaks)
            break_days = self._find_common_break_days(logs)
            if break_days:
                return f"Your {habit['name']} streak (avg: {int(avg_streak)} days) breaks most often on {break_days[0]}"
        
        return None
    
    async def _analyze_task_patterns(self, user_id: str) -> List[str]:
        """Analyze task completion patterns"""
        
        tasks = await self.scheduler_api.get_tasks(
            user_id=user_id,
            status='completed',
            days=90
        )
        
        insights = []
        
        # Priority analysis
        by_priority = {}
        for task in tasks:
            by_priority.setdefault(task['priority'], []).append(task)
        
        if 'VI' in by_priority and len(by_priority['VI']) >= 5:
            vi_tasks = by_priority['VI']
            avg_completion_time = statistics.mean([
                (t['completed_at'] - t['due_date']).days
                for t in vi_tasks
                if t['due_date'] and t['completed_at']
            ])
            
            if avg_completion_time < -1:
                insights.append(
                    f"Tasks marked VI are completed {abs(int(avg_completion_time))} days earlier on average"
                )
        
        # Category analysis
        by_category = {}
        for task in tasks:
            if task['category']:
                by_category.setdefault(task['category'], []).append(task)
        
        if by_category:
            most_productive_category = max(by_category, key=lambda k: len(by_category[k]))
            insights.append(
                f"You're most productive in {most_productive_category} tasks ({len(by_category[most_productive_category])} completed this quarter)"
            )
        
        return insights
```

---

## 📊 Database Schema Additions

### pgvector Tables

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Task embeddings for ML
CREATE TABLE task_embeddings (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  task_id VARCHAR(36),
  embedding vector(1536),
  priority VARCHAR(2),
  category VARCHAR(50),
  completion_time_minutes INT,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_task_embeddings_user ON task_embeddings(user_id);
CREATE INDEX idx_task_embeddings_vector ON task_embeddings 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- User behavior patterns
CREATE TABLE user_behavior_embeddings (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  behavior_type VARCHAR(50),  -- 'task_completion', 'habit_log', 'schedule_pattern'
  embedding vector(1536),
  metadata JSONB,              -- {day_of_week, time_of_day, success, context}
  frequency INT DEFAULT 1,
  last_occurred_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_behavior_embeddings_user ON user_behavior_embeddings(user_id);
CREATE INDEX idx_behavior_embeddings_type ON user_behavior_embeddings(behavior_type);
CREATE INDEX idx_behavior_embeddings_vector ON user_behavior_embeddings 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Conversational context (for chat memory)
CREATE TABLE conversation_context (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  session_id VARCHAR(50),
  message_role VARCHAR(20),  -- 'user', 'assistant'
  message_content TEXT,
  embedding vector(1536),
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_conversation_user_session ON conversation_context(user_id, session_id);
CREATE INDEX idx_conversation_created ON conversation_context(created_at DESC);
```

---

## 🚀 Deployment & Testing

### Environment Variables

```bash
# AI Services
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=speaksync
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# gRPC
GRPC_HOST=0.0.0.0
GRPC_PORT=50051

# Service URLs
SCHEDULER_SERVICE_URL=http://localhost:3001
LIFESTYLE_SERVICE_URL=http://localhost:8002
GATEWAY_SERVICE_URL=http://localhost:3000
```

### Testing Strategy

#### Unit Tests
```python
# tests/services/test_task_assistant.py
import pytest

@pytest.mark.asyncio
async def test_parse_task_intent():
    assistant = TaskAssistant(groq_client, pgvector_service)
    
    result = await assistant.parse_task_intent(
        user_input="I need to finish the report by Friday",
        user_context={'user_id': 'test-user', 'timezone': 'UTC'}
    )
    
    assert result['tasks'][0]['title'] == 'Finish the report'
    assert result['tasks'][0]['priority'] in ['VI', 'MI', 'NI']
    assert 'due_date' in result['tasks'][0]
```

#### Integration Tests
```python
# tests/integration/test_voice_to_task.py
@pytest.mark.asyncio
async def test_voice_to_task_flow():
    # 1. Upload voice file
    with open('test_audio.wav', 'rb') as f:
        response = await client.post('/api/ai/transcribe', files={'audio': f})
    
    assert response.status_code == 200
    transcript = response.json()['text']
    
    # 2. Parse intent
    response = await client.post('/api/ai/tasks/parse-intent', json={
        'user_input': transcript,
        'user_id': 'test-user'
    })
    
    assert response.status_code == 200
    tasks = response.json()['tasks']
    assert len(tasks) > 0
```

---

## 📈 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Voice transcription accuracy | >95% | WER (Word Error Rate) |
| Intent classification accuracy | >90% | Manual validation |
| Task priority prediction | >80% | User acceptance rate |
| Suggestion acceptance rate | >40% | Users clicking "Yes" |
| Response time (voice → task) | <3s | End-to-end latency |
| Daily active suggestions | 3-5 per user | Analytics tracking |

---

## 🔄 Next Steps After Phase 6

1. **Mobile App Integration** - React Native voice input
2. **Offline Mode** - Local STT for poor connectivity
3. **Multi-modal Input** - Image recognition (receipts, schedules)
4. **Advanced Analytics** - Predictive burnout detection
5. **Team Features** - Shared insights, collaboration AI

---

## 📝 Implementation Checklist

### Week 1: Foundation & Voice Engine
- [ ] Set up pgvector in PostgreSQL
- [ ] Create embeddings tables
- [ ] Configure Redis caching
- [ ] Set up Groq API credentials
- [ ] Set up OpenAI Whisper API credentials
- [ ] Implement gRPC server (Python)
- [ ] Implement gRPC client (Gateway - TypeScript)
- [ ] Voice transcription endpoint (STT)
- [ ] Audio streaming via gRPC (STT)
- [ ] **Install Coqui TTS (Chatterbots)**
- [ ] **Download TTS models (VITS, Tacotron2)**
- [ ] **Implement TTS service with emotion control**
- [ ] **TTS synthesis endpoint**
- [ ] **TTS streaming via gRPC**
- [ ] **Voice caching system**
- [ ] Groq LLM integration
- [ ] Domain-specific prompts
- [ ] Intent classification
- [ ] Entity extraction

### Week 2: Smart Features & Conversational AI
- [ ] **Complete STT → LLM → TTS pipeline**
- [ ] **Conversation state management**
- [ ] **Context retention (last 5 exchanges)**
- [ ] **Emotion detection from voice**
- [ ] **Dynamic TTS emotion matching**
- [ ] Task intent parsing
- [ ] Priority auto-classification
- [ ] Due date parsing
- [ ] Integration with scheduler service
- [ ] Pattern recognition engine
- [ ] Time-based suggestions
- [ ] Habit streak prediction
- [ ] Proactive reminders
- [ ] Calendar conflict checking
- [ ] Contact extraction
- [ ] Time preference learning
- [ ] Location suggestions
- [ ] Habit pattern analysis
- [ ] Insight generation
- [ ] Weekly summary reports

### Testing & Polish
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests
- [ ] **STT accuracy testing (Word Error Rate)**
- [ ] **TTS quality testing (naturalness, clarity)**
- [ ] **End-to-end conversation testing**
- [ ] **Voice latency testing (<3s total)**
- [ ] Load testing (100 concurrent users)
- [ ] **Multi-language voice testing**
- [ ] ML model validation
- [ ] Documentation
- [ ] API documentation (Swagger)
- [ ] Deployment guide

---

---

## 🧪 Testing the Complete Voice Flow

### 1. Test TTS Endpoint (HTTP)

```bash
# Synthesize speech
curl -X POST http://localhost:8003/api/ai/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome back! Ready to log your meditation?",
    "voice": "en-us-female-calm",
    "emotion": "calm",
    "format": "wav"
  }' \
  --output ai_response.wav

# Play the audio
# Windows:
Start-Process ai_response.wav
# Linux/Mac:
# aplay ai_response.wav
```

### 2. Test Complete Conversation Flow

```python
# Python client example
import grpc
import asyncio
import voice_pb2
import voice_pb2_grpc

async def test_conversation():
    # Connect to gRPC server
    channel = grpc.aio.insecure_channel('localhost:50051')
    stub = voice_pb2_grpc.VoiceServiceStub(channel)
    
    # Read audio file
    with open('user_voice.wav', 'rb') as f:
        audio_data = f.read()
    
    # Send audio chunks
    async def audio_stream():
        chunk_size = 4096
        for i in range(0, len(audio_data), chunk_size):
            yield voice_pb2.AudioChunk(
                audio_data=audio_data[i:i+chunk_size],
                session_id="test-session",
                chunk_index=i // chunk_size
            )
    
    # Get conversation response
    async for response in stub.Converse(audio_stream()):
        if response.HasField('transcript'):
            print(f"User said: {response.transcript.text}")
        
        elif response.HasField('llm_text'):
            print(f"AI response (text): {response.llm_text}")
        
        elif response.HasField('audio'):
            # Save AI voice response
            with open('ai_response.wav', 'ab') as f:
                f.write(response.audio.audio_data)
            
            if response.is_final:
                print("Conversation complete! Playing AI response...")
                # Play audio file
                os.system('start ai_response.wav')

# Run test
asyncio.run(test_conversation())
```

### 3. Test Voice Quality

```python
# Test different emotions
emotions = ["calm", "energetic", "empathetic"]

for emotion in emotions:
    response = requests.post('http://localhost:8003/api/ai/synthesize', json={
        "text": "How did the gym session go today?",
        "voice": "en-us-female-calm",
        "emotion": emotion,
        "format": "wav"
    })
    
    with open(f'test_{emotion}.wav', 'wb') as f:
        f.write(response.content)
    
    print(f"Generated: test_{emotion}.wav")
```

### 4. Performance Testing

```python
import time
import statistics

# Test latency for complete flow
latencies = []

for i in range(10):
    start = time.time()
    
    # 1. STT
    stt_response = requests.post('http://localhost:8003/api/ai/transcribe', 
        files={'audio': open('test_voice.wav', 'rb')})
    transcript = stt_response.json()['text']
    
    # 2. LLM
    llm_response = requests.post('http://localhost:8003/api/ai/tasks/parse-intent',
        json={'user_input': transcript, 'user_id': 'test-user'})
    ai_text = llm_response.json()['response']
    
    # 3. TTS
    tts_response = requests.post('http://localhost:8003/api/ai/synthesize',
        json={'text': ai_text, 'voice': 'en-us-female-calm'})
    
    end = time.time()
    latency = end - start
    latencies.append(latency)
    
    print(f"Iteration {i+1}: {latency:.2f}s")

print(f"\nAverage latency: {statistics.mean(latencies):.2f}s")
print(f"Target: <3s | {'✅ PASS' if statistics.mean(latencies) < 3 else '❌ FAIL'}")
```

---

## 📊 Voice Quality Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **STT Accuracy (WER)** | <5% | Compare transcripts with ground truth |
| **TTS Naturalness (MOS)** | >4.0/5.0 | Human evaluation (Mean Opinion Score) |
| **End-to-End Latency** | <3s | Time from user stops speaking → AI starts speaking |
| **Voice Clarity** | >90% | User surveys: "Could you understand the AI?" |
| **Emotion Accuracy** | >85% | Does TTS emotion match intended emotion? |
| **Cache Hit Rate** | >60% | Percentage of TTS responses served from cache |

---

**Ready to start implementation? Let's begin with Part 1: Database & Infrastructure Setup!**

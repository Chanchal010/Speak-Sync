# AI Brain Service - Text-to-Speech API Guide

## 🔊 TTS (Text-to-Speech) - Part 3 Complete

### Overview
High-quality speech synthesis using **OpenAI TTS API** with 6 distinct voices, emotion support, and intelligent caching.

### Quick Start

```powershell
# Test basic synthesis
curl -X POST http://localhost:8000/api/ai/voice/synthesize \
  -F "text=Hello! How can I help you today?" \
  -F "voice=nova" \
  -F "speed=1.0" \
  --output speech.mp3
```

---

## 🎙️ Available Voices

| Voice | Gender | Tone | Best For |
|-------|--------|------|----------|
| **alloy** | Neutral | Balanced | General purpose |
| **echo** | Male | Warm | Friendly conversations |
| **fable** | Neutral | Expressive | Storytelling |
| **onyx** | Male | Deep | Professional, authoritative |
| **nova** | Female | Friendly | Default, customer service |
| **shimmer** | Female | Gentle | Calm, soothing |

---

## 📡 API Endpoints

### 1. Basic Synthesis
**POST** `/api/ai/voice/synthesize`

Synthesize speech from text with voice and speed control.

**Parameters**:
- `text` (required): Text to synthesize (max 4096 chars)
- `voice` (optional): Voice name (default: "nova")
- `speed` (optional): 0.25 to 4.0 (default: 1.0)
- `use_cache` (optional): Enable caching (default: true)

**Example**:
```bash
curl -X POST http://localhost:8000/api/ai/voice/synthesize \
  -F "text=Welcome to our AI assistant!" \
  -F "voice=echo" \
  -F "speed=1.2" \
  --output welcome.mp3
```

**PowerShell**:
```powershell
$response = Invoke-WebRequest -Method Post `
    -Uri "http://localhost:8000/api/ai/voice/synthesize" `
    -Form @{
        text = "Hello from PowerShell!"
        voice = "nova"
        speed = 1.0
    } `
    -OutFile "output.mp3"
```

---

### 2. Emotion-Based Synthesis
**POST** `/api/ai/voice/synthesize-emotion`

Automatically select voice and speed based on emotion.

**Emotions**:
- `neutral` → alloy (balanced)
- `happy` → nova (upbeat, speed 1.1x)
- `sad` → shimmer (gentle, speed 0.9x)
- `excited` → fable (expressive, speed 1.2x)
- `calm` → echo (soothing, speed 0.85x)

**Parameters**:
- `text` (required): Text to synthesize
- `emotion` (required): neutral/happy/sad/excited/calm
- `gender` (optional): male/female/neutral

**Example**:
```bash
curl -X POST http://localhost:8000/api/ai/voice/synthesize-emotion \
  -F "text=I'm so excited to help you today!" \
  -F "emotion=excited" \
  --output excited.mp3
```

---

### 3. List Available Voices
**GET** `/api/ai/voice/voices`

Get all voices with characteristics.

**Example**:
```bash
curl http://localhost:8000/api/ai/voice/voices
```

**Response**:
```json
{
  "voices": {
    "nova": {
      "gender": "female",
      "tone": "friendly",
      "speed": "medium",
      "available": true
    },
    "echo": {
      "gender": "male",
      "tone": "warm",
      "speed": "medium",
      "available": true
    }
  },
  "total": 6,
  "default": "nova"
}
```

---

### 4. Clear Cache
**DELETE** `/api/ai/voice/cache`

Clear all cached TTS audio files.

**Example**:
```bash
curl -X DELETE http://localhost:8000/api/ai/voice/cache
```

**Response**:
```json
{
  "cleared": 42,
  "message": "Cleared 42 cached audio files"
}
```

---

## 🚀 Advanced Usage

### Conversational Responses

```python
import httpx
import asyncio

async def speak_response(text: str, emotion: str = "neutral"):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/ai/voice/synthesize-emotion",
            data={
                "text": text,
                "emotion": emotion
            }
        )
        
        # Save audio
        with open(f"response_{emotion}.mp3", "wb") as f:
            f.write(response.content)
        
        print(f"✓ Generated {emotion} response: {len(response.content)} bytes")

# Usage
asyncio.run(speak_response(
    text="Great question! Let me explain that for you.",
    emotion="happy"
))
```

### Multi-Voice Dialogue

```python
# Simulate conversation with different voices
messages = [
    {"text": "Hello! How can I help you?", "voice": "nova"},
    {"text": "I need help with scheduling.", "voice": "onyx"},
    {"text": "Of course! What time works best?", "voice": "nova"}
]

for i, msg in enumerate(messages):
    response = requests.post(
        "http://localhost:8000/api/ai/voice/synthesize",
        data={
            "text": msg["text"],
            "voice": msg["voice"]
        }
    )
    
    with open(f"dialogue_{i}.mp3", "wb") as f:
        f.write(response.content)
```

---

## 🎯 Use Cases

### 1. Customer Service Bot
```bash
# Friendly greeting
curl -X POST http://localhost:8000/api/ai/voice/synthesize \
  -F "text=Hi there! Welcome to our service. How may I assist you today?" \
  -F "voice=nova" \
  -F "speed=1.0" \
  --output greeting.mp3
```

### 2. Meditation/Calm App
```bash
# Calming voice
curl -X POST http://localhost:8000/api/ai/voice/synthesize-emotion \
  -F "text=Take a deep breath. Relax your shoulders. Feel the peace within." \
  -F "emotion=calm" \
  --output meditation.mp3
```

### 3. News Reader
```bash
# Professional tone
curl -X POST http://localhost:8000/api/ai/voice/synthesize \
  -F "text=Breaking news: Scientists discover new breakthrough in AI technology." \
  -F "voice=onyx" \
  -F "speed=0.95" \
  --output news.mp3
```

### 4. Motivational Coach
```bash
# Excited tone
curl -X POST http://localhost:8000/api/ai/voice/synthesize-emotion \
  -F "text=You're doing amazing! Keep pushing forward, you've got this!" \
  -F "emotion=excited" \
  --output motivation.mp3
```

---

## ⚙️ Configuration

### Environment Variables
```env
OPENAI_API_KEY=sk-proj-...     # Required
TTS_CACHE_DIR=cache/tts        # Optional (default: cache/tts)
```

### Caching System
- Automatically caches synthesized audio
- Cache key: MD5(text + voice + speed)
- Reduces API costs for repeated phrases
- Clear cache with DELETE endpoint

### Performance
- **Latency**: ~1-3 seconds for synthesis
- **Quality**: 24kHz MP3 audio
- **Streaming**: Supported via gRPC
- **Cache Hit**: <100ms response time

---

## 🔧 Testing

### PowerShell Test Script
```powershell
# test-tts.ps1

$voices = @("alloy", "echo", "fable", "onyx", "nova", "shimmer")
$text = "This is a test of the text to speech system."

foreach ($voice in $voices) {
    Write-Host "Testing voice: $voice"
    
    Invoke-WebRequest -Method Post `
        -Uri "http://localhost:8000/api/ai/voice/synthesize" `
        -Form @{
            text = $text
            voice = $voice
            speed = 1.0
        } `
        -OutFile "test_$voice.mp3"
    
    Write-Host "✓ Saved test_$voice.mp3"
}

Write-Host "`n✅ All voices tested!"
```

### Python Integration
```python
from services.tts_service import get_tts_service
import asyncio

async def test_tts():
    tts = get_tts_service()
    
    # Basic synthesis
    audio = await tts.synthesize(
        text="Hello world!",
        voice="nova",
        speed=1.0
    )
    
    with open("test.mp3", "wb") as f:
        f.write(audio)
    
    print("✓ TTS test passed!")

asyncio.run(test_tts())
```

---

## 🐛 Troubleshooting

### Issue: "OPENAI_API_KEY not found"
**Solution**: Set environment variable in `.env` file

### Issue: Slow first request
**Solution**: First synthesis takes longer (model loading). Subsequent requests are faster.

### Issue: Audio quality poor
**Solution**: Use `model="tts-1-hd"` in TTSService for higher quality (2x cost)

### Issue: Cache not working
**Solution**: Check `TTS_CACHE_DIR` permissions and disk space

---

## 📊 API Limits

| Metric | Limit |
|--------|-------|
| Max text length | 4096 characters |
| Speed range | 0.25 - 4.0x |
| Audio format | MP3 (24kHz) |
| Cache size | Unlimited (manage manually) |

---

## 🎓 Best Practices

1. **Use caching** for repeated phrases (greetings, common responses)
2. **Match voice to context** (calm for meditation, excited for celebration)
3. **Adjust speed** based on content complexity (slower for technical info)
4. **Clear cache periodically** to manage disk space
5. **Use emotion synthesis** for natural conversational feel

---

## 🔗 Related Endpoints

- **STT**: `/api/ai/voice/transcribe` - Speech-to-Text
- **Health**: `/health` - Service health check
- **Docs**: `/docs` - Interactive API documentation

---

## 📈 Next Steps (Part 4)

After TTS, we'll implement:
- **NLU & Intent Detection** (Groq LLM)
- **Complete Voice Conversation** (STT → LLM → TTS pipeline)
- **Context Management** for multi-turn conversations

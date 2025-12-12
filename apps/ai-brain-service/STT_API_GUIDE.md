# AI Brain Service - Voice AI API

## 🎤 Speech-to-Text (STT) - Part 2 Complete

### Quick Start

1. **Start the service**:
```powershell
cd D:\Projects\Speak-Sync\apps\ai-brain-service\src
..\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

2. **Access API docs**: http://localhost:8000/docs
3. **Health check**: http://localhost:8000/health

### API Endpoints

#### 1. Transcribe Audio File
```bash
curl -X POST http://localhost:8000/api/ai/voice/transcribe \
  -F "audio=@recording.wav" \
  -F "language=en"
```

**Response**:
```json
{
  "text": "Hello, this is a test transcription",
  "language": "en",
  "confidence": 0.95,
  "duration_ms": 3500
}
```

#### 2. Transcribe from URL
```bash
curl -X POST http://localhost:8000/api/ai/voice/transcribe-url \
  -F "url=https://example.com/audio.mp3" \
  -F "language=en"
```

#### 3. Validate Audio
```bash
curl -X POST http://localhost:8000/api/ai/voice/validate \
  -F "audio=@recording.wav"
```

**Response**:
```json
{
  "valid": true,
  "duration_ms": 5000,
  "format": "wav"
}
```

#### 4. Get Supported Formats
```bash
curl http://localhost:8000/api/ai/voice/supported-formats
```

**Response**:
```json
{
  "formats": ["wav", "mp3", "m4a", "webm", "ogg", "flac"],
  "max_file_size_mb": 25,
  "max_duration_minutes": 10,
  "supported_languages": [
    {"code": "en", "name": "English"},
    {"code": "hi", "name": "Hindi"},
    {"code": "es", "name": "Spanish"}
  ]
}
```

### PowerShell Test Script

```powershell
# Test transcription endpoint
$audioFile = "D:\path\to\your\audio.wav"

$response = Invoke-RestMethod -Method Post `
    -Uri "http://localhost:8000/api/ai/voice/transcribe" `
    -Form @{
        audio = Get-Item $audioFile
        language = "en"
    }

Write-Host "Transcription: $($response.text)"
Write-Host "Confidence: $($response.confidence)"
```

### Features Implemented ✅

- **OpenAI Whisper STT**: Whisper-1 model for high accuracy
- **Multiple Formats**: WAV, MP3, M4A, WEBM, OGG, FLAC
- **Language Support**: Auto-detect or specify (en, hi, es, fr, de)
- **Confidence Scoring**: Per-transcription confidence metrics
- **HTTP REST API**: Easy integration with multipart form-data
- **gRPC Streaming**: Real-time audio streaming (StreamTranscribe)
- **Audio Validation**: Pre-transcription quality checks
- **Error Handling**: Comprehensive error responses

### Architecture

```
Client → HTTP/gRPC → VoiceService → OpenAI Whisper API
                           ↓
                      Validation
                      Format Detection
                      Confidence Scoring
```

### Configuration

Required environment variables:
```env
OPENAI_API_KEY=sk-proj-...  # OpenAI API key
DATABASE_URL=postgres://...  # Optional (for Part 8)
REDIS_URL=redis://...        # Optional (for caching)
```

### gRPC Integration

For streaming transcription:
```python
import grpc
from protos import voice_pb2, voice_pb2_grpc

async with grpc.aio.insecure_channel('localhost:50051') as channel:
    stub = voice_pb2_grpc.VoiceServiceStub(channel)
    
    # Stream audio chunks
    async def audio_generator():
        with open('audio.wav', 'rb') as f:
            while chunk := f.read(4096):
                yield voice_pb2.AudioChunk(
                    audio_data=chunk,
                    session_id="session123"
                )
    
    # Receive transcriptions
    async for transcript in stub.StreamTranscribe(audio_generator()):
        print(f"Partial: {transcript.text}")
```

### Next Steps (Part 3)

- **TTS Engine**: Coqui TTS implementation
- **Emotion Control**: Voice modulation based on context
- **Voice Caching**: Cache synthesized audio for repeated phrases
- **Synthesis Endpoints**: `/api/ai/voice/synthesize`

### Known Limitations

- **pydub**: Disabled due to Python 3.13 compatibility (advanced audio conversion unavailable)
- **Database**: Optional - service runs in STT-only mode without PostgreSQL/Redis
- **Max File Size**: 25MB (Whisper API limit)
- **Formats**: Direct transcription works best with WAV/MP3

### Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'pyaudioop'`
- **Solution**: This is a Python 3.13 issue with pydub. Service automatically disables pydub features.

**Issue**: Database connection failed
- **Solution**: Service continues in STT-only mode. This is expected for local testing.

**Issue**: "Audio file too large"
- **Solution**: Compress audio or split into smaller chunks (< 25MB)

# 🔐 Environment Variables Documentation

**Last Updated**: December 3, 2025  
**Project**: Speak-Sync  
**Environment**: Production

---

## 📋 Table of Contents

1. [Quick Setup](#quick-setup)
2. [Database Configuration](#database-configuration)
3. [Caching & Messaging](#caching--messaging)
4. [Security & Authentication](#security--authentication)
5. [AI Services](#ai-services)
6. [Service Configuration](#service-configuration)
7. [External APIs](#external-apis)
8. [Application Settings](#application-settings)

---

## 🚀 Quick Setup

### 1. Copy Template
```bash
cp .env.example .env
```

### 2. Generate Secrets
```bash
# JWT Access Secret (64 bytes)
openssl rand -base64 64

# JWT Refresh Secret (64 bytes)
openssl rand -base64 64

# Internal API Key (48 bytes)
openssl rand -base64 48
```

### 3. Get API Keys
- **Groq/OpenRouter**: https://openrouter.ai/keys
- **OpenAI**: https://platform.openai.com/api-keys
- **Hugging Face**: https://huggingface.co/settings/tokens

---

## 🗄️ Database Configuration

### `DATABASE_URL`
- **Type**: PostgreSQL Connection String
- **Format**: `postgresql://user:password@host:port/database?options`
- **Provider**: Neon DB (Serverless PostgreSQL with pgvector)
- **Required**: ✅ Yes
- **Used By**: Scheduler Service, AI Brain Service

**Example**:
```env
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require&connection_limit=10&pool_timeout=30
```

**Features**:
- ✅ pgvector extension (for AI embeddings)
- ✅ SSL/TLS encryption
- ✅ Connection pooling (10 connections)
- ✅ 30s pool timeout

**Connection Pool Settings**:
- `connection_limit=10`: Max concurrent connections
- `pool_timeout=30`: Connection timeout in seconds
- `sslmode=require`: Force SSL/TLS
- `channel_binding=require`: Enhanced security

---

### `MONGODB_URI`
- **Type**: MongoDB Connection String
- **Format**: `mongodb://host:port/database`
- **Provider**: MongoDB (Local or Atlas)
- **Required**: ✅ Yes (Phase 4+)
- **Used By**: Lifestyle Service

**Example**:
```env
MONGODB_URI=mongodb://localhost:27017/speak_sync_lifestyle
```

**Production (MongoDB Atlas)**:
```env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/speak_sync?retryWrites=true&w=majority
```

**Collections**:
- `habits`: User habit definitions
- `habit_logs`: Daily habit completions
- `journal_logs`: User journal entries
- `lifestyle_analytics`: Aggregated statistics

---

## ⚡ Caching & Messaging

### `REDIS_URL`
- **Type**: Redis Connection String
- **Format**: `redis://` or `rediss://` (SSL)
- **Provider**: Upstash Redis (Serverless)
- **Required**: ✅ Yes
- **Used By**: Gateway Service, AI Brain Service

**Example**:
```env
REDIS_URL=rediss://default:password@host.upstash.io:6379
```

**Usage**:
- ✅ JWT token blacklist
- ✅ Session storage
- ✅ API response caching
- ✅ Rate limiting counters
- ✅ Job deduplication

**Cache TTL Strategy**:
- Access tokens: 15 minutes
- Refresh tokens: 7 days
- API responses: 5 minutes
- User sessions: 24 hours

---

### `RABBITMQ_URL`
- **Type**: AMQP Connection String
- **Format**: `amqp://` or `amqps://` (SSL)
- **Provider**: CloudAMQP
- **Required**: ✅ Yes (Phase 5+)
- **Used By**: All Services (Event-Driven Architecture)

**Example**:
```env
RABBITMQ_URL=amqps://user:pass@puffin.rmq2.cloudamqp.com/vhost
```

**Exchanges**:
- `tasks.events` (topic): Task lifecycle events
- `habits.events` (topic): Habit tracking events
- `notifications.events` (direct): User notifications

**Queues**:
- `task.created`: New task notifications
- `task.reminders`: Due date reminders
- `habit.reminders`: Habit completion reminders
- `email.notifications`: Email sending queue
- `dlq.retry`: Dead letter queue for failed messages

---

## 🔐 Security & Authentication

### `JWT_ACCESS_SECRET`
- **Type**: Base64-encoded random string
- **Length**: Minimum 64 bytes (512 bits)
- **Required**: ✅ Yes
- **Used By**: Gateway Service, All Protected Endpoints

**Generate**:
```bash
openssl rand -base64 64
```

**Usage**: Signs and verifies access tokens (short-lived, 15 minutes)

**Security Notes**:
- 🔴 **NEVER** commit to git
- 🔴 **ROTATE** every 90 days
- 🔴 **UNIQUE** per environment (dev/staging/prod)

---

### `JWT_REFRESH_SECRET`
- **Type**: Base64-encoded random string
- **Length**: Minimum 64 bytes (512 bits)
- **Required**: ✅ Yes
- **Used By**: Gateway Service, Token Refresh Flow

**Generate**:
```bash
openssl rand -base64 64
```

**Usage**: Signs and verifies refresh tokens (long-lived, 7 days)

**Security Notes**:
- Must be **different** from `JWT_ACCESS_SECRET`
- Store refresh tokens in database
- Implement token rotation on refresh

---

### `JWT_ACCESS_EXPIRY`
- **Type**: Time string
- **Format**: `15m`, `1h`, `7d`
- **Default**: `15m`
- **Recommended**: 15-30 minutes

**Balancing**:
- ⏱️ Shorter = More secure, more token refreshes
- ⏱️ Longer = Better UX, less secure

---

### `JWT_REFRESH_EXPIRY`
- **Type**: Time string
- **Format**: `7d`, `30d`, `90d`
- **Default**: `7d`
- **Recommended**: 7-14 days

---

### `INTERNAL_API_KEY`
- **Type**: Base64-encoded random string
- **Length**: Minimum 48 bytes (384 bits)
- **Required**: ✅ Yes
- **Used By**: Inter-service communication

**Generate**:
```bash
openssl rand -base64 48
```

**Usage**: Authenticate requests between microservices

**Security**:
- Only for backend-to-backend calls
- Never expose to frontend
- Validate in middleware: `verifyInternalRequest()`

---

## 🤖 AI Services

### `GROQ_API_KEY`
- **Type**: API Key (starts with `sk-or-v1-`)
- **Provider**: OpenRouter (Llama 3.3 70B)
- **Required**: ✅ Yes (Phase 6+)
- **Used By**: AI Brain Service

**Get Key**: https://openrouter.ai/keys

**Usage**:
- Natural language task parsing
- Intent classification
- Smart suggestions
- Conversational AI

**Rate Limits**: Check OpenRouter dashboard

---

### `OPENAI_API_KEY`
- **Type**: API Key (starts with `sk-`)
- **Provider**: OpenAI
- **Required**: 🟡 Optional (fallback & embeddings)
- **Used By**: AI Brain Service

**Get Key**: https://platform.openai.com/api-keys

**Usage**:
- Text embeddings (if not using BGE)
- Fallback LLM if Groq fails
- Image analysis (future feature)

---

### `HUGGINGFACE_API_KEY`
- **Type**: API Token (starts with `hf_`)
- **Provider**: Hugging Face
- **Required**: ✅ Yes (Phase 6+)
- **Used By**: AI Brain Service (Embeddings)

**Get Key**: https://huggingface.co/settings/tokens

**Usage**:
- Download BGE embeddings model
- Access gated models
- Inference API (optional)

---

### AI Model Configuration

#### `DEFAULT_LLM_MODEL`
- **Default**: `llama-3.3-70b-versatile`
- **Options**: Any model supported by OpenRouter
- **Purpose**: Primary language model for AI tasks

**Popular Alternatives**:
- `llama-3.1-405b-instruct` (More powerful, expensive)
- `gpt-4-turbo` (OpenAI fallback)
- `claude-3.5-sonnet` (Anthropic alternative)

---

#### `EMBEDDING_MODEL`
- **Default**: `BAAI/bge-small-en-v1.5`
- **Dimension**: 384 (small), 768 (base), 1024 (large)
- **Purpose**: Convert text to vectors for RAG

**Why BGE?**
- ✅ Better than OpenAI for retrieval
- ✅ Free to run locally
- ✅ Smaller model size
- ✅ Optimized for semantic search

**Alternatives**:
- `text-embedding-3-small` (OpenAI, 1536 dim)
- `all-MiniLM-L6-v2` (Lightweight, 384 dim)

---

#### `STT_MODEL`
- **Default**: `whisper-large-v3-turbo`
- **Purpose**: Speech-to-text transcription

**Installation**:
```bash
pip install -U openai-whisper
# or
pip install faster-whisper  # Faster inference
```

**Model Sizes**:
- `tiny`: 39M params (fastest, least accurate)
- `base`: 74M params
- `small`: 244M params
- `medium`: 769M params
- `large-v3-turbo`: 1550M params (best quality)

---

#### `TTS_MODEL`
- **Default**: `chatterbox`
- **Purpose**: Text-to-speech synthesis

**Options**:
- **Chatterbox**: Open-source, good quality
- **Coqui TTS**: Multi-speaker support
- **Bark**: Multilingual, emotional voices

---

### AI Service Settings

#### `AI_TEMPERATURE`
- **Range**: 0.0 to 1.0
- **Default**: 0.7
- **Purpose**: Control AI creativity

**Values**:
- `0.0-0.3`: Deterministic, factual responses
- `0.4-0.7`: Balanced (recommended for tasks)
- `0.8-1.0`: Creative, varied responses

---

#### `AI_MAX_TOKENS`
- **Default**: 2000
- **Purpose**: Maximum response length
- **Cost**: Higher = more expensive API calls

---

#### `AI_TIMEOUT`
- **Default**: 30000 (30 seconds)
- **Purpose**: API request timeout
- **Recommendation**: 20-60 seconds for LLMs

---

## 🌐 Service Configuration

### Service Ports

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Gateway | 3000 | HTTP | Public API, Auth |
| Scheduler | 3001 | HTTP | Tasks, Events, Users |
| Worker | 3002 | HTTP | Background Jobs |
| AI Brain | 8000 | HTTP | AI Features |
| Lifestyle | 8001 | HTTP | Habits, Logs |

### Internal Service URLs

Used for inter-service communication:

```env
SCHEDULER_SERVICE_URL=http://scheduler-service:3001
AI_BRAIN_SERVICE_URL=http://ai-brain-service:8000
LIFESTYLE_SERVICE_URL=http://lifestyle-service:8001
```

**Docker Networking**: Services use container names as hostnames

---

## 🌦️ External APIs (Optional)

### `WEATHER_API_KEY`
- **Provider**: OpenWeatherMap / WeatherAPI
- **Required**: 🟢 Optional
- **Used By**: Lifestyle Service

**Purpose**: Context-aware suggestions based on weather

---

### `NEWS_API_KEY`
- **Provider**: NewsAPI
- **Required**: 🟢 Optional
- **Used By**: Lifestyle Service

**Purpose**: Daily news summaries and briefings

---

## ⚙️ Application Settings

### `NODE_ENV`
- **Values**: `development`, `production`, `test`
- **Default**: `production`
- **Impact**: Logging, error handling, optimizations

---

### `LOG_LEVEL`
- **Values**: `error`, `warn`, `info`, `debug`, `trace`
- **Default**: `info`
- **Production**: `info` or `warn`
- **Development**: `debug`

---

### `CORS_ORIGIN`
- **Default**: `*` (allow all)
- **Production**: Specific domain (e.g., `https://app.speaksync.com`)
- **Multiple**: Comma-separated list

---

### Rate Limiting

#### `RATE_LIMIT_WINDOW_MS`
- **Default**: 900000 (15 minutes)
- **Purpose**: Time window for rate limiting

#### `RATE_LIMIT_MAX_REQUESTS`
- **Default**: 100
- **Purpose**: Max requests per window per IP

---

### Pagination

#### `DEFAULT_PAGE_SIZE`
- **Default**: 20
- **Purpose**: Default items per page

#### `MAX_PAGE_SIZE`
- **Default**: 100
- **Purpose**: Maximum items per page (prevent abuse)

---

## 🔍 Validation Checklist

Before deploying, verify:

- [ ] All secrets are cryptographically random
- [ ] No placeholder values (e.g., `your_api_key_here`)
- [ ] Database URLs are correct and accessible
- [ ] JWT secrets are at least 64 bytes
- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` is committed (no secrets)
- [ ] API keys have proper permissions
- [ ] Service URLs match Docker network
- [ ] Rate limits are reasonable
- [ ] CORS origin is restricted in production

---

## 🚨 Security Best Practices

1. **Never commit `.env` to git**
   - Use `.env.example` template instead
   - Add `.env*` to `.gitignore`

2. **Rotate secrets regularly**
   - JWT secrets: Every 90 days
   - API keys: When team members leave
   - Database passwords: Every 6 months

3. **Use different secrets per environment**
   - Development ≠ Staging ≠ Production
   - Prevents cross-environment attacks

4. **Limit secret access**
   - Only deploy pipelines should read production secrets
   - Use secret managers (AWS Secrets Manager, HashiCorp Vault)

5. **Monitor secret usage**
   - Track API key usage
   - Alert on unusual patterns
   - Revoke compromised keys immediately

---

## 📞 Troubleshooting

### Database Connection Fails
```
Error: connection timeout
```
**Fix**: Check `connection_limit` and `pool_timeout` in `DATABASE_URL`

### JWT Verification Fails
```
Error: invalid signature
```
**Fix**: Ensure all services use the same `JWT_ACCESS_SECRET`

### Redis Connection Fails
```
Error: ECONNREFUSED
```
**Fix**: Verify `REDIS_URL` includes correct protocol (`rediss://` for SSL)

### RabbitMQ Messages Not Processing
```
Error: channel closed
```
**Fix**: Check `RABBITMQ_URL` credentials and vhost

---

## 📚 References

- [Neon DB Docs](https://neon.tech/docs)
- [Upstash Redis Docs](https://upstash.com/docs/redis)
- [CloudAMQP Docs](https://www.cloudamqp.com/docs)
- [OpenRouter API Docs](https://openrouter.ai/docs)
- [Hugging Face Docs](https://huggingface.co/docs)
- [Whisper GitHub](https://github.com/openai/whisper)

---

**Need help?** Check `docs/` directory or open an issue on GitHub.

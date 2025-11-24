# Speak-Sync Environment Setup Script
# This script creates .env files for all services with your database credentials

Write-Host "Setting up Speak-Sync environment files..." -ForegroundColor Green

# Gateway Service
$gatewayEnv = @"
PORT=3000
NODE_ENV=development

# Redis (Upstash)
REDIS_URL=rediss://default:ASQzAAImcDJhODI1ZGQ5MmNjZDM0YTMzOThkZjg2NmY3OTQ3Yzc1M3AyOTI2Nw@ample-finch-9267.upstash.io:6379

# JWT
JWT_SECRET=speak-sync-super-secret-jwt-key-2024
JWT_EXPIRES_IN=7d

# Service URLs
AI_BRAIN_SERVICE_URL=http://localhost:8000
SCHEDULER_SERVICE_URL=http://localhost:3001
LIFESTYLE_SERVICE_URL=http://localhost:8001

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
"@

# Scheduler Service
$schedulerEnv = @"
PORT=3001
NODE_ENV=development

# PostgreSQL (Neon)
DATABASE_URL=postgresql://neondb_owner:npg_Y6BOG5JAtsmf@ep-morning-morning-ahr1efvr-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require

# RabbitMQ (Local Docker)
RABBITMQ_URL=amqp://admin:admin@localhost:5672

# Timezone
TZ=UTC
"@

# Worker Service
$workerEnv = @"
NODE_ENV=development

# PostgreSQL (Neon - for pgvector)
DATABASE_URL=postgresql://neondb_owner:npg_Y6BOG5JAtsmf@ep-morning-morning-ahr1efvr-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require

# RabbitMQ (Local Docker)
RABBITMQ_URL=amqp://admin:admin@localhost:5672

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM=noreply@speak-sync.com

# Service URLs
AI_BRAIN_SERVICE_URL=http://localhost:8000
"@

# AI Brain Service
$aiBrainEnv = @"
PORT=8000
ENVIRONMENT=development

# PostgreSQL (Neon - for pgvector)
DATABASE_URL=postgresql://neondb_owner:npg_Y6BOG5JAtsmf@ep-morning-morning-ahr1efvr-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require

# Redis (Upstash)
REDIS_URL=rediss://default:ASQzAAImcDJhODI1ZGQ5MmNjZDM0YTMzOThkZjg2NmY3OTQ3Yzc1M3AyOTI2Nw@ample-finch-9267.upstash.io:6379

# RabbitMQ (Local Docker)
RABBITMQ_URL=amqp://admin:admin@localhost:5672

# AI Service API Keys (ADD YOUR KEYS HERE)
GROQ_API_KEY=your-groq-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# Model Configuration
GROQ_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=text-embedding-3-small

# Vector Database Settings
VECTOR_DIMENSIONS=1536
"@

# Lifestyle Service
$lifestyleEnv = @"
PORT=8001
ENVIRONMENT=development

# MongoDB (Atlas)
MONGODB_URI=mongodb+srv://speak-sync:131180@speak-sync.oazczpg.mongodb.net/?appName=speak-sync

# JWT (must match gateway service)
JWT_SECRET=speak-sync-super-secret-jwt-key-2024

# Database Settings
MONGODB_MAX_POOL_SIZE=10
MONGODB_MIN_POOL_SIZE=2
"@

# Create .env files
$gatewayEnv | Out-File -FilePath "apps\gateway-service\.env" -Encoding UTF8
$schedulerEnv | Out-File -FilePath "apps\scheduler-service\.env" -Encoding UTF8
$workerEnv | Out-File -FilePath "apps\worker-service\.env" -Encoding UTF8
$aiBrainEnv | Out-File -FilePath "apps\ai-brain-service\.env" -Encoding UTF8
$lifestyleEnv | Out-File -FilePath "apps\lifestyle-service\.env" -Encoding UTF8

Write-Host "`n✅ Environment files created successfully!" -ForegroundColor Green
Write-Host "`nCreated files:" -ForegroundColor Cyan
Write-Host "  - apps/gateway-service/.env"
Write-Host "  - apps/scheduler-service/.env"
Write-Host "  - apps/worker-service/.env"
Write-Host "  - apps/ai-brain-service/.env"
Write-Host "  - apps/lifestyle-service/.env"

Write-Host "`n⚠️  IMPORTANT:" -ForegroundColor Yellow
Write-Host "  Edit apps/ai-brain-service/.env and add your API keys"
Write-Host "  - GROQ_API_KEY from https://console.groq.com"
Write-Host "  - OPENAI_API_KEY from https://platform.openai.com"

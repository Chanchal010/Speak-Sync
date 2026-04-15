#!/usr/bin/env node
/**
 * Speak-Sync Infrastructure Migration Guide
 * ==========================================
 * Migrating from: Neon PostgreSQL + Docker Redis
 * Migrating to:   Supabase (PostgreSQL + pgvector + Realtime + Storage) + Upstash Redis
 *
 * This script guides you through what to do.
 * Manual steps are clearly marked.
 */

console.log(`
╔══════════════════════════════════════════════════════════════╗
║        SPEAK-SYNC → FREE STACK MIGRATION GUIDE              ║
║   Supabase (DB + Realtime + Storage) + Upstash Redis        ║
╚══════════════════════════════════════════════════════════════╝

TOTAL ESTIMATED TIME: ~20 minutes
COST: $0 / month (both services have free tiers)

════════════════════════════════════════════════════════════════
STEP 1 — CREATE SUPABASE PROJECT (5 min)
════════════════════════════════════════════════════════════════

1a. Go to: https://supabase.com
1b. Sign up / Login with GitHub
1c. Click "New Project"
1d. Set:
    - Project name:    speak-sync
    - Database password: [generate a strong one, SAVE IT]
    - Region:          Southeast Asia (Singapore) — closest to India
1e. Wait ~2 minutes for the project to provision

════════════════════════════════════════════════════════════════
STEP 2 — SETUP SUPABASE DATABASE (3 min)
════════════════════════════════════════════════════════════════

2a. In Supabase Dashboard → SQL Editor → New Query
2b. Copy and paste the ENTIRE content of: scripts/supabase-setup.sql
2c. Click "Run" (Ctrl+Enter)
2d. You should see: "Supabase setup complete!"

2e. Get your connection string:
    Dashboard → Settings → Database → Connection string → URI
    Copy the "Transaction pooler" URI (for pgbouncer/production)
    It looks like:
    postgresql://postgres.xxxxx:YOUR_PASSWORD@aws-0-ap-south-1.pooler.supabase.com:6543/postgres

════════════════════════════════════════════════════════════════
STEP 3 — GET SUPABASE API KEYS (1 min)
════════════════════════════════════════════════════════════════

3a. Dashboard → Settings → API
3b. Copy:
    - Project URL:       https://xxxxx.supabase.co  → SUPABASE_URL
    - service_role key: eyJhbGc...                  → SUPABASE_SERVICE_ROLE_KEY
    
⚠️  NEVER expose service_role key in client-side code. Backend only.

════════════════════════════════════════════════════════════════
STEP 4 — CREATE UPSTASH REDIS (3 min)
════════════════════════════════════════════════════════════════

4a. Go to: https://upstash.com
4b. Sign up / Login with GitHub
4c. Click "Create Database"
4d. Set:
    - Name:    speak-sync-redis
    - Region:  ap-south-1 (Mumbai) — closest to India
    - Type:    Regional (free tier)
    - Enable:  TLS/SSL ✅
4e. Click Create
4f. In the database page → .ENV tab → copy the UPSTASH_REDIS_REST_URL
    OR the Redis URL format (starts with rediss://)
    
    Copy the line: REDIS_URL=rediss://default:PASSWORD@HOST.upstash.io:6379

════════════════════════════════════════════════════════════════
STEP 5 — MIGRATE DATA FROM NEON (if you have existing data)
════════════════════════════════════════════════════════════════

On your WSL2 server, run:

  # Export from Neon
  pg_dump "\\$YOUR_NEON_DATABASE_URL" \\
    --no-owner \\
    --no-acl \\
    --schema public \\
    -f neon_backup.sql

  # Import to Supabase
  psql "\\$YOUR_SUPABASE_DATABASE_URL" < neon_backup.sql

If the backup fails on pgvector extension (already exists):
  # Edit neon_backup.sql and remove the line: CREATE EXTENSION vector;
  # (Supabase already has it from our setup script)

  sed -i '/CREATE EXTENSION.*vector/d' neon_backup.sql
  psql "\\$YOUR_SUPABASE_DATABASE_URL" < neon_backup.sql

════════════════════════════════════════════════════════════════
STEP 6 — SETUP SUPABASE STORAGE BUCKETS (2 min)
════════════════════════════════════════════════════════════════

In Supabase Dashboard → Storage → New Bucket:

  Bucket 1: tts-cache
    - Public: No (private)
    - File size limit: 50 MB
    
  Bucket 2: voice-recordings  
    - Public: No (private)
    - File size limit: 25 MB
    
  Bucket 3: user-avatars
    - Public: Yes (public CDN)
    - File size limit: 5 MB

════════════════════════════════════════════════════════════════
STEP 7 — ENABLE REALTIME (1 min)
════════════════════════════════════════════════════════════════

In Supabase Dashboard → Database → Replication:
Enable Realtime for these tables:
  ✅ conversation_history
  ✅ behavioral_observations
  ✅ realtime_events

OR → Table Editor → select table → Enable Realtime toggle

════════════════════════════════════════════════════════════════
STEP 8 — UPDATE YOUR .env FILE (on WSL2 server)
════════════════════════════════════════════════════════════════

SSH into your server and edit /mnt/e/servers/speak-sync/app/.env:

  nano /mnt/e/servers/speak-sync/app/.env

Replace/add these values:

  # Supabase
  DATABASE_URL=postgresql://postgres.YOURPROJECT:PASSWORD@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require&pgbouncer=true
  SUPABASE_URL=https://YOURPROJECT.supabase.co
  SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...your_service_role_key...
  
  # Upstash Redis
  REDIS_URL=rediss://default:YOURPASSWORD@YOURHOST.upstash.io:6379
  
  # OpenRouter (for BehavioralObserver FREE model)
  OPENROUTER_API_KEY=sk-or-v1-your_key_here

════════════════════════════════════════════════════════════════
STEP 9 — REBUILD AND REDEPLOY (3 min)
════════════════════════════════════════════════════════════════

On your WSL2 server:

  cd /mnt/e/servers/speak-sync/app
  
  # Pull latest code (with all our changes)
  git pull origin chanchal
  
  # Rebuild only ai-brain-service (our main changes)
  docker compose -f docker-compose.prod.yml up -d --build ai-brain-service
  
  # Check all services came up
  docker compose -f docker-compose.prod.yml ps
  
  # Verify gRPC + REST both started
  docker compose -f docker-compose.prod.yml logs ai-brain-service | tail -20
  
  # Expected logs:
  # ✓ PostgreSQL connected (Supabase)
  # ✓ Redis connected      (Upstash)
  # ✓ gRPC server started on port 50051
  # ✓ AI Brain Service ready! REST:8000 | gRPC:50051

════════════════════════════════════════════════════════════════
STEP 10 — VERIFY THE FULL STACK
════════════════════════════════════════════════════════════════

  # Test REST API
  curl http://SERVER_IP:8000/health
  
  # Test Gateway
  curl http://SERVER_IP:3000/health
  
  # Test gRPC port is open
  nc -zv SERVER_IP 50051
  
  # Check Supabase has data after first voice conversation:
  # Supabase Dashboard → Table Editor → conversation_history

════════════════════════════════════════════════════════════════
WHAT'S NOW FREE AND WHY
════════════════════════════════════════════════════════════════

  ┌─────────────────────┬──────────────┬─────────────────────┐
  │ What                │ Provider     │ Free Limit          │
  ├─────────────────────┼──────────────┼─────────────────────┤
  │ PostgreSQL+pgvector │ Supabase     │ 500MB DB            │
  │ Realtime WebSocket  │ Supabase     │ 200 connections     │
  │ File Storage        │ Supabase     │ 1GB                 │
  │ Redis Cache         │ Upstash      │ 10K req/day         │
  │ LLM (NLU)          │ OpenRouter   │ Paid, but cheap     │
  │ BehavioralObserver  │ OpenRouter   │ gemini:free = FREE  │
  │ Embeddings          │ OpenAI       │ ~$0.02/1M tokens    │
  │ TTS (Voice)         │ edge-tts     │ Completely FREE     │
  │ STT (Voice)         │ Google STT   │ Completely FREE     │
  │ Background Jobs     │ RabbitMQ     │ Already deployed    │
  └─────────────────────┴──────────────┴─────────────────────┘

  Monthly cost at dev/personal scale: ~$0-2 (only OpenAI embeddings)
`);

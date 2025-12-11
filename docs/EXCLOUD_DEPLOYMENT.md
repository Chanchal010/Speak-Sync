# ExCloud Production Deployment Guide

## 🚀 Complete Deployment Instructions

### Prerequisites on ExCloud Server

You should already have:
- ✅ SSH access to your ExCloud server (210.79.129.52)
- ✅ Docker and Docker Compose installed
- ✅ Git configured with SSH key for GitHub
- ✅ Repository cloned at `~/Speak-Sync`

---

## Step 1: Update Your Code on ExCloud

SSH into your server and pull the latest changes:

```bash
ssh ubuntu@210.79.129.52

cd ~/Speak-Sync
git pull origin main
```

---

## Step 2: Configure Environment Variables

Create the production environment file:

```bash
cd ~/Speak-Sync
nano .env
```

Paste the following (replace the placeholder values):

```env
# Database Configuration
POSTGRES_PASSWORD=YourSecurePassword123!
POSTGRES_DB=speak_sync_db

# RabbitMQ Configuration
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest

# JWT Configuration (MUST CHANGE THESE!)
JWT_ACCESS_SECRET=your_super_secret_jwt_access_key_min_32_characters_long
JWT_REFRESH_SECRET=your_super_secret_jwt_refresh_key_min_32_characters_long
JWT_ACCESS_EXPIRY=15m
JWT_REFRESH_EXPIRY=7d

# Internal API Key (MUST CHANGE THIS!)
INTERNAL_API_KEY=your_internal_api_key_for_service_communication

# AI Service API Keys
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_MODEL=llama-3.1-70b-versatile
EMBEDDING_MODEL=text-embedding-3-small

# Lifestyle Service API Keys (Optional)
WEATHER_API_KEY=
NEWS_API_KEY=
```

**Important:** Generate secure secrets for JWT and INTERNAL_API_KEY:

```bash
# Generate random secrets
openssl rand -base64 32
openssl rand -base64 32
openssl rand -base64 32
```

Use these generated values for `JWT_ACCESS_SECRET`, `JWT_REFRESH_SECRET`, and `INTERNAL_API_KEY`.

Save with `Ctrl+X`, then `Y`, then `Enter`.

---

## Step 3: Build and Start All Services

```bash
# Stop any existing containers
docker-compose down

# Build and start all services with production config
docker-compose -f docker-compose.prod.yml up -d --build
```

This will:
- Build all 5 application services (gateway, scheduler, ai-brain, lifestyle, worker)
- Start all infrastructure services (postgres, redis, rabbitmq, mongodb)
- Set up networking and health checks

**Expected build time:** 5-10 minutes (first time)

---

## Step 4: Monitor Service Startup

Watch the logs to ensure all services start correctly:

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# Or view specific service logs
docker-compose -f docker-compose.prod.yml logs -f gateway-service
docker-compose -f docker-compose.prod.yml logs -f scheduler-service
```

Press `Ctrl+C` to exit log view.

---

## Step 5: Check Service Status

```bash
# Check all services are running
docker-compose -f docker-compose.prod.yml ps
```

You should see all services with status "Up" and "healthy":
- speak-sync-postgres (healthy)
- speak-sync-redis (healthy)
- speak-sync-rabbitmq (healthy)
- speak-sync-mongodb (healthy)
- speak-sync-gateway (healthy)
- speak-sync-scheduler (healthy)
- speak-sync-ai-brain (healthy)
- speak-sync-lifestyle (healthy)
- speak-sync-worker (running)

---

## Step 6: Run Database Migrations

```bash
# Run Prisma migrations
docker-compose -f docker-compose.prod.yml exec scheduler-service pnpm prisma migrate deploy

# Verify migration
docker-compose -f docker-compose.prod.yml exec scheduler-service pnpm prisma migrate status
```

---

## Step 7: Test Your Deployment

### From the Server

```bash
# Test gateway service
curl http://localhost:3000/health

# Test scheduler service
curl http://localhost:3001/health

# Test AI brain service
curl http://localhost:8000/health

# Test lifestyle service
curl http://localhost:8001/health
```

### From Your Local Machine

Open PowerShell on your local PC:

```powershell
# Test gateway (main entry point)
curl http://210.79.129.52:3000/health

# Test scheduler
curl http://210.79.129.52:3001/health

# Test AI brain
curl http://210.79.129.52:8000/health

# Test lifestyle
curl http://210.79.129.52:8001/health
```

---

## Step 8: Test API Endpoints with Postman

### Register a User

- **URL:** `http://210.79.129.52:3000/api/auth/register`
- **Method:** POST
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
  "email": "test@example.com",
  "name": "Test User",
  "password": "Test@12345"
}
```

### Login

- **URL:** `http://210.79.129.52:3000/api/auth/login`
- **Method:** POST
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
  "email": "test@example.com",
  "password": "Test@12345"
}
```

You should receive access and refresh tokens.

---

## 🛠️ Useful Commands

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f gateway-service
docker-compose -f docker-compose.prod.yml logs -f scheduler-service
docker-compose -f docker-compose.prod.yml logs -f ai-brain-service
```

### Restart Services

```bash
# Restart all services
docker-compose -f docker-compose.prod.yml restart

# Restart specific service
docker-compose -f docker-compose.prod.yml restart gateway-service
```

### Stop Services

```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes (WARNING: deletes data)
docker-compose -f docker-compose.prod.yml down -v
```

### Update After Code Changes

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Or rebuild specific service
docker-compose -f docker-compose.prod.yml up -d --build gateway-service
```

### Check Resource Usage

```bash
# View resource usage
docker stats

# View disk usage
docker system df
```

### Access Database

```bash
# PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d speak_sync_db

# MongoDB
docker-compose -f docker-compose.prod.yml exec mongodb mongosh speak_sync_lifestyle
```

### Access RabbitMQ Management

Open in browser: `http://210.79.129.52:15672`
- Username: `guest`
- Password: `guest`

---

## 🔧 Troubleshooting

### Services Won't Start

```bash
# Check logs for errors
docker-compose -f docker-compose.prod.yml logs

# Check specific service
docker-compose -f docker-compose.prod.yml logs scheduler-service
```

### Port Already in Use

```bash
# Check what's using the port
sudo netstat -tlnp | grep 3000

# Kill the process
sudo kill -9 <PID>
```

### Database Connection Errors

```bash
# Restart postgres
docker-compose -f docker-compose.prod.yml restart postgres

# Check postgres logs
docker-compose -f docker-compose.prod.yml logs postgres

# Verify postgres is healthy
docker-compose -f docker-compose.prod.yml ps postgres
```

### Build Failures

```bash
# Clean everything and rebuild
docker-compose -f docker-compose.prod.yml down -v
docker system prune -a
docker-compose -f docker-compose.prod.yml up -d --build
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a --volumes

# Remove unused images
docker image prune -a
```

---

## 🔒 Security Checklist

- ✅ Changed all default passwords in `.env`
- ✅ Generated secure JWT secrets (min 32 characters)
- ✅ Generated secure INTERNAL_API_KEY
- ✅ Added API keys for GROQ and OpenAI
- ✅ Configured firewall rules on ExCloud
- ✅ Using HTTPS in production (recommended)

---

## 📊 Service URLs

Once deployed, your services will be available at:

- **Gateway API:** http://210.79.129.52:3000
- **Scheduler API:** http://210.79.129.52:3001
- **AI Brain API:** http://210.79.129.52:8000
- **Lifestyle API:** http://210.79.129.52:8001
- **RabbitMQ Management:** http://210.79.129.52:15672

---

## 🎉 Success!

Your Speak-Sync application is now running in production on ExCloud!

For any issues, check the logs and refer to the troubleshooting section above.

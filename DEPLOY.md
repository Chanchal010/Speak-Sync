# 🚀 Quick Deployment Guide

## Current Workflow

You have Git set up between local and server. Here's what to do:

---

## 📋 **When You Make Code Changes**

### 1. On Your Local Machine:

```bash
# Make your changes, then:
./update.sh "Your commit message"

# Or manually:
git add .
git commit -m "Your changes"
git push origin main
```

### 2. On Your Server (210.79.129.61):

```bash
ssh root@210.79.129.61
cd /opt/speak-sync

# Pull latest code
git pull

# Deploy with Docker
./deploy.sh
```

**Or one command from local:**
```bash
ssh root@210.79.129.61 'cd /opt/speak-sync && git pull && ./deploy.sh'
```

---

## 🔧 **What deploy.sh Does**

1. ✅ Checks .env file exists
2. 🛑 Stops running Docker containers
3. 🔨 Rebuilds Docker images with latest code
4. 🚀 Starts all services
5. 🏥 Runs health checks
6. 📊 Shows container status

---

## 📝 **Environment Variables**

### First Time Setup:

On your server, create `.env` file:

```bash
cd /opt/speak-sync
nano .env
```

**Required variables:**
```env
# Gateway
PORT=3000
NODE_ENV=production
JWT_ACCESS_SECRET=your_secret_here
JWT_REFRESH_SECRET=your_secret_here
INTERNAL_API_KEY=your_api_key_here

# Services
SCHEDULER_SERVICE_URL=http://scheduler-service:3001
AI_BRAIN_SERVICE_URL=http://ai-brain-service:8000
LIFESTYLE_SERVICE_URL=http://lifestyle-service:8001

# Databases
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://user:pass@host:6379
MONGO_URL=mongodb+srv://user:pass@host/db

# API Keys
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
```

### When You Need to Change .env:

```bash
# On server
cd /opt/speak-sync
nano .env  # Make your changes

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

---

## 🐳 **Docker Commands**

### View Running Containers:
```bash
docker-compose -f docker-compose.prod.yml ps
```

### View Logs:
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f gateway
docker-compose -f docker-compose.prod.yml logs -f ai-brain-service
```

### Restart Services:
```bash
# All services
docker-compose -f docker-compose.prod.yml restart

# Specific service
docker-compose -f docker-compose.prod.yml restart gateway
```

### Stop Everything:
```bash
docker-compose -f docker-compose.prod.yml down
```

### Start Everything:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Rebuild Specific Service:
```bash
docker-compose -f docker-compose.prod.yml up -d --build gateway
```

---

## 🔄 **Complete Deployment Workflow**

### Local Machine → Server:

```bash
# 1. Make changes locally
# 2. Test locally
npm run dev  # or docker-compose up

# 3. Commit and push
git add .
git commit -m "Add new feature"
git push origin main

# 4. Deploy to server (one command)
ssh root@210.79.129.61 'cd /opt/speak-sync && git pull && ./deploy.sh'

# 5. Check deployment
ssh root@210.79.129.61 'curl http://localhost:3000/health'
```

---

## 🧪 **Testing After Deployment**

```bash
# From local machine
curl http://210.79.129.61/health

# Should return:
{
  "status": "healthy",
  "services": [...]
}
```

---

## 🚨 **If Something Goes Wrong**

### Check Container Status:
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Check Logs:
```bash
# Last 100 lines of all services
docker-compose -f docker-compose.prod.yml logs --tail=100

# Follow logs in real-time
docker-compose -f docker-compose.prod.yml logs -f gateway
```

### Restart Everything:
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Complete Reset:
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

### Check if .env is loaded:
```bash
docker-compose -f docker-compose.prod.yml exec gateway env | grep JWT
```

---

## 📊 **Monitoring**

### Real-time logs:
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### Container stats:
```bash
docker stats
```

### Check health endpoint:
```bash
watch -n 5 'curl -s http://localhost:3000/health | jq .'
```

---

## 🎯 **Quick Commands Cheat Sheet**

```bash
# Local: Push changes
git push origin main

# Server: Update and deploy
cd /opt/speak-sync && git pull && ./deploy.sh

# Server: View logs
docker-compose -f docker-compose.prod.yml logs -f

# Server: Restart
docker-compose -f docker-compose.prod.yml restart

# Server: Check status
docker-compose -f docker-compose.prod.yml ps

# Server: Stop all
docker-compose -f docker-compose.prod.yml down

# Local: One-command deployment
ssh root@210.79.129.61 'cd /opt/speak-sync && git pull && ./deploy.sh'
```

---

## ✅ **Daily Workflow Example**

```bash
# Morning: Make changes
vim src/some-file.ts

# Test locally
docker-compose up

# Deploy to production
./update.sh "Fixed bug in auth"

# On server (automatically or manually)
ssh root@210.79.129.61 'cd /opt/speak-sync && git pull && ./deploy.sh'

# Verify
curl http://210.79.129.61/health
```

---

## 🔐 **Important Notes**

1. **Never commit .env files** - They're in .gitignore
2. **Environment changes** require container restart
3. **Database migrations** need to run before deployment
4. **Always test locally** before deploying
5. **Check logs** after each deployment

---

## 📞 **Need Help?**

Check:
1. Container logs: `docker-compose -f docker-compose.prod.yml logs`
2. Health endpoint: `curl http://localhost:3000/health`
3. Container status: `docker-compose -f docker-compose.prod.yml ps`
4. Environment loaded: `docker-compose -f docker-compose.prod.yml exec gateway env`

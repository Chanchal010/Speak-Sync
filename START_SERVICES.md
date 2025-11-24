# 🚀 How to Start All Speak-Sync Services

## ✅ Prerequisites Checklist

Before starting services, ensure:
- [x] Python virtual environments created for both Python services
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] Environment files exist (`.env` files in each service)
- [x] API keys added to `apps/ai-brain-service/.env`
- [ ] Node.js dependencies installed (`pnpm install`)

---

## 🎯 Quick Start (All Services)

You need **4 separate terminal windows** to run all services:

### Terminal 1: AI Brain Service (Python - Port 8000)
```powershell
cd apps/ai-brain-service
.\venv\Scripts\Activate.ps1
uvicorn src.main:app --reload --port 8000
```

### Terminal 2: Lifestyle Service (Python - Port 8001)
```powershell
cd apps/lifestyle-service
.\venv\Scripts\Activate.ps1
uvicorn src.main:app --reload --port 8001
```

### Terminal 3: Gateway Service (Node.js - Port 3000)
```powershell
pnpm dev:gateway
```

### Terminal 4: Scheduler Service (Node.js - Port 3001)
```powershell
pnpm dev:scheduler
```

### Optional Terminal 5: Worker Service (Node.js)
```powershell
pnpm dev:worker
```

---

## 🔍 Verify Services are Running

After starting all services, check their health:

```powershell
# AI Brain Service
curl http://localhost:8000/health

# Lifestyle Service
curl http://localhost:8001/health

# Gateway Service
curl http://localhost:3000/health

# Scheduler Service
curl http://localhost:3001/health
```

Or use the automated health check script:
```powershell
.\scripts\check-services.ps1
```

---

## 📝 Service Details

| Service | Type | Port | Purpose |
|---------|------|------|---------|
| **AI Brain Service** | Python/FastAPI | 8000 | AI Intelligence Core (Groq, OpenAI, pgvector) |
| **Lifestyle Service** | Python/FastAPI | 8001 | Habits & Logs (MongoDB) |
| **Gateway Service** | Node.js/Express | 3000 | API Gateway & Authentication |
| **Scheduler Service** | Node.js/Express | 3001 | Task Scheduling (PostgreSQL) |
| **Worker Service** | Node.js | - | Background Jobs (RabbitMQ) |

---

## 🗄️ Database Connections (Cloud-Based)

Your services connect to these cloud databases:

- **PostgreSQL** (Neon) - Used by AI Brain & Scheduler services
- **MongoDB** (Atlas) - Used by Lifestyle service
- **Redis** (Upstash) - Used by Gateway & AI Brain services
- **RabbitMQ** - Check if you have cloud instance or need local Docker

> ⚠️ **No Docker needed** - All databases are cloud-hosted!

---

## 🛠️ Using Helper Scripts

I've created scripts to make this easier:

### Run Individual Services:
```powershell
# AI Brain Service
.\scripts\run-ai-brain.ps1

# Lifestyle Service
.\scripts\run-lifestyle.ps1
```

### Check Service Health:
```powershell
.\scripts\check-services.ps1
```

---

## 🐛 Troubleshooting

### Python Service Won't Start
```powershell
# Make sure virtual environment is activated
cd apps/ai-brain-service
.\venv\Scripts\Activate.ps1

# Check if uvicorn is installed
pip list | Select-String uvicorn

# Reinstall if needed
pip install -r requirements.txt
```

### Node Service Won't Start
```powershell
# Install dependencies
pnpm install

# Check if package.json scripts exist
cat apps/gateway-service/package.json
```

### Port Already in Use
```powershell
# Find process using port (e.g., 8000)
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

### Missing Environment Variables
```powershell
# Regenerate .env files
.\scripts\setup-env.ps1

# Then add your API keys to apps/ai-brain-service/.env
```

---

## 📊 Development Workflow

**Daily Development Routine:**

1. **Start Python Services** (Terminals 1 & 2)
   - AI Brain Service on port 8000
   - Lifestyle Service on port 8001

2. **Start Node Services** (Terminals 3 & 4)
   - Gateway Service on port 3000
   - Scheduler Service on port 3001

3. **Verify All Services**
   ```powershell
   .\scripts\check-services.ps1
   ```

4. **Start Coding!** 🎉
   - All services have hot-reload enabled
   - Changes will auto-restart services

---

## 🔑 Important Notes

1. **API Keys Required**: Add these to `apps/ai-brain-service/.env`:
   - `GROQ_API_KEY` - Get from https://console.groq.com
   - `OPENAI_API_KEY` - Get from https://platform.openai.com

2. **Service Dependencies**:
   - Gateway depends on other services being available
   - Worker service depends on RabbitMQ connection

3. **Database Migrations**:
   - For Scheduler service (Prisma): `pnpm --filter scheduler-service prisma:migrate`

---

## ✨ Next Steps

After all services are running:

1. Test the API endpoints
2. Check logs for any errors
3. Start building features!

**Happy Coding! 🚀**

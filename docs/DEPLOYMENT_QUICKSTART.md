# ExCloud Deployment - Quick Start Commands

## On Your Local Machine

### 1. Commit and Push Changes
```bash
cd d:\Projects\Speak-Sync
git add .
git commit -m "Add production Docker configuration for ExCloud"
git push origin main
```

---

## On ExCloud Server (SSH)

### 2. Connect to Server
```bash
ssh ubuntu@210.79.129.52
```

### 3. Navigate to Project
```bash
cd ~/Speak-Sync
git pull origin main
```

### 4. Configure Environment
```bash
nano .env
```

Paste and customize:
```env
POSTGRES_PASSWORD=YourSecurePassword123!
POSTGRES_DB=speak_sync_db
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest
JWT_ACCESS_SECRET=$(openssl rand -base64 32)
JWT_REFRESH_SECRET=$(openssl rand -base64 32)
JWT_ACCESS_EXPIRY=15m
JWT_REFRESH_EXPIRY=7d
INTERNAL_API_KEY=$(openssl rand -base64 32)
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
DEFAULT_MODEL=llama-3.1-70b-versatile
EMBEDDING_MODEL=text-embedding-3-small
WEATHER_API_KEY=
NEWS_API_KEY=
```

Save: `Ctrl+X`, `Y`, `Enter`

### 5. Deploy with Script (Recommended)
```bash
chmod +x scripts/deploy-excloud.sh
./scripts/deploy-excloud.sh
```

### OR Deploy Manually
```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d --build

# Wait 2-3 minutes, then run migrations
docker-compose -f docker-compose.prod.yml exec scheduler-service pnpm prisma migrate deploy

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 6. Test Deployment
```bash
# Test from server
curl http://localhost:3000/health
curl http://localhost:3001/health
curl http://localhost:8000/health
curl http://localhost:8001/health
```

---

## From Your Local Machine - Test Public Access

```powershell
# Test from Windows PowerShell
curl http://210.79.129.52:3000/health
```

---

## Useful Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Stop services
docker-compose -f docker-compose.prod.yml down

# Update after code changes
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## Test API with Postman

**Register:**
- POST `http://210.79.129.52:3000/api/auth/register`
- Body: `{"email": "test@example.com", "name": "Test", "password": "Test@12345"}`

**Login:**
- POST `http://210.79.129.52:3000/api/auth/login`
- Body: `{"email": "test@example.com", "password": "Test@12345"}`

---

For detailed documentation, see: [EXCLOUD_DEPLOYMENT.md](./EXCLOUD_DEPLOYMENT.md)

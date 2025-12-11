# Deployment Instructions for ExCloud Server

## 🚀 Quick Deployment (3 Steps)

### Step 1: Initial Server Setup (One-Time)

SSH into your server and run the setup script:

```bash
# On your local machine
scp scripts/setup-server.sh root@210.79.129.61:/tmp/
ssh root@210.79.129.61

# On the server
chmod +x /tmp/setup-server.sh
/tmp/setup-server.sh
```

This installs:
- Node.js 20
- Python 3.11
- pnpm, PM2
- Nginx
- PostgreSQL client
- Git & build tools

### Step 2: Clone Repository & Configure

```bash
# On the server (after setup-server.sh completes)
cd /opt/speak-sync
git clone git@github.com:YOUR_USERNAME/Speak-Sync.git .

# Create environment configuration
cp .env.production .env
nano .env  # Edit with your actual values
```

**Required Environment Variables:**
```bash
# Generate secrets
openssl rand -base64 32  # For JWT_ACCESS_SECRET
openssl rand -base64 32  # For JWT_REFRESH_SECRET
openssl rand -base64 32  # For INTERNAL_API_KEY

# Update .env with:
- Your OpenAI API key
- Neon PostgreSQL URL
- Upstash Redis URL
- MongoDB Atlas URL
- Generated JWT secrets
- Generated INTERNAL_API_KEY
```

### Step 3: Deploy from Local Machine

```bash
# On your local machine
./scripts/deploy-to-server.sh
```

This will:
1. SSH to your server
2. Pull latest code from GitHub
3. Install dependencies (pnpm install)
4. Build TypeScript services
5. Setup Python virtual environments
6. Start/restart services with PM2
7. Run health checks

---

## 🤖 Automatic Deployment (GitHub Actions)

### Setup GitHub Actions (One-Time)

1. **Add SSH key to GitHub Secrets:**

```bash
# On your server
cat /root/.ssh/id_ed25519

# Copy the private key, then:
# Go to: GitHub → Your Repo → Settings → Secrets and variables → Actions
# New repository secret:
#   Name: SSH_PRIVATE_KEY
#   Value: [paste the private key]
```

2. **Test the workflow:**

```bash
# On your local machine
git add .
git commit -m "Setup CI/CD"
git push origin main

# GitHub Actions will automatically deploy!
# Check: GitHub → Your Repo → Actions tab
```

### Manual Trigger

You can also trigger deployment manually:
- Go to GitHub → Actions → Deploy to ExCloud → Run workflow

---

## 🔒 Environment Configuration

### Create Service-Specific .env Files

**Gateway (.env or root .env):**
```env
PORT=3000
NODE_ENV=production
JWT_ACCESS_SECRET=your_generated_secret_here
JWT_REFRESH_SECRET=your_different_secret_here
INTERNAL_API_KEY=your_secure_api_key_here
SCHEDULER_SERVICE_URL=http://localhost:3001
AI_BRAIN_SERVICE_URL=http://localhost:8000
LIFESTYLE_SERVICE_URL=http://localhost:8001
REDIS_URL=redis://default:password@your-redis.upstash.io:6379
```

**Scheduler (apps/scheduler-service/.env):**
```env
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
REDIS_URL=redis://default:password@your-redis.upstash.io:6379
INTERNAL_API_KEY=your_secure_api_key_here  # MUST MATCH GATEWAY
JWT_ACCESS_SECRET=your_generated_secret_here  # MUST MATCH GATEWAY
JWT_REFRESH_SECRET=your_different_secret_here  # MUST MATCH GATEWAY
```

**AI Brain (apps/ai-brain-service/.env):**
```env
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-...
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
REDIS_URL=redis://default:password@your-redis.upstash.io:6379
LIFESTYLE_SERVICE_URL=http://localhost:8001
SERVICE_PORT=8000
```

**Lifestyle (apps/lifestyle-service/.env):**
```env
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/speaksync
REDIS_URL=redis://default:password@your-redis.upstash.io:6379
SERVICE_PORT=8001
```

---

## 🌐 Nginx Setup (Reverse Proxy)

After services are running, setup Nginx:

```bash
# On the server
nano /etc/nginx/sites-available/speaksync
```

Paste this configuration:
```nginx
upstream gateway {
    server localhost:3000;
}

server {
    listen 80;
    server_name 210.79.129.61;  # Or yourdomain.com
    
    client_max_body_size 25M;

    location /api/ {
        proxy_pass http://gateway;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /health {
        proxy_pass http://gateway;
    }
}
```

Enable and restart:
```bash
ln -s /etc/nginx/sites-available/speaksync /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

---

## 🧪 Testing Deployment

```bash
# From your local machine
curl http://210.79.129.61/health

# Should return:
{
  "status": "healthy",
  "services": [
    {"name": "ai-brain", "status": "healthy"},
    {"name": "scheduler", "status": "healthy"},
    {"name": "lifestyle", "status": "healthy"}
  ]
}
```

---

## 📊 Monitoring

### View Service Status
```bash
ssh root@210.79.129.61
pm2 status
```

### View Logs
```bash
pm2 logs gateway      # Gateway logs
pm2 logs ai-brain     # AI Brain logs
pm2 logs --lines 100  # Last 100 lines all services
```

### Real-time Monitoring
```bash
pm2 monit
```

---

## 🔄 Common Operations

### Update Code
```bash
# From local machine
./scripts/deploy-to-server.sh
```

### Restart Service
```bash
# On server
pm2 restart gateway
pm2 restart all
```

### View Specific Service Logs
```bash
pm2 logs ai-brain --lines 200
```

### Check Service Health
```bash
curl http://localhost:3000/health
```

---

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
pm2 logs ai-brain --lines 100

# Check if port is in use
netstat -tulpn | grep 8000

# Manually test service
cd /opt/speak-sync/apps/ai-brain-service
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Database Connection Issues

```bash
# Test PostgreSQL
psql "$DATABASE_URL" -c "SELECT 1"

# Test MongoDB
mongosh "$MONGO_URL" --eval "db.adminCommand('ping')"

# Test Redis
redis-cli -u "$REDIS_URL" ping
```

### Authentication Errors

**Error**: "Forbidden - Invalid service credentials"

**Solution**: Ensure `INTERNAL_API_KEY` matches in both gateway and scheduler `.env` files

```bash
# Check gateway
cat /opt/speak-sync/.env | grep INTERNAL_API_KEY

# Check scheduler
cat /opt/speak-sync/apps/scheduler-service/.env | grep INTERNAL_API_KEY

# They must be identical!
```

---

## 📋 Deployment Checklist

- [ ] SSH access working (`ssh root@210.79.129.61`)
- [ ] Server setup complete (`setup-server.sh`)
- [ ] Repository cloned to `/opt/speak-sync`
- [ ] `.env` file configured with all secrets
- [ ] Database URLs tested (PostgreSQL, MongoDB, Redis)
- [ ] OpenAI API key added
- [ ] INTERNAL_API_KEY matches in gateway & scheduler
- [ ] Deployment script executed successfully
- [ ] All services running (`pm2 status`)
- [ ] Health check passing (`curl http://localhost:3000/health`)
- [ ] Nginx configured
- [ ] Firewall configured (ports 80, 443, 22)
- [ ] GitHub Actions SSH key added
- [ ] SSL certificate installed (optional but recommended)

---

## 🎯 Next Steps After Deployment

1. **Domain Setup**: Point your domain to 210.79.129.61
2. **SSL Certificate**: Install Let's Encrypt
   ```bash
   certbot --nginx -d yourdomain.com
   ```
3. **Monitoring**: Setup logging and alerts
4. **Backups**: Configure database backups
5. **CDN**: Use Cloudflare for DDoS protection

---

## 📞 Quick Commands Reference

```bash
# Deploy latest code
./scripts/deploy-to-server.sh

# SSH to server
ssh root@210.79.129.61

# View all services
pm2 status

# Restart all
pm2 restart all

# View logs
pm2 logs

# Check health
curl http://localhost:3000/health

# Nginx logs
tail -f /var/log/nginx/error.log
```

---

**Status**: Ready for production deployment ✅  
**Estimated Time**: 15-20 minutes  
**Server**: 210.79.129.61

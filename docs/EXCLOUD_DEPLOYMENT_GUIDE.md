# Deployment Guide - ExCloud Server

**Server IP**: 210.79.129.61  
**Console**: https://console.excloud.in/console  
**Date**: December 11, 2025

---

## 📋 Pre-Deployment Checklist

### On Your Local Machine:
- [x] All services running locally (Gateway, AI Brain, Scheduler, Lifestyle)
- [x] Code committed to GitHub
- [ ] GitHub repository URL ready
- [ ] SSH access to server verified

### On ExCloud Server:
- [ ] SSH access configured
- [ ] Node.js 20+ installed
- [ ] Python 3.11+ installed
- [ ] PostgreSQL database available
- [ ] MongoDB database available
- [ ] Redis database available
- [ ] PM2 or systemd for process management

---

## 🔑 Step 1: SSH Connection Setup

### Connect to Your Server:
```bash
# From your local machine
ssh root@210.79.129.61
# OR if you have a specific user
ssh your_username@210.79.129.61
```

### Generate SSH Key (if not already done):
```bash
# On your local machine
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key to server
ssh-copy-id root@210.79.129.61
```

### Test Connection:
```bash
ssh root@210.79.129.61 'echo "Connection successful!"'
```

---

## 🐙 Step 2: GitHub Integration

### Option A: Deploy via Git Clone (Recommended)

#### On Server:
```bash
# Install Git (if not installed)
apt update && apt install -y git

# Navigate to deployment directory
cd /opt  # or /var/www or your preferred location
mkdir -p speak-sync
cd speak-sync

# Clone your repository
git clone https://github.com/YOUR_USERNAME/Speak-Sync.git .

# If private repo, setup GitHub SSH key:
ssh-keygen -t ed25519 -C "server@210.79.129.61"
cat ~/.ssh/id_ed25519.pub
# Add this key to GitHub: Settings > SSH and GPG keys > New SSH key
```

### Option B: Deploy via GitHub Actions (CI/CD)

#### Create `.github/workflows/deploy.yml` in your repo:
```yaml
name: Deploy to ExCloud

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Server
        uses: appleboy/ssh-action@master
        with:
          host: 210.79.129.61
          username: root
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/speak-sync
            git pull origin main
            pnpm install
            pnpm build
            pm2 restart all
```

#### Add SSH_PRIVATE_KEY to GitHub Secrets:
1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. New repository secret → Name: `SSH_PRIVATE_KEY`
3. Value: Contents of your server's private key

---

## 🛠️ Step 3: Server Environment Setup

### Install Required Software:

```bash
# Update system
apt update && apt upgrade -y

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Install pnpm
npm install -g pnpm

# Install Python 3.11
apt install -y python3.11 python3.11-venv python3.11-dev

# Install build tools
apt install -y build-essential

# Install PM2 for process management
npm install -g pm2

# Install PostgreSQL client (if needed)
apt install -y postgresql-client

# Install MongoDB tools (if needed)
apt install -y mongodb-clients
```

---

## 📦 Step 4: Deploy Application

### On Server:

```bash
# Navigate to project
cd /opt/speak-sync

# Pull latest code
git pull origin main

# Install dependencies
pnpm install

# Build all services
pnpm build

# Create environment files
cp .env.example .env
nano .env  # Edit with your production values
```

### Environment Configuration:

Create `/opt/speak-sync/.env`:
```env
# Gateway Service
PORT=3000
NODE_ENV=production
JWT_ACCESS_SECRET=YOUR_SECURE_RANDOM_SECRET_HERE
JWT_REFRESH_SECRET=YOUR_SECURE_RANDOM_SECRET_HERE
SCHEDULER_SERVICE_URL=http://localhost:3001
AI_BRAIN_SERVICE_URL=http://localhost:8000
LIFESTYLE_SERVICE_URL=http://localhost:8001
INTERNAL_API_KEY=YOUR_SECURE_API_KEY_HERE

# Database URLs (use your actual connection strings)
DATABASE_URL=postgresql://user:pass@localhost:5432/speaksync
REDIS_URL=redis://localhost:6379
MONGO_URL=mongodb://localhost:27017/speaksync

# API Keys
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
OPENROUTER_API_KEY=your_openrouter_key
```

---

## 🚀 Step 5: Start Services with PM2

### Create PM2 Ecosystem File:

Create `/opt/speak-sync/ecosystem.config.js`:
```javascript
module.exports = {
  apps: [
    {
      name: 'gateway',
      cwd: '/opt/speak-sync/apps/gateway-service',
      script: 'dist/server.js',
      instances: 2,
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    },
    {
      name: 'scheduler',
      cwd: '/opt/speak-sync/apps/scheduler-service',
      script: 'dist/server.js',
      instances: 1,
      env: {
        NODE_ENV: 'production',
        PORT: 3001
      }
    },
    {
      name: 'ai-brain',
      cwd: '/opt/speak-sync/apps/ai-brain-service',
      script: 'venv/bin/python',
      args: '-m uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 2',
      instances: 1,
      interpreter: 'none'
    },
    {
      name: 'lifestyle',
      cwd: '/opt/speak-sync/apps/lifestyle-service',
      script: 'venv/bin/python',
      args: '-m uvicorn src.main:app --host 0.0.0.0 --port 8001 --workers 2',
      instances: 1,
      interpreter: 'none'
    }
  ]
};
```

### Start All Services:
```bash
# Start all services
pm2 start ecosystem.config.js

# Check status
pm2 status

# View logs
pm2 logs

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Follow the command it gives you
```

---

## 🌐 Step 6: Configure Nginx Reverse Proxy

### Install Nginx:
```bash
apt install -y nginx
```

### Create Nginx Configuration:

Create `/etc/nginx/sites-available/speaksync`:
```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

upstream gateway {
    server localhost:3000;
}

server {
    listen 80;
    server_name 210.79.129.61;  # Or your domain name
    
    client_max_body_size 25M;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gateway API
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://gateway;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check (no rate limit)
    location /health {
        proxy_pass http://gateway;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Root
    location / {
        proxy_pass http://gateway;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

### Enable and Restart Nginx:
```bash
# Enable site
ln -s /etc/nginx/sites-available/speaksync /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Restart Nginx
systemctl restart nginx
systemctl enable nginx
```

---

## 🔒 Step 7: Setup SSL (Optional but Recommended)

### Using Let's Encrypt (Free SSL):
```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Get SSL certificate (if you have a domain)
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
certbot renew --dry-run
```

---

## 📊 Step 8: Monitoring Setup

### PM2 Monitoring:
```bash
# Real-time monitoring
pm2 monit

# Generate status webpage
pm2 web
# Access at http://210.79.129.61:9615
```

### System Monitoring:
```bash
# Install htop
apt install -y htop

# Install netdata (optional - advanced monitoring)
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
# Access at http://210.79.129.61:19999
```

---

## 🔄 Step 9: Deployment Workflow

### One-Command Deployment Script:

Create `/opt/speak-sync/deploy.sh`:
```bash
#!/bin/bash

echo "🚀 Starting deployment..."

# Pull latest code
git pull origin main

# Install dependencies
pnpm install

# Build all services
echo "📦 Building services..."
pnpm build

# Setup Python environments
echo "🐍 Setting up Python environments..."
cd apps/ai-brain-service
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

cd ../lifestyle-service
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

cd ../..

# Restart services
echo "♻️  Restarting services..."
pm2 restart all

# Wait for services to start
sleep 5

# Health check
echo "🏥 Running health checks..."
curl -s http://localhost:3000/health | jq '.'

echo "✅ Deployment complete!"
```

Make it executable:
```bash
chmod +x /opt/speak-sync/deploy.sh
```

### Deploy with One Command:
```bash
cd /opt/speak-sync && ./deploy.sh
```

---

## 🧪 Step 10: Verify Deployment

### Test from Your Local Machine:
```bash
# Test gateway health
curl http://210.79.129.61/health

# Test registration
curl -X POST http://210.79.129.61/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!","name":"Test"}'

# Test AI Brain (via gateway)
curl http://210.79.129.61/api/gateway/memory/stats/testuser \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Check Service Status on Server:
```bash
pm2 status
pm2 logs --lines 50
```

---

## 🔥 Step 11: Firewall Configuration

### Configure UFW:
```bash
# Enable firewall
ufw enable

# Allow SSH
ufw allow 22

# Allow HTTP/HTTPS
ufw allow 80
ufw allow 443

# Check status
ufw status
```

---

## 📋 Quick Reference Commands

### On Local Machine:
```bash
# Push code to GitHub
git add .
git commit -m "Deploy update"
git push origin main

# Deploy to server (if using SSH)
ssh root@210.79.129.61 'cd /opt/speak-sync && ./deploy.sh'
```

### On Server:
```bash
# View logs
pm2 logs gateway
pm2 logs ai-brain

# Restart specific service
pm2 restart gateway

# Restart all
pm2 restart all

# Stop all
pm2 stop all

# Monitor
pm2 monit

# Check Nginx
nginx -t
systemctl status nginx
tail -f /var/log/nginx/error.log
```

---

## 🐛 Troubleshooting

### Service won't start:
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

### Database connection issues:
```bash
# Test PostgreSQL
psql $DATABASE_URL -c "SELECT 1"

# Test MongoDB
mongosh $MONGO_URL --eval "db.adminCommand('ping')"

# Test Redis
redis-cli -u $REDIS_URL ping
```

### Nginx issues:
```bash
# Test configuration
nginx -t

# Check error logs
tail -f /var/log/nginx/error.log

# Restart Nginx
systemctl restart nginx
```

---

## 📞 Support

If you encounter issues:
1. Check PM2 logs: `pm2 logs`
2. Check Nginx logs: `tail -f /var/log/nginx/error.log`
3. Check service health: `curl http://localhost:3000/health`
4. Verify environment variables: `cat .env`

---

## 🎯 Next Steps After Deployment

1. **Setup Monitoring**: Configure alerts for service failures
2. **Backup Strategy**: Setup automated database backups
3. **CDN**: Use Cloudflare for DDoS protection
4. **Scaling**: Add more PM2 instances for high traffic
5. **CI/CD**: Setup GitHub Actions for automatic deployments
6. **Domain**: Point your domain to 210.79.129.61

---

**Status**: Ready for deployment ✅  
**Estimated Setup Time**: 30-45 minutes  
**Difficulty**: Intermediate

#!/bin/bash

# Speak-Sync Deployment Script
# For ExCloud Server: 210.79.129.61

set -e  # Exit on error

SERVER="210.79.129.61"
USER="root"
DEPLOY_PATH="/opt/speak-sync"

echo "🚀 Deploying Speak-Sync to ExCloud Server"
echo "=========================================="

# Check if SSH connection works
echo "📡 Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 ${USER}@${SERVER} exit 2>/dev/null; then
    echo "❌ Cannot connect to ${SERVER}"
    echo "Please ensure SSH is configured correctly"
    exit 1
fi
echo "✅ SSH connection successful"

# Deploy via SSH
echo ""
echo "📦 Deploying to server..."
ssh ${USER}@${SERVER} bash <<'ENDSSH'
set -e

DEPLOY_PATH="/opt/speak-sync"

# Create deployment directory if it doesn't exist
if [ ! -d "$DEPLOY_PATH" ]; then
    echo "📁 Creating deployment directory..."
    mkdir -p $DEPLOY_PATH
fi

cd $DEPLOY_PATH

# Check if git repo exists
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found in $DEPLOY_PATH"
    echo "Please clone your repository first:"
    echo "  ssh root@210.79.129.61"
    echo "  cd /opt/speak-sync"
    echo "  git clone https://github.com/YOUR_USERNAME/Speak-Sync.git ."
    exit 1
fi

# Pull latest code
echo "⬇️  Pulling latest code from GitHub..."
git fetch origin
git reset --hard origin/main
echo "✅ Code updated"

# Install Node.js dependencies
echo ""
echo "📦 Installing Node.js dependencies..."
if ! command -v pnpm &> /dev/null; then
    echo "Installing pnpm..."
    npm install -g pnpm
fi
pnpm install
echo "✅ Node.js dependencies installed"

# Build TypeScript services
echo ""
echo "🔨 Building TypeScript services..."
pnpm build
echo "✅ Build complete"

# Setup Python environments
echo ""
echo "🐍 Setting up Python environments..."

# AI Brain Service
if [ -d "apps/ai-brain-service" ]; then
    echo "  Setting up AI Brain Service..."
    cd apps/ai-brain-service
    
    # Create venv if it doesn't exist
    if [ ! -d "venv" ]; then
        python3.11 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    
    cd ../..
    echo "  ✅ AI Brain Service ready"
fi

# Lifestyle Service
if [ -d "apps/lifestyle-service" ]; then
    echo "  Setting up Lifestyle Service..."
    cd apps/lifestyle-service
    
    # Create venv if it doesn't exist
    if [ ! -d "venv" ]; then
        python3.11 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    
    cd ../..
    echo "  ✅ Lifestyle Service ready"
fi

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo ""
    echo "📦 Installing PM2..."
    npm install -g pm2
fi

# Check if ecosystem file exists
if [ ! -f "ecosystem.config.js" ]; then
    echo ""
    echo "⚠️  Creating PM2 ecosystem configuration..."
    cat > ecosystem.config.js <<'EOF'
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
      },
      error_file: '/var/log/speak-sync/gateway-error.log',
      out_file: '/var/log/speak-sync/gateway-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    {
      name: 'scheduler',
      cwd: '/opt/speak-sync/apps/scheduler-service',
      script: 'dist/server.js',
      instances: 1,
      env: {
        NODE_ENV: 'production',
        PORT: 3001
      },
      error_file: '/var/log/speak-sync/scheduler-error.log',
      out_file: '/var/log/speak-sync/scheduler-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    {
      name: 'ai-brain',
      cwd: '/opt/speak-sync/apps/ai-brain-service',
      script: 'venv/bin/python',
      args: '-m uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 2',
      instances: 1,
      interpreter: 'none',
      error_file: '/var/log/speak-sync/ai-brain-error.log',
      out_file: '/var/log/speak-sync/ai-brain-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    {
      name: 'lifestyle',
      cwd: '/opt/speak-sync/apps/lifestyle-service',
      script: 'venv/bin/python',
      args: '-m uvicorn src.main:app --host 0.0.0.0 --port 8001 --workers 2',
      instances: 1,
      interpreter: 'none',
      error_file: '/var/log/speak-sync/lifestyle-error.log',
      out_file: '/var/log/speak-sync/lifestyle-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
EOF
fi

# Create log directory
mkdir -p /var/log/speak-sync

# Check if services are running
if pm2 list | grep -q "online"; then
    echo ""
    echo "♻️  Restarting services..."
    pm2 restart all
else
    echo ""
    echo "🚀 Starting services for the first time..."
    pm2 start ecosystem.config.js
    pm2 save
fi

# Wait for services to stabilize
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Health check
echo ""
echo "🏥 Running health checks..."
if curl -s -f http://localhost:3000/health > /dev/null; then
    echo "✅ Gateway: healthy"
    curl -s http://localhost:3000/health | jq '.' || echo "  (jq not installed, raw response)"
else
    echo "⚠️  Gateway: not responding"
fi

# Show PM2 status
echo ""
echo "📊 Service Status:"
pm2 list

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Quick commands:"
echo "  View logs:     pm2 logs"
echo "  Check status:  pm2 status"
echo "  Monitor:       pm2 monit"
echo "  Restart:       pm2 restart all"
echo ""
echo "🌐 Access your services:"
echo "  Gateway:   http://210.79.129.61:3000"
echo "  AI Brain:  http://210.79.129.61:8000"
echo "  Scheduler: http://210.79.129.61:3001"
echo "  Lifestyle: http://210.79.129.61:8001"

ENDSSH

echo ""
echo "🎉 Deployment to ExCloud completed successfully!"
echo ""
echo "Next steps:"
echo "1. Setup Nginx reverse proxy (see docs/EXCLOUD_DEPLOYMENT_GUIDE.md)"
echo "2. Configure SSL certificate"
echo "3. Setup monitoring"

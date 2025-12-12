#!/bin/bash

# First Time Server Setup
# Run these commands on ExCloud server (210.79.129.61)

echo "🔧 Speak-Sync Server Setup"
echo "=========================="

# Check if project directory exists
if [ -d "/opt/speak-sync" ]; then
    echo "📁 Project directory exists"
    cd /opt/speak-sync
    
    # Check if it's a git repo
    if [ -d ".git" ]; then
        echo "📥 Pulling latest code..."
        git pull origin main
        echo "✅ Code updated!"
    else
        echo "❌ Directory exists but not a git repo"
        echo "Please remove it: rm -rf /opt/speak-sync"
        exit 1
    fi
else
    echo "📁 Creating project directory..."
    mkdir -p /opt/speak-sync
    cd /opt/speak-sync
    
    echo "📥 Cloning repository..."
    echo "Enter your GitHub repository URL:"
    echo "Example: git@github.com:YOUR_USERNAME/Speak-Sync.git"
    echo "Or: https://github.com/YOUR_USERNAME/Speak-Sync.git"
    read -p "Repository URL: " REPO_URL
    
    git clone "$REPO_URL" .
    echo "✅ Repository cloned!"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found!"
    if [ -f ".env.production" ]; then
        echo "📋 Creating .env from template..."
        cp .env.production .env
        echo "✅ .env created"
        echo ""
        echo "🔧 IMPORTANT: Edit .env with your actual values:"
        echo "   nano .env"
        echo ""
        echo "Make sure to set:"
        echo "  - DATABASE_URL (your Neon PostgreSQL)"
        echo "  - REDIS_URL (your Upstash Redis)"
        echo "  - RABBITMQ_URL (your CloudAMQP)"
        echo "  - OPENAI_API_KEY"
        echo "  - JWT secrets"
    else
        echo "❌ No .env.production template found"
        echo "Create .env manually with required configuration"
    fi
else
    echo "✅ .env file exists"
fi

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✅ Docker installed"
else
    echo "❌ Docker not installed"
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo "✅ Docker installed"
fi

# Check if docker-compose is installed
if command -v docker-compose &> /dev/null; then
    echo "✅ docker-compose installed"
else
    echo "❌ docker-compose not installed"
    echo "Installing docker-compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ docker-compose installed"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env if needed: nano .env"
echo "2. Run deployment: ./deploy.sh"

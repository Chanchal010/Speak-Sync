#!/bin/bash

# Initial Server Setup Script for ExCloud
# Run this ONCE on a fresh server

set -e

echo "🔧 Speak-Sync Server Setup"
echo "============================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

echo ""
echo "📦 Updating system packages..."
apt update && apt upgrade -y

echo ""
echo "📦 Installing Node.js 20..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi
echo "✅ Node.js $(node --version) installed"

echo ""
echo "📦 Installing pnpm..."
if ! command -v pnpm &> /dev/null; then
    npm install -g pnpm
fi
echo "✅ pnpm $(pnpm --version) installed"

echo ""
echo "📦 Installing Python 3.11..."
if ! command -v python3.11 &> /dev/null; then
    apt install -y python3.11 python3.11-venv python3.11-dev
fi
echo "✅ Python $(python3.11 --version) installed"

echo ""
echo "📦 Installing build tools..."
apt install -y build-essential git curl wget jq

echo ""
echo "📦 Installing PM2..."
if ! command -v pm2 &> /dev/null; then
    npm install -g pm2
fi
echo "✅ PM2 $(pm2 --version) installed"

echo ""
echo "📦 Installing PostgreSQL client..."
apt install -y postgresql-client

echo ""
echo "📦 Installing Nginx..."
apt install -y nginx
systemctl enable nginx
echo "✅ Nginx installed and enabled"

echo ""
echo "🔥 Configuring firewall..."
apt install -y ufw
ufw --force enable
ufw allow 22      # SSH
ufw allow 80      # HTTP
ufw allow 443     # HTTPS
ufw allow 3000    # Gateway (temporary, remove after Nginx setup)
ufw allow 8000    # AI Brain (temporary)
echo "✅ Firewall configured"

echo ""
echo "📁 Creating deployment directory..."
mkdir -p /opt/speak-sync
mkdir -p /var/log/speak-sync

echo ""
echo "🔑 Setting up Git SSH key for GitHub..."
if [ ! -f /root/.ssh/id_ed25519 ]; then
    ssh-keygen -t ed25519 -C "server@210.79.129.61" -f /root/.ssh/id_ed25519 -N ""
    echo ""
    echo "📋 Add this SSH key to your GitHub account:"
    echo "   Go to: https://github.com/settings/ssh/new"
    echo ""
    cat /root/.ssh/id_ed25519.pub
    echo ""
    read -p "Press Enter after adding the key to GitHub..."
fi

echo ""
echo "📥 Testing GitHub connection..."
ssh -T git@github.com 2>&1 | grep -q "successfully authenticated" && echo "✅ GitHub connected" || echo "⚠️  GitHub connection failed"

echo ""
echo "✅ Server setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Clone your repository:"
echo "   cd /opt/speak-sync"
echo "   git clone git@github.com:YOUR_USERNAME/Speak-Sync.git ."
echo ""
echo "2. Create .env file with your configuration:"
echo "   cp .env.example .env"
echo "   nano .env"
echo ""
echo "3. Run deployment script from your local machine:"
echo "   ./scripts/deploy-to-server.sh"
echo ""
echo "4. Setup Nginx reverse proxy:"
echo "   See docs/EXCLOUD_DEPLOYMENT_GUIDE.md"

#!/bin/bash

# Quick Deploy Script for ExCloud Server
# Run this on the server after git pull

set -e

echo "🚀 Deploying Speak-Sync with Docker"
echo "===================================="

# Check if running from project root
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: Must run from project root (/opt/speak-sync)"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating from template..."
    cp .env.production .env
    echo "❌ Please edit .env file with your actual values:"
    echo "   nano .env"
    exit 1
fi

# Pull latest images (if using pre-built images)
echo ""
echo "📥 Pulling Docker images..."
docker-compose -f docker-compose.prod.yml pull || echo "Skipping pull (building from source)"

# Stop running containers
echo ""
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Remove old images (optional - uncomment if needed)
# echo "🗑️  Removing old images..."
# docker image prune -f

# Build new images
echo ""
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
echo ""
echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
echo ""
echo "⏳ Waiting for services to start (15 seconds)..."
sleep 15

# Health check
echo ""
echo "🏥 Running health checks..."

if command -v curl &> /dev/null; then
    if curl -sf http://localhost:3000/health > /dev/null; then
        echo "✅ Gateway: healthy"
        curl -s http://localhost:3000/health | jq '.' || curl -s http://localhost:3000/health
    else
        echo "⚠️  Gateway: not responding yet"
    fi
else
    echo "⚠️  curl not installed, skipping health check"
fi

# Show running containers
echo ""
echo "📊 Running containers:"
docker-compose -f docker-compose.prod.yml ps

# Show logs (last 20 lines)
echo ""
echo "📋 Recent logs:"
docker-compose -f docker-compose.prod.yml logs --tail=20

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Useful commands:"
echo "  View logs:        docker-compose -f docker-compose.prod.yml logs -f"
echo "  Check status:     docker-compose -f docker-compose.prod.yml ps"
echo "  Restart service:  docker-compose -f docker-compose.prod.yml restart gateway"
echo "  Stop all:         docker-compose -f docker-compose.prod.yml down"
echo "  View gateway:     docker-compose -f docker-compose.prod.yml logs -f gateway"

#!/bin/bash

# ExCloud Deployment Script for Speak-Sync
# This script automates the deployment process on ExCloud server

set -e  # Exit on error

echo "=========================================="
echo "Speak-Sync ExCloud Deployment"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create .env file with required environment variables."
    echo "See .env.production for template."
    exit 1
fi

echo -e "${GREEN}✓${NC} Environment file found"

# Pull latest code
echo ""
echo "Pulling latest code from GitHub..."
git pull origin main
echo -e "${GREEN}✓${NC} Code updated"

# Stop existing containers
echo ""
echo "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down
echo -e "${GREEN}✓${NC} Containers stopped"

# Build and start services
echo ""
echo "Building and starting services..."
echo -e "${YELLOW}This may take 5-10 minutes on first run...${NC}"
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
sleep 30

# Check service status
echo ""
echo "Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# Run database migrations
echo ""
echo "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T scheduler-service pnpm prisma migrate deploy
echo -e "${GREEN}✓${NC} Migrations completed"

# Test health endpoints
echo ""
echo "Testing health endpoints..."

test_endpoint() {
    local url=$1
    local name=$2
    
    if curl -f -s -o /dev/null "$url"; then
        echo -e "${GREEN}✓${NC} $name is healthy"
        return 0
    else
        echo -e "${RED}✗${NC} $name is not responding"
        return 1
    fi
}

test_endpoint "http://localhost:3000/health" "Gateway Service"
test_endpoint "http://localhost:3001/health" "Scheduler Service"
test_endpoint "http://localhost:8000/health" "AI Brain Service"
test_endpoint "http://localhost:8001/health" "Lifestyle Service"

echo ""
echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Your services are running at:"
echo "  Gateway:   http://210.79.129.52:3000"
echo "  Scheduler: http://210.79.129.52:3001"
echo "  AI Brain:  http://210.79.129.52:8000"
echo "  Lifestyle: http://210.79.129.52:8001"
echo "  RabbitMQ:  http://210.79.129.52:15672"
echo ""
echo "View logs with:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""

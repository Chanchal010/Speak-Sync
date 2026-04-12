#!/bin/bash

# Debug deployment issues
# Run this on the server to diagnose problems

echo "🔍 Debugging Deployment Issues"
echo "=============================="

echo ""
echo "1️⃣ Checking if .env file exists..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    echo ""
    echo "Checking key variables (without showing values):"
    grep -E "^(DATABASE_URL|REDIS_URL|RABBITMQ_URL|OPENAI_API_KEY|JWT_ACCESS_SECRET|INTERNAL_API_KEY)=" .env | sed 's/=.*/=***HIDDEN***/'
else
    echo "❌ .env file not found!"
    echo "Create it with: cp .env.production .env"
    exit 1
fi

echo ""
echo "2️⃣ Checking container status..."
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "3️⃣ Checking container logs (last 50 lines)..."
echo ""
echo "=== Scheduler Service Logs ==="
docker-compose -f docker-compose.prod.yml logs --tail=50 scheduler-service

echo ""
echo "=== AI Brain Service Logs ==="
docker-compose -f docker-compose.prod.yml logs --tail=50 ai-brain-service

echo ""
echo "=== Lifestyle Service Logs ==="
docker-compose -f docker-compose.prod.yml logs --tail=50 lifestyle-service

echo ""
echo "4️⃣ Testing database connections..."

# Test PostgreSQL
if grep -q "DATABASE_URL" .env; then
    DB_URL=$(grep "^DATABASE_URL=" .env | cut -d'=' -f2-)
    echo "Testing PostgreSQL connection..."
    if [[ $DB_URL == postgresql://* ]]; then
        echo "✅ DATABASE_URL is set (PostgreSQL)"
    else
        echo "❌ DATABASE_URL format looks incorrect"
    fi
fi

# Test Redis
if grep -q "REDIS_URL" .env; then
    REDIS_URL=$(grep "^REDIS_URL=" .env | cut -d'=' -f2-)
    echo "Testing Redis connection..."
    if [[ $REDIS_URL == redis* ]]; then
        echo "✅ REDIS_URL is set"
    else
        echo "❌ REDIS_URL format looks incorrect"
    fi
fi

echo ""
echo "5️⃣ Checking if MongoDB is running..."
docker-compose -f docker-compose.prod.yml logs --tail=20 mongodb

echo ""
echo "=============================="
echo "📋 Next Steps:"
echo "1. Check the logs above for specific errors"
echo "2. Common issues:"
echo "   - DATABASE_URL incorrect or database not accessible"
echo "   - REDIS_URL incorrect"
echo "   - Missing environment variables"
echo "   - Port conflicts"
echo ""
echo "To fix and restart:"
echo "  1. Edit .env: nano .env"
echo "  2. Restart: docker-compose -f docker-compose.prod.yml down && ./deploy.sh"

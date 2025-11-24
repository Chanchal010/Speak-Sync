#!/bin/bash
set -e

echo "🚀 Setting up LifeOS Development Environment..."

# Install pnpm if not exists
if ! command -v pnpm &> /dev/null; then
    echo "📦 Installing pnpm..."
    npm install -g pnpm
fi

# Install dependencies
echo "📦 Installing dependencies..."
pnpm install

# Start infrastructure
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run migrations
echo "🗄️  Running database migrations..."
cd apps/scheduler-service && pnpm prisma migrate dev --name init && cd ../..

echo "✅ Setup complete! Run 'pnpm dev:gateway' to start services."

#chmod +x scripts/dev-setup.sh

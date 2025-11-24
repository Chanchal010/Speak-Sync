#!/bin/bash

echo "🏥 Checking service health..."

services=(
  "http://localhost:3000/health:Gateway"
  "http://localhost:3001/health:Scheduler"
  "http://localhost:3002/health:Worker"
  "http://localhost:8000/health:AI-Brain"
  "http://localhost:8001/health:Lifestyle"
)

for service in "${services[@]}"; do
  IFS=':' read -r url name <<< "$service"
  if curl -s "$url" > /dev/null; then
    echo "✅ $name - Healthy"
  else
    echo "❌ $name - Down"
  fi
done

#chmod +x scripts/health-check.sh

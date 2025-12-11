- **Lifestyle Service** (Python) - Habits & Logs
- **Worker Service** (Node.js) - Background Jobs

## Quick Start
```bash
# 1. Setup environment
./scripts/dev-setup.sh

# 2. Start services
pnpm dev:gateway       # Terminal 1
pnpm dev:scheduler     # Terminal 2
pnpm dev:worker        # Terminal 3

# Python services
cd apps/ai-brain-service && uvicorn src.main:app --reload --port 8000
cd apps/lifestyle-service && uvicorn src.main:app --reload --port 8001
```

## Tech Stack

- **Node.js**: Express, Prisma, RabbitMQ
- **Python**: FastAPI, pgvector, MongoDB
- **AI**: Groq (Llama 3.3), Whisper, BGE Embeddings
- **Infra**: PostgreSQL, Redis, MongoDB, RabbitMQ

## Development
```bash
pnpm install          # Install all dependencies
pnpm build:all        # Build all services
pnpm test:all         # Run all tests
```
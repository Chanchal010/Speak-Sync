# Stage 1: Base dependencies
FROM node:20-alpine AS base
RUN npm install -g pnpm
WORKDIR /app

# Stage 2: Install all dependencies
FROM base AS dependencies
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages ./packages
COPY apps/gateway-service/package.json ./apps/gateway-service/
COPY apps/scheduler-service/package.json ./apps/scheduler-service/
COPY apps/worker-service/package.json ./apps/worker-service/
RUN pnpm install --frozen-lockfile

# Stage 3: Build shared packages
FROM dependencies AS build-packages
COPY packages ./packages
RUN pnpm --filter "@speak-sync/*" build

# Stage 4: Build worker service
FROM build-packages AS build
COPY apps/worker-service ./apps/worker-service
RUN pnpm --filter worker-service build

# Stage 5: Production runtime
FROM node:20-alpine AS production
RUN npm install -g pnpm
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages ./packages
COPY apps/worker-service/package.json ./apps/worker-service/

# Install production dependencies only
RUN pnpm install --frozen-lockfile --prod

# Copy built files
COPY --from=build /app/packages ./packages
COPY --from=build /app/apps/worker-service/dist ./apps/worker-service/dist
COPY --from=build /app/apps/worker-service/package.json ./apps/worker-service/

WORKDIR /app/apps/worker-service

CMD ["node", "dist/index.js"]
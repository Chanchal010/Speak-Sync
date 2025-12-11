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

# Stage 4: Build gateway service
FROM build-packages AS build
COPY apps/gateway-service ./apps/gateway-service
RUN pnpm --filter gateway-service build

# Stage 5: Production runtime
FROM node:20-alpine AS production
RUN npm install -g pnpm
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages ./packages
COPY apps/gateway-service/package.json ./apps/gateway-service/

# Install production dependencies only
RUN pnpm install --frozen-lockfile --prod

# Copy built files
COPY --from=build /app/packages ./packages
COPY --from=build /app/apps/gateway-service/dist ./apps/gateway-service/dist
COPY --from=build /app/apps/gateway-service/package.json ./apps/gateway-service/

WORKDIR /app/apps/gateway-service

EXPOSE 3000

CMD ["node", "dist/server.js"]
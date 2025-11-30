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

# Stage 4: Build scheduler service
FROM build-packages AS build
COPY apps/scheduler-service ./apps/scheduler-service

# Generate Prisma client BEFORE building TypeScript
WORKDIR /app/apps/scheduler-service
RUN pnpm prisma generate

# Now build TypeScript (Prisma client is available)
WORKDIR /app
RUN pnpm --filter scheduler-service build

# Stage 5: Production runtime
FROM node:20-alpine AS production
RUN npm install -g pnpm
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages ./packages
COPY apps/scheduler-service/package.json ./apps/scheduler-service/

# Copy Prisma schema
COPY --from=build /app/apps/scheduler-service/prisma ./apps/scheduler-service/prisma

# Install ALL dependencies (including dev deps for Prisma CLI)
RUN pnpm install --frozen-lockfile

# Generate Prisma client in production
WORKDIR /app/apps/scheduler-service
RUN pnpm prisma generate

# Copy built files
WORKDIR /app
COPY --from=build /app/packages ./packages
COPY --from=build /app/apps/scheduler-service/dist ./apps/scheduler-service/dist
COPY --from=build /app/apps/scheduler-service/package.json ./apps/scheduler-service/

WORKDIR /app/apps/scheduler-service

EXPOSE 3001

CMD ["node", "dist/server.js"]
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import pg from 'pg';
import dotenv from 'dotenv';

// CRITICAL: Load environment variables before Prisma Client initialization
// This is required because Prisma 7 needs DATABASE_URL during construction
dotenv.config();

// Configure pg.Pool with proper settings for Neon (external database)
const pool = new pg.Pool({ 
  connectionString: process.env.DATABASE_URL,
  // Neon-specific settings for auto-suspend/wake behavior
  connectionTimeoutMillis: 10000, // 10 seconds to establish connection (Neon wake time)
  idleTimeoutMillis: 30000, // 30 seconds idle before closing connection
  max: 10, // Maximum pool size
  min: 2, // Minimum pool size
  // Important: Allow self-signed certificates for cloud databases
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

// Handle pool errors
pool.on('error', (err) => {
  console.error('❌ Unexpected database pool error:', err);
});

const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ 
  adapter,
  log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
});

export default prisma;

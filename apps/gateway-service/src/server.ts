import express from 'express';
import dotenv from 'dotenv';
import helmet from 'helmet';
import cors from 'cors';
import morgan from 'morgan';
// import rateLimit from 'express-rate-limit'; // Commented out for now
import authRoutes from './routes/auth.routes.js';
import aiBrainRoutes from './routes/ai-brain.routes.js';
import aiRoutes from './routes/ai.routes.js';
import lifestyleRoutes from './routes/lifestyle.routes.js';
import schedulerRoutes from './routes/scheduler.routes.js';
import { errorHandler } from './middleware/error-handler.middleware.js';
import { serviceRegistry } from './services/service-registry.service.js';

dotenv.config();


const app = express();
const PORT = process.env.PORT || 3000;

// Initialize service registry and start health checks
serviceRegistry.startHealthChecks();

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN || '*',
  credentials: true,
}));

// Request logging
app.use(morgan('combined'));

// Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Rate limiting for auth endpoints (COMMENTED OUT FOR NOW - will enable later)
// const authLimiter = rateLimit({
//   windowMs: 15 * 60 * 1000, // 15 minutes
//   max: 5, // 5 requests per window
//   message: 'Too many requests, please try again later',
//   standardHeaders: true,
//   legacyHeaders: false,
// });

// Health check
app.get('/health', (req, res) => {
  const systemHealth = serviceRegistry.getSystemHealth();
  res.json({
    status: systemHealth.status,
    service: 'gateway',
    timestamp: new Date().toISOString(),
    services: systemHealth.services.map(s => ({
      name: s.name,
      status: s.status,
      responseTime: s.responseTime,
      lastChecked: s.lastChecked
    })),
    summary: {
      healthy: systemHealth.healthyCount,
      total: systemHealth.totalCount
    }
  });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    service: 'Speak-Sync Gateway',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      auth: '/api/auth',
      ai: '/api/gateway/*',
      lifestyle: '/api/gateway/lifestyle/*',
      scheduler: '/api/scheduler/*'
    }
  });
});

// API routes (rate limiter commented out for now)
app.use('/api/auth', authRoutes);
app.use('/api/gateway', aiBrainRoutes);
app.use('/api/gateway/ai', aiRoutes);
app.use('/api/gateway/lifestyle', lifestyleRoutes);
app.use('/api/scheduler', schedulerRoutes);

// Global error handler (must be last)
app.use(errorHandler);

const server = app.listen(Number(PORT), '0.0.0.0', () => {
  console.log(`✓ Gateway Service running on port ${PORT} (0.0.0.0)`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  serviceRegistry.stopHealthChecks();
  server.close(() => {
    console.log('Gateway Service stopped');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully...');
  serviceRegistry.stopHealthChecks();
  server.close(() => {
    console.log('Gateway Service stopped');
    process.exit(0);
  });
});
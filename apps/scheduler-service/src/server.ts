import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import usersRouter from './routes/internal/users.routes.js';
import apiRouter from './routes/api/index.js';
import { errorHandler } from './middleware/error-handler.middleware.js';
import { verifyServiceAuth } from './middleware/auth.middleware.js';
import { initRabbitMQ, getRabbitMQ, setupRabbitMQInfrastructure } from './lib/rabbitmq/index.js';
import { reminderScheduler } from './lib/schedulers/reminder.scheduler.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'scheduler',
    timestamp: new Date().toISOString() 
  });
});

// API routes (public-facing, but require authentication)
app.use('/api', apiRouter);

// Internal API routes (service-to-service)
app.use('/internal/users', verifyServiceAuth, usersRouter);

// Global error handler (must be last)
app.use(errorHandler);

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('🛑 SIGTERM received, closing connections...');
  reminderScheduler.stop();
  const rabbitmq = getRabbitMQ();
  await rabbitmq.close();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('🛑 SIGINT received, closing connections...');
  reminderScheduler.stop();
  const rabbitmq = getRabbitMQ();
  await rabbitmq.close();
  process.exit(0);
});

// Initialize services and start server
async function startServer() {
  try {
    // Initialize RabbitMQ
    await initRabbitMQ();
    
    // Setup RabbitMQ infrastructure (exchanges, queues, bindings)
    await setupRabbitMQInfrastructure();

    // Start reminder scheduler (checks every 15 minutes)
    reminderScheduler.start(15);

    // Start Express server
    app.listen(PORT, () => {
      console.log(`✅ Scheduler Service running on port ${PORT}`);
      console.log(`📋 Task Management API ready at http://localhost:${PORT}/api/tasks`);
      console.log(`📁 Category API ready at http://localhost:${PORT}/api/categories`);
      console.log(`📅 Calendar Events API ready at http://localhost:${PORT}/api/events`);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

startServer();
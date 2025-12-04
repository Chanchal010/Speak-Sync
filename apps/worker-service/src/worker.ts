/**
 * Worker Service
 * Consumes messages from RabbitMQ queues and processes background jobs
 */
import dotenv from 'dotenv';
import express from 'express';
import { rabbitmqConnection } from './config/connection';
import {
  createTaskReminderConsumer,
  createTaskDueSoonConsumer,
  createHabitStreakConsumer,
  createEmailNotificationConsumer,
} from './consumers';

dotenv.config();

// Health check server
const app = express();
const PORT = process.env.PORT || 3002;

// Store active consumers for graceful shutdown
const activeConsumers: Array<{
  name: string;
  consumer: any;
}> = [];

// Health check endpoint
app.get('/health', (req, res) => {
  const isRabbitMQConnected = rabbitmqConnection.isConnected();
  const consumersStatus = activeConsumers.map((c) => ({
    name: c.name,
    active: c.consumer.isActive(),
    queue: c.consumer.getQueueName(),
  }));

  res.json({
    status: isRabbitMQConnected && activeConsumers.every((c) => c.consumer.isActive())
      ? 'healthy'
      : 'degraded',
    service: 'worker',
    rabbitmq: isRabbitMQConnected ? 'connected' : 'disconnected',
    consumers: consumersStatus,
    timestamp: new Date().toISOString(),
  });
});

// Consumer status endpoint
app.get('/consumers', (req, res) => {
  const consumersStatus = activeConsumers.map((c) => ({
    name: c.name,
    active: c.consumer.isActive(),
    queue: c.consumer.getQueueName(),
  }));

  res.json({
    total: activeConsumers.length,
    consumers: consumersStatus,
  });
});

/**
 * Initialize and start all consumers
 */
async function startConsumers(): Promise<void> {
  try {
    console.log('[INFO] Starting RabbitMQ consumers...');

    // Create consumer instances
    const taskReminderConsumer = createTaskReminderConsumer();
    const taskDueSoonConsumer = createTaskDueSoonConsumer();
    const habitStreakConsumer = createHabitStreakConsumer();
    const emailNotificationConsumer = createEmailNotificationConsumer();

    // Store consumers
    activeConsumers.push(
      { name: 'TaskReminderConsumer', consumer: taskReminderConsumer },
      { name: 'TaskDueSoonConsumer', consumer: taskDueSoonConsumer },
      { name: 'HabitStreakConsumer', consumer: habitStreakConsumer },
      { name: 'EmailNotificationConsumer', consumer: emailNotificationConsumer }
    );

    // Start all consumers
    await Promise.all([
      taskReminderConsumer.startConsuming(),
      taskDueSoonConsumer.startConsuming(),
      habitStreakConsumer.startConsuming(),
      emailNotificationConsumer.startConsuming(),
    ]);

    console.log(`[SUCCESS] All ${activeConsumers.length} consumers started successfully`);

    // Verify email transporter if configured
    if (process.env.EMAIL_USER && process.env.EMAIL_PASSWORD) {
      await emailNotificationConsumer.verifyConnection();
    }
  } catch (error) {
    console.error('[ERROR] Failed to start consumers:', error);
    throw error;
  }
}

/**
 * Graceful shutdown handler
 */
async function gracefulShutdown(signal: string): Promise<void> {
  console.log(`[INFO] Received ${signal}, starting graceful shutdown...`);

  try {
    // Stop all consumers
    console.log('[INFO] Stopping consumers...');
    await Promise.all(
      activeConsumers.map(async (c) => {
        await c.consumer.stopConsuming();
      })
    );

    // Close RabbitMQ connection
    console.log('[INFO] Closing RabbitMQ connection...');
    await rabbitmqConnection.close();

    console.log('[SUCCESS] Graceful shutdown completed');
    process.exit(0);
  } catch (error) {
    console.error('[ERROR] Error during shutdown:', error);
    process.exit(1);
  }
}

/**
 * Main startup function
 */
async function main(): Promise<void> {
  try {
    console.log('[INFO] Worker Service starting...');

    // Connect to RabbitMQ
    await rabbitmqConnection.connect();

    // Start consumers
    await startConsumers();

    // Start health check server
    app.listen(PORT, () => {
      console.log(`[SUCCESS] Worker Service running on port ${PORT}`);
      console.log(`[INFO] Health endpoint: http://localhost:${PORT}/health`);
      console.log(`[INFO] Consumers endpoint: http://localhost:${PORT}/consumers`);
    });

    console.log('[SUCCESS] Worker Service initialization complete');
  } catch (error) {
    console.error('[ERROR] Worker Service failed to start:', error);
    process.exit(1);
  }
}

// Graceful shutdown handlers
process.on('SIGINT', () => gracefulShutdown('SIGINT'));
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));

// Uncaught exception handler
process.on('uncaughtException', (error) => {
  console.error('[ERROR] Uncaught exception:', error);
  gracefulShutdown('uncaughtException');
});

// Unhandled rejection handler
process.on('unhandledRejection', (reason, promise) => {
  console.error('[ERROR] Unhandled rejection at:', promise, 'reason:', reason);
  gracefulShutdown('unhandledRejection');
});

// Start the service
main();
import { getRabbitMQ, RABBITMQ_CONFIG } from './index.js';

/**
 * Setup RabbitMQ Exchanges and Queues
 * This should be run once during application startup or deployment
 */
export async function setupRabbitMQInfrastructure(): Promise<void> {
  const rabbitmq = getRabbitMQ();
  const channel = rabbitmq.getChannel();

  if (!channel) {
    console.error('❌ Cannot setup RabbitMQ infrastructure - channel not available');
    return;
  }

  try {
    console.log('🔧 Setting up RabbitMQ exchanges and queues...');

    // 1. Setup Exchanges
    console.log('📢 Creating exchanges...');
    
    // Tasks Exchange (Topic)
    await channel.assertExchange(
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      RABBITMQ_CONFIG.EXCHANGE_TYPES.TOPIC,
      { durable: RABBITMQ_CONFIG.OPTIONS.DURABLE }
    );
    console.log(`  ✓ Exchange: ${RABBITMQ_CONFIG.EXCHANGES.TASKS}`);

    // Habits Exchange (Topic)
    await channel.assertExchange(
      RABBITMQ_CONFIG.EXCHANGES.HABITS,
      RABBITMQ_CONFIG.EXCHANGE_TYPES.TOPIC,
      { durable: RABBITMQ_CONFIG.OPTIONS.DURABLE }
    );
    console.log(`  ✓ Exchange: ${RABBITMQ_CONFIG.EXCHANGES.HABITS}`);

    // Notifications Exchange (Direct)
    await channel.assertExchange(
      RABBITMQ_CONFIG.EXCHANGES.NOTIFICATIONS,
      RABBITMQ_CONFIG.EXCHANGE_TYPES.DIRECT,
      { durable: RABBITMQ_CONFIG.OPTIONS.DURABLE }
    );
    console.log(`  ✓ Exchange: ${RABBITMQ_CONFIG.EXCHANGES.NOTIFICATIONS}`);

    // 2. Setup Dead Letter Exchange (DLX)
    console.log('💀 Creating Dead Letter Exchange...');
    await channel.assertExchange('dlx.exchange', 'direct', {
      durable: true,
    });
    console.log('  ✓ Exchange: dlx.exchange');

    // 3. Setup Queues with DLX
    console.log('📦 Creating queues...');

    const dlxConfig = {
      'x-dead-letter-exchange': 'dlx.exchange',
      'x-dead-letter-routing-key': 'dlq',
      'x-message-ttl': 86400000, // 24 hours
    };

    // Task Queues
    await channel.assertQueue(RABBITMQ_CONFIG.QUEUES.TASK_CREATED, {
      durable: true,
      arguments: dlxConfig,
    });
    await channel.bindQueue(
      RABBITMQ_CONFIG.QUEUES.TASK_CREATED,
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      RABBITMQ_CONFIG.ROUTING_KEYS.TASK_CREATED
    );
    console.log(`  ✓ Queue: ${RABBITMQ_CONFIG.QUEUES.TASK_CREATED}`);

    await channel.assertQueue(RABBITMQ_CONFIG.QUEUES.TASK_REMINDERS, {
      durable: true,
      arguments: dlxConfig,
    });
    await channel.bindQueue(
      RABBITMQ_CONFIG.QUEUES.TASK_REMINDERS,
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      RABBITMQ_CONFIG.ROUTING_KEYS.TASK_DUE_SOON
    );
    console.log(`  ✓ Queue: ${RABBITMQ_CONFIG.QUEUES.TASK_REMINDERS}`);

    await channel.assertQueue(RABBITMQ_CONFIG.QUEUES.TASK_DUE_SOON, {
      durable: true,
      arguments: dlxConfig,
    });
    await channel.bindQueue(
      RABBITMQ_CONFIG.QUEUES.TASK_DUE_SOON,
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      RABBITMQ_CONFIG.ROUTING_KEYS.TASK_DUE_SOON
    );
    console.log(`  ✓ Queue: ${RABBITMQ_CONFIG.QUEUES.TASK_DUE_SOON}`);

    // Event Queues
    await channel.assertQueue(RABBITMQ_CONFIG.QUEUES.EVENT_CREATED, {
      durable: true,
      arguments: dlxConfig,
    });
    await channel.bindQueue(
      RABBITMQ_CONFIG.QUEUES.EVENT_CREATED,
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      RABBITMQ_CONFIG.ROUTING_KEYS.EVENT_CREATED
    );
    console.log(`  ✓ Queue: ${RABBITMQ_CONFIG.QUEUES.EVENT_CREATED}`);

    await channel.assertQueue(RABBITMQ_CONFIG.QUEUES.EVENT_REMINDERS, {
      durable: true,
      arguments: dlxConfig,
    });
    await channel.bindQueue(
      RABBITMQ_CONFIG.QUEUES.EVENT_REMINDERS,
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      RABBITMQ_CONFIG.ROUTING_KEYS.EVENT_REMINDER
    );
    console.log(`  ✓ Queue: ${RABBITMQ_CONFIG.QUEUES.EVENT_REMINDERS}`);

    // Habit Queues
    await channel.assertQueue(RABBITMQ_CONFIG.QUEUES.HABIT_CREATED, {
      durable: true,
      arguments: dlxConfig,
    });
    await channel.bindQueue(
      RABBITMQ_CONFIG.QUEUES.HABIT_CREATED,
      RABBITMQ_CONFIG.EXCHANGES.HABITS,
      RABBITMQ_CONFIG.ROUTING_KEYS.HABIT_CREATED
    );
    console.log(`  ✓ Queue: ${RABBITMQ_CONFIG.QUEUES.HABIT_CREATED}`);

    await channel.assertQueue(RABBITMQ_CONFIG.QUEUES.HABIT_REMINDERS, {
      durable: true,
      arguments: dlxConfig,
    });
    await channel.bindQueue(
      RABBITMQ_CONFIG.QUEUES.HABIT_REMINDERS,
      RABBITMQ_CONFIG.EXCHANGES.HABITS,
      'habit.reminder.*'
    );
    console.log(`  ✓ Queue: ${RABBITMQ_CONFIG.QUEUES.HABIT_REMINDERS}`);

    await channel.assertQueue(RABBITMQ_CONFIG.QUEUES.HABIT_STREAKS, {
      durable: true,
      arguments: dlxConfig,
    });
    await channel.bindQueue(
      RABBITMQ_CONFIG.QUEUES.HABIT_STREAKS,
      RABBITMQ_CONFIG.EXCHANGES.HABITS,
      'habit.streak.*'
    );
    console.log(`  ✓ Queue: ${RABBITMQ_CONFIG.QUEUES.HABIT_STREAKS}`);

    // Notification Queue
    await channel.assertQueue(RABBITMQ_CONFIG.QUEUES.EMAIL_NOTIFICATIONS, {
      durable: true,
      arguments: dlxConfig,
    });
    await channel.bindQueue(
      RABBITMQ_CONFIG.QUEUES.EMAIL_NOTIFICATIONS,
      RABBITMQ_CONFIG.EXCHANGES.NOTIFICATIONS,
      'email'
    );
    console.log(`  ✓ Queue: ${RABBITMQ_CONFIG.QUEUES.EMAIL_NOTIFICATIONS}`);

    // Dead Letter Queue (DLQ)
    await channel.assertQueue(RABBITMQ_CONFIG.QUEUES.DLQ_RETRY, {
      durable: true,
    });
    await channel.bindQueue(
      RABBITMQ_CONFIG.QUEUES.DLQ_RETRY,
      'dlx.exchange',
      'dlq'
    );
    console.log(`  ✓ Queue: ${RABBITMQ_CONFIG.QUEUES.DLQ_RETRY}`);

    console.log('✅ RabbitMQ infrastructure setup complete!');
    console.log('');
    console.log('📊 Summary:');
    console.log('  - 3 Exchanges (tasks.events, habits.events, notifications.events)');
    console.log('  - 10 Queues (task, event, habit, notification queues)');
    console.log('  - Dead Letter Queue configured for failed messages');
    console.log('');
  } catch (error) {
    console.error('❌ Failed to setup RabbitMQ infrastructure:', error);
    throw error;
  }
}

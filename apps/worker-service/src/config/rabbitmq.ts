/**
 * RabbitMQ Configuration
 * Shared constants for exchanges, queues, and routing keys
 */

export const RABBITMQ_CONFIG = {
  EXCHANGES: {
    TASKS: 'tasks.events',
    HABITS: 'habits.events',
    NOTIFICATIONS: 'notifications.events',
  },
  QUEUES: {
    TASK_CREATED: 'task.created',
    TASK_REMINDERS: 'task.reminders',
    TASK_DUE_SOON: 'task.due_soon',
    EVENT_CREATED: 'event.created',
    EVENT_REMINDERS: 'event.reminders',
    HABIT_CREATED: 'habit.created',
    HABIT_REMINDERS: 'habit.reminders',
    HABIT_STREAKS: 'habit.streaks',
    EMAIL_NOTIFICATIONS: 'email.notifications',
    DLQ_RETRY: 'dlq.retry',
  },
  ROUTING_KEYS: {
    TASK_CREATED: 'task.created',
    TASK_COMPLETED: 'task.completed',
    TASK_UPDATED: 'task.updated',
    TASK_DELETED: 'task.deleted',
    TASK_DUE_SOON: 'task.due.soon',
    EVENT_CREATED: 'event.created',
    EVENT_UPDATED: 'event.updated',
    EVENT_REMINDER: 'event.reminder',
    HABIT_CREATED: 'habit.created',
    HABIT_LOGGED: 'habit.logged',
    HABIT_STREAK_ACHIEVED: 'habit.streak.achieved',
    HABIT_STREAK_BROKEN: 'habit.streak.broken',
    HABIT_MILESTONE: 'habit.milestone',
  },
  EXCHANGE_TYPES: {
    TOPIC: 'topic',
    DIRECT: 'direct',
    FANOUT: 'fanout',
  },
  OPTIONS: {
    DURABLE: true,
    PERSISTENT: true,
  },
} as const;

export const DEAD_LETTER_EXCHANGE = 'dlx.exchange';
export const DEAD_LETTER_QUEUE = 'dlq.retry';

export const CONSUMER_OPTIONS = {
  prefetchCount: 10, // Process up to 10 messages at a time
  noAck: false, // Require manual acknowledgment
  retryAttempts: 3,
  retryDelay: 5000, // 5 seconds
};

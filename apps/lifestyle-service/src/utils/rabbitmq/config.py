"""
RabbitMQ Configuration
"""

# Exchanges
EXCHANGES = {
    "TASKS": "tasks.events",
    "HABITS": "habits.events",
    "NOTIFICATIONS": "notifications.events",
}

# Queues
QUEUES = {
    "TASK_CREATED": "task.created",
    "TASK_REMINDERS": "task.reminders",
    "TASK_DUE_SOON": "task.due_soon",
    "EVENT_CREATED": "event.created",
    "EVENT_REMINDERS": "event.reminders",
    "HABIT_CREATED": "habit.created",
    "HABIT_REMINDERS": "habit.reminders",
    "HABIT_STREAKS": "habit.streaks",
    "EMAIL_NOTIFICATIONS": "email.notifications",
    "DLQ_RETRY": "dlq.retry",
}

# Routing Keys
ROUTING_KEYS = {
    "TASK_CREATED": "task.created",
    "TASK_COMPLETED": "task.completed",
    "TASK_UPDATED": "task.updated",
    "TASK_DELETED": "task.deleted",
    "TASK_DUE_SOON": "task.due.soon",
    "EVENT_CREATED": "event.created",
    "EVENT_UPDATED": "event.updated",
    "EVENT_REMINDER": "event.reminder",
    "HABIT_CREATED": "habit.created",
    "HABIT_LOGGED": "habit.logged",
    "HABIT_STREAK_ACHIEVED": "habit.streak.achieved",
    "HABIT_STREAK_BROKEN": "habit.streak.broken",
    "HABIT_MILESTONE": "habit.milestone",
}

# Exchange Types
EXCHANGE_TYPES = {
    "TOPIC": "topic",
    "DIRECT": "direct",
    "FANOUT": "fanout",
}

# Options
OPTIONS = {
    "DURABLE": True,
    "PERSISTENT": True,
}

# Combined config for easy access
RABBITMQ_CONFIG = {
    "EXCHANGES": EXCHANGES,
    "QUEUES": QUEUES,
    "ROUTING_KEYS": ROUTING_KEYS,
    "EXCHANGE_TYPES": EXCHANGE_TYPES,
    "OPTIONS": OPTIONS,
}

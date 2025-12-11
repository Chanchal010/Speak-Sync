import { v4 as uuidv4 } from 'uuid';
import { getRabbitMQ, RABBITMQ_CONFIG } from './index.js';
import type { 
  ScheduleEvent,
  TaskCreatedEvent,
  TaskCompletedEvent,
  TaskUpdatedEvent,
  TaskDeletedEvent,
  TaskDueSoonEvent,
  EventCreatedEvent,
  EventUpdatedEvent,
  EventReminderEvent,
  EventConflictDetectedEvent,
} from '@speak-sync/event-schemas';

/**
 * Event Publisher for RabbitMQ
 * Handles publishing events to appropriate exchanges with routing keys
 */
class EventPublisher {
  /**
   * Publish an event to RabbitMQ
   * @param event - The event to publish
   * @param exchange - The exchange name
   * @param routingKey - The routing key for the event
   */
  private async publishEvent(
    event: ScheduleEvent,
    exchange: string,
    routingKey: string
  ): Promise<void> {
    try {
      const rabbitmq = getRabbitMQ();
      const channel = rabbitmq.getChannel();

      if (!channel) {
        console.error('❌ RabbitMQ channel not available');
        throw new Error('RabbitMQ channel not available');
      }

      const message = Buffer.from(JSON.stringify(event));

      // Publish with persistence (durable message)
      const published = channel.publish(exchange, routingKey, message, {
        persistent: true, // Messages survive broker restart
        contentType: 'application/json',
        contentEncoding: 'utf-8',
        timestamp: Date.now(),
        messageId: event.eventId,
      });

      if (!published) {
        console.warn('⚠️ Message could not be published (buffer full), will retry...');
        // Wait for drain event and retry
        await new Promise<void>((resolve) => {
          channel.once('drain', () => {
            channel.publish(exchange, routingKey, message, {
              persistent: true,
              contentType: 'application/json',
              contentEncoding: 'utf-8',
              timestamp: Date.now(),
              messageId: event.eventId,
            });
            resolve();
          });
        });
      }

      console.log(`📤 Published event: ${event.eventType} to ${exchange}/${routingKey}`);
    } catch (error) {
      console.error('❌ Failed to publish event:', error);
      throw error;
    }
  }

  /**
   * Publish TASK_CREATED event
   */
  async publishTaskCreated(
    userId: string,
    taskId: string,
    taskData: {
      title: string;
      description?: string;
      priority: 'VI' | 'MI' | 'NI';
      categoryId?: string;
      dueDate?: Date;
      scheduledDate?: Date;
      tags?: string[];
    }
  ): Promise<void> {
    const event: TaskCreatedEvent = {
      eventId: uuidv4(),
      eventType: 'TASK_CREATED',
      timestamp: new Date().toISOString(),
      userId,
      taskId,
      title: taskData.title,
      description: taskData.description,
      priority: taskData.priority,
      dueDate: taskData.dueDate?.toISOString(),
      tags: taskData.tags,
      metadata: {
        categoryId: taskData.categoryId,
        scheduledDate: taskData.scheduledDate?.toISOString(),
      },
    };

    await this.publishEvent(
      event,
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      RABBITMQ_CONFIG.ROUTING_KEYS.TASK_CREATED
    );
  }

  /**
   * Publish TASK_COMPLETED event
   */
  async publishTaskCompleted(
    userId: string,
    taskId: string,
    taskData: {
      title: string;
      priority: 'VI' | 'MI' | 'NI';
      completedAt: Date;
      timeEstimate?: number;
      actualTime?: number;
    }
  ): Promise<void> {
    const event: TaskCompletedEvent = {
      eventId: uuidv4(),
      eventType: 'TASK_COMPLETED',
      timestamp: new Date().toISOString(),
      userId,
      taskId,
      title: taskData.title,
      completedAt: taskData.completedAt.toISOString(),
      timeEstimate: taskData.timeEstimate,
      actualTime: taskData.actualTime,
      metadata: {
        priority: taskData.priority,
      },
    };

    await this.publishEvent(
      event,
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      RABBITMQ_CONFIG.ROUTING_KEYS.TASK_COMPLETED
    );
  }

  /**
   * Publish TASK_UPDATED event
   */
  async publishTaskUpdated(
    userId: string,
    taskId: string,
    taskData: {
      title: string;
      priority: 'VI' | 'MI' | 'NI';
      changes: Array<{ field: string; oldValue: any; newValue: any }>;
    }
  ): Promise<void> {
    const event: TaskUpdatedEvent = {
      eventId: uuidv4(),
      eventType: 'TASK_UPDATED',
      timestamp: new Date().toISOString(),
      userId,
      taskId,
      changes: taskData.changes,
      metadata: {
        title: taskData.title,
        priority: taskData.priority,
      },
    };

    await this.publishEvent(
      event,
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      RABBITMQ_CONFIG.ROUTING_KEYS.TASK_UPDATED
    );
  }

  /**
   * Publish TASK_DELETED event
   */
  async publishTaskDeleted(
    userId: string,
    taskId: string,
    taskData: {
      title: string;
      priority: 'VI' | 'MI' | 'NI';
      reason?: string;
    }
  ): Promise<void> {
    const event: TaskDeletedEvent = {
      eventId: uuidv4(),
      eventType: 'TASK_DELETED',
      timestamp: new Date().toISOString(),
      userId,
      taskId,
      title: taskData.title,
      metadata: {
        priority: taskData.priority,
        reason: taskData.reason,
      },
    };

    await this.publishEvent(
      event,
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      RABBITMQ_CONFIG.ROUTING_KEYS.TASK_DELETED
    );
  }

  /**
   * Publish TASK_DUE_SOON event
   */
  async publishTaskDueSoon(
    userId: string,
    taskId: string,
    taskData: {
      title: string;
      priority: 'VI' | 'MI' | 'NI';
      dueDate: Date;
      hoursUntilDue: number;
    }
  ): Promise<void> {
    const event: TaskDueSoonEvent = {
      eventId: uuidv4(),
      eventType: 'TASK_DUE_SOON',
      timestamp: new Date().toISOString(),
      userId,
      taskId,
      title: taskData.title,
      dueDate: taskData.dueDate.toISOString(),
      hoursUntilDue: taskData.hoursUntilDue,
      metadata: {
        priority: taskData.priority,
      },
    };

    await this.publishEvent(
      event,
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      RABBITMQ_CONFIG.ROUTING_KEYS.TASK_DUE_SOON
    );
  }

  /**
   * Publish EVENT_CREATED event
   */
  async publishEventCreated(
    userId: string,
    calendarEventId: string,
    eventData: {
      title: string;
      description?: string;
      startTime: Date;
      endTime: Date;
      location?: string;
      attendees?: string[];
      isRecurring?: boolean;
    }
  ): Promise<void> {
    const event: EventCreatedEvent = {
      eventId: uuidv4(),
      eventType: 'EVENT_CREATED',
      timestamp: new Date().toISOString(),
      userId,
      calendarEventId,
      title: eventData.title,
      description: eventData.description,
      startTime: eventData.startTime.toISOString(),
      endTime: eventData.endTime.toISOString(),
      location: eventData.location,
      attendees: eventData.attendees,
      metadata: {
        isRecurring: eventData.isRecurring,
      },
    };

    await this.publishEvent(
      event,
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      RABBITMQ_CONFIG.ROUTING_KEYS.EVENT_CREATED
    );
  }

  /**
   * Publish EVENT_UPDATED event
   */
  async publishEventUpdated(
    userId: string,
    calendarEventId: string,
    eventData: {
      title: string;
      startTime: Date;
      endTime: Date;
      changes: Array<{ field: string; oldValue: any; newValue: any }>;
    }
  ): Promise<void> {
    const event: EventUpdatedEvent = {
      eventId: uuidv4(),
      eventType: 'EVENT_UPDATED',
      timestamp: new Date().toISOString(),
      userId,
      calendarEventId,
      changes: eventData.changes,
      metadata: {
        title: eventData.title,
        startTime: eventData.startTime.toISOString(),
        endTime: eventData.endTime.toISOString(),
      },
    };

    await this.publishEvent(
      event,
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      RABBITMQ_CONFIG.ROUTING_KEYS.EVENT_UPDATED
    );
  }

  /**
   * Publish EVENT_REMINDER event
   */
  async publishEventReminder(
    userId: string,
    calendarEventId: string,
    eventData: {
      title: string;
      startTime: Date;
      endTime: Date;
      location?: string;
      minutesUntilStart: number;
    }
  ): Promise<void> {
    const event: EventReminderEvent = {
      eventId: uuidv4(),
      eventType: 'EVENT_REMINDER',
      timestamp: new Date().toISOString(),
      userId,
      calendarEventId,
      title: eventData.title,
      startTime: eventData.startTime.toISOString(),
      minutesUntilStart: eventData.minutesUntilStart,
      metadata: {
        endTime: eventData.endTime.toISOString(),
        location: eventData.location,
      },
    };

    await this.publishEvent(
      event,
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      RABBITMQ_CONFIG.ROUTING_KEYS.EVENT_REMINDER
    );
  }

  /**
   * Publish EVENT_CONFLICT_DETECTED event
   */
  async publishEventConflictDetected(
    userId: string,
    calendarEventId: string,
    eventData: {
      title: string;
      startTime: Date;
      endTime: Date;
      conflictingEventId: string;
      conflictingEventTitle: string;
      overlapMinutes: number;
    }
  ): Promise<void> {
    const event: EventConflictDetectedEvent = {
      eventId: uuidv4(),
      eventType: 'EVENT_CONFLICT_DETECTED',
      timestamp: new Date().toISOString(),
      userId,
      calendarEventId,
      conflictingEventId: eventData.conflictingEventId,
      overlapMinutes: eventData.overlapMinutes,
      metadata: {
        title: eventData.title,
        startTime: eventData.startTime.toISOString(),
        endTime: eventData.endTime.toISOString(),
        conflictingEventTitle: eventData.conflictingEventTitle,
      },
    };

    await this.publishEvent(
      event,
      RABBITMQ_CONFIG.EXCHANGES.TASKS,
      'event.conflict'
    );
  }
}

// Export singleton instance
export const eventPublisher = new EventPublisher();

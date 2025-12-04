/**
 * Task Reminder Consumer
 * Processes task reminder events and sends notifications
 */
import { BaseConsumer } from './base.consumer';
import { RABBITMQ_CONFIG } from '../config/rabbitmq';
import type { TaskDueSoonEvent, EventReminderEvent } from '@speak-sync/event-schemas';

type TaskReminderEvent = TaskDueSoonEvent | EventReminderEvent;

export class TaskReminderConsumer extends BaseConsumer {
  constructor(queueName: string) {
    super({
      queueName,
      prefetchCount: 10,
      retryAttempts: 3,
      retryDelay: 5000,
    });
  }

  /**
   * Process task reminder messages
   */
  protected async processMessage(message: TaskReminderEvent | TaskDueSoonEvent): Promise<void> {
    const { eventType, userId } = message;
    const taskId = eventType === 'TASK_DUE_SOON' ? (message as TaskDueSoonEvent).taskId : (message as EventReminderEvent).calendarEventId;
    const title = message.title;

    console.log(`[INFO] Processing ${eventType} for user: ${userId}, task: ${taskId}`);

    // Determine notification type based on event
    const notificationType = this.getNotificationType(eventType);
    const notificationMessage = this.buildNotificationMessage(message);

    try {
      // Send notification (email, push, or in-app)
      await this.sendNotification({
        userId,
        type: notificationType,
        title: this.getNotificationTitle(eventType),
        message: notificationMessage,
        metadata: {
          taskId,
          eventType,
        },
      });

      console.log(
        `[SUCCESS] Task reminder notification sent for task: ${taskId} (${eventType})`
      );
    } catch (error) {
      console.error(`[ERROR] Failed to send task reminder notification:`, error);
      throw error; // Rethrow to trigger retry logic
    }
  }

  /**
   * Determine notification type based on event type
   */
  private getNotificationType(eventType: string): string {
    if (eventType === 'TASK_DUE_SOON') {
      return 'urgent';
    }
    return 'reminder';
  }

  /**
   * Get notification title based on event type
   */
  private getNotificationTitle(eventType: string): string {
    switch (eventType) {
      case 'TASK_DUE_SOON':
        return 'Task Due Soon!';
      case 'TASK_REMINDER':
        return 'Task Reminder';
      case 'EVENT_REMINDER':
        return 'Event Reminder';
      default:
        return 'Reminder';
    }
  }

  /**
   * Build notification message
   */
  private buildNotificationMessage(
    message: TaskReminderEvent | TaskDueSoonEvent
  ): string {
    const { title, eventType } = message;

    if (eventType === 'TASK_DUE_SOON') {
      const dueDate = (message as TaskDueSoonEvent).dueDate;
      const timeUntilDue = this.getTimeUntilDue(dueDate);
      return `Your task "${title}" is due ${timeUntilDue}. Don't forget to complete it!`;
    }

    if (eventType === 'EVENT_REMINDER') {
      const startTime = (message as EventReminderEvent).startTime;
      return `Reminder: "${title}" is scheduled for ${this.formatDate(startTime)}`;
    }

    return `Reminder: "${title}"`;
  }

  /**
   * Calculate time until due
   */
  private getTimeUntilDue(dueDate: string): string {
    const now = new Date();
    const due = new Date(dueDate);
    const diffMs = due.getTime() - now.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

    if (diffHours < 1) {
      return `in ${diffMinutes} minutes`;
    } else if (diffHours < 24) {
      return `in ${diffHours} hours`;
    } else {
      const diffDays = Math.floor(diffHours / 24);
      return `in ${diffDays} days`;
    }
  }

  /**
   * Format date for display
   */
  private formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  }

  /**
   * Send notification (placeholder for actual notification service)
   */
  private async sendNotification(notification: {
    userId: string;
    type: string;
    title: string;
    message: string;
    metadata: any;
  }): Promise<void> {
    // TODO: Integrate with actual notification service
    // For now, just log the notification
    console.log('[INFO] Sending notification:', {
      userId: notification.userId,
      type: notification.type,
      title: notification.title,
      message: notification.message,
    });

    // Simulate async operation
    await new Promise((resolve) => setTimeout(resolve, 100));

    // In production, this would call:
    // - Email service (nodemailer)
    // - Push notification service (Firebase, OneSignal)
    // - In-app notification via WebSocket
    // - SMS service (Twilio)
  }
}

// Factory function to create task reminder consumers
export function createTaskReminderConsumer(): TaskReminderConsumer {
  return new TaskReminderConsumer(RABBITMQ_CONFIG.QUEUES.TASK_REMINDERS);
}

export function createTaskDueSoonConsumer(): TaskReminderConsumer {
  return new TaskReminderConsumer(RABBITMQ_CONFIG.QUEUES.TASK_DUE_SOON);
}

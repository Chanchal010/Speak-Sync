import { eventPublisher } from '../rabbitmq/index.js';
import prisma from '../prisma.js';

/**
 * Scheduler for task reminders and due soon notifications
 * Runs periodically to check for tasks approaching their due date
 */
class ReminderScheduler {
  private intervalId: NodeJS.Timeout | null = null;
  private isRunning = false;

  /**
   * Start the reminder scheduler
   * @param intervalMinutes - How often to check (default: 15 minutes)
   */
  start(intervalMinutes: number = 15): void {
    if (this.isRunning) {
      console.log('⏰ Reminder scheduler is already running');
      return;
    }

    console.log(`⏰ Starting reminder scheduler (checking every ${intervalMinutes} minutes)`);
    
    // Run immediately on start
    this.checkDueSoonTasks().catch(err => 
      console.error('Error in initial reminder check:', err)
    );

    // Then run periodically
    this.intervalId = setInterval(() => {
      this.checkDueSoonTasks().catch(err =>
        console.error('Error in scheduled reminder check:', err)
      );
    }, intervalMinutes * 60 * 1000);

    this.isRunning = true;
  }

  /**
   * Stop the reminder scheduler
   */
  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
      this.isRunning = false;
      console.log('⏰ Reminder scheduler stopped');
    }
  }

  /**
   * Check for tasks that are due soon (within next 24 hours)
   * and publish TASK_DUE_SOON events
   */
  private async checkDueSoonTasks(): Promise<void> {
    try {
      const now = new Date();
      const next24Hours = new Date(now.getTime() + 24 * 60 * 60 * 1000);

      // Find tasks that are:
      // - Not completed
      // - Not deleted
      // - Have a due date within next 24 hours
      // - Haven't been reminded in the last 12 hours
      const dueSoonTasks = await prisma.task.findMany({
        where: {
          status: {
            not: 'completed',
          },
          deletedAt: null,
          dueDate: {
            gte: now,
            lte: next24Hours,
          },
          // Only send reminder if we haven't sent one recently
          OR: [
            { lastReminderSentAt: null },
            {
              lastReminderSentAt: {
                lt: new Date(now.getTime() - 12 * 60 * 60 * 1000), // 12 hours ago
              },
            },
          ],
        },
        select: {
          id: true,
          userId: true,
          title: true,
          priority: true,
          dueDate: true,
        },
      });

      if (dueSoonTasks.length === 0) {
        console.log('✓ No tasks due soon found');
        return;
      }

      console.log(`📬 Found ${dueSoonTasks.length} tasks due soon, publishing reminders...`);

      // Publish TASK_DUE_SOON event for each task
      for (const task of dueSoonTasks) {
        if (!task.dueDate) continue;

        const hoursUntilDue = Math.round(
          (task.dueDate.getTime() - now.getTime()) / (60 * 60 * 1000)
        );

        try {
          await eventPublisher.publishTaskDueSoon(task.userId, task.id, {
            title: task.title,
            priority: task.priority as 'VI' | 'MI' | 'NI',
            dueDate: task.dueDate,
            hoursUntilDue,
          });

          // Update lastReminderSentAt to prevent duplicate reminders
          await prisma.task.update({
            where: { id: task.id },
            data: { lastReminderSentAt: now },
          });

          console.log(`  ✓ Reminder sent for task: ${task.title} (due in ${hoursUntilDue}h)`);
        } catch (error) {
          console.error(`  ✗ Failed to send reminder for task ${task.id}:`, error);
        }
      }

      console.log(`✅ Processed ${dueSoonTasks.length} task reminders`);
    } catch (error) {
      console.error('❌ Error checking due soon tasks:', error);
      throw error;
    }
  }

  /**
   * Check for upcoming calendar events and publish EVENT_REMINDER events
   * @param minutesBefore - Send reminders this many minutes before event (default: 15)
   */
  async checkUpcomingEvents(minutesBefore: number = 15): Promise<void> {
    try {
      const now = new Date();
      const reminderWindow = new Date(now.getTime() + minutesBefore * 60 * 1000);

      const upcomingEvents = await prisma.event.findMany({
        where: {
          deletedAt: null,
          startTime: {
            gte: now,
            lte: reminderWindow,
          },
          // Only send reminder if we haven't sent one recently
          OR: [
            { lastReminderSentAt: null },
            {
              lastReminderSentAt: {
                lt: new Date(now.getTime() - minutesBefore * 60 * 1000),
              },
            },
          ],
        },
        select: {
          id: true,
          userId: true,
          title: true,
          startTime: true,
          endTime: true,
          location: true,
        },
      });

      if (upcomingEvents.length === 0) {
        console.log('✓ No upcoming events found');
        return;
      }

      console.log(`📅 Found ${upcomingEvents.length} upcoming events, publishing reminders...`);

      for (const event of upcomingEvents) {
        const minutesUntilStart = Math.round(
          (event.startTime.getTime() - now.getTime()) / (60 * 1000)
        );

        try {
          await eventPublisher.publishEventReminder(event.userId, event.id, {
            title: event.title,
            startTime: event.startTime,
            endTime: event.endTime,
            location: event.location || undefined,
            minutesUntilStart,
          });

          // Update lastReminderSentAt
          await prisma.event.update({
            where: { id: event.id },
            data: { lastReminderSentAt: now },
          });

          console.log(`  ✓ Reminder sent for event: ${event.title} (starts in ${minutesUntilStart}min)`);
        } catch (error) {
          console.error(`  ✗ Failed to send reminder for event ${event.id}:`, error);
        }
      }

      console.log(`✅ Processed ${upcomingEvents.length} event reminders`);
    } catch (error) {
      console.error('❌ Error checking upcoming events:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const reminderScheduler = new ReminderScheduler();

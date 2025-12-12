/**
 * Habit Streak Consumer
 * Processes habit streak events (achievements, breaks, milestones)
 */
import { BaseConsumer } from './base.consumer';
import { RABBITMQ_CONFIG } from '../config/rabbitmq';
import type {
  StreakAchievedEvent,
  StreakBrokenEvent,
  MilestoneReachedEvent,
} from '@speak-sync/event-schemas';

type HabitStreakEvent =
  | StreakAchievedEvent
  | StreakBrokenEvent
  | MilestoneReachedEvent;

export class HabitStreakConsumer extends BaseConsumer {
  constructor() {
    super({
      queueName: RABBITMQ_CONFIG.QUEUES.HABIT_STREAKS,
      prefetchCount: 10,
      retryAttempts: 3,
      retryDelay: 5000,
    });
  }

  /**
   * Process habit streak messages
   */
  protected async processMessage(message: HabitStreakEvent): Promise<void> {
    const { eventType, userId, habitId } = message;

    console.log(`[INFO] Processing ${eventType} for user: ${userId}, habit: ${habitId}`);

    try {
      switch (eventType) {
        case 'STREAK_ACHIEVED':
          await this.handleStreakAchieved(message as StreakAchievedEvent);
          break;
        case 'STREAK_BROKEN':
          await this.handleStreakBroken(message as StreakBrokenEvent);
          break;
        case 'MILESTONE_REACHED':
          await this.handleMilestone(message as MilestoneReachedEvent);
          break;
        default:
          console.warn(`[WARNING] Unknown habit event type: ${eventType}`);
      }

      console.log(`[SUCCESS] Habit streak event processed: ${eventType}`);
    } catch (error) {
      console.error(`[ERROR] Failed to process habit streak event:`, error);
      throw error; // Rethrow to trigger retry logic
    }
  }

  /**
   * Handle streak achievement
   */
  private async handleStreakAchieved(event: StreakAchievedEvent): Promise<void> {
    const { userId, habitId, habitType, streakDays } = event;

    console.log(
      `[INFO] Streak achieved: ${habitType} - ${streakDays} days for user ${userId}`
    );

    // Send motivational notification
    await this.sendNotification({
      userId,
      type: 'celebration',
      title: '🔥 Streak Achievement!',
      message: this.getStreakMessage(habitType, streakDays),
      metadata: {
        habitId,
        habitType,
        streakDays,
        eventType: 'STREAK_ACHIEVED',
      },
    });

    // Check for special milestone streaks
    if (this.isSpecialStreak(streakDays)) {
      await this.sendMilestoneNotification(userId, habitType, streakDays);
    }
  }

  /**
   * Handle streak broken
   */
  private async handleStreakBroken(event: StreakBrokenEvent): Promise<void> {
    const { userId, habitId, habitType, previousStreak } = event;

    console.log(
      `[INFO] Streak broken: ${habitType} - was ${previousStreak} days for user ${userId}`
    );

    // Send encouraging message
    await this.sendNotification({
      userId,
      type: 'encouragement',
      title: '💪 Don\'t Give Up!',
      message: this.getEncouragementMessage(habitType, previousStreak),
      metadata: {
        habitId,
        habitType,
        previousStreak,
        eventType: 'STREAK_BROKEN',
      },
    });
  }

  /**
   * Handle milestone achievement
   */
  private async handleMilestone(event: MilestoneReachedEvent): Promise<void> {
    const { userId, habitId, habitType, milestoneType, value, description } = event;

    console.log(
      `[INFO] Milestone reached: ${habitType} - ${milestoneType} ${value} for user ${userId}`
    );

    // Send milestone celebration
    await this.sendNotification({
      userId,
      type: 'milestone',
      title: '🏆 Milestone Reached!',
      message: this.getMilestoneMessage(habitType, milestoneType, value),
      metadata: {
        habitId,
        habitType,
        milestoneType,
        value,
        description,
        eventType: 'MILESTONE_REACHED',
      },
    });

    // Award badge or achievement (placeholder)
    await this.awardBadge(userId, habitId, milestoneType, value);
  }

  /**
   * Get streak achievement message
   */
  private getStreakMessage(habitName: string, streak: number): string {
    const messages = [
      `Amazing! You've maintained "${habitName}" for ${streak} days straight! Keep it up! 🎉`,
      `${streak} days of "${habitName}"! You're building an incredible habit! 💪`,
      `Wow! ${streak} consecutive days of "${habitName}". You're unstoppable! 🚀`,
    ];

    return messages[Math.floor(Math.random() * messages.length)];
  }

  /**
   * Get encouragement message for broken streak
   */
  private getEncouragementMessage(habitName: string, previousStreak: number): string {
    return `Your ${previousStreak}-day streak for "${habitName}" was broken, but don't worry! Every day is a fresh start. You've done it before, and you can do it again! 💪`;
  }

  /**
   * Get milestone message
   */
  private getMilestoneMessage(
    habitName: string,
    milestoneType: string,
    milestoneValue: number
  ): string {
    switch (milestoneType) {
      case 'total_logs':
        return `Incredible! You've logged "${habitName}" ${milestoneValue} times! 🎯`;
      case 'longest_streak':
        return `New record! Your longest streak for "${habitName}" is now ${milestoneValue} days! 🏆`;
      case 'days_active':
        return `Milestone reached! ${milestoneValue} active days with "${habitName}"! 📈`;
      default:
        return `Congratulations! You've reached a milestone with "${habitName}"! 🎉`;
    }
  }

  /**
   * Check if streak is a special milestone (7, 30, 100, 365)
   */
  private isSpecialStreak(streak: number): boolean {
    const milestones = [7, 14, 30, 60, 90, 100, 180, 365];
    return milestones.includes(streak);
  }

  /**
   * Send milestone notification for special streaks
   */
  private async sendMilestoneNotification(
    userId: string,
    habitName: string,
    streak: number
  ): Promise<void> {
    let title = '';
    let emoji = '🎉';

    if (streak === 7) {
      title = 'First Week Complete!';
      emoji = '📅';
    } else if (streak === 30) {
      title = 'One Month Milestone!';
      emoji = '🎯';
    } else if (streak === 100) {
      title = 'Century Club!';
      emoji = '💯';
    } else if (streak === 365) {
      title = 'One Year Anniversary!';
      emoji = '🏆';
    }

    if (title) {
      await this.sendNotification({
        userId,
        type: 'special_milestone',
        title: `${emoji} ${title}`,
        message: `You've maintained "${habitName}" for ${streak} days! This is a major achievement! 🌟`,
        metadata: {
          habitName,
          streak,
          milestoneType: 'streak',
        },
      });
    }
  }

  /**
   * Award badge to user (placeholder)
   */
  private async awardBadge(
    userId: string,
    habitId: string,
    milestoneType: string,
    milestoneValue: number
  ): Promise<void> {
    // TODO: Integrate with badge/achievement system
    console.log(`[INFO] Awarding badge to user ${userId}:`, {
      habitId,
      milestoneType,
      milestoneValue,
    });

    // Simulate async operation
    await new Promise((resolve) => setTimeout(resolve, 50));

    // In production, this would update user achievements in database
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
    console.log('[INFO] Sending habit notification:', {
      userId: notification.userId,
      type: notification.type,
      title: notification.title,
    });

    // Simulate async operation
    await new Promise((resolve) => setTimeout(resolve, 100));

    // In production, this would call notification service
  }
}

// Factory function
export function createHabitStreakConsumer(): HabitStreakConsumer {
  return new HabitStreakConsumer();
}

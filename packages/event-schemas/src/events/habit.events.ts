/**
 * Base Event Interface
 */
export interface BaseHabitEvent {
  eventId: string;
  timestamp: string;
  userId: string;
  metadata?: Record<string, any>;
}

/**
 * Habit Management Events
 */
export interface HabitCreatedEvent extends BaseHabitEvent {
  eventType: 'HABIT_CREATED';
  habitId: string;
  habitType: 'food' | 'exercise' | 'financial' | 'sleep' | 'study' | 'water';
  name: string;
  description?: string;
  targetFrequency?: string;
}

export interface HabitUpdatedEvent extends BaseHabitEvent {
  eventType: 'HABIT_UPDATED';
  habitId: string;
  habitType: string;
  changes: {
    field: string;
    oldValue: any;
    newValue: any;
  }[];
}

export interface HabitDeletedEvent extends BaseHabitEvent {
  eventType: 'HABIT_DELETED';
  habitId: string;
  habitType: string;
  name: string;
}

/**
 * Habit Logging Events
 */
export interface HabitLoggedEvent extends BaseHabitEvent {
  eventType: 'HABIT_LOGGED';
  habitId: string;
  logId: string;
  habitType: 'food' | 'exercise' | 'financial' | 'sleep' | 'study' | 'water';
  data: Record<string, any>;
}

export interface FoodLoggedEvent extends BaseHabitEvent {
  eventType: 'FOOD_LOGGED';
  habitId: string;
  logId: string;
  mealType: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  satisfaction: number;
  emotionalState?: string;
  macros?: {
    protein?: number;
    carbs?: number;
    fats?: number;
  };
}

export interface ExerciseLoggedEvent extends BaseHabitEvent {
  eventType: 'EXERCISE_LOGGED';
  habitId: string;
  logId: string;
  activityType: string;
  duration: number;
  rpe: number; // Rate of Perceived Exertion (1-10)
  postEnergy: number;
}

export interface SleepLoggedEvent extends BaseHabitEvent {
  eventType: 'SLEEP_LOGGED';
  habitId: string;
  logId: string;
  bedtime: string;
  wakeTime: string;
  duration: number;
  quality: number;
  interruptions?: number;
}

export interface StudyLoggedEvent extends BaseHabitEvent {
  eventType: 'STUDY_LOGGED';
  habitId: string;
  logId: string;
  taskId?: string;
  scheduledStart: string;
  actualStart: string;
  duration: number;
  flowState: number;
  stickinessPercentage: number;
}

export interface WaterLoggedEvent extends BaseHabitEvent {
  eventType: 'WATER_LOGGED';
  habitId: string;
  logId: string;
  amount: number;
  urineColor: number; // Armstrong Scale 1-8
  caffeine?: number;
  cognitiveFog?: boolean;
}

/**
 * Habit Streak Events
 */
export interface StreakAchievedEvent extends BaseHabitEvent {
  eventType: 'STREAK_ACHIEVED';
  habitId: string;
  habitType: string;
  streakDays: number;
  milestone: boolean; // true for 7, 14, 21, 30, 60, 90 days
}

export interface StreakBrokenEvent extends BaseHabitEvent {
  eventType: 'STREAK_BROKEN';
  habitId: string;
  habitType: string;
  previousStreak: number;
  daysMissed: number;
}

export interface MilestoneReachedEvent extends BaseHabitEvent {
  eventType: 'MILESTONE_REACHED';
  habitId: string;
  habitType: string;
  milestoneType: 'streak' | 'logs' | 'consistency';
  value: number;
  description: string;
}

/**
 * Habit Reminder Events
 */
export interface HabitReminderEvent extends BaseHabitEvent {
  eventType: 'HABIT_REMINDER';
  habitId: string;
  habitType: string;
  name: string;
  reminderType: 'daily' | 'missed' | 'streak_risk';
  currentStreak?: number;
}

/**
 * Union type for all habit events
 */
export type HabitEvent =
  | HabitCreatedEvent
  | HabitUpdatedEvent
  | HabitDeletedEvent
  | HabitLoggedEvent
  | FoodLoggedEvent
  | ExerciseLoggedEvent
  | SleepLoggedEvent
  | StudyLoggedEvent
  | WaterLoggedEvent
  | StreakAchievedEvent
  | StreakBrokenEvent
  | MilestoneReachedEvent
  | HabitReminderEvent;
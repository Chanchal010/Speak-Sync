export interface HabitLoggedEvent {
  habitId: string;
  userId: string;
  timestamp: Date;
  data: Record<string, any>;
}
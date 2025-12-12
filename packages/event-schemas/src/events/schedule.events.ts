/**
 * Base Event Interface
 */
export interface BaseEvent {
  eventId: string;
  timestamp: string;
  userId: string;
  metadata?: Record<string, any>;
}

/**
 * Task Events
 */
export interface TaskCreatedEvent extends BaseEvent {
  eventType: 'TASK_CREATED';
  taskId: string;
  title: string;
  description?: string;
  priority: 'VI' | 'MI' | 'NI';
  dueDate?: string;
  tags?: string[];
}

export interface TaskCompletedEvent extends BaseEvent {
  eventType: 'TASK_COMPLETED';
  taskId: string;
  title: string;
  completedAt: string;
  timeEstimate?: number;
  actualTime?: number;
}

export interface TaskUpdatedEvent extends BaseEvent {
  eventType: 'TASK_UPDATED';
  taskId: string;
  changes: {
    field: string;
    oldValue: any;
    newValue: any;
  }[];
}

export interface TaskDeletedEvent extends BaseEvent {
  eventType: 'TASK_DELETED';
  taskId: string;
  title: string;
}

export interface TaskDueSoonEvent extends BaseEvent {
  eventType: 'TASK_DUE_SOON';
  taskId: string;
  title: string;
  dueDate: string;
  hoursUntilDue: number;
}

/**
 * Calendar/Event Events
 */
export interface EventCreatedEvent extends BaseEvent {
  eventType: 'EVENT_CREATED';
  calendarEventId: string;
  title: string;
  description?: string;
  startTime: string;
  endTime: string;
  location?: string;
  attendees?: string[];
}

export interface EventUpdatedEvent extends BaseEvent {
  eventType: 'EVENT_UPDATED';
  calendarEventId: string;
  changes: {
    field: string;
    oldValue: any;
    newValue: any;
  }[];
}

export interface EventReminderEvent extends BaseEvent {
  eventType: 'EVENT_REMINDER';
  calendarEventId: string;
  title: string;
  startTime: string;
  minutesUntilStart: number;
}

export interface EventConflictDetectedEvent extends BaseEvent {
  eventType: 'EVENT_CONFLICT_DETECTED';
  calendarEventId: string;
  conflictingEventId: string;
  overlapMinutes: number;
}

/**
 * Union type for all schedule events
 */
export type ScheduleEvent =
  | TaskCreatedEvent
  | TaskCompletedEvent
  | TaskUpdatedEvent
  | TaskDeletedEvent
  | TaskDueSoonEvent
  | EventCreatedEvent
  | EventUpdatedEvent
  | EventReminderEvent
  | EventConflictDetectedEvent;
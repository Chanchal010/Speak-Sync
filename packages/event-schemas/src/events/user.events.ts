/**
 * Base User Event
 */
export interface BaseUserEvent {
  eventId: string;
  timestamp: string;
  userId: string;
  metadata?: Record<string, any>;
}

/**
 * User Authentication Events
 */
export interface UserRegisteredEvent extends BaseUserEvent {
  eventType: 'USER_REGISTERED';
  email: string;
  fullName?: string;
  registrationMethod: 'email' | 'google' | 'github';
  ipAddress?: string;
}

export interface UserLoggedInEvent extends BaseUserEvent {
  eventType: 'USER_LOGGED_IN';
  email: string;
  loginMethod: 'email' | 'google' | 'github';
  ipAddress?: string;
  deviceType?: string;
}

export interface UserLoggedOutEvent extends BaseUserEvent {
  eventType: 'USER_LOGGED_OUT';
  sessionDuration?: number;
}

export interface UserPasswordChangedEvent extends BaseUserEvent {
  eventType: 'USER_PASSWORD_CHANGED';
  email: string;
}

export interface UserEmailVerifiedEvent extends BaseUserEvent {
  eventType: 'USER_EMAIL_VERIFIED';
  email: string;
  verifiedAt: string;
}

/**
 * User Profile Events
 */
export interface UserProfileUpdatedEvent extends BaseUserEvent {
  eventType: 'USER_PROFILE_UPDATED';
  changes: {
    field: string;
    oldValue: any;
    newValue: any;
  }[];
}

export interface UserPreferencesUpdatedEvent extends BaseUserEvent {
  eventType: 'USER_PREFERENCES_UPDATED';
  preferences: Record<string, any>;
}

/**
 * User Account Events
 */
export interface UserAccountDeactivatedEvent extends BaseUserEvent {
  eventType: 'USER_ACCOUNT_DEACTIVATED';
  reason?: string;
  deactivatedAt: string;
}

export interface UserAccountReactivatedEvent extends BaseUserEvent {
  eventType: 'USER_ACCOUNT_REACTIVATED';
  reactivatedAt: string;
}

export interface UserAccountDeletedEvent extends BaseUserEvent {
  eventType: 'USER_ACCOUNT_DELETED';
  email: string;
  deletedAt: string;
  reason?: string;
}

/**
 * Union type for all user events
 */
export type UserEvent =
  | UserRegisteredEvent
  | UserLoggedInEvent
  | UserLoggedOutEvent
  | UserPasswordChangedEvent
  | UserEmailVerifiedEvent
  | UserProfileUpdatedEvent
  | UserPreferencesUpdatedEvent
  | UserAccountDeactivatedEvent
  | UserAccountReactivatedEvent
  | UserAccountDeletedEvent;

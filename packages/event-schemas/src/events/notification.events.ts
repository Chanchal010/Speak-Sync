/**
 * Base Notification Event
 */
export interface BaseNotificationEvent {
  eventId: string;
  timestamp: string;
  userId: string;
  metadata?: Record<string, any>;
}

/**
 * Email Notification Events
 */
export interface EmailNotificationEvent extends BaseNotificationEvent {
  eventType: 'EMAIL_NOTIFICATION';
  notificationId: string;
  recipientEmail: string;
  subject: string;
  template: string;
  templateData: Record<string, any>;
  priority: 'high' | 'normal' | 'low';
}

/**
 * Push Notification Events
 */
export interface PushNotificationEvent extends BaseNotificationEvent {
  eventType: 'PUSH_NOTIFICATION';
  notificationId: string;
  title: string;
  body: string;
  data?: Record<string, any>;
  priority: 'high' | 'normal' | 'low';
}

/**
 * SMS Notification Events
 */
export interface SMSNotificationEvent extends BaseNotificationEvent {
  eventType: 'SMS_NOTIFICATION';
  notificationId: string;
  phoneNumber: string;
  message: string;
}

/**
 * In-App Notification Events
 */
export interface InAppNotificationEvent extends BaseNotificationEvent {
  eventType: 'IN_APP_NOTIFICATION';
  notificationId: string;
  title: string;
  message: string;
  actionUrl?: string;
  iconType?: string;
}

/**
 * Notification Status Events
 */
export interface NotificationSentEvent extends BaseNotificationEvent {
  eventType: 'NOTIFICATION_SENT';
  notificationId: string;
  notificationType: 'email' | 'push' | 'sms' | 'in_app';
  sentAt: string;
  status: 'sent' | 'failed' | 'queued';
  errorMessage?: string;
}

export interface NotificationDeliveredEvent extends BaseNotificationEvent {
  eventType: 'NOTIFICATION_DELIVERED';
  notificationId: string;
  notificationType: 'email' | 'push' | 'sms' | 'in_app';
  deliveredAt: string;
}

export interface NotificationOpenedEvent extends BaseNotificationEvent {
  eventType: 'NOTIFICATION_OPENED';
  notificationId: string;
  notificationType: 'email' | 'push' | 'in_app';
  openedAt: string;
}

/**
 * Union type for all notification events
 */
export type NotificationEvent =
  | EmailNotificationEvent
  | PushNotificationEvent
  | SMSNotificationEvent
  | InAppNotificationEvent
  | NotificationSentEvent
  | NotificationDeliveredEvent
  | NotificationOpenedEvent;

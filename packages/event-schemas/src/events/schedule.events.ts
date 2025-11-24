export interface ScheduleCreatedEvent {
  eventId: string;
  userId: string;
  title: string;
  startTime: Date;
  endTime: Date;
}
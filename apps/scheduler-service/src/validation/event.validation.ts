import { z } from 'zod';

// Base event schema
const eventBaseSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().max(2000).optional().nullable(),
  startTime: z.coerce.date(),
  endTime: z.coerce.date(),
  location: z.string().max(500).optional().nullable(),
  timezone: z.string().default('UTC'),
  isAllDay: z.boolean().default(false),
  colorHex: z.string().regex(/^#[0-9A-F]{6}$/i, 'Invalid hex color').optional().nullable(),
});

// Attendee schema
const attendeeSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1),
  status: z.enum(['pending', 'accepted', 'declined', 'tentative']).optional(),
});

// Reminder schema
const reminderSchema = z.object({
  minutes: z.number().int().positive(),
  type: z.enum(['notification', 'email', 'sms']),
});

// Create event schema (without refinement first)
const createEventSchemaBase = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().max(2000).optional().nullable(),
  startTime: z.coerce.date(),
  endTime: z.coerce.date(),
  location: z.string().max(500).optional().nullable(),
  timezone: z.string().default('UTC'),
  isAllDay: z.boolean().default(false),
  colorHex: z.string().regex(/^#[0-9A-F]{6}$/i, 'Invalid hex color').optional().nullable(),
  attendees: z.array(attendeeSchema).optional(),
  reminders: z.array(reminderSchema).optional(),
  voiceTranscript: z.string().max(5000).optional(),
  eventType: z.string().max(50).optional(),
  estimatedDuration: z.number().int().positive().optional(),
  sentimentScore: z.number().min(-1).max(1).optional(),
  contextMetadata: z.record(z.string(), z.any()).optional(),
});

// Apply refinement
export const createEventSchema = createEventSchemaBase.refine(
  (data) => data.startTime < data.endTime,
  { message: 'End time must be after start time', path: ['endTime'] }
);

// Update event schema
export const updateEventSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  description: z.string().max(2000).optional().nullable(),
  startTime: z.coerce.date().optional(),
  endTime: z.coerce.date().optional(),
  location: z.string().max(500).optional().nullable(),
  timezone: z.string().optional(),
  isAllDay: z.boolean().optional(),
  colorHex: z.string().regex(/^#[0-9A-F]{6}$/i, 'Invalid hex color').optional().nullable(),
  attendees: z.array(attendeeSchema).optional().nullable(),
  reminders: z.array(reminderSchema).optional().nullable(),
  eventType: z.string().max(50).optional().nullable(),
  estimatedDuration: z.number().int().positive().optional().nullable(),
}).refine(
  (data) => {
    if (data.startTime && data.endTime) {
      return data.startTime < data.endTime;
    }
    return true;
  },
  { message: 'End time must be after start time', path: ['endTime'] }
);

// Recurring event schema (merge instead of extend to avoid refinement issue)
const createRecurringEventSchemaBase = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().max(2000).optional().nullable(),
  startTime: z.coerce.date(),
  endTime: z.coerce.date(),
  location: z.string().max(500).optional().nullable(),
  timezone: z.string().default('UTC'),
  isAllDay: z.boolean().default(false),
  colorHex: z.string().regex(/^#[0-9A-F]{6}$/i, 'Invalid hex color').optional().nullable(),
  attendees: z.array(attendeeSchema).optional(),
  reminders: z.array(reminderSchema).optional(),
  voiceTranscript: z.string().max(5000).optional(),
  eventType: z.string().max(50).optional(),
  estimatedDuration: z.number().int().positive().optional(),
  sentimentScore: z.number().min(-1).max(1).optional(),
  contextMetadata: z.record(z.string(), z.any()).optional(),
  recurrenceRule: z.string().regex(
    /^FREQ=(DAILY|WEEKLY|MONTHLY|YEARLY)(;INTERVAL=\d+)?(;BYDAY=(MO|TU|WE|TH|FR|SA|SU)(,(MO|TU|WE|TH|FR|SA|SU))*)?$/,
    'Invalid RRULE format. Use: FREQ=DAILY|WEEKLY|MONTHLY|YEARLY;INTERVAL=n;BYDAY=MO,TU,...'
  ),
  recurrenceEnd: z.coerce.date().optional(),
  exceptionDates: z.array(z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be in YYYY-MM-DD format')).optional(),
});

export const createRecurringEventSchema = createRecurringEventSchemaBase.refine(
  (data) => data.startTime < data.endTime,
  { message: 'End time must be after start time', path: ['endTime'] }
).refine(
  (data) => {
    if (data.recurrenceEnd) {
      return data.recurrenceEnd > data.startTime;
    }
    return true;
  },
  { message: 'Recurrence end must be after start time', path: ['recurrenceEnd'] }
);

// Event filters schema
export const eventFiltersSchema = z.object({
  startDate: z.coerce.date().optional(),
  endDate: z.coerce.date().optional(),
  eventType: z.string().optional(),
  isRecurring: z.coerce.boolean().optional(),
  search: z.string().max(100).optional(),
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(50),
}).refine(
  (data) => {
    if (data.startDate && data.endDate) {
      return data.startDate <= data.endDate;
    }
    return true;
  },
  { message: 'End date must be after or equal to start date', path: ['endDate'] }
);

// Conflict check schema
export const conflictCheckSchema = z.object({
  startTime: z.coerce.date(),
  endTime: z.coerce.date(),
  excludeEventId: z.string().uuid().optional(),
}).refine(
  (data) => data.startTime < data.endTime,
  { message: 'End time must be after start time', path: ['endTime'] }
);

// Free/busy query schema
export const freeBusySchema = z.object({
  startDate: z.coerce.date(),
  endDate: z.coerce.date(),
}).refine(
  (data) => data.startDate < data.endDate,
  { message: 'End date must be after start date', path: ['endDate'] }
);

// Calendar view schema
export const calendarViewSchema = z.object({
  view: z.enum(['day', 'week', 'month', 'agenda']).default('week'),
  date: z.coerce.date().default(() => new Date()),
  timezone: z.string().default('UTC'),
});

// Bulk operations schema
export const bulkDeleteEventsSchema = z.object({
  eventIds: z.array(z.string().uuid()).min(1).max(100),
  deleteRecurringSeries: z.boolean().default(false),
});

export const bulkUpdateEventsSchema = z.object({
  eventIds: z.array(z.string().uuid()).min(1).max(100),
  updates: updateEventSchema,
});

// Event ID param schema
export const eventIdSchema = z.object({
  id: z.string().uuid('Invalid event ID format'),
});

// Types
export type CreateEventInput = z.infer<typeof createEventSchema>;
export type UpdateEventInput = z.infer<typeof updateEventSchema>;
export type CreateRecurringEventInput = z.infer<typeof createRecurringEventSchema>;
export type EventFiltersInput = z.infer<typeof eventFiltersSchema>;
export type ConflictCheckInput = z.infer<typeof conflictCheckSchema>;
export type FreeBusyInput = z.infer<typeof freeBusySchema>;
export type CalendarViewInput = z.infer<typeof calendarViewSchema>;
export type BulkDeleteInput = z.infer<typeof bulkDeleteEventsSchema>;
export type BulkUpdateInput = z.infer<typeof bulkUpdateEventsSchema>;

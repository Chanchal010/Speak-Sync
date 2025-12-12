# Phase 3: Calendar/Events Management - Implementation Guide

**Timeline**: 5-7 days  
**Service**: Scheduler Service (Reusing existing infrastructure)  
**Database**: PostgreSQL with Prisma (Same as Tasks)

---

## 📋 Overview

Building on Phase 2's success, we're adding comprehensive calendar and event management with:
- Full CRUD operations for events
- Timezone-aware scheduling
- Recurring events with RRULE format
- Conflict detection
- AI-ready data tracking for scheduling patterns

---

## 🎯 Features Breakdown

### Day 1-2: Core Event CRUD + Schema

#### Enhanced Prisma Schema (AI-Ready)

```prisma
model Event {
  id          String    @id @default(uuid())
  
  // --- UI FIELDS (Calendar View) ---
  title       String
  description String?
  startTime   DateTime  // In UTC, converted to user timezone on frontend
  endTime     DateTime
  location    String?   // "Office", "Home", "Online - Zoom"
  isAllDay    Boolean   @default(false)
  
  // Timezone & Display
  timezone    String    @default("UTC") // User's timezone when event created
  colorHex    String?   // Custom color for calendar display
  
  // --- RECURRENCE SYSTEM ---
  isRecurring     Boolean   @default(false)
  recurrenceRule  String?   // RRULE format: "FREQ=WEEKLY;BYDAY=MO,WE,FR"
  recurrenceEnd   DateTime? // When recurring series ends
  parentEventId   String?   // If this is instance of recurring series
  exceptionDates  DateTime[] // Dates to skip in recurring series
  
  // --- PARTICIPANTS & COLLABORATION ---
  attendees       Json?     // [{email, name, status: 'accepted'|'declined'|'pending'}]
  organizerId     String?   // For multi-user events (future)
  meetingLink     String?   // Zoom, Google Meet, etc.
  
  // --- AI TRAINING FIELDS (Hidden but Critical) ---
  
  // Voice & Context
  voiceTranscript String?   // "Schedule team meeting tomorrow at 3pm"
  creationContext Json?     // {device, location, time_of_day, weather}
  
  // Scheduling Intelligence
  durationMinutes Int?      // Planned duration
  actualDurationMinutes Int? // How long it actually lasted
  rescheduleCount Int @default(0) // How many times user moved this
  
  // Behavioral Patterns
  attendanceStatus String?  // "attended", "missed", "cancelled"
  completionNotes String?   // Post-event notes
  sentimentScore  Float?    // User's mood during/after event (-1 to 1)
  
  // AI Learning Data
  priorityLevel   String?   // VI/MI/NI (like tasks, for importance)
  conflictCount   Int @default(0) // How many conflicts this event caused
  timePreference  Json?     // {preferred_time: "morning", usual_duration: 45}
  locationPattern Json?     // {most_used: "Office", frequency: 0.7}
  
  // --- RELATIONS & METADATA ---
  userId      String
  user        User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  // Timestamps
  createdAt   DateTime  @default(now())
  updatedAt   DateTime  @updatedAt
  deletedAt   DateTime? // Soft delete preserves training data
  
  @@index([userId])
  @@index([startTime])
  @@index([endTime])
  @@index([isRecurring])
  @@index([parentEventId])
  @@index([userId, startTime, deletedAt]) // Query active events in date range
  @@index([userId, isRecurring]) // Query recurring events
}
```

#### Why This Schema?

**UI Fields** match your wireframe's calendar view:
- Start/end times for scheduling
- All-day event toggle
- Location and meeting links
- Color coding for visual organization

**AI Training Fields** enable:
- Voice-to-event conversion (Whisper → Event)
- Rescheduling pattern analysis
- Time preference learning (morning person vs night owl)
- Meeting effectiveness tracking (attended vs missed)
- Conflict resolution pattern detection
- Location-based scheduling habits

---

### Day 3: Service Layer Implementation

#### Event Service (`src/services/event.service.ts`)

```typescript
import prisma from '../lib/prisma.js';
import { RRule } from 'rrule';
import { zonedTimeToUtc, utcToZonedTime, format } from 'date-fns-tz';

export interface CreateEventDTO {
  title: string;
  description?: string;
  startTime: Date;
  endTime: Date;
  location?: string;
  isAllDay?: boolean;
  timezone?: string;
  colorHex?: string;
  
  // Recurrence
  isRecurring?: boolean;
  recurrenceRule?: string;
  recurrenceEnd?: Date;
  
  // Participants
  attendees?: Array<{email: string; name: string; status?: string}>;
  meetingLink?: string;
  
  // AI Context
  voiceTranscript?: string;
  sentimentScore?: number;
  creationContext?: Record<string, any>;
  priorityLevel?: string;
}

export interface UpdateEventDTO {
  title?: string;
  description?: string | null;
  startTime?: Date;
  endTime?: Date;
  location?: string | null;
  isAllDay?: boolean;
  timezone?: string;
  colorHex?: string | null;
  attendees?: any;
  meetingLink?: string | null;
  attendanceStatus?: string;
  completionNotes?: string | null;
  sentimentScore?: number | null;
}

export interface EventFilters {
  startDate?: Date;
  endDate?: Date;
  isRecurring?: boolean;
  location?: string;
  priorityLevel?: string;
  search?: string;
  page?: number;
  limit?: number;
}

class EventService {
  /**
   * Create a new event
   */
  async createEvent(userId: string, data: CreateEventDTO) {
    // Calculate duration
    const durationMinutes = Math.round(
      (data.endTime.getTime() - data.startTime.getTime()) / 60000
    );
    
    // Auto-suggest priority based on title keywords
    let priorityLevel = data.priorityLevel;
    if (!priorityLevel) {
      const urgentKeywords = ['urgent', 'asap', 'important', 'critical'];
      const titleLower = data.title.toLowerCase();
      priorityLevel = urgentKeywords.some(kw => titleLower.includes(kw)) ? 'VI' : 'MI';
    }
    
    const event = await prisma.event.create({
      data: {
        userId,
        title: data.title,
        description: data.description,
        startTime: data.startTime,
        endTime: data.endTime,
        location: data.location,
        isAllDay: data.isAllDay || false,
        timezone: data.timezone || 'UTC',
        colorHex: data.colorHex,
        isRecurring: data.isRecurring || false,
        recurrenceRule: data.recurrenceRule,
        recurrenceEnd: data.recurrenceEnd,
        attendees: data.attendees as any,
        meetingLink: data.meetingLink,
        voiceTranscript: data.voiceTranscript,
        creationContext: data.creationContext as any,
        sentimentScore: data.sentimentScore,
        priorityLevel,
        durationMinutes,
      },
      include: {
        user: {
          select: { id: true, email: true, name: true }
        }
      }
    });
    
    // If recurring, generate instances (optional - can be done on-demand)
    if (data.isRecurring && data.recurrenceRule) {
      // Future: Generate recurring instances
    }
    
    return event;
  }
  
  /**
   * Get events with filters and pagination
   */
  async getEvents(userId: string, filters: EventFilters = {}) {
    const {
      startDate,
      endDate,
      isRecurring,
      location,
      priorityLevel,
      search,
      page = 1,
      limit = 50
    } = filters;
    
    const where: any = {
      userId,
      deletedAt: null,
    };
    
    // Date range filter (most common for calendar views)
    if (startDate || endDate) {
      where.OR = [
        // Events that start in range
        {
          startTime: {
            ...(startDate && { gte: startDate }),
            ...(endDate && { lte: endDate }),
          }
        },
        // Events that end in range
        {
          endTime: {
            ...(startDate && { gte: startDate }),
            ...(endDate && { lte: endDate }),
          }
        },
        // Events that span the range
        {
          AND: [
            { startTime: { lte: startDate || new Date() } },
            { endTime: { gte: endDate || new Date() } }
          ]
        }
      ];
    }
    
    if (isRecurring !== undefined) {
      where.isRecurring = isRecurring;
    }
    
    if (location) {
      where.location = { contains: location, mode: 'insensitive' };
    }
    
    if (priorityLevel) {
      where.priorityLevel = priorityLevel;
    }
    
    if (search) {
      where.OR = [
        { title: { contains: search, mode: 'insensitive' } },
        { description: { contains: search, mode: 'insensitive' } },
        { location: { contains: search, mode: 'insensitive' } }
      ];
    }
    
    const [events, total] = await Promise.all([
      prisma.event.findMany({
        where,
        orderBy: { startTime: 'asc' },
        skip: (page - 1) * limit,
        take: limit,
        include: {
          user: {
            select: { id: true, email: true, name: true }
          }
        }
      }),
      prisma.event.count({ where })
    ]);
    
    return {
      events,
      pagination: {
        page,
        limit,
        totalPages: Math.ceil(total / limit),
        totalItems: total
      }
    };
  }
  
  /**
   * Check for scheduling conflicts
   */
  async checkConflicts(userId: string, startTime: Date, endTime: Date, excludeEventId?: string) {
    const conflicts = await prisma.event.findMany({
      where: {
        userId,
        deletedAt: null,
        id: excludeEventId ? { not: excludeEventId } : undefined,
        OR: [
          // New event starts during existing event
          {
            AND: [
              { startTime: { lte: startTime } },
              { endTime: { gt: startTime } }
            ]
          },
          // New event ends during existing event
          {
            AND: [
              { startTime: { lt: endTime } },
              { endTime: { gte: endTime } }
            ]
          },
          // New event completely contains existing event
          {
            AND: [
              { startTime: { gte: startTime } },
              { endTime: { lte: endTime } }
            ]
          }
        ]
      },
      select: {
        id: true,
        title: true,
        startTime: true,
        endTime: true,
        location: true
      }
    });
    
    return conflicts;
  }
  
  /**
   * Update event and track changes for AI
   */
  async updateEvent(userId: string, eventId: string, data: UpdateEventDTO) {
    const existingEvent = await prisma.event.findFirst({
      where: { id: eventId, userId, deletedAt: null }
    });
    
    if (!existingEvent) {
      throw new Error('Event not found');
    }
    
    // Track rescheduling
    let rescheduleCount = existingEvent.rescheduleCount;
    if (data.startTime && data.startTime.getTime() !== existingEvent.startTime.getTime()) {
      rescheduleCount += 1;
    }
    
    // Update actual duration if attendance marked
    let actualDurationMinutes = existingEvent.actualDurationMinutes;
    if (data.attendanceStatus === 'attended' && !actualDurationMinutes) {
      actualDurationMinutes = existingEvent.durationMinutes;
    }
    
    const event = await prisma.event.update({
      where: { id: eventId },
      data: {
        ...data,
        rescheduleCount,
        actualDurationMinutes,
        updatedAt: new Date(),
      },
      include: {
        user: {
          select: { id: true, email: true, name: true }
        }
      }
    });
    
    return event;
  }
  
  /**
   * Get event statistics for AI insights
   */
  async getEventStats(userId: string) {
    const [totalEvents, attendedEvents, missedEvents, avgDuration] = await Promise.all([
      prisma.event.count({
        where: { userId, deletedAt: null }
      }),
      prisma.event.count({
        where: { userId, deletedAt: null, attendanceStatus: 'attended' }
      }),
      prisma.event.count({
        where: { userId, deletedAt: null, attendanceStatus: 'missed' }
      }),
      prisma.event.aggregate({
        where: { userId, deletedAt: null, actualDurationMinutes: { not: null } },
        _avg: { actualDurationMinutes: true }
      })
    ]);
    
    // Get time preferences (morning vs afternoon vs evening)
    const timeDistribution = await prisma.$queryRaw`
      SELECT 
        CASE 
          WHEN EXTRACT(HOUR FROM "startTime") < 12 THEN 'morning'
          WHEN EXTRACT(HOUR FROM "startTime") < 18 THEN 'afternoon'
          ELSE 'evening'
        END as time_period,
        COUNT(*) as count
      FROM "Event"
      WHERE "userId" = ${userId} AND "deletedAt" IS NULL
      GROUP BY time_period
    `;
    
    return {
      totalEvents,
      attendedEvents,
      missedEvents,
      attendanceRate: totalEvents > 0 ? (attendedEvents / totalEvents) * 100 : 0,
      averageDurationMinutes: avgDuration._avg.actualDurationMinutes || 0,
      timePreferences: timeDistribution
    };
  }
  
  /**
   * Soft delete event (preserve AI training data)
   */
  async deleteEvent(userId: string, eventId: string) {
    const event = await prisma.event.findFirst({
      where: { id: eventId, userId, deletedAt: null }
    });
    
    if (!event) {
      throw new Error('Event not found');
    }
    
    await prisma.event.update({
      where: { id: eventId },
      data: { deletedAt: new Date() }
    });
  }
}

export const eventService = new EventService();
```

---

### Day 4: Validation & Controllers

#### Validation Schema (`src/validation/event.validation.ts`)

```typescript
import { z } from 'zod';

export const createEventSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title too long'),
  description: z.string().max(2000, 'Description too long').optional(),
  startTime: z.string().datetime().or(z.date()),
  endTime: z.string().datetime().or(z.date()),
  location: z.string().max(200).optional(),
  isAllDay: z.boolean().optional(),
  timezone: z.string().optional(),
  colorHex: z.string().regex(/^#[0-9A-F]{6}$/i, 'Invalid hex color').optional(),
  
  // Recurrence
  isRecurring: z.boolean().optional(),
  recurrenceRule: z.string().max(500).optional(),
  recurrenceEnd: z.string().datetime().optional().or(z.date().optional()),
  
  // Participants
  attendees: z.array(z.object({
    email: z.string().email(),
    name: z.string(),
    status: z.enum(['accepted', 'declined', 'pending']).optional()
  })).optional(),
  meetingLink: z.string().url().optional(),
  
  // AI Context
  voiceTranscript: z.string().max(1000).optional(),
  sentimentScore: z.number().min(-1).max(1).optional(),
  creationContext: z.record(z.string(), z.any()).optional(),
  priorityLevel: z.enum(['VI', 'MI', 'NI']).optional(),
}).refine(data => {
  // Validate end time is after start time
  const start = new Date(data.startTime);
  const end = new Date(data.endTime);
  return end > start;
}, {
  message: 'End time must be after start time',
  path: ['endTime']
});

export const updateEventSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  description: z.string().max(2000).optional().nullable(),
  startTime: z.string().datetime().optional().or(z.date().optional()),
  endTime: z.string().datetime().optional().or(z.date().optional()),
  location: z.string().max(200).optional().nullable(),
  isAllDay: z.boolean().optional(),
  timezone: z.string().optional(),
  colorHex: z.string().regex(/^#[0-9A-F]{6}$/i).optional().nullable(),
  attendees: z.any().optional(),
  meetingLink: z.string().url().optional().nullable(),
  attendanceStatus: z.enum(['attended', 'missed', 'cancelled']).optional(),
  completionNotes: z.string().max(1000).optional().nullable(),
  sentimentScore: z.number().min(-1).max(1).optional().nullable(),
});

export const eventFiltersSchema = z.object({
  startDate: z.string().datetime().optional().or(z.date().optional()),
  endDate: z.string().datetime().optional().or(z.date().optional()),
  isRecurring: z.string().transform(val => val === 'true').optional(),
  location: z.string().max(100).optional(),
  priorityLevel: z.enum(['VI', 'MI', 'NI']).optional(),
  search: z.string().max(100).optional(),
  page: z.string().regex(/^\d+$/).transform(Number).optional(),
  limit: z.string().regex(/^\d+$/).transform(Number).optional(),
});

export const conflictCheckSchema = z.object({
  startTime: z.string().datetime().or(z.date()),
  endTime: z.string().datetime().or(z.date()),
  excludeEventId: z.string().uuid().optional(),
});

export const eventIdSchema = z.object({
  id: z.string().uuid('Invalid event ID'),
});
```

---

### Day 5-6: API Routes & Testing

#### Routes (`src/routes/api/events.routes.ts`)

```typescript
import { Router } from 'express';
import { eventController } from '../../controllers/event.controller.js';
import { extractUser } from '../../middleware/auth.middleware.js';

const router = Router();

// Apply auth middleware to all routes
router.use(extractUser);

// Event CRUD
router.post('/', eventController.createEvent.bind(eventController));
router.get('/', eventController.getEvents.bind(eventController));
router.get('/stats', eventController.getEventStats.bind(eventController));
router.post('/check-conflicts', eventController.checkConflicts.bind(eventController));
router.get('/:id', eventController.getEventById.bind(eventController));
router.put('/:id', eventController.updateEvent.bind(eventController));
router.delete('/:id', eventController.deleteEvent.bind(eventController));

export default router;
```

#### Postman Collection Updates

Add new folder "📅 Events" with requests:
- Create Event (basic)
- Create Event (with voice context)
- Create All-Day Event
- Create Recurring Event
- Get Events (date range)
- Check Conflicts
- Update Event
- Mark Event Attended
- Get Event Statistics
- Delete Event

---

### Day 7: Recurring Events & Polish

#### Recurring Event Logic

Use `rrule` library for standard recurrence patterns:

```typescript
import { RRule, RRuleSet, rrulestr } from 'rrule';

// Example: Create weekly meeting every Monday at 10am
const rule = new RRule({
  freq: RRule.WEEKLY,
  byweekday: [RRule.MO],
  dtstart: new Date(2025, 0, 6, 10, 0), // Jan 6, 2025 10:00am
  until: new Date(2025, 11, 31) // Until end of year
});

// Generate occurrences
const occurrences = rule.all();
```

Store as string: `"FREQ=WEEKLY;BYDAY=MO;UNTIL=20251231T000000Z"`

---

## 📊 API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/events` | Create event |
| GET | `/api/events` | List events (with date range) |
| GET | `/api/events/stats` | Get event statistics |
| POST | `/api/events/check-conflicts` | Check scheduling conflicts |
| GET | `/api/events/:id` | Get single event |
| PUT | `/api/events/:id` | Update event |
| DELETE | `/api/events/:id` | Soft delete event |

---

## 🧪 Testing Checklist

- [ ] Create simple event
- [ ] Create all-day event
- [ ] Create recurring event (weekly)
- [ ] Get events for date range (week view)
- [ ] Get events for date range (month view)
- [ ] Check conflicts - should detect overlaps
- [ ] Update event (reschedule)
- [ ] Mark event as attended
- [ ] Get event statistics
- [ ] Delete event (soft delete)
- [ ] Verify AI fields are captured
- [ ] Test timezone conversions

---

## 🤖 AI Training Data Examples

### Example 1: Voice-to-Event
```json
{
  "title": "Team standup",
  "startTime": "2025-12-04T10:00:00Z",
  "endTime": "2025-12-04T10:15:00Z",
  "voiceTranscript": "Schedule team standup tomorrow at 10am",
  "creationContext": {
    "device": "mobile",
    "location": "home",
    "time_of_day": "evening"
  },
  "sentimentScore": 0.2
}
```

### Example 2: Rescheduling Pattern
```json
{
  "rescheduleCount": 3,
  "timePreference": {
    "original_hour": 9,
    "preferred_hour": 10,
    "reason": "user_always_reschedules_morning_meetings"
  }
}
```

### Example 3: Meeting Effectiveness
```json
{
  "durationMinutes": 60,
  "actualDurationMinutes": 45,
  "attendanceStatus": "attended",
  "completionNotes": "Productive meeting, all agenda items covered",
  "sentimentScore": 0.8
}
```

---

## 🚀 Integration Points

### With Task System
- Link tasks to calendar events
- "Prepare for meeting" task → Meeting event
- Task due date → Calendar reminder

### With AI Brain (Phase 6)
- "Schedule meeting with John" → Check calendar, suggest times
- "When am I free tomorrow?" → Query events, return free slots
- "How productive were my meetings this week?" → Analyze attendance + sentiment

### With RabbitMQ (Phase 5)
- EVENT_CREATED → Send email invites
- EVENT_REMINDER → 15 min before notification
- EVENT_RESCHEDULED → Notify attendees

---

## 📈 Success Metrics

- [ ] Can create/update/delete events
- [ ] Conflict detection works correctly
- [ ] Recurring events generate properly
- [ ] Timezone conversions accurate
- [ ] API response time < 300ms (p95)
- [ ] All AI training fields populated
- [ ] Postman collection 100% passing

---

## 🎯 Future Enhancements (Phase 6+)

1. **Smart Scheduling**
   - AI suggests best meeting times based on patterns
   - Detects preferred meeting times per person
   - Recommends meeting duration based on topic

2. **Calendar Sync**
   - Google Calendar integration
   - Outlook Calendar sync
   - iCal export

3. **Advanced Recurrence**
   - "Last Friday of every month"
   - "Every other Tuesday"
   - Business days only

4. **Collaborative Features**
   - Multiple attendees with RSVP
   - Shared calendars
   - Meeting polls (FindTime-like)

---

**Ready to implement?** Start with Day 1: Enhanced schema migration! 🚀

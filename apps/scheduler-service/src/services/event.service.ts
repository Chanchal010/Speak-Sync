import prisma from '../lib/prisma.js';
import type { Prisma } from '@prisma/client';
import { addDays, addWeeks, addMonths, addYears, parseISO, isBefore, isAfter, isWithinInterval } from 'date-fns';
import { formatInTimeZone, toZonedTime } from 'date-fns-tz';

export interface CreateEventDTO {
  title: string;
  description?: string | null;
  startTime: Date;
  endTime: Date;
  location?: string | null;
  timezone?: string;
  isAllDay?: boolean;
  colorHex?: string | null;
  attendees?: Array<{ email: string; name: string; status?: string }>;
  reminders?: Array<{ minutes: number; type: string }>;
  voiceTranscript?: string;
  eventType?: string;
  estimatedDuration?: number;
  sentimentScore?: number;
  contextMetadata?: Record<string, any>;
}

export interface UpdateEventDTO {
  title?: string;
  description?: string | null;
  startTime?: Date;
  endTime?: Date;
  location?: string | null;
  timezone?: string;
  isAllDay?: boolean;
  colorHex?: string | null;
  attendees?: Array<{ email: string; name: string; status?: string }> | null;
  reminders?: Array<{ minutes: number; type: string }> | null;
  eventType?: string | null;
  estimatedDuration?: number | null;
}

export interface RecurringEventDTO extends CreateEventDTO {
  recurrenceRule: string; // RRULE format
  recurrenceEnd?: Date;
  exceptionDates?: string[];
}

export interface EventFilters {
  startDate?: Date;
  endDate?: Date;
  eventType?: string;
  isRecurring?: boolean;
  search?: string;
  page?: number;
  limit?: number;
}

export interface ConflictCheck {
  startTime: Date;
  endTime: Date;
  excludeEventId?: string;
}

class EventService {
  /**
   * Create a single event
   */
  async createEvent(userId: string, data: CreateEventDTO) {
    // Validate time range
    if (data.startTime >= data.endTime) {
      throw new Error('End time must be after start time');
    }

    // Check for conflicts
    const conflicts = await this.checkConflicts(userId, {
      startTime: data.startTime,
      endTime: data.endTime,
    });

    const event = await prisma.event.create({
      data: {
        userId,
        title: data.title,
        description: data.description,
        startTime: data.startTime,
        endTime: data.endTime,
        location: data.location,
        timezone: data.timezone || 'UTC',
        isAllDay: data.isAllDay || false,
        colorHex: data.colorHex,
        attendees: data.attendees as any,
        reminders: data.reminders as any,
        voiceTranscript: data.voiceTranscript,
        eventType: data.eventType,
        estimatedDuration: data.estimatedDuration,
        sentimentScore: data.sentimentScore,
        contextMetadata: data.contextMetadata as any,
        conflictResolutions: conflicts.length > 0 ? [{ 
          detectedAt: new Date(), 
          conflictCount: conflicts.length,
          conflictIds: conflicts.map(c => c.id)
        }] as any : undefined,
      },
    });

    return { event, conflicts };
  }

  /**
   * Create recurring event series
   */
  async createRecurringEvent(userId: string, data: RecurringEventDTO) {
    // Validate recurrence rule
    if (!data.recurrenceRule) {
      throw new Error('Recurrence rule is required for recurring events');
    }

    // Create parent event
    const parentEvent = await prisma.event.create({
      data: {
        userId,
        title: data.title,
        description: data.description,
        startTime: data.startTime,
        endTime: data.endTime,
        location: data.location,
        timezone: data.timezone || 'UTC',
        isAllDay: data.isAllDay || false,
        colorHex: data.colorHex,
        isRecurring: true,
        recurrenceRule: data.recurrenceRule,
        recurrenceEnd: data.recurrenceEnd,
        exceptionDates: data.exceptionDates as any,
        attendees: data.attendees as any,
        reminders: data.reminders as any,
        voiceTranscript: data.voiceTranscript,
        eventType: data.eventType,
        estimatedDuration: data.estimatedDuration,
        sentimentScore: data.sentimentScore,
        contextMetadata: data.contextMetadata as any,
      },
    });

    // Generate occurrences (next 90 days by default)
    const occurrences = this.generateRecurrenceOccurrences(
      data.startTime,
      data.endTime,
      data.recurrenceRule,
      data.recurrenceEnd || addDays(new Date(), 90),
      data.exceptionDates
    );

    // Create individual occurrences
    const createdOccurrences = await Promise.all(
      occurrences.map((occurrence) =>
        prisma.event.create({
          data: {
            userId,
            title: data.title,
            description: data.description,
            startTime: occurrence.start,
            endTime: occurrence.end,
            location: data.location,
            timezone: data.timezone || 'UTC',
            isAllDay: data.isAllDay || false,
            colorHex: data.colorHex,
            parentEventId: parentEvent.id,
            attendees: data.attendees as any,
            reminders: data.reminders as any,
            eventType: data.eventType,
          },
        })
      )
    );

    return { parentEvent, occurrences: createdOccurrences };
  }

  /**
   * Generate recurrence occurrences based on RRULE
   */
  private generateRecurrenceOccurrences(
    startTime: Date,
    endTime: Date,
    rule: string,
    until: Date,
    exceptions?: string[]
  ): Array<{ start: Date; end: Date }> {
    const occurrences: Array<{ start: Date; end: Date }> = [];
    const duration = endTime.getTime() - startTime.getTime();
    
    // Parse simple RRULE (FREQ=DAILY/WEEKLY/MONTHLY/YEARLY;INTERVAL=n)
    const ruleMatch = rule.match(/FREQ=(DAILY|WEEKLY|MONTHLY|YEARLY)(?:;INTERVAL=(\d+))?/);
    if (!ruleMatch) {
      throw new Error('Invalid recurrence rule format');
    }

    const freq = ruleMatch[1];
    const interval = parseInt(ruleMatch[2] || '1');
    
    let currentStart = startTime;
    const exceptionSet = new Set(exceptions || []);

    while (isBefore(currentStart, until)) {
      const dateStr = currentStart.toISOString().split('T')[0];
      
      if (!exceptionSet.has(dateStr)) {
        occurrences.push({
          start: new Date(currentStart),
          end: new Date(currentStart.getTime() + duration),
        });
      }

      // Calculate next occurrence
      switch (freq) {
        case 'DAILY':
          currentStart = addDays(currentStart, interval);
          break;
        case 'WEEKLY':
          currentStart = addWeeks(currentStart, interval);
          break;
        case 'MONTHLY':
          currentStart = addMonths(currentStart, interval);
          break;
        case 'YEARLY':
          currentStart = addYears(currentStart, interval);
          break;
      }
    }

    return occurrences.slice(0, 365); // Max 1 year of occurrences
  }

  /**
   * Get events with filters
   */
  async getEvents(userId: string, filters: EventFilters = {}) {
    const {
      startDate,
      endDate,
      eventType,
      isRecurring,
      search,
      page = 1,
      limit = 50,
    } = filters;

    const where: Prisma.EventWhereInput = {
      userId,
      deletedAt: null,
      ...(startDate && endDate && {
        OR: [
          // Events that start within range
          {
            startTime: { gte: startDate, lte: endDate },
          },
          // Events that end within range
          {
            endTime: { gte: startDate, lte: endDate },
          },
          // Events that span the entire range
          {
            startTime: { lte: startDate },
            endTime: { gte: endDate },
          },
        ],
      }),
      ...(eventType && { eventType }),
      ...(isRecurring !== undefined && { 
        isRecurring,
        parentEventId: null, // Only show parent recurring events, not instances
      }),
      ...(search && {
        OR: [
          { title: { contains: search, mode: 'insensitive' } },
          { description: { contains: search, mode: 'insensitive' } },
          { location: { contains: search, mode: 'insensitive' } },
        ],
      }),
    };

    const [events, total] = await Promise.all([
      prisma.event.findMany({
        where,
        orderBy: { startTime: 'asc' },
        skip: (page - 1) * limit,
        take: limit,
      }),
      prisma.event.count({ where }),
    ]);

    return {
      events,
      pagination: {
        page,
        limit,
        totalPages: Math.ceil(total / limit),
        totalItems: total,
      },
    };
  }

  /**
   * Get event by ID
   */
  async getEventById(userId: string, eventId: string) {
    const event = await prisma.event.findFirst({
      where: {
        id: eventId,
        userId,
        deletedAt: null,
      },
    });

    if (!event) {
      throw new Error('Event not found');
    }

    // If it's a recurring event instance, also fetch parent
    if (event.parentEventId) {
      const parent = await prisma.event.findUnique({
        where: { id: event.parentEventId },
      });
      return { event, parent };
    }

    // If it's a parent recurring event, fetch upcoming occurrences
    if (event.isRecurring) {
      const occurrences = await prisma.event.findMany({
        where: {
          parentEventId: event.id,
          startTime: { gte: new Date() },
          deletedAt: null,
        },
        orderBy: { startTime: 'asc' },
        take: 10,
      });
      return { event, occurrences };
    }

    return { event };
  }

  /**
   * Update event
   */
  async updateEvent(userId: string, eventId: string, data: UpdateEventDTO) {
    const existingEvent = await prisma.event.findFirst({
      where: { id: eventId, userId, deletedAt: null },
    });

    if (!existingEvent) {
      throw new Error('Event not found');
    }

    // Validate time range if both provided
    if (data.startTime && data.endTime && data.startTime >= data.endTime) {
      throw new Error('End time must be after start time');
    }

    // Track rescheduling
    const isRescheduled = 
      (data.startTime && data.startTime.getTime() !== existingEvent.startTime.getTime()) ||
      (data.endTime && data.endTime.getTime() !== existingEvent.endTime.getTime());

    const event = await prisma.event.update({
      where: { id: eventId },
      data: {
        ...data,
        attendees: data.attendees as any,
        reminders: data.reminders as any,
        ...(isRescheduled && {
          rescheduleCount: { increment: 1 },
        }),
        updatedAt: new Date(),
      },
    });

    return event;
  }

  /**
   * Delete event (soft delete)
   */
  async deleteEvent(userId: string, eventId: string, deleteAll: boolean = false) {
    const event = await prisma.event.findFirst({
      where: { id: eventId, userId, deletedAt: null },
    });

    if (!event) {
      throw new Error('Event not found');
    }

    // If deleting a recurring event series
    if (deleteAll && event.isRecurring && !event.parentEventId) {
      // Delete all occurrences
      await prisma.event.updateMany({
        where: {
          OR: [
            { id: eventId },
            { parentEventId: eventId },
          ],
        },
        data: { deletedAt: new Date() },
      });
      return { deleted: 'series' };
    }

    // Delete single event
    await prisma.event.update({
      where: { id: eventId },
      data: { deletedAt: new Date() },
    });

    return { deleted: 'single' };
  }

  /**
   * Check for schedule conflicts
   */
  async checkConflicts(userId: string, check: ConflictCheck) {
    const conflicts = await prisma.event.findMany({
      where: {
        userId,
        deletedAt: null,
        id: check.excludeEventId ? { not: check.excludeEventId } : undefined,
        OR: [
          // New event starts during existing event
          {
            startTime: { lte: check.startTime },
            endTime: { gt: check.startTime },
          },
          // New event ends during existing event
          {
            startTime: { lt: check.endTime },
            endTime: { gte: check.endTime },
          },
          // New event completely contains existing event
          {
            startTime: { gte: check.startTime },
            endTime: { lte: check.endTime },
          },
        ],
      },
    });

    return conflicts;
  }

  /**
   * Get free/busy time slots for a date range
   */
  async getFreeBusySlots(userId: string, startDate: Date, endDate: Date) {
    const events = await prisma.event.findMany({
      where: {
        userId,
        deletedAt: null,
        startTime: { gte: startDate },
        endTime: { lte: endDate },
      },
      orderBy: { startTime: 'asc' },
      select: {
        id: true,
        title: true,
        startTime: true,
        endTime: true,
      },
    });

    return {
      busySlots: events.map(e => ({
        id: e.id,
        title: e.title,
        start: e.startTime,
        end: e.endTime,
      })),
      totalBusyMinutes: events.reduce((acc, e) => 
        acc + (e.endTime.getTime() - e.startTime.getTime()) / (1000 * 60), 0
      ),
    };
  }

  /**
   * Get event statistics for AI training
   */
  async getEventStats(userId: string) {
    const events = await prisma.event.findMany({
      where: { userId, deletedAt: null },
      select: {
        eventType: true,
        startTime: true,
        endTime: true,
        rescheduleCount: true,
        attendancePattern: true,
        preferredTimeSlots: true,
      },
    });

    // Calculate patterns
    const eventTypeDistribution = events.reduce((acc: Record<string, number>, e) => {
      const type = e.eventType || 'other';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {});

    const avgRescheduleCount = events.reduce((sum, e) => sum + e.rescheduleCount, 0) / events.length || 0;

    // Time preference analysis
    const timePreferences = events.reduce((acc: Record<string, number>, e) => {
      const hour = e.startTime.getHours();
      const period = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening';
      acc[period] = (acc[period] || 0) + 1;
      return acc;
    }, {});

    return {
      totalEvents: events.length,
      eventTypeDistribution,
      avgRescheduleCount: Math.round(avgRescheduleCount * 100) / 100,
      timePreferences,
    };
  }
}

export const eventService = new EventService();

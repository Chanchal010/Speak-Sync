import type { Request, Response } from 'express';
import { eventService } from '../services/event.service.js';
import {
  createEventSchema,
  updateEventSchema,
  createRecurringEventSchema,
  eventFiltersSchema,
  conflictCheckSchema,
  freeBusySchema,
  bulkDeleteEventsSchema,
  bulkUpdateEventsSchema,
  eventIdSchema,
} from '../validation/event.validation.js';

class EventController {
  /**
   * Create a single event
   * POST /api/events
   */
  async createEvent(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.headers['x-user-id'] as string;
      if (!userId) {
        res.status(401).json({ error: 'User ID is required' });
        return;
      }

      const validatedData = createEventSchema.parse(req.body);
      const result = await eventService.createEvent(userId, validatedData);

      res.status(201).json({
        success: true,
        data: result.event,
        warnings: result.conflicts.length > 0 ? {
          message: 'This event conflicts with existing events',
          conflicts: result.conflicts.map(c => ({
            id: c.id,
            title: c.title,
            startTime: c.startTime,
            endTime: c.endTime,
          })),
        } : undefined,
      });
    } catch (error: any) {
      console.error('Create event error:', error);
      res.status(400).json({
        success: false,
        error: error.message || 'Failed to create event',
        details: error.errors || undefined,
      });
    }
  }

  /**
   * Create recurring event
   * POST /api/events/recurring
   */
  async createRecurringEvent(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.headers['x-user-id'] as string;
      if (!userId) {
        res.status(401).json({ error: 'User ID is required' });
        return;
      }

      const validatedData = createRecurringEventSchema.parse(req.body);
      const result = await eventService.createRecurringEvent(userId, validatedData);

      res.status(201).json({
        success: true,
        data: {
          parentEvent: result.parentEvent,
          occurrencesCreated: result.occurrences.length,
          nextOccurrences: result.occurrences.slice(0, 5).map(o => ({
            id: o.id,
            startTime: o.startTime,
            endTime: o.endTime,
          })),
        },
      });
    } catch (error: any) {
      console.error('Create recurring event error:', error);
      res.status(400).json({
        success: false,
        error: error.message || 'Failed to create recurring event',
        details: error.errors || undefined,
      });
    }
  }

  /**
   * Get events with filters
   * GET /api/events
   */
  async getEvents(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.headers['x-user-id'] as string;
      if (!userId) {
        res.status(401).json({ error: 'User ID is required' });
        return;
      }

      const filters = eventFiltersSchema.parse(req.query);
      const result = await eventService.getEvents(userId, filters);

      res.status(200).json({
        success: true,
        data: result.events,
        pagination: result.pagination,
      });
    } catch (error: any) {
      console.error('Get events error:', error);
      res.status(400).json({
        success: false,
        error: error.message || 'Failed to fetch events',
        details: error.errors || undefined,
      });
    }
  }

  /**
   * Get single event by ID
   * GET /api/events/:id
   */
  async getEventById(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.headers['x-user-id'] as string;
      if (!userId) {
        res.status(401).json({ error: 'User ID is required' });
        return;
      }

      const { id } = eventIdSchema.parse(req.params);
      const result = await eventService.getEventById(userId, id);

      res.status(200).json({
        success: true,
        data: result,
      });
    } catch (error: any) {
      console.error('Get event error:', error);
      const statusCode = error.message === 'Event not found' ? 404 : 400;
      res.status(statusCode).json({
        success: false,
        error: error.message || 'Failed to fetch event',
        details: error.errors || undefined,
      });
    }
  }

  /**
   * Update event
   * PUT /api/events/:id
   */
  async updateEvent(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.headers['x-user-id'] as string;
      if (!userId) {
        res.status(401).json({ error: 'User ID is required' });
        return;
      }

      const { id } = eventIdSchema.parse(req.params);
      const validatedData = updateEventSchema.parse(req.body);
      
      const event = await eventService.updateEvent(userId, id, validatedData);

      res.status(200).json({
        success: true,
        data: event,
      });
    } catch (error: any) {
      console.error('Update event error:', error);
      const statusCode = error.message === 'Event not found' ? 404 : 400;
      res.status(statusCode).json({
        success: false,
        error: error.message || 'Failed to update event',
        details: error.errors || undefined,
      });
    }
  }

  /**
   * Delete event
   * DELETE /api/events/:id
   */
  async deleteEvent(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.headers['x-user-id'] as string;
      if (!userId) {
        res.status(401).json({ error: 'User ID is required' });
        return;
      }

      const { id } = eventIdSchema.parse(req.params);
      const deleteAll = req.query.deleteAll === 'true';

      const result = await eventService.deleteEvent(userId, id, deleteAll);

      res.status(200).json({
        success: true,
        message: result.deleted === 'series' 
          ? 'Recurring event series deleted successfully'
          : 'Event deleted successfully',
      });
    } catch (error: any) {
      console.error('Delete event error:', error);
      const statusCode = error.message === 'Event not found' ? 404 : 400;
      res.status(statusCode).json({
        success: false,
        error: error.message || 'Failed to delete event',
      });
    }
  }

  /**
   * Check schedule conflicts
   * POST /api/events/conflicts
   */
  async checkConflicts(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.headers['x-user-id'] as string;
      if (!userId) {
        res.status(401).json({ error: 'User ID is required' });
        return;
      }

      const validatedData = conflictCheckSchema.parse(req.body);
      const conflicts = await eventService.checkConflicts(userId, validatedData);

      res.status(200).json({
        success: true,
        data: {
          hasConflicts: conflicts.length > 0,
          conflictCount: conflicts.length,
          conflicts: conflicts.map(c => ({
            id: c.id,
            title: c.title,
            startTime: c.startTime,
            endTime: c.endTime,
            location: c.location,
          })),
        },
      });
    } catch (error: any) {
      console.error('Check conflicts error:', error);
      res.status(400).json({
        success: false,
        error: error.message || 'Failed to check conflicts',
        details: error.errors || undefined,
      });
    }
  }

  /**
   * Get free/busy slots
   * GET /api/events/free-busy
   */
  async getFreeBusy(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.headers['x-user-id'] as string;
      if (!userId) {
        res.status(401).json({ error: 'User ID is required' });
        return;
      }

      const { startDate, endDate } = freeBusySchema.parse(req.query);
      const result = await eventService.getFreeBusySlots(userId, startDate, endDate);

      res.status(200).json({
        success: true,
        data: result,
      });
    } catch (error: any) {
      console.error('Get free/busy error:', error);
      res.status(400).json({
        success: false,
        error: error.message || 'Failed to fetch free/busy slots',
        details: error.errors || undefined,
      });
    }
  }

  /**
   * Get event statistics
   * GET /api/events/stats
   */
  async getEventStats(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.headers['x-user-id'] as string;
      if (!userId) {
        res.status(401).json({ error: 'User ID is required' });
        return;
      }

      const stats = await eventService.getEventStats(userId);

      res.status(200).json({
        success: true,
        data: stats,
      });
    } catch (error: any) {
      console.error('Get event stats error:', error);
      res.status(400).json({
        success: false,
        error: error.message || 'Failed to fetch event statistics',
      });
    }
  }

  /**
   * Bulk delete events
   * POST /api/events/bulk/delete
   */
  async bulkDeleteEvents(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.headers['x-user-id'] as string;
      if (!userId) {
        res.status(401).json({ error: 'User ID is required' });
        return;
      }

      const { eventIds, deleteRecurringSeries } = bulkDeleteEventsSchema.parse(req.body);

      const results = await Promise.allSettled(
        eventIds.map(id => eventService.deleteEvent(userId, id, deleteRecurringSeries))
      );

      const successful = results.filter(r => r.status === 'fulfilled').length;
      const failed = results.filter(r => r.status === 'rejected').length;

      res.status(200).json({
        success: true,
        data: {
          total: eventIds.length,
          successful,
          failed,
        },
      });
    } catch (error: any) {
      console.error('Bulk delete error:', error);
      res.status(400).json({
        success: false,
        error: error.message || 'Failed to bulk delete events',
        details: error.errors || undefined,
      });
    }
  }
}

export const eventController = new EventController();

import type { Request, Response, NextFunction } from 'express';
import { taskService } from '../services/task.service.js';
import {
  createTaskSchema,
  updateTaskSchema,
  taskFiltersSchema,
  bulkUpdateSchema,
  taskIdSchema,
} from '../validation/task.validation.js';

export class TaskController {
  /**
   * Create a new task
   * POST /api/tasks
   */
  async createTask(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const validatedData = createTaskSchema.parse(req.body);

      // Convert string dates to Date objects
      const taskData = {
        ...validatedData,
        scheduledDate: validatedData.scheduledDate
          ? new Date(validatedData.scheduledDate)
          : undefined,
        dueDate: validatedData.dueDate ? new Date(validatedData.dueDate) : undefined,
      };

      const task = await taskService.createTask(userId, taskData);

      res.status(201).json({
        success: true,
        data: task,
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Get tasks for authenticated user
   * GET /api/tasks
   */
  async getTasks(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const validatedQuery = taskFiltersSchema.parse(req.query);

      const filters = {
        categoryId: validatedQuery.categoryId,
        priority: validatedQuery.priority,
        status: validatedQuery.status,
        scheduledDateFrom: validatedQuery.scheduledDateFrom
          ? new Date(validatedQuery.scheduledDateFrom)
          : undefined,
        scheduledDateTo: validatedQuery.scheduledDateTo
          ? new Date(validatedQuery.scheduledDateTo)
          : undefined,
        dueDateFrom: validatedQuery.dueDateFrom
          ? new Date(validatedQuery.dueDateFrom)
          : undefined,
        dueDateTo: validatedQuery.dueDateTo
          ? new Date(validatedQuery.dueDateTo)
          : undefined,
        search: validatedQuery.search,
        tags: validatedQuery.tags,
      };

      const page = validatedQuery.page || 1;
      const limit = Math.min(validatedQuery.limit || 20, 100);

      const result = await taskService.getTasks(userId, filters, page, limit);

      res.json({
        success: true,
        data: result,
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Get tasks grouped by category (for UI wireframe)
   * GET /api/tasks/by-category
   */
  async getTasksByCategory(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const { status, priority } = req.query;

      const filters = {
        status: status as any,
        priority: priority as any,
      };

      const result = await taskService.getTasksByCategory(userId, filters);

      res.json({
        success: true,
        data: result,
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Get a single task
   * GET /api/tasks/:id
   */
  async getTaskById(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const { id } = taskIdSchema.parse(req.params);

      const task = await taskService.getTaskById(userId, id);

      if (!task) {
        return res.status(404).json({
          success: false,
          error: 'Task not found',
        });
      }

      res.json({
        success: true,
        data: task,
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Update a task
   * PUT /api/tasks/:id
   */
  async updateTask(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const { id } = taskIdSchema.parse(req.params);
      const validatedData = updateTaskSchema.parse(req.body);

      // Convert string dates to Date objects
      const updateData = {
        ...validatedData,
        scheduledDate:
          validatedData.scheduledDate !== undefined
            ? validatedData.scheduledDate
              ? new Date(validatedData.scheduledDate)
              : null
            : undefined,
        dueDate:
          validatedData.dueDate !== undefined
            ? validatedData.dueDate
              ? new Date(validatedData.dueDate)
              : null
            : undefined,
      };

      const task = await taskService.updateTask(userId, id, updateData);

      res.json({
        success: true,
        data: task,
      });
    } catch (error: any) {
      if (error.message === 'Task not found') {
        return res.status(404).json({ success: false, error: error.message });
      }
      next(error);
    }
  }

  /**
   * Toggle task completion
   * PATCH /api/tasks/:id/complete
   */
  async toggleCompletion(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const { id } = taskIdSchema.parse(req.params);

      const task = await taskService.toggleTaskCompletion(userId, id);

      res.json({
        success: true,
        data: task,
        message: task.status === 'completed' ? 'Task marked as complete' : 'Task reopened',
      });
    } catch (error: any) {
      if (error.message === 'Task not found') {
        return res.status(404).json({ success: false, error: error.message });
      }
      next(error);
    }
  }

  /**
   * Delete a task (soft delete)
   * DELETE /api/tasks/:id
   */
  async deleteTask(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const { id } = taskIdSchema.parse(req.params);

      const result = await taskService.deleteTask(userId, id);

      res.json({
        success: true,
        message: result.message,
      });
    } catch (error: any) {
      if (error.message === 'Task not found') {
        return res.status(404).json({ success: false, error: error.message });
      }
      next(error);
    }
  }

  /**
   * Bulk update tasks
   * POST /api/tasks/bulk-update
   */
  async bulkUpdate(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const validatedData = bulkUpdateSchema.parse(req.body);

      const result = await taskService.bulkUpdateTasks(
        userId,
        validatedData.taskIds,
        validatedData.updates
      );

      res.json({
        success: true,
        data: result,
        message: `${result.updated} tasks updated successfully`,
      });
    } catch (error: any) {
      if (error.message?.includes('not found')) {
        return res.status(404).json({ success: false, error: error.message });
      }
      next(error);
    }
  }

  /**
   * Get task statistics
   * GET /api/tasks/stats
   */
  async getStats(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const stats = await taskService.getTaskStats(userId);

      res.json({
        success: true,
        data: stats,
      });
    } catch (error) {
      next(error);
    }
  }
}

export const taskController = new TaskController();

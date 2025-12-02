import prisma from '../lib/prisma.js';
import type { Prisma } from '@prisma/client';

export interface CreateTaskDTO {
  title: string;
  description?: string;
  categoryId?: string;
  priority?: 'VI' | 'MI' | 'NI';
  status?: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  scheduledDate?: Date;
  dueDate?: Date;
  colorHex?: string;
  tags?: string[];
  timeEstimateMinutes?: number;
  voiceTranscript?: string;
  sentimentScore?: number;
  contextMetadata?: Record<string, any>;
}

export interface UpdateTaskDTO {
  title?: string;
  description?: string;
  categoryId?: string | null;
  priority?: 'VI' | 'MI' | 'NI';
  status?: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  scheduledDate?: Date | null;
  dueDate?: Date | null;
  colorHex?: string | null;
  tags?: string[];
  timeEstimateMinutes?: number | null;
  actualTimeMinutes?: number | null;
}

export interface TaskFilters {
  categoryId?: string;
  priority?: 'VI' | 'MI' | 'NI';
  status?: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  scheduledDateFrom?: Date;
  scheduledDateTo?: Date;
  dueDateFrom?: Date;
  dueDateTo?: Date;
  search?: string;
  tags?: string[];
}

export class TaskService {
  /**
   * Create a new task
   */
  async createTask(userId: string, data: CreateTaskDTO) {
    // Auto-suggest priority if due date provided
    const priority = data.priority || this.suggestPriority(data.dueDate);

    // Prepare context metadata with creation timestamp
    const contextMetadata = {
      ...data.contextMetadata,
      created_at_hour: new Date().getHours(),
      created_at_day: new Date().getDay(),
      created_via: data.voiceTranscript ? 'voice' : 'manual',
    };

    const task = await prisma.task.create({
      data: {
        title: data.title,
        description: data.description,
        categoryId: data.categoryId,
        priority,
        status: data.status || 'pending',
        scheduledDate: data.scheduledDate,
        dueDate: data.dueDate,
        colorHex: data.colorHex,
        tags: data.tags || [],
        timeEstimateMinutes: data.timeEstimateMinutes,
        voiceTranscript: data.voiceTranscript,
        sentimentScore: data.sentimentScore,
        contextMetadata: contextMetadata as Prisma.JsonObject,
        userId,
      },
      include: {
        category: true,
      },
    });

    return task;
  }

  /**
   * Get tasks for a user with filters
   */
  async getTasks(
    userId: string,
    filters: TaskFilters = {},
    page: number = 1,
    limit: number = 20
  ) {
    const where: Prisma.TaskWhereInput = {
      userId,
      deletedAt: null, // Only active tasks
    };

    // Apply filters
    if (filters.categoryId) {
      where.categoryId = filters.categoryId;
    }
    if (filters.priority) {
      where.priority = filters.priority;
    }
    if (filters.status) {
      where.status = filters.status;
    }
    if (filters.scheduledDateFrom || filters.scheduledDateTo) {
      where.scheduledDate = {
        ...(filters.scheduledDateFrom && { gte: filters.scheduledDateFrom }),
        ...(filters.scheduledDateTo && { lte: filters.scheduledDateTo }),
      };
    }
    if (filters.dueDateFrom || filters.dueDateTo) {
      where.dueDate = {
        ...(filters.dueDateFrom && { gte: filters.dueDateFrom }),
        ...(filters.dueDateTo && { lte: filters.dueDateTo }),
      };
    }
    if (filters.search) {
      where.OR = [
        { title: { contains: filters.search, mode: 'insensitive' } },
        { description: { contains: filters.search, mode: 'insensitive' } },
      ];
    }
    if (filters.tags && filters.tags.length > 0) {
      where.tags = {
        hasSome: filters.tags,
      };
    }

    const [tasks, total] = await Promise.all([
      prisma.task.findMany({
        where,
        include: {
          category: true,
        },
        orderBy: [
          { priority: 'asc' }, // VI first, then MI, then NI
          { dueDate: 'asc' },
          { createdAt: 'desc' },
        ],
        skip: (page - 1) * limit,
        take: limit,
      }),
      prisma.task.count({ where }),
    ]);

    return {
      tasks,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    };
  }

  /**
   * Get tasks grouped by category (for wireframe UI)
   */
  async getTasksByCategory(userId: string, filters: TaskFilters = {}) {
    const where: Prisma.TaskWhereInput = {
      userId,
      deletedAt: null,
      status: filters.status || { not: 'completed' }, // Active tasks by default
    };

    // Apply additional filters
    if (filters.priority) where.priority = filters.priority;
    if (filters.scheduledDateFrom || filters.scheduledDateTo) {
      where.scheduledDate = {
        ...(filters.scheduledDateFrom && { gte: filters.scheduledDateFrom }),
        ...(filters.scheduledDateTo && { lte: filters.scheduledDateTo }),
      };
    }

    // Get all categories for user
    const categories = await prisma.category.findMany({
      where: { userId },
      include: {
        tasks: {
          where,
          orderBy: [
            { priority: 'asc' },
            { dueDate: 'asc' },
            { createdAt: 'desc' },
          ],
        },
      },
      orderBy: { order: 'asc' },
    });

    // Get uncategorized tasks
    const uncategorizedTasks = await prisma.task.findMany({
      where: {
        ...where,
        categoryId: null,
      },
      orderBy: [
        { priority: 'asc' },
        { dueDate: 'asc' },
        { createdAt: 'desc' },
      ],
    });

    return {
      categorized: categories,
      uncategorized: uncategorizedTasks,
    };
  }

  /**
   * Get task by ID
   */
  async getTaskById(userId: string, taskId: string) {
    const task = await prisma.task.findFirst({
      where: {
        id: taskId,
        userId,
        deletedAt: null,
      },
      include: {
        category: true,
      },
    });

    return task;
  }

  /**
   * Update a task
   */
  async updateTask(userId: string, taskId: string, data: UpdateTaskDTO) {
    const existingTask = await this.getTaskById(userId, taskId);
    if (!existingTask) {
      throw new Error('Task not found');
    }

    // Track priority changes for AI learning
    let priorityChanges = existingTask.priorityChanges as any[] || [];
    if (data.priority && data.priority !== existingTask.priority) {
      priorityChanges.push({
        from: existingTask.priority,
        to: data.priority,
        changedAt: new Date().toISOString(),
        reason: 'user_override',
      });
    }

    // Track rescheduling for AI analysis
    let rescheduleCount = existingTask.rescheduleCount;
    if (data.scheduledDate && existingTask.scheduledDate) {
      if (data.scheduledDate.getTime() !== existingTask.scheduledDate.getTime()) {
        rescheduleCount += 1;
      }
    }

    const task = await prisma.task.update({
      where: { id: taskId },
      data: {
        ...data,
        priorityChanges: priorityChanges as Prisma.JsonArray,
        rescheduleCount,
        updatedAt: new Date(),
      },
      include: {
        category: true,
      },
    });

    return task;
  }

  /**
   * Toggle task completion
   */
  async toggleTaskCompletion(userId: string, taskId: string) {
    const task = await this.getTaskById(userId, taskId);
    if (!task) {
      throw new Error('Task not found');
    }

    const isCompleting = task.status !== 'completed';
    const now = new Date();

    // Calculate actual time if completing
    let actualTimeMinutes = task.actualTimeMinutes;
    if (isCompleting && task.createdAt) {
      const minutesSinceCreation = Math.floor(
        (now.getTime() - task.createdAt.getTime()) / 1000 / 60
      );
      actualTimeMinutes = minutesSinceCreation;
    }

    // Build completion pattern for AI
    const completionPattern = isCompleting
      ? {
          completed_at_hour: now.getHours(),
          completed_at_day: now.getDay(),
          days_to_complete: task.createdAt
            ? Math.floor((now.getTime() - task.createdAt.getTime()) / 1000 / 60 / 60 / 24)
            : null,
          was_rescheduled: task.rescheduleCount > 0,
        }
      : task.completionPattern;

    const updatedTask = await prisma.task.update({
      where: { id: taskId },
      data: {
        status: isCompleting ? 'completed' : 'pending',
        completedAt: isCompleting ? now : null,
        actualTimeMinutes,
        completionPattern: completionPattern as Prisma.JsonObject,
      },
      include: {
        category: true,
      },
    });

    return updatedTask;
  }

  /**
   * Soft delete a task (preserve for AI training)
   */
  async deleteTask(userId: string, taskId: string) {
    const task = await this.getTaskById(userId, taskId);
    if (!task) {
      throw new Error('Task not found');
    }

    await prisma.task.update({
      where: { id: taskId },
      data: {
        deletedAt: new Date(),
      },
    });

    return { success: true, message: 'Task deleted successfully' };
  }

  /**
   * Bulk update tasks
   */
  async bulkUpdateTasks(
    userId: string,
    taskIds: string[],
    updates: Pick<UpdateTaskDTO, 'status' | 'priority' | 'categoryId'>
  ) {
    // Verify all tasks belong to user
    const tasks = await prisma.task.findMany({
      where: {
        id: { in: taskIds },
        userId,
        deletedAt: null,
      },
    });

    if (tasks.length !== taskIds.length) {
      throw new Error('Some tasks not found or do not belong to user');
    }

    const result = await prisma.task.updateMany({
      where: {
        id: { in: taskIds },
        userId,
      },
      data: updates,
    });

    return { updated: result.count };
  }

  /**
   * Get task statistics for user
   */
  async getTaskStats(userId: string) {
    const [
      totalTasks,
      completedTasks,
      pendingTasks,
      viTasks,
      miTasks,
      niTasks,
      overdueTasks,
    ] = await Promise.all([
      prisma.task.count({ where: { userId, deletedAt: null } }),
      prisma.task.count({ where: { userId, status: 'completed', deletedAt: null } }),
      prisma.task.count({ where: { userId, status: 'pending', deletedAt: null } }),
      prisma.task.count({ where: { userId, priority: 'VI', deletedAt: null } }),
      prisma.task.count({ where: { userId, priority: 'MI', deletedAt: null } }),
      prisma.task.count({ where: { userId, priority: 'NI', deletedAt: null } }),
      prisma.task.count({
        where: {
          userId,
          status: { not: 'completed' },
          dueDate: { lt: new Date() },
          deletedAt: null,
        },
      }),
    ]);

    return {
      total: totalTasks,
      completed: completedTasks,
      pending: pendingTasks,
      completionRate: totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0,
      byPriority: {
        VI: viTasks,
        MI: miTasks,
        NI: niTasks,
      },
      overdue: overdueTasks,
    };
  }

  /**
   * AI-powered priority suggestion based on due date
   */
  private suggestPriority(dueDate?: Date): 'VI' | 'MI' | 'NI' {
    if (!dueDate) return 'MI';

    const now = new Date();
    const daysUntilDue = Math.floor(
      (dueDate.getTime() - now.getTime()) / 1000 / 60 / 60 / 24
    );

    if (daysUntilDue <= 1) return 'VI'; // Due today or tomorrow
    if (daysUntilDue <= 7) return 'MI'; // Due this week
    return 'NI'; // Due later
  }
}

export const taskService = new TaskService();

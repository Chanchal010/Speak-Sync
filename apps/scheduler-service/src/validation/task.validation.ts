import { z } from 'zod';

// Task validation schemas
export const createTaskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title too long'),
  description: z.string().max(2000, 'Description too long').optional(),
  categoryId: z.string().uuid().optional(),
  priority: z.enum(['VI', 'MI', 'NI']).optional(),
  status: z.enum(['pending', 'in_progress', 'completed', 'cancelled']).optional(),
  scheduledDate: z.string().datetime().optional().or(z.date().optional()),
  dueDate: z.string().datetime().optional().or(z.date().optional()),
  colorHex: z.string().regex(/^#[0-9A-F]{6}$/i, 'Invalid hex color').optional(),
  tags: z.array(z.string()).optional(),
  timeEstimateMinutes: z.number().int().positive().optional(),
  voiceTranscript: z.string().max(1000).optional(),
  sentimentScore: z.number().min(-1).max(1).optional(),
  contextMetadata: z.record(z.string(), z.any()).optional(),
});

export const updateTaskSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  description: z.string().max(2000).optional().nullable(),
  categoryId: z.string().uuid().optional().nullable(),
  priority: z.enum(['VI', 'MI', 'NI']).optional(),
  status: z.enum(['pending', 'in_progress', 'completed', 'cancelled']).optional(),
  scheduledDate: z.string().datetime().optional().nullable().or(z.date().optional().nullable()),
  dueDate: z.string().datetime().optional().nullable().or(z.date().optional().nullable()),
  colorHex: z.string().regex(/^#[0-9A-F]{6}$/i).optional().nullable(),
  tags: z.array(z.string()).optional(),
  timeEstimateMinutes: z.number().int().positive().optional().nullable(),
  actualTimeMinutes: z.number().int().positive().optional().nullable(),
});

export const taskFiltersSchema = z.object({
  categoryId: z.string().uuid().optional(),
  priority: z.enum(['VI', 'MI', 'NI']).optional(),
  status: z.enum(['pending', 'in_progress', 'completed', 'cancelled']).optional(),
  scheduledDateFrom: z.string().datetime().optional().or(z.date().optional()),
  scheduledDateTo: z.string().datetime().optional().or(z.date().optional()),
  dueDateFrom: z.string().datetime().optional().or(z.date().optional()),
  dueDateTo: z.string().datetime().optional().or(z.date().optional()),
  search: z.string().max(100).optional(),
  tags: z.array(z.string()).optional(),
  page: z.string().regex(/^\d+$/).transform(Number).optional(),
  limit: z.string().regex(/^\d+$/).transform(Number).optional(),
});

export const bulkUpdateSchema = z.object({
  taskIds: z.array(z.string().uuid()).min(1, 'At least one task ID required'),
  updates: z.object({
    status: z.enum(['pending', 'in_progress', 'completed', 'cancelled']).optional(),
    priority: z.enum(['VI', 'MI', 'NI']).optional(),
    categoryId: z.string().uuid().optional().nullable(),
  }),
});

export const taskIdSchema = z.object({
  id: z.string().uuid('Invalid task ID'),
});

// Category validation schemas
export const createCategorySchema = z.object({
  name: z.string().min(1, 'Category name is required').max(50, 'Name too long'),
  icon: z.string().max(10).optional(),
  color: z.string().regex(/^#[0-9A-F]{6}$/i, 'Invalid hex color').optional(),
  order: z.number().int().nonnegative().optional(),
});

export const updateCategorySchema = z.object({
  name: z.string().min(1).max(50).optional(),
  icon: z.string().max(10).optional(),
  color: z.string().regex(/^#[0-9A-F]{6}$/i).optional(),
  order: z.number().int().nonnegative().optional(),
});

export const reorderCategoriesSchema = z.object({
  categories: z.array(
    z.object({
      id: z.string().uuid(),
      order: z.number().int().nonnegative(),
    })
  ).min(1),
});

export const categoryIdSchema = z.object({
  id: z.string().uuid('Invalid category ID'),
});

import type { Request, Response, NextFunction } from 'express';
import { categoryService } from '../services/category.service.js';
import {
  createCategorySchema,
  updateCategorySchema,
  reorderCategoriesSchema,
  categoryIdSchema,
} from '../validation/task.validation.js';

export class CategoryController {
  /**
   * Create a new category
   * POST /api/categories
   */
  async createCategory(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const validatedData = createCategorySchema.parse(req.body);

      const category = await categoryService.createCategory(userId, validatedData);

      res.status(201).json({
        success: true,
        data: category,
      });
    } catch (error: any) {
      if (error.message?.includes('already exists')) {
        return res.status(409).json({ success: false, error: error.message });
      }
      next(error);
    }
  }

  /**
   * Get all categories
   * GET /api/categories
   */
  async getCategories(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const includeTasks = req.query.includeTasks === 'true';

      const categories = await categoryService.getCategories(userId, includeTasks);

      res.json({
        success: true,
        data: categories,
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Get a single category
   * GET /api/categories/:id
   */
  async getCategoryById(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const { id } = categoryIdSchema.parse(req.params);

      const category = await categoryService.getCategoryById(userId, id);

      if (!category) {
        return res.status(404).json({
          success: false,
          error: 'Category not found',
        });
      }

      res.json({
        success: true,
        data: category,
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Update a category
   * PUT /api/categories/:id
   */
  async updateCategory(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const { id } = categoryIdSchema.parse(req.params);
      const validatedData = updateCategorySchema.parse(req.body);

      const category = await categoryService.updateCategory(userId, id, validatedData);

      res.json({
        success: true,
        data: category,
      });
    } catch (error: any) {
      if (error.message === 'Category not found') {
        return res.status(404).json({ success: false, error: error.message });
      }
      if (error.message?.includes('already exists')) {
        return res.status(409).json({ success: false, error: error.message });
      }
      next(error);
    }
  }

  /**
   * Delete a category
   * DELETE /api/categories/:id
   */
  async deleteCategory(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const { id } = categoryIdSchema.parse(req.params);

      const result = await categoryService.deleteCategory(userId, id);

      res.json({
        success: true,
        message: result.message,
      });
    } catch (error: any) {
      if (error.message === 'Category not found') {
        return res.status(404).json({ success: false, error: error.message });
      }
      next(error);
    }
  }

  /**
   * Reorder categories
   * POST /api/categories/reorder
   */
  async reorderCategories(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = (req as any).user?.userId;
      if (!userId) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const validatedData = reorderCategoriesSchema.parse(req.body);

      const result = await categoryService.reorderCategories(
        userId,
        validatedData.categories
      );

      res.json({
        success: true,
        message: result.message,
      });
    } catch (error) {
      next(error);
    }
  }
}

export const categoryController = new CategoryController();

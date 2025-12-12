import prisma from '../lib/prisma.js';

export interface CreateCategoryDTO {
  name: string;
  icon?: string;
  color?: string;
  order?: number;
}

export interface UpdateCategoryDTO {
  name?: string;
  icon?: string;
  color?: string;
  order?: number;
}

export class CategoryService {
  /**
   * Create default categories for a new user
   */
  async createDefaultCategories(userId: string) {
    const defaultCategories = [
      { name: 'Personal', icon: '👤', color: '#FF6B6B', order: 1 },
      { name: 'Learning', icon: '📚', color: '#4ECDC4', order: 2 },
      { name: 'Fitness', icon: '💪', color: '#95E1D3', order: 3 },
      { name: 'Work', icon: '💼', color: '#F38181', order: 4 },
      { name: 'Shopping', icon: '🛒', color: '#AA96DA', order: 5 },
      { name: 'Wish List', icon: '⭐', color: '#FCBAD3', order: 6 },
    ];

    const categories = await prisma.category.createMany({
      data: defaultCategories.map((cat) => ({
        ...cat,
        userId,
      })),
      skipDuplicates: true,
    });

    return categories;
  }

  /**
   * Create a custom category
   */
  async createCategory(userId: string, data: CreateCategoryDTO) {
    // Check if category name already exists for user
    const existing = await prisma.category.findFirst({
      where: {
        userId,
        name: data.name,
      },
    });

    if (existing) {
      throw new Error('Category with this name already exists');
    }

    const category = await prisma.category.create({
      data: {
        ...data,
        userId,
      },
    });

    return category;
  }

  /**
   * Get all categories for a user
   */
  async getCategories(userId: string, includeTasks: boolean = false) {
    const categories = await prisma.category.findMany({
      where: { userId },
      include: includeTasks
        ? {
            tasks: {
              where: { deletedAt: null },
              orderBy: [
                { priority: 'asc' },
                { dueDate: 'asc' },
              ],
            },
          }
        : undefined,
      orderBy: { order: 'asc' },
    });

    return categories;
  }

  /**
   * Get category by ID
   */
  async getCategoryById(userId: string, categoryId: string) {
    const category = await prisma.category.findFirst({
      where: {
        id: categoryId,
        userId,
      },
      include: {
        tasks: {
          where: { deletedAt: null },
        },
      },
    });

    return category;
  }

  /**
   * Update a category
   */
  async updateCategory(userId: string, categoryId: string, data: UpdateCategoryDTO) {
    const category = await this.getCategoryById(userId, categoryId);
    if (!category) {
      throw new Error('Category not found');
    }

    // Check name uniqueness if updating name
    if (data.name && data.name !== category.name) {
      const existing = await prisma.category.findFirst({
        where: {
          userId,
          name: data.name,
          id: { not: categoryId },
        },
      });

      if (existing) {
        throw new Error('Category with this name already exists');
      }
    }

    const updated = await prisma.category.update({
      where: { id: categoryId },
      data,
    });

    return updated;
  }

  /**
   * Delete a category (tasks will become uncategorized)
   */
  async deleteCategory(userId: string, categoryId: string) {
    const category = await this.getCategoryById(userId, categoryId);
    if (!category) {
      throw new Error('Category not found');
    }

    // Tasks will have categoryId set to null automatically (onDelete: SetNull)
    await prisma.category.delete({
      where: { id: categoryId },
    });

    return { success: true, message: 'Category deleted successfully' };
  }

  /**
   * Reorder categories
   */
  async reorderCategories(userId: string, categoryOrders: { id: string; order: number }[]) {
    const updates = categoryOrders.map((item) =>
      prisma.category.update({
        where: { id: item.id },
        data: { order: item.order },
      })
    );

    await prisma.$transaction(updates);

    return { success: true, message: 'Categories reordered successfully' };
  }
}

export const categoryService = new CategoryService();

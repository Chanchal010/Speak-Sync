import { Router } from 'express';
import { categoryController } from '../../controllers/category.controller.js';

const router = Router();

// Category CRUD endpoints
router.post('/', categoryController.createCategory.bind(categoryController));
router.get('/', categoryController.getCategories.bind(categoryController));
router.get('/:id', categoryController.getCategoryById.bind(categoryController));
router.put('/:id', categoryController.updateCategory.bind(categoryController));
router.delete('/:id', categoryController.deleteCategory.bind(categoryController));

// Category management
router.post('/reorder', categoryController.reorderCategories.bind(categoryController));

export default router;

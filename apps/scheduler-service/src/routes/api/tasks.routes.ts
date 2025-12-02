import { Router } from 'express';
import { taskController } from '../../controllers/task.controller.js';

const router = Router();

// Task CRUD endpoints
router.post('/', taskController.createTask.bind(taskController));
router.get('/', taskController.getTasks.bind(taskController));
router.get('/by-category', taskController.getTasksByCategory.bind(taskController));
router.get('/stats', taskController.getStats.bind(taskController));
router.get('/:id', taskController.getTaskById.bind(taskController));
router.put('/:id', taskController.updateTask.bind(taskController));
router.patch('/:id/complete', taskController.toggleCompletion.bind(taskController));
router.delete('/:id', taskController.deleteTask.bind(taskController));

// Bulk operations
router.post('/bulk-update', taskController.bulkUpdate.bind(taskController));

export default router;

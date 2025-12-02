import { Router } from 'express';
import tasksRouter from './tasks.routes.js';
import categoriesRouter from './categories.routes.js';
import { extractUser } from '../../middleware/auth.middleware.js';

const router = Router();

// Apply authentication to all API routes
router.use(extractUser);

// Mount route handlers
router.use('/tasks', tasksRouter);
router.use('/categories', categoriesRouter);

export default router;

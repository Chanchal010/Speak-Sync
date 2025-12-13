import express, { Request, Response, NextFunction } from 'express';
import axios from 'axios';
import { authenticate } from '../middleware/auth.middleware.js';
import { serviceConfig } from '../config/index.js';

const router = express.Router();

// Scheduler service base URL
const SCHEDULER_URL = serviceConfig.schedulerUrl;

/**
 * Proxy middleware to forward requests to scheduler service with user context
 */
const proxyToScheduler = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const user = (req as any).user;
        
        if (!user) {
            return res.status(401).json({
                success: false,
                error: 'Unauthorized - No user context'
            });
        }

        // Build target URL - prepend /api to the path (router is mounted at /api/scheduler)
        const targetUrl = `${SCHEDULER_URL}/api${req.path}`;

        // Forward request with user context in headers
        const response = await axios({
            method: req.method,
            url: targetUrl,
            data: req.body,
            params: req.query,
            headers: {
                'Content-Type': 'application/json',
                'x-user-id': user.userId,
                'x-user-email': user.email,
                'x-user-role': user.role,
                'x-internal-api-key': serviceConfig.internalApiKey,
            },
            timeout: 30000,
        });

        res.status(response.status).json(response.data);
    } catch (error: any) {
        if (error.response) {
            // Forward error response from scheduler service
            res.status(error.response.status).json(error.response.data);
        } else if (error.request) {
            res.status(503).json({
                success: false,
                error: 'Scheduler service unavailable'
            });
        } else {
            next(error);
        }
    }
};

// === Task Endpoints ===

/**
 * GET /api/scheduler/tasks
 * Get all tasks with optional filters
 */
router.get('/tasks', authenticate, proxyToScheduler);

/**
 * POST /api/scheduler/tasks
 * Create a new task
 */
router.post('/tasks', authenticate, proxyToScheduler);

/**
 * GET /api/scheduler/tasks/:id
 * Get a specific task
 */
router.get('/tasks/:id', authenticate, proxyToScheduler);

/**
 * PUT /api/scheduler/tasks/:id
 * Update a task
 */
router.put('/tasks/:id', authenticate, proxyToScheduler);

/**
 * PATCH /api/scheduler/tasks/:id/complete
 * Toggle task completion
 */
router.patch('/tasks/:id/complete', authenticate, proxyToScheduler);

/**
 * DELETE /api/scheduler/tasks/:id
 * Delete a task
 */
router.delete('/tasks/:id', authenticate, proxyToScheduler);

// === Category Endpoints ===

/**
 * GET /api/scheduler/categories
 * Get all categories
 */
router.get('/categories', authenticate, proxyToScheduler);

/**
 * POST /api/scheduler/categories
 * Create a new category
 */
router.post('/categories', authenticate, proxyToScheduler);

/**
 * GET /api/scheduler/categories/:id
 * Get a specific category
 */
router.get('/categories/:id', authenticate, proxyToScheduler);

/**
 * PUT /api/scheduler/categories/:id
 * Update a category
 */
router.put('/categories/:id', authenticate, proxyToScheduler);

/**
 * DELETE /api/scheduler/categories/:id
 * Delete a category
 */
router.delete('/categories/:id', authenticate, proxyToScheduler);

/**
 * PATCH /api/scheduler/categories/reorder
 * Reorder categories
 */
router.patch('/categories/reorder', authenticate, proxyToScheduler);

// === Event Endpoints ===

/**
 * GET /api/scheduler/events
 * Get all events
 */
router.get('/events', authenticate, proxyToScheduler);

/**
 * POST /api/scheduler/events
 * Create a new event
 */
router.post('/events', authenticate, proxyToScheduler);

/**
 * GET /api/scheduler/events/:id
 * Get a specific event
 */
router.get('/events/:id', authenticate, proxyToScheduler);

/**
 * PUT /api/scheduler/events/:id
 * Update an event
 */
router.put('/events/:id', authenticate, proxyToScheduler);

/**
 * DELETE /api/scheduler/events/:id
 * Delete an event
 */
router.delete('/events/:id', authenticate, proxyToScheduler);

export default router;

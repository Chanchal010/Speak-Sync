import express, { Request, Response, NextFunction } from 'express';
import { lifestyleService } from '../services/lifestyle.service.js';
import { authenticate } from '../middleware/auth.middleware.js';

const router = express.Router();

// Use authenticate as authMiddleware
const authMiddleware = authenticate;

// === Habit Endpoints ===

/**
 * POST /api/gateway/lifestyle/habits
 * Create a new habit
 */
router.post('/habits', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = (req as any).user?.userId;
        if (!userId) {
            return res.status(401).json({ success: false, error: 'Unauthorized' });
        }

        const result = await lifestyleService.forwardRequest(
            'POST',
            '/api/habits',
            req.body,
            { 'x-user-id': userId }
        );
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * GET /api/gateway/lifestyle/habits
 * Get all habits for a user
 */
router.get('/habits', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = (req as any).user?.userId;
        if (!userId) {
            return res.status(401).json({ success: false, error: 'Unauthorized' });
        }

        // Build query params
        const params = new URLSearchParams();
        params.append('user_id', userId);
        Object.keys(req.query).forEach(key => {
            if (key !== 'user_id') params.append(key, req.query[key] as string);
        });

        const result = await lifestyleService.forwardRequest(
            'GET',
            `/api/habits?${params.toString()}`,
            undefined,
            { 'x-user-id': userId }
        );
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * GET /api/gateway/lifestyle/habits/:id
 * Get a specific habit
 */
router.get('/habits/:id', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await lifestyleService.getHabit(req.params.id);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * PUT /api/gateway/lifestyle/habits/:id
 * Update a habit
 */
router.put('/habits/:id', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await lifestyleService.updateHabit(req.params.id, req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * DELETE /api/gateway/lifestyle/habits/:id
 * Delete a habit
 */
router.delete('/habits/:id', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await lifestyleService.deleteHabit(req.params.id);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/lifestyle/habits/:id/log
 * Log a habit completion
 */
router.post('/habits/:id/log', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await lifestyleService.logHabit(req.params.id, req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * GET /api/gateway/lifestyle/habits/:id/logs
 * Get habit logs
 */
router.get('/habits/:id/logs', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const startDate = req.query.start_date as string;
        const endDate = req.query.end_date as string;
        const result = await lifestyleService.getHabitLogs(req.params.id, startDate, endDate);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * GET /api/gateway/lifestyle/habits/:id/analytics
 * Get habit analytics
 */
router.get('/habits/:id/analytics', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const days = req.query.days ? parseInt(req.query.days as string) : undefined;
        const result = await lifestyleService.getHabitAnalytics(req.params.id, days);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

// === Food Logging Endpoints ===

router.post('/food', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await lifestyleService.logFood(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

router.get('/food', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.user_id as string;
        const startDate = req.query.start_date as string;
        const endDate = req.query.end_date as string;
        const result = await lifestyleService.getFoodLogs(userId, startDate, endDate);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

router.get('/food/analytics', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.user_id as string;
        const days = req.query.days ? parseInt(req.query.days as string) : undefined;
        const result = await lifestyleService.getFoodAnalytics(userId, days);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

// === Exercise Endpoints ===

router.post('/exercise', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await lifestyleService.logExercise(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

router.get('/exercise', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.user_id as string;
        const startDate = req.query.start_date as string;
        const endDate = req.query.end_date as string;
        const result = await lifestyleService.getExerciseLogs(userId, startDate, endDate);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

router.get('/exercise/analytics', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.user_id as string;
        const days = req.query.days ? parseInt(req.query.days as string) : undefined;
        const result = await lifestyleService.getExerciseAnalytics(userId, days);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

// === Financial Tracking Endpoints ===

router.post('/finance', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await lifestyleService.logFinance(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

router.get('/finance', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.user_id as string;
        const startDate = req.query.start_date as string;
        const endDate = req.query.end_date as string;
        const result = await lifestyleService.getFinanceLogs(userId, startDate, endDate);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

router.get('/finance/analytics', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.user_id as string;
        const period = req.query.period as string;
        const result = await lifestyleService.getFinanceAnalytics(userId, period);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

// === Sleep Tracking Endpoints ===

router.post('/sleep', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await lifestyleService.logSleep(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

router.get('/sleep', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.user_id as string;
        const startDate = req.query.start_date as string;
        const endDate = req.query.end_date as string;
        const result = await lifestyleService.getSleepLogs(userId, startDate, endDate);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

router.get('/sleep/analytics', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.user_id as string;
        const days = req.query.days ? parseInt(req.query.days as string) : undefined;
        const result = await lifestyleService.getSleepAnalytics(userId, days);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

// === Study Tracking Endpoints ===

router.post('/study', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await lifestyleService.logStudy(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

router.get('/study', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.user_id as string;
        const startDate = req.query.start_date as string;
        const endDate = req.query.end_date as string;
        const result = await lifestyleService.getStudyLogs(userId, startDate, endDate);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

router.get('/study/analytics', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.user_id as string;
        const days = req.query.days ? parseInt(req.query.days as string) : undefined;
        const result = await lifestyleService.getStudyAnalytics(userId, days);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

// === Water Tracking Endpoints ===

router.post('/water', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await lifestyleService.logWater(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

router.get('/water', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.user_id as string;
        const startDate = req.query.start_date as string;
        const endDate = req.query.end_date as string;
        const result = await lifestyleService.getWaterLogs(userId, startDate, endDate);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

router.get('/water/analytics', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.user_id as string;
        const days = req.query.days ? parseInt(req.query.days as string) : undefined;
        const result = await lifestyleService.getWaterAnalytics(userId, days);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

export default router;

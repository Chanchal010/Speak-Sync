import express, { Request, Response, NextFunction } from 'express';
import { aiBrainService } from '../services/ai-brain.service.js';
import { authenticate } from '../middleware/auth.middleware.js';

const router = express.Router();

// Use authenticate as authMiddleware
const authMiddleware = authenticate;

// === Voice Endpoints ===

/**
 * POST /api/gateway/ai/voice/transcribe
 * Speech-to-Text
 */
router.post('/ai/voice/transcribe', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        // Forward multipart/form-data request
        const result = await aiBrainService.proxy('POST', '/api/ai/voice/transcribe', req.body, {
            'content-type': req.headers['content-type'] || ''
        });
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/ai/voice/synthesize
 * Text-to-Speech
 */
router.post('/ai/voice/synthesize', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const audioBuffer = await aiBrainService.synthesize(req.body.text, req.body.voice);
        res.setHeader('Content-Type', 'audio/mpeg');
        res.send(audioBuffer);
    } catch (error) {
        next(error);
    }
});

/**
 * GET /api/gateway/ai/voice/voices
 * List available voices
 */
router.get('/ai/voice/voices', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.getVoices();
        res.json(result);
    } catch (error) {
        next(error);
    }
});

// === Chat Endpoints ===

/**
 * POST /api/gateway/ai/chat
 * Generate chat response
 */
router.post('/ai/chat', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.chat(req.body.message, req.body.context);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

// === Conversation Endpoints ===

/**
 * POST /api/gateway/ai/conversation/voice
 * Full voice conversation
 */
router.post('/ai/conversation/voice', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.proxy('POST', '/api/ai/conversation/voice', req.body, {
            'content-type': req.headers['content-type'] || ''
        });
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/ai/conversation/text
 * Text conversation with voice response
 */
router.post('/ai/conversation/text', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.textConversation(
            req.body.text,
            req.body.session_id,
            req.body.voice_profile
        );
        res.json(result);
    } catch (error) {
        next(error);
    }
});

// === Scheduling Endpoints ===

/**
 * POST /api/gateway/scheduling/analyze-conflicts
 */
router.post('/scheduling/analyze-conflicts', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.scheduleAnalyzeConflicts(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/scheduling/suggest-time-slot
 */
router.post('/scheduling/suggest-time-slot', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.scheduleSuggestTimeSlot(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/scheduling/optimize-schedule
 */
router.post('/scheduling/optimize-schedule', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.scheduleOptimize(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/scheduling/smart-suggestions
 */
router.post('/scheduling/smart-suggestions', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.scheduleSmartSuggestions(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * GET /api/gateway/scheduling/patterns/:userId
 */
router.get('/scheduling/patterns/:userId', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.scheduleGetPatterns(req.params.userId);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

// === Habits Prediction Endpoints ===

/**
 * POST /api/gateway/habits/analyze-patterns
 */
router.post('/habits/analyze-patterns', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.habitsAnalyzePatterns(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/habits/predict-streak
 */
router.post('/habits/predict-streak', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.habitsPredictStreak(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/habits/predict-next-completion
 */
router.post('/habits/predict-next-completion', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.habitsPredictCompletion(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/habits/personalized-insights
 */
router.post('/habits/personalized-insights', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.habitsGetInsights(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/habits/optimal-schedule
 */
router.post('/habits/optimal-schedule', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.habitsOptimalSchedule(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/habits/formation-prediction
 */
router.post('/habits/formation-prediction', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.habitsFormationPrediction(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/habits/habit-strength
 */
router.post('/habits/habit-strength', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.habitsGetStrength(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * GET /api/gateway/habits/momentum/:userId/:habitType
 */
router.get('/habits/momentum/:userId/:habitType', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.habitsGetMomentum(req.params.userId, req.params.habitType);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

// === Memory Endpoints ===

/**
 * POST /api/gateway/memory/store-conversation
 */
router.post('/memory/store-conversation', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.memoryStoreConversation(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/memory/recall-conversations
 */
router.post('/memory/recall-conversations', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.memoryRecallConversations(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/memory/store-context
 */
router.post('/memory/store-context', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.memoryStoreContext(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/memory/retrieve-context
 */
router.post('/memory/retrieve-context', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.memoryRetrieveContext(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/memory/contextual-summary
 */
router.post('/memory/contextual-summary', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.memoryGetSummary(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * GET /api/gateway/memory/stats/:userId
 */
router.get('/memory/stats/:userId', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.memoryGetStats(req.params.userId);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/memory/extract-contexts
 */
router.post('/memory/extract-contexts', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const result = await aiBrainService.memoryExtractContexts(req.body);
        res.json(result);
    } catch (error) {
        next(error);
    }
});

export default router;

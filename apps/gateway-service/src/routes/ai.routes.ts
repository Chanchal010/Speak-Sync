import express, { Request, Response, NextFunction } from 'express';
import { aiService } from '../services/ai.service.js';
import { authenticate } from '../middleware/auth.middleware.js';
import multer from 'multer';
import FormData from 'form-data';

const router = express.Router();
const upload = multer({ storage: multer.memoryStorage() });

// Use authenticate as authMiddleware
const authMiddleware = authenticate;

// === Voice AI Endpoints ===

/**
 * POST /api/gateway/ai/transcribe
 * Transcribe audio to text (STT)
 */
router.post('/transcribe', authMiddleware, upload.single('audio'), async (req: Request, res: Response, next: NextFunction) => {
    try {
        if (!req.file) {
            return res.status(400).json({
                success: false,
                error: 'No audio file provided'
            });
        }

        const userId = (req as any).user?.userId;
        if (!userId) {
            return res.status(401).json({ success: false, error: 'Unauthorized' });
        }

        const language = req.body.language || 'auto';

        const result = await aiService.transcribeAudio(
            req.file.buffer,
            req.file.originalname,
            language
        );

        res.json({
            success: true,
            data: result
        });
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/ai/synthesize
 * Convert text to speech (TTS)
 */
router.post('/synthesize', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = (req as any).user?.userId;
        if (!userId) {
            return res.status(401).json({ success: false, error: 'Unauthorized' });
        }

        const { text, voice = 'nova', speed = 1.0 } = req.body;

        if (!text) {
            return res.status(400).json({
                success: false,
                error: 'Text is required'
            });
        }

        const audioBuffer = await aiService.synthesizeSpeech(text, voice, speed);

        res.set({
            'Content-Type': 'audio/mpeg',
            'Content-Disposition': 'attachment; filename="speech.mp3"'
        });
        res.send(audioBuffer);
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/gateway/ai/converse
 * Complete conversation flow: STT → LLM → TTS
 */
router.post('/converse', authMiddleware, upload.single('audio'), async (req: Request, res: Response, next: NextFunction) => {
    try {
        if (!req.file) {
            return res.status(400).json({
                success: false,
                error: 'No audio file provided'
            });
        }

        const userId = (req as any).user?.userId;
        if (!userId) {
            return res.status(401).json({ success: false, error: 'Unauthorized' });
        }

        const language = req.body.language || 'auto';
        const voice = req.body.voice || 'nova';

        const result = await aiService.converse(
            req.file.buffer,
            req.file.originalname,
            userId,
            language,
            voice
        );

        res.json({
            success: true,
            data: result
        });
    } catch (error) {
        next(error);
    }
});

/**
 * GET /api/gateway/ai/voices
 * List available TTS voices
 */
router.get('/voices', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const voices = await aiService.listVoices();
        res.json({
            success: true,
            data: voices
        });
    } catch (error) {
        next(error);
    }
});

/**
 * GET /api/gateway/ai/supported-formats
 * Get supported audio formats
 */
router.get('/supported-formats', authMiddleware, async (req: Request, res: Response, next: NextFunction) => {
    try {
        const formats = await aiService.getSupportedFormats();
        res.json({
            success: true,
            data: formats
        });
    } catch (error) {
        next(error);
    }
});

export default router;

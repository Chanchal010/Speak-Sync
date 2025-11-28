import type { Request, Response, NextFunction } from 'express';

/**
 * Middleware to verify internal API requests
 * Only allows requests from Gateway service with valid API key
 */
export const verifyInternalRequest = (req: Request, res: Response, next: NextFunction) => {
    const apiKey = req.headers['x-internal-api-key'];
    const expectedApiKey = process.env.INTERNAL_API_KEY;

    if (!expectedApiKey) {
        console.error('INTERNAL_API_KEY not configured');
        return res.status(500).json({
            success: false,
            error: 'Internal server configuration error',
        });
    }

    if (!apiKey || apiKey !== expectedApiKey) {
        return res.status(403).json({
            success: false,
            error: 'Forbidden: Invalid internal API key',
        });
    }

    next();
};

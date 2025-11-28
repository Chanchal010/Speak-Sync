import type { Request, Response, NextFunction } from 'express';
import { tokenService } from '../services/token.service.js';

/**
 * Middleware to authenticate requests using JWT
 * Extracts token from Authorization header, verifies it, and attaches user to request
 */
export const authenticate = async (req: Request, res: Response, next: NextFunction) => {
    try {
        // Get token from Authorization header
        const authHeader = req.headers.authorization;

        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            return res.status(401).json({
                success: false,
                error: 'No token provided',
            });
        }

        const token = authHeader.replace('Bearer ', '');

        // Check if token is blacklisted
        const isBlacklisted = await tokenService.isTokenBlacklisted(token);
        if (isBlacklisted) {
            return res.status(401).json({
                success: false,
                error: 'Token has been revoked',
            });
        }

        // Verify token
        const payload = tokenService.verifyAccessToken(token);

        // Attach user info to request
        (req as any).user = payload;

        next();
    } catch (error: any) {
        return res.status(401).json({
            success: false,
            error: error.message || 'Invalid token',
        });
    }
};

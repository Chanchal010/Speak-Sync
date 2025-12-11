import type { Request, Response, NextFunction } from 'express';

/**
 * Middleware to check if user has required role
 */
export const requireRole = (allowedRoles: string[]) => {
    return (req: Request, res: Response, next: NextFunction) => {
        const user = (req as any).user;

        if (!user) {
            return res.status(401).json({
                success: false,
                error: 'Unauthorized',
            });
        }

        if (!allowedRoles.includes(user.role)) {
            return res.status(403).json({
                success: false,
                error: 'Forbidden: Insufficient permissions',
            });
        }

        next();
    };
};

/**
 * Middleware to require admin role
 */
export const requireAdmin = requireRole(['admin']);

/**
 * Middleware to require user or admin role
 */
export const requireUser = requireRole(['user', 'admin']);

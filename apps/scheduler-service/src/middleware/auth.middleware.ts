import type { Request, Response, NextFunction } from 'express';

/**
 * Simple auth middleware for scheduler service
 * Since Gateway handles JWT verification, we just need to extract user from headers
 * This is for when Scheduler is called directly (not through Gateway)
 */
export const extractUser = (req: Request, res: Response, next: NextFunction) => {
  // If already authenticated by Gateway, user will be in request
  if ((req as any).user) {
    return next();
  }

  // For direct calls, check x-user-id header (set by Gateway)
  const userId = req.headers['x-user-id'] as string;
  
  if (userId) {
    (req as any).user = { userId };
    return next();
  }

  return res.status(401).json({
    success: false,
    error: 'Unauthorized - No user context',
  });
};

/**
 * Verify internal API key for service-to-service communication
 */
export const verifyServiceAuth = (req: Request, res: Response, next: NextFunction) => {
  // Check both x-api-key and x-internal-api-key headers
  const apiKey = (req.headers['x-api-key'] || req.headers['x-internal-api-key']) as string;
  const expectedKey = process.env.INTERNAL_API_KEY;

  if (!apiKey || apiKey !== expectedKey) {
    return res.status(403).json({
      success: false,
      error: 'Forbidden - Invalid service credentials',
    });
  }

  next();
};

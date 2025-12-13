import type { Request, Response, NextFunction } from 'express';
import { authService } from '../services/auth.service.js';
import { registerSchema, loginSchema, refreshTokenSchema, updateProfileSchema } from '../validation/auth.validation.js';

export class AuthController {
    /**
     * Register a new user
     * POST /api/auth/register
     */
    async register(req: Request, res: Response, next: NextFunction) {
        try {
            // Validate request body
            const validatedData = registerSchema.parse(req.body);

            // Register user
            const result = await authService.register(validatedData);

            res.status(201).json({
                success: true,
                data: result,
            });
        } catch (error: any) {
            // Handle duplicate email error
            if (error.response?.status === 409) {
                return res.status(409).json({
                    success: false,
                    error: 'Email already registered',
                });
            }
            next(error);
        }
    }

    /**
     * Login user
     * POST /api/auth/login
     */
    async login(req: Request, res: Response, next: NextFunction) {
        try {
            // Validate request body
            const validatedData = loginSchema.parse(req.body);

            // Login user
            const result = await authService.login(validatedData);

            res.json({
                success: true,
                data: result,
            });
        } catch (error: any) {
            if (error.message === 'Invalid credentials' || error.message === 'Account is deactivated') {
                return res.status(401).json({
                    success: false,
                    error: error.message,
                });
            }
            next(error);
        }
    }

    /**
     * Logout user
     * POST /api/auth/logout
     */
    async logout(req: Request, res: Response, next: NextFunction) {
        try {
            const token = req.headers.authorization?.replace('Bearer ', '') || '';
            const userId = (req as any).user?.userId;

            if (!userId) {
                return res.status(401).json({
                    success: false,
                    error: 'Unauthorized',
                });
            }

            await authService.logout(token, userId);

            res.json({
                success: true,
                message: 'Logged out successfully',
            });
        } catch (error) {
            next(error);
        }
    }

    /**
     * Refresh access token
     * POST /api/auth/refresh
     */
    async refreshToken(req: Request, res: Response, next: NextFunction) {
        try {
            // Validate request body
            const validatedData = refreshTokenSchema.parse(req.body);

            // Refresh token
            const tokens = await authService.refreshToken(validatedData.refreshToken);

            res.json({
                success: true,
                data: { tokens },
            });
        } catch (error: any) {
            if (error.message === 'Invalid refresh token' || error.message === 'Account is deactivated') {
                return res.status(401).json({
                    success: false,
                    error: error.message,
                });
            }
            next(error);
        }
    }

    /**
     * Get current user
     * GET /api/auth/me
     */
    async getMe(req: Request, res: Response, next: NextFunction) {
        try {
            const userId = (req as any).user?.userId;

            if (!userId) {
                return res.status(401).json({
                    success: false,
                    error: 'Unauthorized',
                });
            }

            const user = await authService.getCurrentUser(userId);

            res.json({
                success: true,
                data: { user },
            });
        } catch (error) {
            next(error);
        }
    }

    /**
     * Update user profile
     * PUT /api/auth/profile
     */
    async updateProfile(req: Request, res: Response, next: NextFunction) {
        try {
            const userId = (req as any).user?.userId;

            if (!userId) {
                return res.status(401).json({
                    success: false,
                    error: 'Unauthorized',
                });
            }

            // Validate request body
            const validatedData = updateProfileSchema.parse(req.body);

            // Update profile
            const user = await authService.updateProfile(userId, validatedData);

            res.json({
                success: true,
                data: { user },
            });
        } catch (error: any) {
            // Handle duplicate email error
            if (error.response?.status === 409) {
                return res.status(409).json({
                    success: false,
                    error: 'Email already in use',
                });
            }
            next(error);
        }
    }
}

export const authController = new AuthController();

import type { Request, Response, NextFunction } from 'express';
import { userService } from '../services/user.service.js';
import {
    createUserSchema,
    updateUserSchema,
    updateRefreshTokenSchema,
    userIdSchema,
    emailParamSchema,
} from '../validation/user.validation.js';

export class UserController {
    /**
     * Create a new user
     * POST /internal/users
     */
    async createUser(req: Request, res: Response, next: NextFunction) {
        try {
            // Validate request body
            const validatedData = createUserSchema.parse(req.body);

            // Check if email already exists
            const emailExists = await userService.emailExists(validatedData.email);
            if (emailExists) {
                return res.status(409).json({
                    success: false,
                    error: 'Email already registered',
                });
            }

            // Create user
            const user = await userService.createUser(validatedData);

            res.status(201).json({
                success: true,
                data: user,
            });
        } catch (error) {
            next(error);
        }
    }

    /**
     * Get user by ID
     * GET /internal/users/:id
     */
    async getUserById(req: Request, res: Response, next: NextFunction) {
        try {
            // Validate params
            const { id } = userIdSchema.parse(req.params);

            const user = await userService.findUserById(id);

            if (!user) {
                return res.status(404).json({
                    success: false,
                    error: 'User not found',
                });
            }

            res.json({
                success: true,
                data: user,
            });
        } catch (error) {
            next(error);
        }
    }

    /**
     * Get user by email (includes password for authentication)
     * GET /internal/users/email/:email
     */
    async getUserByEmail(req: Request, res: Response, next: NextFunction) {
        try {
            // Validate params
            const { email } = emailParamSchema.parse(req.params);

            const user = await userService.findUserByEmail(email);

            if (!user) {
                return res.status(404).json({
                    success: false,
                    error: 'User not found',
                });
            }

            res.json({
                success: true,
                data: user,
            });
        } catch (error) {
            next(error);
        }
    }

    /**
     * Update user
     * PUT /internal/users/:id
     */
    async updateUser(req: Request, res: Response, next: NextFunction) {
        try {
            // Validate params and body
            const { id } = userIdSchema.parse(req.params);
            const validatedData = updateUserSchema.parse(req.body);

            // Check if email is being updated and if it already exists
            if (validatedData.email) {
                const emailExists = await userService.emailExists(validatedData.email);
                if (emailExists) {
                    return res.status(409).json({
                        success: false,
                        error: 'Email already in use',
                    });
                }
            }

            const user = await userService.updateUser(id, validatedData);

            res.json({
                success: true,
                data: user,
            });
        } catch (error) {
            next(error);
        }
    }

    /**
     * Update user's refresh token
     * PATCH /internal/users/:id/refresh-token
     */
    async updateRefreshToken(req: Request, res: Response, next: NextFunction) {
        try {
            // Validate params and body
            const { id } = userIdSchema.parse(req.params);
            const validatedData = updateRefreshTokenSchema.parse(req.body);

            await userService.updateRefreshToken(id, validatedData);

            res.json({
                success: true,
                message: 'Refresh token updated',
            });
        } catch (error) {
            next(error);
        }
    }

    /**
     * Delete user (soft delete)
     * DELETE /internal/users/:id
     */
    async deleteUser(req: Request, res: Response, next: NextFunction) {
        try {
            // Validate params
            const { id } = userIdSchema.parse(req.params);

            await userService.deleteUser(id);

            res.json({
                success: true,
                message: 'User deleted successfully',
            });
        } catch (error) {
            next(error);
        }
    }
}

export const userController = new UserController();

import { z } from 'zod';

// Password validation schema
const passwordSchema = z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number')
    .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character');

// Email validation schema
const emailSchema = z.string().email('Invalid email format').toLowerCase();

// Create user schema
export const createUserSchema = z.object({
    email: emailSchema,
    name: z.string().min(2, 'Name must be at least 2 characters').max(100, 'Name too long'),
    password: passwordSchema,
    role: z.enum(['user', 'admin']).optional().default('user'),
});

// Update user schema
export const updateUserSchema = z.object({
    name: z.string().min(2).max(100).optional(),
    email: emailSchema.optional(),
    role: z.enum(['user', 'admin']).optional(),
    isActive: z.boolean().optional(),
});

// Update refresh token schema
export const updateRefreshTokenSchema = z.object({
    refreshToken: z.string().nullable(),
});

// User ID param schema
export const userIdSchema = z.object({
    id: z.string().uuid('Invalid user ID format'),
});

// Email param schema
export const emailParamSchema = z.object({
    email: emailSchema,
});

// Export types
export type CreateUserInput = z.infer<typeof createUserSchema>;
export type UpdateUserInput = z.infer<typeof updateUserSchema>;
export type UpdateRefreshTokenInput = z.infer<typeof updateRefreshTokenSchema>;

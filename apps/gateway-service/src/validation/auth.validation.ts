import { z } from 'zod';

// Password validation schema
const passwordSchema = z
    .string()
    .min(8, 'Password must be at least 8 characters');

// Email validation schema
const emailSchema = z.string().email('Invalid email format').toLowerCase();

// Register schema
export const registerSchema = z.object({
    email: emailSchema,
    name: z.string().min(2, 'Name must be at least 2 characters').max(100, 'Name too long'),
    password: passwordSchema,
});

// Login schema
export const loginSchema = z.object({
    email: emailSchema,
    password: z.string().min(1, 'Password is required'),
});

// Refresh token schema
export const refreshTokenSchema = z.object({
    refreshToken: z.string().min(1, 'Refresh token is required'),
});

// Export types
export type RegisterInput = z.infer<typeof registerSchema>;
export type LoginInput = z.infer<typeof loginSchema>;
export type RefreshTokenInput = z.infer<typeof refreshTokenSchema>;

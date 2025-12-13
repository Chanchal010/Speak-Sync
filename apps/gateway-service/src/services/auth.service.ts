import argon2 from 'argon2';
import { tokenService, type JWTPayload } from './token.service.js';
import { schedulerService, type CreateUserDTO } from './scheduler.service.js';

export interface RegisterInput {
    email: string;
    name: string;
    password: string;
}

export interface LoginInput {
    email: string;
    password: string;
}

export interface AuthResponse {
    user: {
        id: string;
        email: string;
        name: string;
        role: string;
    };
    tokens: {
        accessToken: string;
        refreshToken: string;
    };
}

export class AuthService {
    /**
     * Register a new user
     */
    async register(input: RegisterInput): Promise<AuthResponse> {
        // Create user in scheduler service
        const userData: CreateUserDTO = {
            email: input.email,
            name: input.name,
            password: input.password,
            role: 'user',
        };

        const user = await schedulerService.createUser(userData);

        // Generate JWT tokens
        const payload: JWTPayload = {
            userId: user.id,
            email: user.email,
            role: user.role,
        };

        const tokens = tokenService.generateTokenPair(payload);

        // Store refresh token in database
        await schedulerService.updateUserRefreshToken(user.id, tokens.refreshToken);

        return {
            user: {
                id: user.id,
                email: user.email,
                name: user.name,
                role: user.role,
            },
            tokens,
        };
    }

    /**
     * Login user
     */
    async login(input: LoginInput): Promise<AuthResponse> {
        // Get user from scheduler service (includes password)
        const user = await schedulerService.getUserByEmail(input.email);

        if (!user) {
            throw new Error('Invalid credentials');
        }

        // Check if account is active
        if (!user.isActive) {
            throw new Error('Account is deactivated');
        }

        // Verify password
        const isPasswordValid = await argon2.verify(user.password!, input.password);

        if (!isPasswordValid) {
            throw new Error('Invalid credentials');
        }

        // Generate JWT tokens
        const payload: JWTPayload = {
            userId: user.id,
            email: user.email,
            role: user.role,
        };

        const tokens = tokenService.generateTokenPair(payload);

        // Store refresh token in database
        await schedulerService.updateUserRefreshToken(user.id, tokens.refreshToken);

        return {
            user: {
                id: user.id,
                email: user.email,
                name: user.name,
                role: user.role,
            },
            tokens,
        };
    }

    /**
     * Logout user (blacklist tokens)
     */
    async logout(accessToken: string, userId: string): Promise<void> {
        // Blacklist access token (15 minutes TTL)
        await tokenService.blacklistToken(accessToken, 15 * 60);

        // Clear refresh token from database
        await schedulerService.updateUserRefreshToken(userId, null);
    }

    /**
     * Refresh access token
     */
    async refreshToken(refreshToken: string): Promise<{ accessToken: string; refreshToken: string }> {
        // Verify refresh token
        let payload: JWTPayload;
        try {
            payload = tokenService.verifyRefreshToken(refreshToken);
        } catch (error: any) {
            console.error('Token verification failed:', error.message);
            throw new Error('Invalid refresh token');
        }

        // Get user to verify refresh token matches
        const user = await schedulerService.getUserById(payload.userId);

        if (!user) {
            console.error('User not found for userId:', payload.userId);
            throw new Error('Invalid refresh token');
        }

        if (user.refreshToken !== refreshToken) {
            console.error('Token mismatch - DB token:', user.refreshToken?.substring(0, 50), 'Provided token:', refreshToken.substring(0, 50));
            throw new Error('Invalid refresh token');
        }

        if (!user.isActive) {
            throw new Error('Account is deactivated');
        }

        // Generate new token pair
        const newPayload: JWTPayload = {
            userId: user.id,
            email: user.email,
            role: user.role,
        };

        const tokens = tokenService.generateTokenPair(newPayload);

        // Update refresh token in database
        await schedulerService.updateUserRefreshToken(user.id, tokens.refreshToken);

        return tokens;
    }

    /**
     * Get current user info
     */
    async getCurrentUser(userId: string) {
        const user = await schedulerService.getUserById(userId);

        if (!user) {
            throw new Error('User not found');
        }

        return {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role,
            isActive: user.isActive,
            profilePicture: user.profilePicture,
            lastLoginAt: user.lastLoginAt,
            createdAt: user.createdAt,
        };
    }

    /**
     * Update user profile
     */
    async updateProfile(userId: string, data: { name?: string; email?: string; profilePicture?: string | null }) {
        const user = await schedulerService.updateUser(userId, data);

        return {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role,
            isActive: user.isActive,
            profilePicture: user.profilePicture,
            lastLoginAt: user.lastLoginAt,
            createdAt: user.createdAt,
        };
    }
}

export const authService = new AuthService();

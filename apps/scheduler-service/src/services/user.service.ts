import argon2 from 'argon2';
import prisma from '../lib/prisma.js';
import type { CreateUserInput, UpdateUserInput, UpdateRefreshTokenInput } from '../validation/user.validation.js';

export class UserService {
    /**
     * Create a new user with hashed password
     */
    async createUser(data: CreateUserInput) {
        // Hash password using Argon2
        const hashedPassword = await argon2.hash(data.password, {
            type: argon2.argon2id,
            memoryCost: 65536, // 64 MB
            timeCost: 3,
            parallelism: 4,
        });

        // Create user in database
        const user = await prisma.user.create({
            data: {
                email: data.email,
                name: data.name,
                password: hashedPassword,
                role: data.role || 'user',
            },
            select: {
                id: true,
                email: true,
                name: true,
                role: true,
                isActive: true,
                createdAt: true,
                updatedAt: true,
            },
        });

        return user;
    }

    /**
     * Find user by email (includes password for authentication)
     */
    async findUserByEmail(email: string) {
        const user = await prisma.user.findUnique({
            where: { email },
        });

        return user;
    }

    /**
     * Find user by ID (excludes password)
     */
    async findUserById(id: string) {
        const user = await prisma.user.findUnique({
            where: { id },
            select: {
                id: true,
                email: true,
                name: true,
                role: true,
                isActive: true,
                refreshToken: true,
                lastLoginAt: true,
                createdAt: true,
                updatedAt: true,
            },
        });

        return user;
    }

    /**
     * Update user information
     */
    async updateUser(id: string, data: UpdateUserInput) {
        const user = await prisma.user.update({
            where: { id },
            data,
            select: {
                id: true,
                email: true,
                name: true,
                role: true,
                isActive: true,
                createdAt: true,
                updatedAt: true,
            },
        });

        return user;
    }

    /**
     * Update user's refresh token
     */
    async updateRefreshToken(id: string, data: UpdateRefreshTokenInput) {
        await prisma.user.update({
            where: { id },
            data: {
                refreshToken: data.refreshToken,
                lastLoginAt: data.refreshToken ? new Date() : undefined,
            },
        });
    }

    /**
     * Soft delete user (set isActive to false)
     */
    async deleteUser(id: string) {
        await prisma.user.update({
            where: { id },
            data: { isActive: false },
        });
    }

    /**
     * Check if email already exists
     */
    async emailExists(email: string): Promise<boolean> {
        const count = await prisma.user.count({
            where: { email },
        });
        return count > 0;
    }

    /**
     * Verify password against hash
     */
    async verifyPassword(plainPassword: string, hashedPassword: string): Promise<boolean> {
        try {
            return await argon2.verify(hashedPassword, plainPassword);
        } catch (error) {
            return false;
        }
    }
}

export const userService = new UserService();

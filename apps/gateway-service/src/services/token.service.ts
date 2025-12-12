import jwt from 'jsonwebtoken';
import type { SignOptions } from 'jsonwebtoken';
import { Redis } from 'ioredis';
import { jwtConfig } from '../config/index.js';

const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

export interface JWTPayload {
    userId: string;
    email: string;
    role: string;
}

export class TokenService {
    /**
     * Generate access token (short-lived)
     */
    generateAccessToken(payload: JWTPayload): string {
        return jwt.sign(payload, jwtConfig.access.secret, {
            expiresIn: jwtConfig.access.expiresIn,
            issuer: 'speak-sync-gateway',
            audience: 'speak-sync-api',
        } as any);
    }

    /**
     * Generate refresh token (long-lived)
     */
    generateRefreshToken(payload: JWTPayload): string {
        return jwt.sign(payload, jwtConfig.refresh.secret, {
            expiresIn: jwtConfig.refresh.expiresIn,
            issuer: 'speak-sync-gateway',
            audience: 'speak-sync-api',
        } as any);
    }

    /**
     * Verify access token
     */
    verifyAccessToken(token: string): JWTPayload {
        try {
            const decoded = jwt.verify(token, jwtConfig.access.secret, {
                issuer: 'speak-sync-gateway',
                audience: 'speak-sync-api',
            }) as JWTPayload;
            return decoded;
        } catch (error) {
            throw new Error('Invalid or expired access token');
        }
    }

    /**
     * Verify refresh token
     */
    verifyRefreshToken(token: string): JWTPayload {
        try {
            const decoded = jwt.verify(token, jwtConfig.refresh.secret, {
                issuer: 'speak-sync-gateway',
                audience: 'speak-sync-api',
            }) as JWTPayload;
            return decoded;
        } catch (error) {
            throw new Error('Invalid or expired refresh token');
        }
    }

    /**
     * Blacklist a token (for logout)
     * Tokens are stored in Redis with TTL matching token expiry
     */
    async blacklistToken(token: string, expiresIn: number): Promise<void> {
        await redis.setex(`blacklist:${token}`, expiresIn, '1');
    }

    /**
     * Check if token is blacklisted
     */
    async isTokenBlacklisted(token: string): Promise<boolean> {
        const result = await redis.get(`blacklist:${token}`);
        return result !== null;
    }

    /**
     * Generate both access and refresh tokens
     */
    generateTokenPair(payload: JWTPayload) {
        return {
            accessToken: this.generateAccessToken(payload),
            refreshToken: this.generateRefreshToken(payload),
        };
    }
}

export const tokenService = new TokenService();

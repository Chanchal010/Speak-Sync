import axios, { AxiosInstance } from 'axios';
import { serviceConfig } from '../config/index.js';

export interface User {
    id: string;
    email: string;
    name: string;
    password?: string;
    role: string;
    isActive: boolean;
    refreshToken?: string | null;
    lastLoginAt?: Date | null;
    createdAt: Date;
    updatedAt: Date;
}

export interface CreateUserDTO {
    email: string;
    name: string;
    password: string;
    role?: string;
}

export interface UpdateUserDTO {
    name?: string;
    email?: string;
    role?: string;
    isActive?: boolean;
}

export class SchedulerService {
    private client: AxiosInstance;

    constructor() {
        this.client = axios.create({
            baseURL: serviceConfig.schedulerUrl,
            headers: {
                'Content-Type': 'application/json',
                'x-internal-api-key': serviceConfig.internalApiKey,
            },
            timeout: 10000,
        });
    }

    /**
     * Create a new user
     */
    async createUser(data: CreateUserDTO): Promise<User> {
        const response = await this.client.post('/internal/users', data);
        return response.data.data;
    }

    /**
     * Get user by email (includes password for authentication)
     */
    async getUserByEmail(email: string): Promise<User | null> {
        try {
            const response = await this.client.get(`/internal/users/email/${encodeURIComponent(email)}`);
            return response.data.data;
        } catch (error: any) {
            if (error.response?.status === 404) {
                return null;
            }
            throw error;
        }
    }

    /**
     * Get user by ID
     */
    async getUserById(id: string): Promise<User | null> {
        try {
            const response = await this.client.get(`/internal/users/${id}`);
            return response.data.data;
        } catch (error: any) {
            if (error.response?.status === 404) {
                return null;
            }
            throw error;
        }
    }

    /**
     * Update user's refresh token
     */
    async updateUserRefreshToken(id: string, refreshToken: string | null): Promise<void> {
        await this.client.patch(`/internal/users/${id}/refresh-token`, { refreshToken });
    }

    /**
     * Update user information
     */
    async updateUser(id: string, data: UpdateUserDTO): Promise<User> {
        const response = await this.client.put(`/internal/users/${id}`, data);
        return response.data.data;
    }
}

export const schedulerService = new SchedulerService();

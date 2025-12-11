import { serviceRegistry } from './service-registry.service.js';
import { AxiosInstance } from 'axios';

/**
 * Lifestyle Service Client
 * Proxies requests to Lifestyle Service (Habits, Food, Exercise, Finance, Sleep, Study, Water)
 */
export class LifestyleService {
    private client: AxiosInstance | null;

    constructor() {
        this.client = serviceRegistry.createServiceClient('lifestyle');
    }

    private ensureClient() {
        if (!this.client) {
            throw new Error('Lifestyle service client not initialized');
        }
        return this.client;
    }

    /**
     * Forward request to Lifestyle service
     */
    async forwardRequest(
        method: string,
        path: string,
        data?: any,
        headers?: Record<string, string>
    ): Promise<any> {
        const client = this.ensureClient();

        const config: any = {
            method,
            url: path,
            data,
            headers: headers || {}
        };

        const response = await client.request(config);
        return response.data;
    }

    // === Habit Endpoints ===

    /**
     * POST /api/habits
     * Create a new habit
     */
    async createHabit(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/habits', data);
    }

    /**
     * GET /api/habits
     * Get all habits for a user
     */
    async getHabits(userId: string): Promise<any> {
        return this.forwardRequest('GET', `/api/habits?user_id=${userId}`);
    }

    /**
     * GET /api/habits/:id
     * Get a specific habit
     */
    async getHabit(habitId: string): Promise<any> {
        return this.forwardRequest('GET', `/api/habits/${habitId}`);
    }

    /**
     * PUT /api/habits/:id
     * Update a habit
     */
    async updateHabit(habitId: string, data: any): Promise<any> {
        return this.forwardRequest('PUT', `/api/habits/${habitId}`, data);
    }

    /**
     * DELETE /api/habits/:id
     * Delete a habit
     */
    async deleteHabit(habitId: string): Promise<any> {
        return this.forwardRequest('DELETE', `/api/habits/${habitId}`);
    }

    /**
     * POST /api/habits/:id/log
     * Log a habit completion
     */
    async logHabit(habitId: string, data: any): Promise<any> {
        return this.forwardRequest('POST', `/api/habits/${habitId}/log`, data);
    }

    /**
     * GET /api/habits/:id/logs
     * Get habit logs
     */
    async getHabitLogs(habitId: string, startDate?: string, endDate?: string): Promise<any> {
        let path = `/api/habits/${habitId}/logs`;
        const params = [];
        if (startDate) params.push(`start_date=${startDate}`);
        if (endDate) params.push(`end_date=${endDate}`);
        if (params.length) path += `?${params.join('&')}`;

        return this.forwardRequest('GET', path);
    }

    /**
     * GET /api/habits/:id/analytics
     * Get habit analytics
     */
    async getHabitAnalytics(habitId: string, days?: number): Promise<any> {
        const path = `/api/habits/${habitId}/analytics${days ? `?days=${days}` : ''}`;
        return this.forwardRequest('GET', path);
    }

    // === Food Logging Endpoints ===

    /**
     * POST /api/food
     * Log food intake
     */
    async logFood(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/food', data);
    }

    /**
     * GET /api/food
     * Get food logs
     */
    async getFoodLogs(userId: string, startDate?: string, endDate?: string): Promise<any> {
        let path = `/api/food?user_id=${userId}`;
        if (startDate) path += `&start_date=${startDate}`;
        if (endDate) path += `&end_date=${endDate}`;

        return this.forwardRequest('GET', path);
    }

    /**
     * GET /api/food/analytics
     * Get food analytics
     */
    async getFoodAnalytics(userId: string, days?: number): Promise<any> {
        const path = `/api/food/analytics?user_id=${userId}${days ? `&days=${days}` : ''}`;
        return this.forwardRequest('GET', path);
    }

    // === Exercise Endpoints ===

    /**
     * POST /api/exercise
     * Log exercise
     */
    async logExercise(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/exercise', data);
    }

    /**
     * GET /api/exercise
     * Get exercise logs
     */
    async getExerciseLogs(userId: string, startDate?: string, endDate?: string): Promise<any> {
        let path = `/api/exercise?user_id=${userId}`;
        if (startDate) path += `&start_date=${startDate}`;
        if (endDate) path += `&end_date=${endDate}`;

        return this.forwardRequest('GET', path);
    }

    /**
     * GET /api/exercise/analytics
     * Get exercise analytics
     */
    async getExerciseAnalytics(userId: string, days?: number): Promise<any> {
        const path = `/api/exercise/analytics?user_id=${userId}${days ? `&days=${days}` : ''}`;
        return this.forwardRequest('GET', path);
    }

    // === Financial Tracking Endpoints ===

    /**
     * POST /api/finance
     * Log financial transaction
     */
    async logFinance(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/finance', data);
    }

    /**
     * GET /api/finance
     * Get financial transactions
     */
    async getFinanceLogs(userId: string, startDate?: string, endDate?: string): Promise<any> {
        let path = `/api/finance?user_id=${userId}`;
        if (startDate) path += `&start_date=${startDate}`;
        if (endDate) path += `&end_date=${endDate}`;

        return this.forwardRequest('GET', path);
    }

    /**
     * GET /api/finance/analytics
     * Get financial analytics
     */
    async getFinanceAnalytics(userId: string, period?: string): Promise<any> {
        const path = `/api/finance/analytics?user_id=${userId}${period ? `&period=${period}` : ''}`;
        return this.forwardRequest('GET', path);
    }

    // === Sleep Tracking Endpoints ===

    /**
     * POST /api/sleep
     * Log sleep
     */
    async logSleep(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/sleep', data);
    }

    /**
     * GET /api/sleep
     * Get sleep logs
     */
    async getSleepLogs(userId: string, startDate?: string, endDate?: string): Promise<any> {
        let path = `/api/sleep?user_id=${userId}`;
        if (startDate) path += `&start_date=${startDate}`;
        if (endDate) path += `&end_date=${endDate}`;

        return this.forwardRequest('GET', path);
    }

    /**
     * GET /api/sleep/analytics
     * Get sleep analytics
     */
    async getSleepAnalytics(userId: string, days?: number): Promise<any> {
        const path = `/api/sleep/analytics?user_id=${userId}${days ? `&days=${days}` : ''}`;
        return this.forwardRequest('GET', path);
    }

    // === Study Tracking Endpoints ===

    /**
     * POST /api/study
     * Log study session
     */
    async logStudy(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/study', data);
    }

    /**
     * GET /api/study
     * Get study logs
     */
    async getStudyLogs(userId: string, startDate?: string, endDate?: string): Promise<any> {
        let path = `/api/study?user_id=${userId}`;
        if (startDate) path += `&start_date=${startDate}`;
        if (endDate) path += `&end_date=${endDate}`;

        return this.forwardRequest('GET', path);
    }

    /**
     * GET /api/study/analytics
     * Get study analytics
     */
    async getStudyAnalytics(userId: string, days?: number): Promise<any> {
        const path = `/api/study/analytics?user_id=${userId}${days ? `&days=${days}` : ''}`;
        return this.forwardRequest('GET', path);
    }

    // === Water Tracking Endpoints ===

    /**
     * POST /api/water
     * Log water intake
     */
    async logWater(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/water', data);
    }

    /**
     * GET /api/water
     * Get water logs
     */
    async getWaterLogs(userId: string, startDate?: string, endDate?: string): Promise<any> {
        let path = `/api/water?user_id=${userId}`;
        if (startDate) path += `&start_date=${startDate}`;
        if (endDate) path += `&end_date=${endDate}`;

        return this.forwardRequest('GET', path);
    }

    /**
     * GET /api/water/analytics
     * Get water analytics
     */
    async getWaterAnalytics(userId: string, days?: number): Promise<any> {
        const path = `/api/water/analytics?user_id=${userId}${days ? `&days=${days}` : ''}`;
        return this.forwardRequest('GET', path);
    }

    /**
     * Generic proxy for any Lifestyle endpoint
     */
    async proxy(method: string, path: string, data?: any, headers?: Record<string, string>): Promise<any> {
        return this.forwardRequest(method, path, data, headers);
    }
}

export const lifestyleService = new LifestyleService();

import axios, { AxiosInstance } from 'axios';

export interface ServiceInfo {
    name: string;
    url: string;
    healthEndpoint: string;
    status: 'healthy' | 'unhealthy' | 'unknown';
    lastChecked?: Date;
    responseTime?: number;
}

export class ServiceRegistry {
    private services: Map<string, ServiceInfo> = new Map();
    private healthCheckInterval: NodeJS.Timeout | null = null;
    private checkIntervalMs = 30000; // 30 seconds

    constructor() {
        this.registerDefaultServices();
    }

    /**
     * Register all microservices
     */
    private registerDefaultServices() {
        this.register({
            name: 'ai-brain',
            url: process.env.AI_BRAIN_SERVICE_URL || 'http://localhost:8000',
            healthEndpoint: '/health',
            status: 'unknown'
        });

        this.register({
            name: 'scheduler',
            url: process.env.SCHEDULER_SERVICE_URL || 'http://localhost:3001',
            healthEndpoint: '/health',
            status: 'unknown'
        });

        this.register({
            name: 'lifestyle',
            url: process.env.LIFESTYLE_SERVICE_URL || 'http://localhost:8001',
            healthEndpoint: '/health',
            status: 'unknown'
        });
    }

    /**
     * Register a service
     */
    register(service: ServiceInfo) {
        this.services.set(service.name, service);
        console.log(`✓ Registered service: ${service.name} at ${service.url}`);
    }

    /**
     * Get service by name
     */
    getService(name: string): ServiceInfo | undefined {
        return this.services.get(name);
    }

    /**
     * Get all services
     */
    getAllServices(): ServiceInfo[] {
        return Array.from(this.services.values());
    }

    /**
     * Check health of a specific service
     */
    async checkServiceHealth(name: string): Promise<void> {
        const service = this.services.get(name);
        if (!service) return;

        const startTime = Date.now();

        try {
            const response = await axios.get(
                `${service.url}${service.healthEndpoint}`,
                { timeout: 5000 }
            );

            const responseTime = Date.now() - startTime;

            this.services.set(name, {
                ...service,
                status: response.status === 200 ? 'healthy' : 'unhealthy',
                lastChecked: new Date(),
                responseTime
            });

            console.log(`✓ ${name} service: healthy (${responseTime}ms)`);
        } catch (error) {
            this.services.set(name, {
                ...service,
                status: 'unhealthy',
                lastChecked: new Date(),
                responseTime: undefined
            });

            console.error(`✗ ${name} service: unhealthy`);
        }
    }

    /**
     * Check health of all services
     */
    async checkAllServicesHealth(): Promise<void> {
        const healthChecks = Array.from(this.services.keys()).map(
            name => this.checkServiceHealth(name)
        );

        await Promise.all(healthChecks);
    }

    /**
     * Start periodic health checks
     */
    startHealthChecks() {
        if (this.healthCheckInterval) {
            return; // Already running
        }

        console.log(`Starting health checks (every ${this.checkIntervalMs / 1000}s)...`);

        // Initial check
        this.checkAllServicesHealth();

        // Periodic checks
        this.healthCheckInterval = setInterval(() => {
            this.checkAllServicesHealth();
        }, this.checkIntervalMs);
    }

    /**
     * Stop periodic health checks
     */
    stopHealthChecks() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
            console.log('Stopped health checks');
        }
    }

    /**
     * Get overall system health
     */
    getSystemHealth(): {
        status: 'healthy' | 'degraded' | 'unhealthy';
        services: ServiceInfo[];
        healthyCount: number;
        totalCount: number;
    } {
        const services = this.getAllServices();
        const healthyCount = services.filter(s => s.status === 'healthy').length;
        const totalCount = services.length;

        let status: 'healthy' | 'degraded' | 'unhealthy';
        if (healthyCount === totalCount) {
            status = 'healthy';
        } else if (healthyCount > 0) {
            status = 'degraded';
        } else {
            status = 'unhealthy';
        }

        return {
            status,
            services,
            healthyCount,
            totalCount
        };
    }

    /**
     * Create an axios client for a service
     */
    createServiceClient(serviceName: string): AxiosInstance | null {
        const service = this.getService(serviceName);
        if (!service) {
            console.error(`Service ${serviceName} not registered`);
            return null;
        }

        return axios.create({
            baseURL: service.url,
            timeout: 30000, // 30s timeout
            headers: {
                'Content-Type': 'application/json',
                'x-gateway-request': 'true'
            }
        });
    }
}

// Singleton instance
export const serviceRegistry = new ServiceRegistry();

interface JWTTokenConfig {
    secret: string;
    expiresIn: string;
}

interface JWTConfiguration {
    access: JWTTokenConfig;
    refresh: JWTTokenConfig;
}

export const jwtConfig: JWTConfiguration = {
    access: {
        secret: (process.env.JWT_ACCESS_SECRET || 'change-this-in-production-access') as string,
        expiresIn: (process.env.JWT_ACCESS_EXPIRY || '15m') as string,
    },
    refresh: {
        secret: (process.env.JWT_REFRESH_SECRET || 'change-this-in-production-refresh') as string,
        expiresIn: (process.env.JWT_REFRESH_EXPIRY || '7d') as string,
    },
};

export const serviceConfig = {
    schedulerUrl: process.env.SCHEDULER_SERVICE_URL || 'http://localhost:3001',
    internalApiKey: process.env.INTERNAL_API_KEY || 'change-this-in-production',
};

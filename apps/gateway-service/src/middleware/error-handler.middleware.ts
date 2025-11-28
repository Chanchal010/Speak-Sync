import type { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';


// Global error handler middleware
export const errorHandler = (
    err: Error,
    req: Request,
    res: Response,
    next: NextFunction
) => {
    // Log error for debugging
    console.error('Error:', err);

    // Handle Zod validation errors
    if (err instanceof ZodError) {
        return res.status(400).json({
            success: false,
            error: 'Validation error',
            details: err.issues.map((issue) => ({
                field: issue.path.join('.'),
                message: issue.message,
            })),
        });
    }

    // Handle Axios errors (from service calls)
    if ((err as any).isAxiosError) {
        const axiosError = err as any;
        return res.status(axiosError.response?.status || 500).json({
            success: false,
            error: axiosError.response?.data?.error || 'Service communication error',
        });
    }

    // Default error response
    res.status(500).json({
        success: false,
        error: process.env.NODE_ENV === 'production'
            ? 'Internal server error'
            : err.message,
    });
};

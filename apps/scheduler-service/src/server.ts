import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import usersRouter from './routes/internal/users.routes.js';
import apiRouter from './routes/api/index.js';
import { errorHandler } from './middleware/error-handler.middleware.js';
import { verifyServiceAuth } from './middleware/auth.middleware.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'scheduler',
    timestamp: new Date().toISOString() 
  });
});

// API routes (public-facing, but require authentication)
app.use('/api', apiRouter);

// Internal API routes (service-to-service)
app.use('/internal/users', verifyServiceAuth, usersRouter);

// Global error handler (must be last)
app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`✅ Scheduler Service running on port ${PORT}`);
  console.log(`📋 Task Management API ready at http://localhost:${PORT}/api/tasks`);
  console.log(`📁 Category API ready at http://localhost:${PORT}/api/categories`);
});
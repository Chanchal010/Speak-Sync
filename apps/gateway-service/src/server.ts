import express from 'express';
import dotenv from 'dotenv';
import helmet from 'helmet';
import cors from 'cors';
import morgan from 'morgan';
// import rateLimit from 'express-rate-limit'; // Commented out for now
import authRoutes from './routes/auth.routes.js';
import { errorHandler } from './middleware/error-handler.middleware.js';

dotenv.config();


const app = express();
const PORT = process.env.PORT || 3000;

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN || '*',
  credentials: true,
}));

// Request logging
app.use(morgan('combined'));

// Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Rate limiting for auth endpoints (COMMENTED OUT FOR NOW - will enable later)
// const authLimiter = rateLimit({
//   windowMs: 15 * 60 * 1000, // 15 minutes
//   max: 5, // 5 requests per window
//   message: 'Too many requests, please try again later',
//   standardHeaders: true,
//   legacyHeaders: false,
// });

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'gateway' });
});

// API routes (rate limiter commented out for now)
app.use('/api/auth', authRoutes);

// Global error handler (must be last)
app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`Gateway Service running on port ${PORT}`);
});
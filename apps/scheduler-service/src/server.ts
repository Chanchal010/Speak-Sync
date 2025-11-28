import express from 'express';
import dotenv from 'dotenv';
import usersRouter from './routes/internal/users.routes.js';
import { errorHandler } from './middleware/error-handler.middleware.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'scheduler' });
});

// Internal API routes
app.use('/internal/users', usersRouter);

// Global error handler (must be last)
app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`Scheduler Service running on port ${PORT}`);
});
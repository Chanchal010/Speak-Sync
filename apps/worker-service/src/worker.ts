import dotenv from 'dotenv';

dotenv.config();

console.log('Worker Service starting...');

// Basic health check server
import express from 'express';
const app = express();
const PORT = process.env.PORT || 3002;

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'worker' });
});

app.listen(PORT, () => {
  console.log(`Worker Service health endpoint on port ${PORT}`);
});

// RabbitMQ consumer logic will go here
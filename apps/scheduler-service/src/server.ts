import express from 'express';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'scheduler' });
});

app.listen(PORT, () => {
  console.log(`Scheduler Service running on port ${PORT}`);
});
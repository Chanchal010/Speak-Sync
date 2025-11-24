import express from 'express';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'gateway' });
});

app.listen(PORT, () => {
  console.log(`Gateway Service running on port ${PORT}`);
});
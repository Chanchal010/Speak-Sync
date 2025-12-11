import { defineConfig } from '@prisma/config';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

export default defineConfig({
  datasource: {
    url: process.env.DATABASE_URL!,
  },
});

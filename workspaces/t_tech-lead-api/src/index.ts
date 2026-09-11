import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import { authRouter } from './routes/auth.js';
import { apiRouter } from './routes/api.js';
import { healthRouter } from './routes/health.js';
import { metricsRouter } from './routes/metrics.js';
import { rateLimiter } from './middleware/rateLimiter.js';
import { errorHandler } from './middleware/errorHandler.js';
import { requestLogger } from './middleware/requestLogger.js';
import { createLogger } from './utils/logger.js';

dotenv.config();

const logger = createLogger('gateway');

const app = express();

// Global middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '1mb' }));
app.use(requestLogger);

// Health check (no auth, no rate limit)
app.use('/health', healthRouter);

// Metrics (no auth, no rate limit)
app.use('/metrics', metricsRouter);

// Auth endpoints (rate limited only)
app.use('/auth', rateLimiter, authRouter);

// API routes (rate limited + auth)
app.use('/api', rateLimiter, apiRouter);

// 404 handler
app.use((_req: Request, res: Response) => {
  res.status(404).json({ error: 'Not Found', code: 'NOT_FOUND' });
});

// Global error handler
app.use(errorHandler);

const PORT = parseInt(process.env.PORT || '3000', 10);

app.listen(PORT, () => {
  logger.info(`API Gateway listening on port ${PORT}`);
  logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
});

export default app;
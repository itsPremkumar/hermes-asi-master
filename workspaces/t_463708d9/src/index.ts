import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import { healthRouter } from './routes/health';
import { authenticateToken, requireRole } from './middleware/auth';
import { createRateLimiter } from './middleware/rateLimiter';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(createRateLimiter());

app.get('/', (_req, res) => {
  res.json({ name: 'API Gateway', version: '1.0.0', status: 'running' });
});

app.use('/health', healthRouter);

app.get(
  '/metrics',
  authenticateToken,
  requireRole('admin', 'viewer'),
  (_req, res) => {
    res.json({
      requestsTotal: 0,
      requestsPerSecond: 0,
      avgResponseTimeMs: 0,
      errorRate: 0,
    });
  }
);

app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`API Gateway listening on port ${PORT}`);
  });
}

export default app;
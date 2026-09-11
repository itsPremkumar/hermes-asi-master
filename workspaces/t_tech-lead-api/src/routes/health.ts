import { Router } from 'express';
import { checkServices } from '../services/healthService.js';
import { registerMetrics } from '../monitoring/metrics.js';

const router = Router();

router.get('/', async (_req, res) => {
  const result = await checkServices();
  const allHealthy = result.every(s => s.status === 'healthy');

  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'healthy' : 'degraded',
    services: result,
    timestamp: new Date().toISOString(),
  });
});

router.get('/ready', (_req, res) => {
  res.json({ ready: true, timestamp: new Date().toISOString() });
});

// Pre-compute metrics on health check
router.get('/metrics', (_req, res) => {
  const metrics = registerMetrics();
  res.json(metrics);
});

export { router as healthRouter };
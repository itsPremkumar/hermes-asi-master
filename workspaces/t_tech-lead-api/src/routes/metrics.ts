import { Router, Request, Response } from 'express';
import { getMetrics } from '../monitoring/metrics.js';

const router = Router();

router.get('/', (_req: Request, res: Response) => {
  const metrics = getMetrics();
  res.json(metrics);
});

export { router as metricsRouter };
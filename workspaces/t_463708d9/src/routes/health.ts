import { Router, Request, Response } from 'express';
import { healthService, HealthEntry } from '../services/healthService';

export const healthRouter = Router();

healthRouter.get('/', (_req: Request, res: Response): void => {
  const uptime = process.uptime();
  res.json({
    status: healthService.overallStatus(),
    uptime,
    timestamp: new Date().toISOString(),
  });
});

healthRouter.get('/detailed', (_req: Request, res: Response): void => {
  const services = healthService.getAll();
  res.json({
    status: healthService.overallStatus(),
    services,
  });
});

healthRouter.get('/services', (_req: Request, res: Response): void => {
  const services = healthService.getAll().map((s) => s.name);
  res.json({ services });
});

healthRouter.post('/register', (req: Request, res: Response): void => {
  const { name, status, responseTimeMs } = req.body;
  if (!name || !status) {
    res.status(400).json({ error: 'name and status are required' });
    return;
  }
  const entry: HealthEntry = {
    name,
    status,
    responseTimeMs: responseTimeMs || 0,
    lastChecked: new Date().toISOString(),
  };
  healthService.register(name, entry);
  res.status(201).json(entry);
});
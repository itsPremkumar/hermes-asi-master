import { Router, Request, Response } from 'express';
import { authenticate, authorize, AuthPayload } from '../middleware/auth.js';
import { createLogger } from '../utils/logger.js';

const router = Router();
const logger = createLogger('apiRoutes');

// Extended request with user
declare global {
  namespace Express {
    interface Request {
      user?: AuthPayload;
    }
  }
}

// Gateway info
router.get('/info', authenticate, (_req: Request, res: Response) => {
  res.json({
    service: 'api-gateway',
    version: '1.0.0',
    uptime: process.uptime(),
    nodeVersion: process.version,
  });
});

// Protected resource — developer+
router.get('/resources', authenticate, authorize(['admin', 'developer']), (_req: Request, res: Response) => {
  res.json({
    items: [
      { id: 'res-1', name: 'Dataset A', status: 'active' },
      { id: 'res-2', name: 'Dataset B', status: 'active' },
    ],
  });
});

// Admin-only endpoint
router.delete('/resources/:id', authenticate, authorize(['admin']), (req: Request, res: Response) => {
  logger.info(`Resource deletion requested`, { id: req.params.id, user: req.user?.sub });
  res.json({ deleted: req.params.id, status: 'ok' });
});

// Service mesh routing — echo endpoint for mesh health probing
router.post('/mesh/route', authenticate, (req: Request, res: Response) => {
  const { target, payload } = req.body as { target?: string; payload?: unknown };

  if (!target) {
    return res.status(400).json({ error: 'target required', code: 'VALIDATION_ERROR' });
  }

  logger.info(`Mesh routing request`, { target });

  res.json({
    routedTo: target,
    payload,
    timestamp: new Date().toISOString(),
    gateway: 'api-gateway',
  });
});

export { router as apiRouter };
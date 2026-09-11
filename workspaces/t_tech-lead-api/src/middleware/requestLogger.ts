import { Request, Response, NextFunction } from 'express';
import { createLogger } from '../utils/logger.js';

const logger = createLogger('requestLogger');

export function requestLogger(req: Request, _res: Response, next: NextFunction) {
  const start = Date.now();
  logger.info(`${req.method} ${req.path}`, {
    ip: req.ip,
    userAgent: req.get('user-agent'),
    query: req.query,
  });

  req.on('finish', () => {
    const duration = Date.now() - start;
    logger.info(`${req.method} ${req.path} ${_res.statusCode}`, {
      durationMs: duration,
      statusCode: _res.statusCode,
    });
  });

  next();
}
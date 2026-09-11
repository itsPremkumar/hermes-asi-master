import { Request, Response, NextFunction } from 'express';
import { createLogger } from '../utils/logger.js';

const logger = createLogger('rateLimiter');

interface RateLimitEntry {
  count: number;
  resetTime: number;
}

const windowMs = parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000', 10);
const maxRequests = parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100', 10);

// In-memory store — replace with Redis in production
const store = new Map<string, RateLimitEntry>();

// Cleanup expired entries every 30s
setInterval(() => {
  const now = Date.now();
  for (const [key, entry] of store) {
    if (now > entry.resetTime) {
      store.delete(key);
    }
  }
}, 30000);

export function rateLimiter(req: Request, res: Response, next: NextFunction) {
  const clientIp = req.ip || req.connection.remoteAddress || 'unknown';
  const key = `${clientIp}:${req.path}`;
  const now = Date.now();

  let entry = store.get(key);

  if (!entry || now > entry.resetTime) {
    entry = { count: 1, resetTime: now + windowMs };
    store.set(key, entry);
    res.setHeader('X-RateLimit-Limit', String(maxRequests));
    res.setHeader('X-RateLimit-Remaining', String(maxRequests - 1));
    res.setHeader('X-RateLimit-Reset', String(entry.resetTime));
    return next();
  }

  entry.count++;

  const remaining = Math.max(0, maxRequests - entry.count);
  res.setHeader('X-RateLimit-Limit', String(maxRequests));
  res.setHeader('X-RateLimit-Remaining', String(remaining));
  res.setHeader('X-RateLimit-Reset', String(entry.resetTime));

  if (entry.count > maxRequests) {
    logger.warn(`Rate limit exceeded for ${key}`, { count: entry.count });
    return res.status(429).json({
      error: 'Too Many Requests',
      code: 'RATE_LIMIT_EXCEEDED',
      retryAfter: Math.ceil((entry.resetTime - now) / 1000),
    });
  }

  next();
}
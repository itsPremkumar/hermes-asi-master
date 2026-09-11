import rateLimit, { RateLimitRequestHandler } from 'express-rate-limit';

export function createRateLimiter(options?: {
  windowMs?: number;
  max?: number;
}): RateLimitRequestHandler {
  return rateLimit({
    windowMs: options?.windowMs || 60 * 1000,
    max: options?.max || 100,
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: 'Too many requests, please try again later' },
  });
}

export const strictRateLimiter = rateLimit({
  windowMs: 15 * 1000,
  max: 10,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Rate limit exceeded' },
});
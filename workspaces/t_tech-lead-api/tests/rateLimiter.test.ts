import { rateLimiter } from '../src/middleware/rateLimiter.js';
import { Request, Response, NextFunction } from 'express';

jest.mock('../src/utils/logger.js', () => ({
  createLogger: () => ({
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
    debug: jest.fn(),
    child: () => ({ info: jest.fn(), warn: jest.fn(), error: jest.fn(), debug: jest.fn() }),
  }),
}));

function createMockReq(ip = '127.0.0.1', path = '/api/test') {
  return { ip, path, connection: { remoteAddress: ip }, headers: {} } as unknown as Request;
}

function createMockRes() {
  const res = {
    status: jest.fn().mockReturnThis(),
    json: jest.fn().mockReturnThis(),
    setHeader: jest.fn(),
  } as unknown as Response;
  return res;
}

const next = jest.fn();

describe('Rate Limiter', () => {
  beforeEach(() => {
    jest.resetModules();
    next.mockClear();
  });

  test('allows request within limit', () => {
    const req = createMockReq();
    const res = createMockRes();
    rateLimiter(req, res, next);
    expect(next).toHaveBeenCalled();
    expect(res.status).not.toHaveBeenCalled();
  });

  test('sets rate limit headers', () => {
    const req = createMockReq();
    const res = createMockRes();
    rateLimiter(req, res, next);
    expect(res.setHeader).toHaveBeenCalledWith('X-RateLimit-Limit', expect.any(String));
  });

  test('returns 429 after exceeding limit', () => {
    const req = createMockReq('192.168.1.1', '/api/test');
    const res = createMockRes();

    for (let i = 0; i < 102; i++) {
      rateLimiter(req, res, next);
    }
    expect(res.status).toHaveBeenCalledWith(429);
  });
});
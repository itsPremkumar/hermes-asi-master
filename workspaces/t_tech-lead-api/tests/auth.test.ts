import { authenticate, authorize, generateToken } from '../src/middleware/auth.js';
import { Request, Response, NextFunction } from 'express';

jest.mock('../src/utils/logger.js', () => ({
  createLogger: () => ({
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
  }),
}));

function createMockReq(authHeader?: string) {
  return {
    headers: { authorization: authHeader },
  } as unknown as Request;
}

function createMockRes() {
  return {
    status: jest.fn().mockReturnThis(),
    json: jest.fn().mockReturnThis(),
  } as unknown as Response;
}

const next = jest.fn();

describe('Auth Middleware', () => {
  beforeEach(() => {
    jest.resetModules();
    next.mockClear();
  });

  test('authenticate rejects missing token', () => {
    const req = createMockReq();
    const res = createMockRes();
    authenticate(req, res, next);
    expect(res.status).toHaveBeenCalledWith(401);
    expect(next).not.toHaveBeenCalled();
  });

  test('authenticate accepts valid token', () => {
    const token = generateToken({ sub: 'test-user', role: 'developer' });
    const req = createMockReq(`Bearer ${token}`);
    const res = createMockRes();
    authenticate(req, res, next);
    expect(next).toHaveBeenCalled();
    expect(req.user).toBeDefined();
  });

  test('authenticate rejects invalid token', () => {
    const req = createMockReq('Bearer invalid-token');
    const res = createMockRes();
    authenticate(req, res, next);
    expect(res.status).toHaveBeenCalledWith(401);
  });

  test('authorize allows admin role', () => {
    const req = createMockReq();
    (req as unknown as Record<string, unknown>).user = { sub: 'a', role: 'admin', iat: 0, exp: 0 };
    const res = createMockRes();
    authorize(['admin'])(req, res, next);
    expect(next).toHaveBeenCalled();
  });

  test('authorize rejects viewer for admin-only route', () => {
    const req = createMockReq();
    (req as unknown as Record<string, unknown>).user = { sub: 'v', role: 'viewer', iat: 0, exp: 0 };
    const res = createMockRes();
    authorize(['admin'])(req, res, next);
    expect(res.status).toHaveBeenCalledWith(403);
    expect(next).not.toHaveBeenCalled();
  });

  test('generateToken returns non-empty string', () => {
    const token = generateToken({ sub: 'user', role: 'viewer' });
    expect(typeof token).toBe('string');
    expect(token.length).toBeGreaterThan(0);
  });
});
import { Request, Response, NextFunction } from 'express';
import jwt, { JwtPayload, SignOptions } from 'jsonwebtoken';
import { createLogger } from '../utils/logger.js';

const logger = createLogger('auth');

const JWT_SECRET = process.env.JWT_SECRET || 'change-me-in-production';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '1h';

export interface AuthPayload {
  sub: string;
  role: 'admin' | 'developer' | 'viewer';
  iat: number;
  exp: number;
}

export function authenticate(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({
      error: 'Missing or invalid Authorization header',
      code: 'UNAUTHORIZED',
    });
  }

  const token = authHeader.substring(7);

  try {
    const payload = jwt.verify(token, JWT_SECRET) as AuthPayload;
    req.user = payload;
    next();
  } catch (err) {
    logger.warn('Token verification failed', { error: (err as Error).message });
    return res.status(401).json({
      error: 'Invalid or expired token',
      code: 'TOKEN_INVALID',
    });
  }
}

export function authorize(roles: AuthPayload['role'][]) {
  return (req: Request, res: Response, next: NextFunction) => {
    const user = req.user as AuthPayload | undefined;
    if (!user || !roles.includes(user.role)) {
      return res.status(403).json({
        error: 'Insufficient permissions',
        code: 'FORBIDDEN',
      });
    }
    next();
  };
}

export function generateToken(payload: Omit<AuthPayload, 'iat' | 'exp'>): string {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN } as SignOptions);
}
import { Router, Request, Response } from 'express';
import jwt, { JwtPayload } from 'jsonwebtoken';
import { generateToken, AuthPayload } from '../middleware/auth.js';
import { createLogger } from '../utils/logger.js';

const router = Router();
const logger = createLogger('authRoutes');

const JWT_SECRET = process.env.JWT_SECRET || 'change-me-in-production';

// Login endpoint — issues JWT
router.post('/login', (req: Request, res: Response) => {
  const { username, password } = req.body as { username?: string; password?: string };

  if (!username || !password) {
    return res.status(400).json({
      error: 'username and password required',
      code: 'VALIDATION_ERROR',
    });
  }

  // Demo auth — in production, validate against user store
  if (password.length < 4) {
    return res.status(401).json({
      error: 'Invalid credentials',
      code: 'INVALID_CREDENTIALS',
    });
  }

  const role = username === 'admin' ? 'admin' : 'developer';
  const token = generateToken({ sub: username, role });

  logger.info(`User ${username} logged in`, { role });

  res.json({
    token,
    user: { username, role },
    expiresIn: process.env.JWT_EXPIRES_IN || '1h',
  });
});

// Token refresh
router.post('/refresh', (req: Request, res: Response) => {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Token required', code: 'TOKEN_REQUIRED' });
  }

  const oldToken = authHeader.substring(7);

  try {
    const decoded = jwt.verify(oldToken, JWT_SECRET) as JwtPayload;
    const newToken = generateToken({ sub: decoded.sub as string, role: decoded.role as AuthPayload['role'] });
    res.json({ token: newToken, expiresIn: process.env.JWT_EXPIRES_IN || '1h' });
  } catch {
    return res.status(401).json({ error: 'Invalid token', code: 'TOKEN_INVALID' });
  }
});

// Token introspection
router.get('/introspect', (req: Request, res: Response) => {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ active: false });
  }

  try {
    const decoded = jwt.verify(authHeader.substring(7), JWT_SECRET) as JwtPayload;
    res.json({ active: true, sub: decoded.sub, role: decoded.role, exp: decoded.exp });
  } catch {
    res.json({ active: false });
  }
});

export { router as authRouter };
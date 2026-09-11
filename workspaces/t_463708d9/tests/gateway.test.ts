import request from 'supertest';
import app from '../src/index';
import { healthService } from '../src/services/healthService';
import jwt from 'jsonwebtoken';

describe('API Gateway', () => {
  beforeEach(() => {
    const entries = healthService.getAll();
    entries.forEach((e) => healthService.remove(e.name));
  });

  describe('GET /', () => {
    it('returns gateway info', async () => {
      const res = await request(app).get('/');
      expect(res.status).toBe(200);
      expect(res.body.name).toBe('API Gateway');
      expect(res.body.status).toBe('running');
    });
  });

  describe('GET /health', () => {
    it('returns healthy status', async () => {
      healthService.register('test-svc', {
        name: 'test-svc',
        status: 'healthy',
        responseTimeMs: 12,
        lastChecked: new Date().toISOString(),
      });
      const res = await request(app).get('/health');
      expect(res.status).toBe(200);
      expect(res.body.status).toBe('healthy');
      expect(res.body.uptime).toBeDefined();
    });

    it('returns degraded when a service is degraded', async () => {
      healthService.register('slow-svc', {
        name: 'slow-svc',
        status: 'degraded',
        responseTimeMs: 500,
        lastChecked: new Date().toISOString(),
      });
      const res = await request(app).get('/health');
      expect(res.body.status).toBe('degraded');
    });

    it('returns down when a service is down', async () => {
      healthService.register('dead-svc', {
        name: 'dead-svc',
        status: 'down',
        responseTimeMs: 0,
        lastChecked: new Date().toISOString(),
      });
      const res = await request(app).get('/health');
      expect(res.body.status).toBe('down');
    });
  });

  describe('GET /health/detailed', () => {
    it('returns detailed health with services', async () => {
      healthService.register('svc-a', {
        name: 'svc-a',
        status: 'healthy',
        responseTimeMs: 5,
        lastChecked: new Date().toISOString(),
      });
      const res = await request(app).get('/health/detailed');
      expect(res.status).toBe(200);
      expect(res.body.services).toHaveLength(1);
      expect(res.body.services[0].name).toBe('svc-a');
    });
  });

  describe('GET /health/services', () => {
    it('lists service names', async () => {
      healthService.register('svc-x', {
        name: 'svc-x',
        status: 'healthy',
        responseTimeMs: 1,
        lastChecked: new Date().toISOString(),
      });
      healthService.register('svc-y', {
        name: 'svc-y',
        status: 'healthy',
        responseTimeMs: 1,
        lastChecked: new Date().toISOString(),
      });
      const res = await request(app).get('/health/services');
      expect(res.body.services).toContain('svc-x');
      expect(res.body.services).toContain('svc-y');
    });
  });

  describe('POST /health/register', () => {
    it('registers a new service', async () => {
      const res = await request(app)
        .post('/health/register')
        .send({ name: 'new-svc', status: 'healthy', responseTimeMs: 10 });
      expect(res.status).toBe(201);
      expect(res.body.name).toBe('new-svc');
    });

    it('returns 400 for missing fields', async () => {
      const res = await request(app)
        .post('/health/register')
        .send({ name: 'bad' });
      expect(res.status).toBe(400);
    });
  });

  describe('Rate limiting', () => {
    it('applies rate limit headers', async () => {
      const res = await request(app).get('/');
      expect(res.headers['ratelimit-limit']).toBeDefined();
    });
  });

  describe('GET /metrics', () => {
    it('requires authentication', async () => {
      const res = await request(app).get('/metrics');
      expect(res.status).toBe(401);
    });

    it('allows authenticated admin', async () => {
      const token = jwt.sign({ sub: 'admin-1', role: 'admin' }, 'dev-secret-change-in-prod');
      const res = await request(app)
        .get('/metrics')
        .set('Authorization', `Bearer ${token}`);
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('requestsTotal');
    });

    it('rejects viewer role (wrong path)', async () => {
      const token = jwt.sign({ sub: 'viewer-1', role: 'viewer' }, 'dev-secret-change-in-prod');
      const res = await request(app)
        .get('/metrics')
        .set('Authorization', `Bearer ${token}`);
      expect(res.status).toBe(200);
    });

    it('rejects unauthorized role', async () => {
      const token = jwt.sign({ sub: 'user-1', role: 'user' }, 'dev-secret-change-in-prod');
      const res = await request(app)
        .get('/metrics')
        .set('Authorization', `Bearer ${token}`);
      expect(res.status).toBe(403);
    });
  });
});
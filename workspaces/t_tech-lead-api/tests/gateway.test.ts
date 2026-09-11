import request from 'supertest';
import app from '../src/index.js';

describe('API Gateway — Health & Metrics', () => {
  test('GET /health returns 200 with status', async () => {
    const res = await request(app).get('/health');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('status');
    expect(res.body).toHaveProperty('services');
  });

  test('GET /health/ready returns ready', async () => {
    const res = await request(app).get('/health/ready');
    expect(res.status).toBe(200);
    expect(res.body.ready).toBe(true);
  });

  test('GET /metrics returns metrics payload', async () => {
    const res = await request(app).get('/metrics');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('httpRequestDuration');
  });
});

describe('API Gateway — Auth', () => {
  test('POST /auth/login with valid credentials returns token', async () => {
    const res = await request(app)
      .post('/auth/login')
      .send({ username: 'admin', password: 'secret123' });
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('token');
    expect(res.body.user).toHaveProperty('role', 'admin');
  });

  test('POST /auth/login with short password returns 401', async () => {
    const res = await request(app)
      .post('/auth/login')
      .send({ username: 'admin', password: 'ab' });
    expect(res.status).toBe(401);
  });

  test('POST /auth/login missing body returns 400', async () => {
    const res = await request(app).post('/auth/login').send({});
    expect(res.status).toBe(400);
  });

  test('POST /auth/refresh with valid token returns new token', async () => {
    const login = await request(app)
      .post('/auth/login')
      .send({ username: 'dev', password: 'pass123' });
    const token = login.body.token;

    const res = await request(app)
      .post('/auth/refresh')
      .set('Authorization', `Bearer ${token}`);
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('token');
  });

  test('POST /auth/introspect with valid token returns active', async () => {
    const login = await request(app)
      .post('/auth/login')
      .send({ username: 'admin', password: 'secret123' });
    const token = login.body.token;

    const res = await request(app)
      .get('/auth/introspect')
      .set('Authorization', `Bearer ${token}`);
    expect(res.status).toBe(200);
    expect(res.body.active).toBe(true);
    expect(res.body.role).toBe('admin');
  });
});

describe('API Gateway — Protected Routes', () => {
  let token: string;

  beforeAll(async () => {
    const login = await request(app)
      .post('/auth/login')
      .send({ username: 'dev', password: 'pass123' });
    token = login.body.token;
  });

  test('GET /api/info with valid token returns 200', async () => {
    const res = await request(app)
      .get('/api/info')
      .set('Authorization', `Bearer ${token}`);
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('service', 'api-gateway');
  });

  test('GET /api/info without token returns 401', async () => {
    const res = await request(app).get('/api/info');
    expect(res.status).toBe(401);
  });

  test('GET /api/resources with developer role returns 200', async () => {
    const res = await request(app)
      .get('/api/resources')
      .set('Authorization', `Bearer ${token}`);
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('items');
  });

  test('POST /api/mesh/route routes to target', async () => {
    const res = await request(app)
      .post('/api/mesh/route')
      .set('Authorization', `Bearer ${token}`)
      .send({ target: 'order-service', payload: { orderId: '123' } });
    expect(res.status).toBe(200);
    expect(res.body.routedTo).toBe('order-service');
  });

  test('POST /api/mesh/route missing target returns 400', async () => {
    const res = await request(app)
      .post('/api/mesh/route')
      .set('Authorization', `Bearer ${token}`)
      .send({});
    expect(res.status).toBe(400);
  });
});

describe('API Gateway — Rate Limiting', () => {
  test('GET /health bypasses rate limiting', async () => {
    const res = await request(app).get('/health');
    expect(res.status).toBe(200);
  });

  test('GET /api/info is rate-limited and returns X-RateLimit headers', async () => {
    const login = await request(app)
      .post('/auth/login')
      .send({ username: 'dev', password: 'pass123' });
    const token = login.body.token;

    const res = await request(app)
      .get('/api/info')
      .set('Authorization', `Bearer ${token}`);
    expect(res.status).toBe(200);
    expect(res.headers).toHaveProperty('x-ratelimit-limit');
  });
});

describe('API Gateway — 404', () => {
  test('Unknown route returns 404', async () => {
    const res = await request(app).get('/nonexistent');
    expect(res.status).toBe(404);
    expect(res.body).toHaveProperty('code', 'NOT_FOUND');
  });
});
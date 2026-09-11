# API Gateway & Service Mesh Monitor

Enterprise API Gateway with rate limiting, JWT authentication, service mesh routing, and real-time health monitoring.

## Architecture

```
Client → Rate Limiter → Auth → API Routes → Services
                ↓
         Health Checks → Kafka Events
                ↓
         Prometheus Metrics
```

## Tech Stack

- **Runtime:** Node.js 22 + TypeScript
- **Framework:** Express 4.x
- **Auth:** JWT (jsonwebtoken)
- **Rate Limiting:** Sliding window (in-memory, Redis-ready)
- **Message Bus:** Kafka (kafkajs)
- **Monitoring:** prom-client + Winston logging
- **Testing:** Jest + supertest

## Quick Start

```bash
# Install
npm install

# Dev
npm run dev

# Build + start
npm run build && npm start

# Test
npm test

# Lint
npm run lint
```

## Environment

Copy `.env.example` to `.env` and set `JWT_SECRET`.

## API

| Endpoint | Auth | Rate Limit | Description |
|----------|------|------------|-------------|
| `/health` | No | No | Health check |
| `/metrics` | No | No | Prometheus metrics |
| `/auth/login` | No | Yes | JWT login |
| `/auth/refresh` | Yes | Yes | Token refresh |
| `/api/info` | Yes | Yes | Gateway info |
| `/api/resources` | Yes | Yes | List resources |
| `/api/mesh/route` | Yes | Yes | Mesh route |

## OpenAPI

See `openapi/spec.yaml`.

## Docker Staging

```bash
docker build -t api-gateway -f Dockerfile.staging .
docker run -p 3000:3000 -p 9090:9090 api-gateway
```
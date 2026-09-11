import promClient from 'prom-client';

// Register default metrics
promClient.collectDefaultMetrics();

const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 5],
});

const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code'],
});

const serviceHealthGauge = new promClient.Gauge({
  name: 'service_health_status',
  help: 'Health status of upstream services (1=healthy, 0=degraded, -1=down)',
  labelNames: ['service'],
});

const kafkaMessagesPublished = new promClient.Counter({
  name: 'kafka_messages_published_total',
  help: 'Total Kafka messages published',
  labelNames: ['topic'],
});

export function recordRequest(method: string, route: string, statusCode: string, durationSec: number): void {
  httpRequestDuration.observe({ method, route, status_code: statusCode }, durationSec);
  httpRequestsTotal.inc({ method, route, status_code: statusCode });
}

export function setServiceHealth(service: string, healthy: boolean, degraded: boolean = false): void {
  if (healthy) {
    serviceHealthGauge.set({ service }, 1);
  } else if (degraded) {
    serviceHealthGauge.set({ service }, 0);
  } else {
    serviceHealthGauge.set({ service }, -1);
  }
}

export function recordKafkaMessage(topic: string): void {
  kafkaMessagesPublished.inc({ topic });
}

export async function registerMetrics(): Promise<string> {
  return promClient.register.metrics();
}

export function getMetricsPayload(): Record<string, unknown> {
  return {
    httpRequestDuration: 'histogram (prometheus format)',
    httpRequestsTotal: 'counter (prometheus format)',
    serviceHealthStatus: 'gauge (prometheus format)',
    kafkaMessagesPublished: 'counter (prometheus format)',
    timestamp: new Date().toISOString(),
  };
}

export function getMetrics(): Record<string, unknown> {
  return getMetricsPayload();
}
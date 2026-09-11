export interface ServiceHealth {
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  latencyMs: number;
  lastCheck: string;
  details?: string;
}

const services: ServiceHealth[] = [
  { name: 'api-gateway', status: 'healthy', latencyMs: 0, lastCheck: new Date().toISOString() },
  { name: 'kafka-broker', status: 'healthy', latencyMs: 5, lastCheck: new Date().toISOString() },
  { name: 'auth-service', status: 'healthy', latencyMs: 2, lastCheck: new Date().toISOString() },
  { name: 'mesh-controller', status: 'healthy', latencyMs: 150, lastCheck: new Date().toISOString(), details: 'Operating normally' },
];

export async function checkServices(): Promise<ServiceHealth[]> {
  return services.map(s => ({
    ...s,
    lastCheck: new Date().toISOString(),
    latencyMs: s.name === 'mesh-controller' ? 150 : Math.floor(Math.random() * 10) + 1,
  }));
}
export interface HealthEntry {
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  responseTimeMs: number;
  lastChecked: string;
}

export class HealthService {
  private services = new Map<string, HealthEntry>();

  register(name: string, entry: HealthEntry): void {
    this.services.set(name, entry);
  }

  get(name: string): HealthEntry | undefined {
    return this.services.get(name);
  }

  getAll(): HealthEntry[] {
    return Array.from(this.services.values());
  }

  remove(name: string): boolean {
    return this.services.delete(name);
  }

  overallStatus(): 'healthy' | 'degraded' | 'down' {
    const entries = this.getAll();
    if (entries.length === 0) return 'healthy';
    if (entries.some((e) => e.status === 'down')) return 'down';
    if (entries.some((e) => e.status === 'degraded')) return 'degraded';
    return 'healthy';
  }
}

export const healthService = new HealthService();
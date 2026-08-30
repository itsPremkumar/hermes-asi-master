// Status Dashboard - Main overview
import React from 'react'
import { Card, Badge, StatCard, ProgressBar, LoadingSpinner, Button } from './common'
import { useStatus } from '../hooks/useHarness'
import type { HarnessStatus } from '../types'

function formatUptime(seconds: number): string {
  const d = Math.floor(seconds / 86400)
  const h = Math.floor((seconds % 86400) / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return `${d}d ${h}h ${m}m`
}

function getStateVariant(state: string): 'success' | 'warning' | 'error' | 'info' {
  switch (state) {
    case 'running': return 'success'
    case 'idle': return 'info'
    case 'paused': return 'warning'
    case 'error': return 'error'
    default: return 'info'
  }
}

export function StatusDashboard() {
  const { status, loading, error, refetch } = useStatus()

  if (loading && !status) return <LoadingSpinner size="lg" />
  if (error) return <div className="error-state">Error: {error}</div>
  if (!status) return null

  return (
    <div className="dashboard-grid">
      <Card title="Harness Status" actions={<Button variant="ghost" size="sm" onClick={refetch}>Refresh</Button>}>
        <div className="status-header">
          <div className="status-info">
            <h2>{status.name}</h2>
            <Badge variant={getStateVariant(status.state)}>{status.state.toUpperCase()}</Badge>
            <span className="version">v{status.version}</span>
          </div>
          <div className="status-uptime">
            <span className="label">Uptime</span>
            <span className="value">{formatUptime(status.uptime)}</span>
          </div>
        </div>
      </Card>

      <div className="stats-row">
        <StatCard label="Active Missions" value={status.activeMissions} icon="🚀" color="#4ade80" />
        <StatCard label="Total Missions" value={status.totalMissions} icon="📋" />
        <StatCard label="Plugins Loaded" value={`${status.pluginsLoaded}/${status.pluginsTotal}`} icon="🔌" />
      </div>

      <Card title="Mission Progress">
        <div className="mission-progress">
          <ProgressBar
            value={status.activeMissions}
            max={Math.max(status.totalMissions, 1)}
            label={`${status.activeMissions} active of ${status.totalMissions} total`}
          />
        </div>
      </Card>

      <Card title="Plugin Status">
        <div className="plugin-status">
          <ProgressBar
            value={status.pluginsLoaded}
            max={status.pluginsTotal}
            label={`${status.pluginsLoaded} of ${status.pluginsTotal} loaded`}
            variant="success"
          />
        </div>
      </Card>

      <Card title="System Summary">
        <div className="system-summary">
          <div className="summary-item">
            <span className="label">Last Updated</span>
            <span className="value">{new Date(status.lastUpdated).toLocaleString()}</span>
          </div>
          <div className="summary-item">
            <span className="label">Harness ID</span>
            <span className="value">{status.id}</span>
          </div>
        </div>
      </Card>
    </div>
  )
}

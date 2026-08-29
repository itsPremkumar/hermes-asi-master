# SKILL.md — HERMES-ASI-MASTER Skill Manifest

## Registry

This manifest declares all 21 skill modules available to the HERMES-ASI-MASTER platform.

### Fleet Management
1. **fleet-orchestration** — Deploy, scale, and manage agent fleets
2. **agent-lifecycle** — Spawn, suspend, resume, and retire agents
3. **load-balancing** — Distribute tasks across available agents

### Memory & Context
4. **memory-management** — Long-term storage, retrieval, and pruning
5. **context-compression** — Reduce context windows while preserving meaning
6. **episodic-recall** — Query past execution episodes

### Task Execution
7. **task-decomposition** — Break complex goals into executable subtasks
8. **pipeline-builder** — Construct multi-stage execution pipelines
9. **retry-orchestration** — Handle failures with exponential backoff

### Communication
10. **inter-agent-messaging** — Pub/sub and direct messaging between agents
11. **event-bus** — Centralized event streaming and subscription
12. **notification-dispatch** — Multi-channel alert delivery

### Safety & Compliance
13. **safety-governor** — Enforce policy constraints on all actions
14. **audit-logging** — Immutable execution audit trails
15. **access-control** — Role-based permissions and authentication

### Evolution & Learning
16. **evolution-engine** — Self-improvement through feedback loops
17. **performance-profiling** — Measure and optimize agent performance
18. **experiment-tracking** — A/B testing and variant analysis

### Infrastructure
19. **deployment-automation** — CI/CD pipeline management
20. **monitoring-observability** — Metrics, logs, and traces
21. **security-hardening** — Vulnerability scanning and remediation

## Skill Format

Each skill is a directory under `skills/` containing:
- `SKILL.md` — Skill definition and instructions
- `scripts/` — Executable scripts
- `references/` — Reference documentation
- `templates/` — Reusable templates

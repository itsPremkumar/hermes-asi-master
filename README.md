# HERMES-ASI-MASTER

> Flagship Agentic System Intelligence — Master Orchestration Platform

## Overview

HERMES-ASI-MASTER is a production-grade, multi-agent orchestration framework designed to coordinate autonomous AI workflows across distributed systems. It provides a unified control plane for agent lifecycle management, task decomposition, inter-agent communication, and evolutionary self-improvement.

## Architecture

The system follows a hub-and-spoke topology with a central Master Orchestrator coordinating specialized agent fleets. All state is persisted in a shared memory layer with event-sourced audit trails.

### Core Components

- **Master Orchestrator** — Central decision engine and task router
- **Agent Fleet** — 8 specialized roles with distinct capabilities
- **Skill Registry** — 21 modular skill packages
- **Memory Layer** — Long-term context and episodic memory
- **Evolution Engine** — Self-improvement and adaptation loops
- **Safety Governor** — Guardrails and policy enforcement

## Quick Start

```bash
# Install dependencies
python install.py

# Or use Docker
docker-compose up -d

# Run the master orchestrator
python -m hermes_asi_master orchestrate
```

## Repository Structure

```
hermes-asi-master/
├── README.md                 # This file
├── SOUL.md                   # System identity and values
├── SKILL.md                  # Skill manifest
├── AGENTS.md                 # Agent definitions
├── MEMORY.md                 # Memory architecture
├── USER.md                   # User profile
├── install.py                # Installation script
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container image
├── docker-compose.yml        # Multi-service orchestration
├── config/                   # Configuration files
│   ├── system.yaml
│   ├── models.yaml
│   ├── tools.yaml
│   ├── agents.yaml
│   ├── safety.yaml
│   └── evolution.yaml
├── profiles/
│   └── hermes-asi-master/
│       ├── config.yaml
│       ├── state/
│       ├── scripts/
│       └── routines/
├── skills/                   # 21 skill modules
├── agents/                   # 8 agent roles
├── production-line/          # CI/CD pipelines
├── cron/                     # Scheduled tasks
├── docs/                     # Documentation
└── tests/                    # Test suites
```

## Configuration

All configuration is managed through YAML files in the `config/` directory. See `config/system.yaml` for core settings.

## License

MIT License — See LICENSE for details.

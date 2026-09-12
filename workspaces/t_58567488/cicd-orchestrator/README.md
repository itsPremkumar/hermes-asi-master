# CI/CD Orchestrator

CI/CD Pipeline Automation & Blue-Green Deployment Orchestrator.

## Features

- Blue-green deployment strategy on Kubernetes
- HashiCorp Vault integration for secrets management
- Automated rollback on health-check failure
- Monitoring & alerting with deployment event tracking
- GitHub Actions CI/CD pipeline with security gate
- Rollback script for manual recovery

## Quick Start

```bash
# Install dependencies
uv sync --dev

# Deploy blue-green (dry run)
uv run cicd-orchestrator deploy --app myapp --namespace default --image myimg --tag v1 --color blue --dry-run

# Rollback
uv run cicd-orchestrator rollback --app myapp --namespace default --color blue
```

## Project Structure

```
cicd-orchestrator/
├── .github/workflows/ci.yml   # GitHub Actions pipeline
├── orchestrator/               # Core orchestrator
│   ├── deploy_orchestrator.py # Blue-green engine + CLI
│   └── __init__.py
├── k8s/                        # Kubernetes manifests
│   ├── rbac.yaml
│   ├── deployment.yaml
│   └── service.yaml
├── vault/                      # Secret management
│   └── secrets.py
├── monitoring/                 # Monitoring & alerting
│   └── monitor.py
├── scripts/                    # Utility scripts
│   └── rollback.sh
└── tests/                      # Test suite
    └── test_orchestrator.py
```
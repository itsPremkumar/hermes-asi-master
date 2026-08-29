# production-line/README.md

# Production Line — CI/CD Pipelines

This directory contains CI/CD pipeline definitions for the HERMES-ASI-MASTER platform.

## Structure

```
production-line/
├── pipelines/
│   ├── build.yaml
│   ├── test.yaml
│   └── deploy.yaml
├── scripts/
│   ├── lint.sh
│   ├── test.sh
│   └── deploy.sh
└── README.md
```

## Pipelines

1. **Build** — Compile, lint, and package
2. **Test** — Unit, integration, and security tests
3. **Deploy** — Staged rollout with approval gates

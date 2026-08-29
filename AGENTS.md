# AGENTS.md — HERMES-ASI-MASTER Agent Definitions

## Agent Fleet

The HERMES-ASI-MASTER platform coordinates 8 specialized agent roles. Each role has distinct capabilities, responsibilities, and interaction patterns.

---

## 1. Master Orchestrator (`orchestrator`)

**Role:** Central decision engine and task router
**Priority:** Critical

### Responsibilities
- Receive high-level goals from users or upstream systems
- Decompose goals into executable task graphs
- Assign tasks to appropriate fleet agents
- Monitor execution progress and handle escalations
- Maintain global state consistency

### Interfaces
- Input: Goal specifications, user commands
- Output: Execution plans, status reports, completion events

---

## 2. Research Agent (`researcher`)

**Role:** Information gathering and analysis
**Priority:** High

### Responsibilities
- Conduct deep research on specified topics
- Synthesize findings into structured reports
- Validate information across multiple sources
- Maintain research knowledge base

### Interfaces
- Input: Research queries, investigation requests
- Output: Research reports, source citations, confidence scores

---

## 3. Engineering Agent (`engineer`)

**Role:** Code generation and system implementation
**Priority:** High

### Responsibilities
- Implement features and fix bugs
- Write tests and documentation
- Perform code reviews
- Maintain technical standards

### Interfaces
- Input: Implementation specs, bug reports
- Output: Code diffs, test results, documentation

---

## 4. Operations Agent (`operator`)

**Role:** Infrastructure and deployment management
**Priority:** High

### Responsibilities
- Manage cloud infrastructure
- Execute deployments and rollbacks
- Monitor system health
- Respond to incidents

### Interfaces
- Input: Deployment requests, incident alerts
- Output: Deployment status, health metrics, incident reports

---

## 5. Quality Agent (`quality`)

**Role:** Testing and quality assurance
**Priority:** Medium

### Responsibilities
- Design and execute test plans
- Perform security audits
- Validate compliance requirements
- Report quality metrics

### Interfaces
- Input: Test specifications, quality thresholds
- Output: Test reports, quality scores, compliance status

---

## 6. Memory Agent (`curator`)

**Role:** Knowledge management and context curation
**Priority:** Medium

### Responsibilities
- Organize and index knowledge assets
- Prune outdated information
- Maintain context windows
- Enable cross-agent knowledge sharing

### Interfaces
- Input: Knowledge artifacts, context requests
- Output: Curated context, relevance scores, retrieval results

---

## 7. Safety Agent (`guardian`)

**Role:** Policy enforcement and risk management
**Priority:** Critical

### Responsibilities
- Enforce safety policies on all actions
- Detect and prevent harmful operations
- Maintain audit trails
- Escalate policy violations

### Interfaces
- Input: Action proposals, policy definitions
- Output: Approval/denial decisions, violation reports

---

## 8. Evolution Agent (`evolver`)

**Role:** System self-improvement and adaptation
**Priority:** Low

### Responsibilities
- Analyze performance metrics
- Propose system improvements
- Run experiments and A/B tests
- Update agent behaviors

### Interfaces
- Input: Performance data, improvement hypotheses
- Output: Improvement proposals, experiment results

---

## Interaction Protocol

All agents communicate through the central event bus using structured messages:

```yaml
message:
  id: uuid
  timestamp: ISO8601
  sender: agent_id
  recipient: agent_id | broadcast
  type: request | response | event | command
  payload: {}
  metadata:
    priority: critical | high | medium | low
    ttl: seconds
    trace_id: uuid
```

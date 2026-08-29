# Phase 9 ASI Master — Test Plan

≥55 tests mapped to the four pillars + plugin system. All must pass for green-light.

## Plugin System: 10 tests

| # | Test | Assertion |
|---|------|-----------|
| P.1 | Plugin load | Plugin loads, registers capabilities, health check passes |
| P.2 | Plugin unload | Plugin unloads cleanly, releases resources |
| P.3 | Hot-reload | Plugin hot-reloaded without restarting the master |
| P.4 | Dependency resolution | Plugins with dependencies load in correct order |
| P.5 | Circular dependency | Circular dependency detected, load rejected |
| P.6 | Sandbox isolation | Plugin A cannot access Plugin B's memory |
| P.7 | Capability enforcement | Plugin without capability token cannot access resource |
| P.8 | Health monitoring | Unhealthy plugin is restarted automatically |
| P.9 | Plugin registry | Plugin discoverable in local + remote registry |
| P.10 | Version conflict | Two versions of same plugin: latest wins, old deprecated |

## Pillar 1 — Formal Reasoning (Lean/Z3): 12 tests

| # | Test | Assertion |
|---|------|-----------|
| 1.1 | Prove `plus_n_0` | Proof certificate generated, kernel-valid |
| 1.2 | Counterexample search | Z3 returns `sat` with model for false proposition |
| 1.3 | Tactic backtracking | Failed tactic is rolled back, alternative tried |
| 1.4 | Journal integrity | Tampered hash chain is rejected |
| 1.5 | Z3 timeout | Long-running SMT call times out gracefully, returns `unknown` |
| 1.6 | Proof replay | Replaying certificate reproduces the same result |
| 1.7 | Multi-theorem batch | 5 theorems proved in parallel, all certificates valid |
| 1.8 | Induction proof | Induction tactic proves recursive theorem |
| 1.9 | Rewrite tactic | Rewrite with equality produces equivalent goal |
| 1.10 | Simplification | `simp_all` reduces complex expression to normal form |
| 1.11 | Plugin interface | `prove()` / `check()` / `counterexample()` callable via plugin API |
| 1.12 | Cross-pillar | Formal reasoning result consumable by discovery loop plugin |

## Pillar 2 — Scientific Discovery Loop: 11 tests

| # | Test | Assertion |
|---|------|-----------|
| 2.1 | Hypothesis ranking | Novel + testable hypotheses ranked above trivial ones |
| 2.2 | Experiment protocol | Generated protocol includes variables, controls, metrics |
| 2.3 | Evidence synthesis | Confirmed hypothesis updates belief upward; refuted downward |
| 2.4 | Episode memory | Each loop iteration is retrievable with timestamp |
| 2.5 | Stop on confidence | Loop exits when confidence > 0.95 |
| 2.6 | Human override | External halt signal stops loop within 1 iteration |
| 2.7 | Budget exhaustion | Loop exits gracefully when compute budget exhausted |
| 2.8 | Multi-source observation | Ingests papers + datasets + experiment logs simultaneously |
| 2.9 | Plugin interface | `run_loop()` callable via plugin API |
| 2.10 | Cross-pillar | Discovery loop can invoke formal reasoning plugin for hypothesis checking |
| 2.11 | Reproducibility | Same input produces same discovery trace (deterministic seed) |

## Pillar 3 — P2P Agent Mesh: 11 tests

| # | Test | Assertion |
|---|------|-----------|
| 3.1 | Agent discovery | New agent registered, discoverable by peers within 30s |
| 3.2 | Task auction | Highest reputation + capacity bid wins |
| 3.3 | Consensus | Reputation-weighted vote converges on single value |
| 3.4 | Gossip broadcast | Message reaches all N agents within O(log N) hops |
| 3.5 | Failover | Primary agent crash → backup takes over within 60s |
| 3.6 | Capability access | Agent cannot access a resource without the capability token |
| 3.7 | Reputation decay | Inactive agent's reputation decays over time |
| 3.8 | Byzantine tolerance | System tolerates f < n/3 faulty/malicious agents |
| 3.9 | Plugin interface | `discover()` / `auction()` callable via plugin API |
| 3.10 | Cross-pillar | Mesh discovery used by discovery loop to find experiment executors |
| 3.11 | Network partition | System heals after partition merges |

## Pillar 4 — Computer-Use GUI Loop: 11 tests

| # | Test | Assertion |
|---|------|-----------|
| 4.1 | Screen perception | Screenshot + a11y tree → structured UI state |
| 4.2 | Action tree planning | Generated plan has valid expected post-conditions |
| 4.3 | Click + verify | Click performed; post-condition verified via new screenshot |
| 4.4 | Retry on failure | Failed verification replans and retries (max 3 attempts) |
| 4.5 | Safety whitelist | Action outside whitelist is blocked |
| 4.6 | Human confirmation | Destructive action requires explicit human approval |
| 4.7 | Multi-step task | Complex task (e.g. "book a flight") completed end-to-end |
| 4.8 | Undo stack | Action reversed via undo, state restored |
| 4.9 | Plugin interface | `run_loop()` callable via plugin API |
| 4.10 | Cross-pillar | GUI loop can invoke formal reasoning to verify screen state logic |
| 4.11 | Accessibility | Works with screen reader / high-contrast modes |

## Total: 55 tests (10 + 12 + 11 + 11 + 11)

All tests runnable via `pytest` or equivalent. Each pillar is independently
testable; integration tests (e.g. discovery loop running over the mesh) are
additive.

Author: @cto

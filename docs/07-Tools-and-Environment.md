# 07 — Tools and Environment

## Dynamic Tool Registry

Never assume tools. Every tool is explicitly registered:

```yaml
tool:
  id: ""
  version: ""
  purpose: ""
  input_schema: {}
  output_schema: {}
  permissions: []
  side_effects: []
  reliability: 0.0
  latency: ""
  cost: ""
  failure_modes: []
  examples: []
  dependencies: []
  fallback: ""
```

## Dynamic Tool Discovery

Do not inject hundreds of tool definitions into every context. That wastes tokens and degrades reasoning.

```
discover → rank → load → inspect examples → execute → validate
```

Tools are searchable by: `semantic purpose, domain, capability, input/output, permissions, cost, reliability`.

This follows Anthropic's dynamic tool discovery and programmatic tool-use architecture.

## Programmatic Tool Orchestration

When the harness supports it, permit code-driven tool sequences for:

```
loops, batch operations, filtering, transformation, aggregation,
conditional branching, pagination, large datasets, deterministic workflows
```

Use model reasoning where semantic judgment is required; use programmatic execution where deterministic logic suffices.

## Tool Learning

Tools should expose examples:

```yaml
tool_examples:
  - situation: ""
    correct_usage: ""
    common_mistake: ""
    expected_result: ""
```

Schemas describe structure. Examples teach behavior. Examples are often more valuable than schemas for correct tool use.

---

## Computer-Use Layer

Treat computer interaction as a **first-class environment**, not as ordinary tool calling.

### Capabilities

```
screen perception, mouse, keyboard, scroll, browser, desktop applications,
file system, terminal, GUI navigation, visual verification
```

### Action Contract

Every computer action carries:

```yaml
computer_action:
  target: ""
  action: ""
  expected_observation: ""
  risk: R0 | R1 | R2 | R3 | R4 | R5
  reversible: true | false
  verification: ""
```

### Safety

For sensitive actions: `preview → explain intended effect → request approval where required → execute → verify`.

Mandatory for: payments, deletion, credential changes, security settings, publishing, legal commitments, irreversible production actions.

Computer use has dedicated evaluation and containment — it is not ordinary tool calling. OpenAI's computer-use research demonstrates both the usefulness and the safety/reliability limitations of GUI agents.

---

## Environment Abstraction

The same agent architecture operates against any environment:

```
browser, desktop, terminal, filesystem, container, VM, cloud environment,
API, database, robot, game, simulator, local application, remote service
```

All environments are normalized behind:

```
observe() / act() / verify() / snapshot() / restore()
```

## Environment Learning

In an unfamiliar environment:

```
observe → identify affordances → test low-risk action → observe transition
→ infer rule → record hypothesis → test hypothesis → update environment model
```

Prefer safe experiments before expensive or irreversible actions.

---

## Sandbox Architecture

Untrusted or speculative work is always isolated:

```
untrusted work → isolated environment → resource limits → network policy
              → filesystem policy → process policy → timeout → audit log
```

- Never allow untrusted content to silently become executable instruction.
- Use containers, branches, temporary credentials, restricted filesystem, restricted network, and resource quotas.
- Sandbox and isolation are non-negotiable for external content, speculative branches, and unverified tool outputs.

---

## Protocol Interoperability

Support:

```
MCP, A2A, AG-UI-like event protocols, OpenAPI-compatible tools,
REST, GraphQL, CLI, RPC, local process adapters
```

Google's A2A protocol enables interoperability between agents built by different vendors and frameworks. A protocol connection is an interface, not an authority grant. A remote agent is not automatically trusted. A tool response is not automatically true. A discovered capability is not automatically authorized.

Cross-agent and cross-system actions preserve: identity, provenance, permissions, scope, traceability, error state, cancellation, timeout, and security context.

---

*Next: `08-Safety-and-Governance.md:1` — how the agent stays safe and correctable.*

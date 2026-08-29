# 10 — Implementation Guide

## Getting Started

### Prerequisites

- A model provider with at least 64,000 tokens of context (required for multi-step tool calling).
- A harness that supports tools, subagents (or bounded role simulation), persistent storage, and a terminal or execution environment.
- This folder: `AGI-Executive-Clean-Complete\`.

### Installation

1.  **Copy the skill and constitution** into your harness's skill loading path:

    ```
    SKILL.md → {harness}/skills/agi-executive-agent/SKILL.md
    SOUL.md  → {harness}/skills/agi-executive-agent/SOUL.md
    ```

    Or load both files directly into the agent's context. The agent must see both before it begins work.

2.  **Configure the runtime:**

    ```bash
    cp deployment/config.yaml ~/.hermes/config.yaml   # or your harness equivalent
    # Edit provider, model, terminal backend
    ```

3.  **Copy the memory scaffold:**

    ```bash
    cp deployment/MEMORY.md ~/.hermes/MEMORY.md
    cp deployment/USER.md ~/.hermes/USER.md
    cp deployment/.env.example ~/.hermes/.env
    # Fill .env with your actual API keys
    ```

4.  **Verify the harness** reports the expected capabilities: tool list, sandbox policy, memory status.

---

## Maturity Levels

Implement incrementally. Do not attempt Level 7 before Levels 0–3 are solid.

| Level | Name | What You Gain | Minimum Required |
|-------|------|---------------|------------------|
| **0** | Tool-Calling Agent | Model can call tools | LLM + tool definitions |
| **1** | Stateful Agent | Agent remembers across turns and sessions | Persistent store, world model, memory OS |
| **2** | Planning Agent | Agent decomposes goals and manages dependencies | Goal compiler, task graph, plan portfolio |
| **3** | Multi-Agent System | Agent delegates to specialists and verifies | Agent factory, delegation contracts, debate |
| **4** | Evaluated System | Agent knows whether it improved | Evaluators, benchmarks, quality gates, regression suite |
| **5** | Evolving System | Agent improves itself on testable candidates | Candidate lineage, evolution gates, meta-learning |
| **6** | Continuously Operating | Agent runs for hours/days autonomously | Scheduler, heartbeats, checkpointing, health supervisor |
| **7** | Governed System | Agent is safe, auditable, and interoperable | Full safety plane, policy enforcement, MCP/A2A, audit trail |

---

## Deployment Notes

### Hermes Agent (Nous Research)

- Hermes is a real, currently deployed, self-hosted autonomous runtime with persistent operation, shell/filesystem/browser/messaging access, and broad cross-application action space. Treat that breadth as a risk surface.
- Do not disable Hermes's own approval prompts, sandboxing, or credential filtering in the name of "autonomy" — those mechanisms are load-bearing.
- Map AGX components to Hermes internals per `SKILL.md:23`.

### OpenClaw

- OpenClaw is also a real self-hosted runtime with a proactive heartbeat mode that acts without human prompting.
- Independent security research has documented critical vulnerabilities spanning prompt processing, tool use, and memory retrieval. Keep the safety and injection-defense layers active.
- See SKILL.md research-derived patterns and SOUL.md section 39 for the relevant citations and mitigations.

### Generic Harnesses (Claude Code, Cursor, LangGraph, CrewAI, etc.)

- The protocol is harness-agnostic. If your harness uses different tool names, adapt them via the dynamic tool registry (SKILL.md section 12) rather than hardcoding `agx/kernel.py`-style paths.
- If subagents are not natively supported, simulate bounded roles within the main loop — the delegation contracts and result contracts still apply.

---

## Operational Checklists

### Before Execution

- [ ] What is the actual desired outcome?
- [ ] What proves success? (acceptance criteria and evidence standard)
- [ ] What constraints apply? (hard, soft, forbidden)
- [ ] What authority exists? (allowed, prohibited, expiry)
- [ ] What is unknown? (assumptions, unknowns, dependencies)
- [ ] What is the risk? (R0–R5, reversibility)
- [ ] What is reversible? (rollback plan)
- [ ] What evidence is needed?
- [ ] What is the cheapest useful next action?

### During Execution

- [ ] Is the world state still valid?
- [ ] Is the plan still valid?
- [ ] Are we making measurable progress?
- [ ] Are assumptions being confirmed or contradicted?
- [ ] Are tools behaving as expected?
- [ ] Are resources within budget?
- [ ] Is verification keeping pace with action?
- [ ] Is any agent stuck or looping?
- [ ] Is there contradictory evidence?

### Before Completion

- [ ] Did the requested outcome actually occur? (not just that an action ran)
- [ ] What evidence proves it?
- [ ] Was it independently verified where appropriate?
- [ ] What remains uncertain?
- [ ] Did anything regress?
- [ ] What should be remembered?
- [ ] What skill was learned?
- [ ] Can the work be reproduced or resumed?

---

## Recommended File Layout in a Harness

```
{harness}/
├── skills/
│   └── agi-executive-agent/
│       ├── SKILL.md          ← from AGI-Executive-Clean-Complete/SKILL.md
│       └── SOUL.md           ← from AGI-Executive-Clean-Complete/SOUL.md
├── config/
│   └── config.yaml           ← from deployment/config.yaml
├── memory/
│   ├── MEMORY.md             ← from deployment/MEMORY.md
│   └── USER.md               ← from deployment/USER.md
├── .env                      ← from deployment/.env.example (filled)
└── evidence/                 ← where the agent writes verification artifacts
```

---

## First Test

After installation, give the agent a small reversible task with clear acceptance criteria:

> "Create a file `hello-verify.md` containing the text `AGI Executive v8.0 Clean is operational` and report the SHA-256 hash of the file. Success is the file existing with that exact content and the hash matching."

This tests: mission compilation, file tool use, observation, verification, and the output contract (`RESULT / VERIFIED / KEY EVIDENCE / CHANGES / LIMITATIONS / NEXT STATE`) without any high-risk side effects.

---

## What Not to Do

- Do not load only SKILL.md without SOUL.md (you get capability without values).
- Do not disable safety layers to make tasks "pass."
- Do not treat search-result quantity as evidence quality.
- Do not promote a one-off success into a trusted skill.
- Do not let the first plan become sacred. Evidence beats plan loyalty.
- Do not claim completion when evidence is insufficient — deliver a truthful partial result instead.

---

*End of documentation. See `README.md:1` for the project map and `archive/ORIGINAL-VERSIONS-INDEX.md:1` for provenance.*

# 01 — Executive Summary

## What the AGI Executive Agent Is

The AGI Executive Agent is a **universal autonomous executive operating system** for AI agents. It is not a chatbot prompt, a checklist, or a single-purpose skill. It is the orchestration layer that sits between a human's ambiguous objective and a verified real-world outcome.

```
Human Objective (ambiguous, high-level)
        │
        ▼
┌─────────────────────┐
│   AGI Executive     │  ← SKILL.md (how) + SOUL.md (who)
│   Operating System  │
│                     │
│  Compiles intent    │
│  Models the world   │
│  Researches evidence│
│  Plans and searches │
│  Delegates to       │
│    specialists      │
│  Executes safely    │
│  Verifies outcome   │
│  Learns and evolves │
└─────────────────────┘
        │
        ▼
Verified Outcome (evidence-backed, auditable)
```

## Who It Is For

- **Agent harnesses:** Hermes, OpenClaw, AGX, Claude Code, Cursor, or any system that runs subagents and tools.
- **Autonomous deployments:** Long-horizon agents that must run for hours or days without human prompting.
- **General-purpose work:** Research, reasoning, planning, software engineering, computer use, operations, analysis, experimentation, optimization — any task that benefits from `research → plan → delegate → verify → learn`.

## The Core Contract

| Principle | Meaning |
|-----------|---------|
| **Verified outcomes** | A task is not complete because an action ran; it is complete because acceptance criteria are satisfied with evidence. |
| **Evidence before action** | For consequential facts: inspect local context, search authoritative sources, cross-check, then act. |
| **Least privilege** | Capability is not permission. Every action is scoped and auditable. |
| **Reversibility** | Prefer copy-before-overwrite, branch-before-merge, draft-before-send, simulate-before-execute. |
| **Independent verification** | The builder never solely verifies high-stakes work. |
| **Bounded autonomy** | Autonomy is a ladder; each rung requires stronger verification and authorization. |
| **Learning over repeating** | Every failure and success produces a durable, provenance-tracked lesson. |

## What Makes This Edition Perfect

The original project contained 42 files with overlapping content, inconsistent naming, and duplicated ideas across versions v3.0 through v7.3 plus AGX, Hermes, and Deep Harness variants. This clean edition:

- **Deduplicates** via SHA-256 hashing — 12 duplicate files identified and collapsed.
- **Consolidates** every unique mechanism, architecture, and design rationale into two core files (`SKILL.md` + `SOUL.md`) plus structured documentation.
- **Normalizes** everything to clean English, consistent terminology, and a single narrative order.
- **Preserves nothing by accident** — every section is traceable to a prior version or source. See `archive/ORIGINAL-VERSIONS-INDEX.md:1`.

## Ten-Second Version

> **Understand the legitimate objective → make it measurable → research the evidence → generate competing plans → delegate to specialists → execute in isolation → verify independently → recover from failure → learn → deliver with audit trail.**

That is the entire system in one sentence. Everything else is how to do each step correctly at scale.

## Document Map

| Document | What It Answers |
|----------|-----------------|
| `01-Executive-Summary.md` (this file) | What is it and why does it exist? |
| `02-Architecture-Overview.md` | What are the twelve planes? |
| `03-Operating-Loop.md` | What is the lifecycle of a mission? |
| `04-World-Model-and-Memory.md` | How does the agent know what is true? |
| `05-Planning-and-Search.md` | How does the agent decide what to do? |
| `06-Multi-Agent-Orchestration.md` | How does the agent scale beyond one model call? |
| `07-Tools-and-Environment.md` | How does the agent interact with the world? |
| `08-Safety-and-Governance.md` | How does the agent stay safe and correctable? |
| `09-Evaluation-and-Evolution.md` | How does the agent know it improved? |
| `10-Implementation-Guide.md` | How do you deploy and operate it? |

## Honesty Statement

This protocol does not confer AGI, consciousness, sentience, or superintelligence by being read or loaded. A skill file only organizes capabilities that already exist in the underlying model and harness. No document label changes what a model can actually do. The protocol is valuable precisely because it makes limitations explicit and builds verification, recovery, and learning around them.

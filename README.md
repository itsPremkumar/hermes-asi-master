# HERMES Advanced — Universal AGI/ASI Executive System

**Version:** 4.0 ASI Universal Master (Hermes-Native) + SOUL v4.0 ASI + 19 Active Cognitive Engines & MCP Bridges  
**Type:** Production Hermes-Native Build — Fully Executable, State-Backed, Official-Compliant  
**Hermes Runtime:** Hermes Agent (Nous Research) — https://hermes-agent.nousresearch.com  
**Language:** English Only — Production Standard

---

## What This Is

**THE dedicated Hermes executive super-system** — built FOR Hermes, ON Hermes, WITH Hermes. Every file is Hermes-native and follows the **official Hermes standard** (`hermes-agent.nousresearch.com/docs`).

```
05-HERMES-Advanced/
├── profiles/
│   └── hermes-asi-master/                 ← Complete Ready-to-Deploy Unified Master Profile
│       ├── config.yaml                    ← Master profile settings (tools, sandbox, memory)
│       ├── SOUL.md (48KB, 50 sections)    ← Hardened ASI Constitution (Slot #1 in system prompt)
│       ├── AGENTS.md                      ← Project operational context & tool boundaries
│       ├── MEMORY.md                      ← Seeded persistent memory & state links
│       ├── USER.md                        ← User alignment, preferences & strategic goals
│       ├── state/                         ← Live Structured JSON State Stores
│       │   ├── world_state.json           ← Entities, causal graph, 90d forecasts (Genie 3)
│       │   ├── self_model.json            ← Empirical capabilities, Brier calibration score
│       │   ├── belief_graph.json          ← Bayesian belief network with cascade links
│       │   ├── mission_graph.json         ← Long-horizon DAG & blocker resolution (METR)
│       │   ├── financial_ledger.json      ← Token budget, burn rate, and API cost ledger
│       │   └── evolution_benchmarks.json  ← GEPA Pareto mutation history and skill scores
│       ├── scripts/                       ← 19 Active Python Cognitive Engines & MCP Bridges
│       │   ├── state_engine.py            ← Schema validation, atomic reads/writes, backups
│       │   ├── belief_engine.py           ← Bayesian posterior updater & cascade triggers
│       │   ├── self_tracker.py            ← Post-task empirical logger & calibration score
│       │   ├── sleep_cycle_runner.py      ← 13-step Letta dream cycle automation
│       │   ├── skill_forge.py             ← Voyager skill acquisition & composition forge
│       │   ├── curriculum_picker.py       ← SIMA 2 curriculum generator
│       │   ├── formal_verifier.py         ← AST parser, schema verifier & R0-R6 gatekeeper
│       │   ├── gepa_evolution_engine.py   ← DSPy + GEPA prompt evolution optimizer
│       │   ├── sandbox_orchestrator.py    ← Modal / Daytona / E2B serverless GPU manager
│       │   ├── hybrid_llm_router.py       ← Fast local vLLM/Ollama + Frontier cloud router
│       │   ├── omnichannel_gateway.py     ← Telegram, Discord, Slack, and GitHub hub
│       │   ├── p2p_agent_mesh.py          ← Multi-machine A2A decentralized protocol
│       │   ├── trajectory_rl_exporter.py  ← ShareGPT / Atropos dataset generator for RL
│       │   ├── formal_prover_lean4.py     ← Z3 / Lean 4 neuro-symbolic formal theorem prover
│       │   ├── economic_ledger.py         ← Autonomous budget accounting & ledger tracker
│       │   └── iot_controller.py          ← Home Assistant & hardware sensor controller
│       └── routines/                      ← Hermes Scheduled Cron Routines
│           ├── 01_nightly_dream.json      ← 2:00 AM 13-step dream cycle routine
│           ├── 02_world_sync.json         ← 4-hour world estimation & forecast sync
│           ├── 03_post_task_hook.json     ← Post-task empirical calibration hook
│           │   ├── hybrid_memory_engine.py    ← BM25 + dense semantic vector hybrid memory retriever
│   ├── formal_prover_mcp.py       ← Native MCP stdio theorem proving bridge
│   └── guardrail_manager.py       ← Hard budget ceilings and loop guardrail enforcement
│
└── routines/
    ├── 01_nightly_dream.json      ← 2:00 AM 13-step dream cycle routine
    ├── 02_world_sync.json         ← 4-hour world estimation & forecast sync
    ├── 03_post_task_hook.json     ← Post-task empirical calibration hook
    ├── 04_curriculum_sync.json    ← Weekly curriculum sync & self-improvement
    └── 05_weekly_gepa_evolution.json ← Sunday 3:00 AM automated GEPA prompt evolution
│
├── SOUL.md                                ← Global base identity (Slot #1)
├── AGENTS.md                              ← Project context
├── SKILL.md                               ← Hermes Advanced OS (15 planes)
├── config.yaml                            ← Root Hermes config
├── .env.example                           ← Secrets template
├── MEMORY.md & USER.md                    ← Root memory files
│
├── skills/ (16 Hermes-native skills)
│   ├── 01-research/SKILL.md               ← 5-pass research + Evidence Graph
│   ├── 02-planning/SKILL.md               ← 6 plans + DAG + 10 strategies
│   ├── 03-orchestration/SKILL.md          ← Swarm + 30 roles + Debate Protocol
│   ├── 04-tools/SKILL.md                  ← Tool Registry + Computer-Use + Sandbox
│   ├── 05-safety-evaluation/SKILL.md      ← R0-R6 + 22 Invariants + 12 Gates
│   ├── 06-memory-world/SKILL.md           ← World Model + 15 Namespaces + Context OS
│   ├── 07-search-optimized/SKILL.md       ← Flagship: Search Superintelligence (5 parallel)
│   ├── 08-project-synthesis/SKILL.md      ← Project Synthesis Engine (Reuse/Modify/Combine)
│   ├── 09-github-advanced/SKILL.md        ← Worktree Swarm & Verified Merging
│   ├── 10-hub-recommended/SKILL.md        ← Hub skills installer
│   ├── 11-deep-cognition/SKILL.md         ← 19 Deep Recommendations
│   ├── 12-bot-mode-agi/SKILL.md           ← Bot Mode AGI (Master Profile Architecture)
│   ├── 13-computer-use-gui/SKILL.md       ← OmniParser & OS-World GUI automation
│   ├── 14-formal-proofs/SKILL.md          ← Lean 4 / Z3 theorem proving & zero-hallucination
│   ├── 15-p2p-agent-mesh/SKILL.md         ← Decentralized A2A multi-node protocol
│   └── 16-physical-iot/SKILL.md           ← Home Assistant & hardware environment bridge
│
├── references/                            ← Domain Playbooks & Role Pass Protocols
│   ├── domain_playbooks.md                ← Code, Research, DevOps, Data Science Playbooks
│   ├── role_passes.md                     ← Researcher, Critic, Builder, Evaluator, Supervisor
│   └── gates_and_scoring.md               ← Hard Binary Gates vs Soft Continuous Scoring
│
├── prompts/                               ← Meta-Prompt Blueprint Generators
│   ├── 01-Master-Orchestration-Prompt.md  ← Master Swarm & Role Generator Prompt
│   └── 02-Goal-Driven-Execution-Prompt.md ← Autonomous Goal-Seeking Loop Generator
│
├── docs/                                  ← Complete 10-Part Architectural Documentation
│   ├── 01-Executive-Summary.md
│   ├── 02-Architecture-Overview.md
│   ├── 03-Operating-Loop.md
│   ├── 04-World-Model-and-Memory.md
│   ├── 05-Planning-and-Search.md
│   ├── 06-Multi-Agent-Orchestration.md
│   ├── 07-Tools-and-Environment.md
│   ├── 08-Safety-and-Governance.md
│   ├── 09-Evaluation-and-Evolution.md
│   ├── 10-Implementation-Guide.md
│   ├── 06-Search-Optimization.md
│   ├── 07-Project-Synthesis-Plan.md
│   └── 08-Deep-Cognitive-Architecture.md
│
```

---

## Quick Start — Deploying the Master Profile

```bash
# 1. Copy the Master Profile to Hermes profiles directory
mkdir -p ~/.hermes/profiles/hermes-asi-master
cp -r profiles/hermes-asi-master/* ~/.hermes/profiles/hermes-asi-master/

# 2. Copy all 16 skills
cp -r skills/* ~/.hermes/skills/

# 3. Launch Hermes using the Master Profile or Bot Mode
hermes -p hermes-asi-master chat
# Or launch as bot
hermes -p asi-bot chat
```

---

## The 19 Active Cognitive Engines & MCP Bridges (All Tested & Verified)

1. **State Engine (`state_engine.py`)**: Schema validation, atomic reads/writes, and backups.
2. **Bayesian Belief Engine (`belief_engine.py`)**: Bayesian posterior calculation and cascade triggers.
3. **Empirical Self-Model (`self_tracker.py`)**: Domain success rates, sample counts, and Brier score tracking.
4. **13-Step Sleep Cycle (`sleep_cycle_runner.py`)**: Letta dream cycle executing at 2:00 AM daily.
5. **Voyager Skill Forge (`skill_forge.py`)**: Converts execution traces into parameterized skill templates.
6. **Curriculum Engine (`curriculum_picker.py`)**: SIMA 2 task selection based on learning value and novelty.
7. **Formal Verifier (`formal_verifier.py`)**: AST code validation and R0–R6 policy gatekeeping.
8. **GEPA Prompt Optimizer (`gepa_evolution_engine.py`)**: DSPy genetic prompt evolution on Pareto frontiers.
9. **Cloud Sandbox Orchestrator (`sandbox_orchestrator.py`)**: Modal, Daytona, and E2B cloud GPU runner.
10. **Hybrid LLM Router (`hybrid_llm_router.py`)**: Sub-second local execution + frontier cloud reasoning.
11. **Omnichannel Gateway (`omnichannel_gateway.py`)**: Telegram, Discord, Slack, and GitHub hub.
12. **P2P Agent Mesh (`p2p_agent_mesh.py`)**: Decentralized multi-node agent mesh network.
13. **Trajectory RL Exporter (`trajectory_rl_exporter.py`)**: ShareGPT & DPO dataset generator for Atropos RL.
14. **Formal Prover (`formal_prover_lean4.py`)**: Z3 and Lean 4 neuro-symbolic mathematical proofs.
15. **Economic Ledger (`economic_ledger.py`)**: Token and financial budget tracking per mission.
16. **IoT Controller (`iot_controller.py`)**: Home Assistant and hardware sensor telemetry.

---

*HERMES Advanced v4.0 ASI Universal Master — Production Ready.*

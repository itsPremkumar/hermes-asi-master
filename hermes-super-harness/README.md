# Hermes Super-Harness (with DeerFlow 2.0 Integration)

**100% Free-First, Plugin-Native SuperAgent Harness Built on Top of Hermes Agent**  
*Integrated with ByteDance DeerFlow 2.0 SuperAgent Architecture & Hermes ASI Master*

---

## 1. Overview & Architecture

**Hermes Super-Harness** is an evolutionary super-agent execution platform built on top of the complete **Nous Research Hermes Agent** (`core/hermes-agent`). It enables dynamic multi-agent DAG workflows, subagent swarms, long-term memory streams, and sandboxed formal verification using a **100% Plugin-Based Format** and **Zero-Cost Model Routing**.

```
hermes-super-harness/
├── cli.py                                 ← Master Super-Harness CLI Launcher
├── updater.py                             ← Upstream Git Pull, State Backup & 1-Click Certifier
│
├── core/
│   └── hermes-agent/                      ← Complete Official Hermes Agent (10,630 upstream files)
│
├── harness/                               ← Free-First Super-Harness Kernel
│   ├── engine.py                          ← Plugin Discovery & Lifecycle Hook Dispatcher
│   ├── plugin_interface.py                ← Universal Plugin Contract & 3-Ring Security Model
│   ├── router.py                          ← 100% Free Model Router (Ollama, vLLM, OpenRouter Free)
│   ├── state.py                           ← StateGraph & AgentState Multi-Node Workflow
│   └── sandbox.py                         ← Safe Process & Execution Containment
│
├── plugins/                               ← 100% Plugin-Based Subsystems
│   │
│   ├── deerflow_v2/                       ← ByteDance DeerFlow 2.0 SuperAgent Plugin
│   │   ├── manifest.json                  ← Ring R1 Sandbox Permission & Capabilities
│   │   ├── plugin.py                      ← DeerFlowV2Plugin implementation
│   │   ├── graph.py                       ← Plan-Research-Code-Review-Verify-Replan StateGraph
│   │   ├── memory/memory_stream.py        ← Long-Term Fact Extraction & Context Injection
│   │   └── agents/                        ← Specialized Subagent Swarm
│   │       ├── planner.py                 ← Step Decomposer & Dynamic Replanner
│   │       ├── researcher.py              ← Evidence & Technical Fact Synthesizer
│   │       ├── coder.py                   ← Production Code Synthesizer
│   │       ├── reviewer.py                ← Adversarial Critic & Security Reviewer
│   │       └── verifier.py                ← Formal AST & Sandbox Execution Verifier
│   │
│   ├── hermes_asi_core/                   ← Hermes ASI Master Core Plugin
│   │   ├── manifest.json                  ← Ring R0 Core Kernel Permission
│   │   └── plugin.py                      ← SOUL v4.0 constitution, 21 skills, 26 cognitive engines
│   │
│   └── gepa_evolution/                    ← GEPA Pareto Evolution Plugin
│       ├── manifest.json                  ← Ring R1 Sandbox Permission
│       └── plugin.py                      ← Multi-Objective Genetic Prompt Mutation Engine
│
└── tests/                                 ← Automated Pytest Master Suite (100% Passing)
    ├── test_plugin_framework.py           ← Manifest schema & dynamic discovery tests
    ├── test_deerflow_v2.py                ← DeerFlow 2.0 StateGraph & Swarm tests
    └── test_router_and_sandbox.py         ← Zero-cost router, sandbox & GEPA tests
```

---

## 2. Key Features

1. **100% Free-First / Zero Paid Keys Required**:
   - Automatically utilizes local Ollama (`hermes3`, `llama3`), local vLLM endpoints, or OpenRouter free tiers, with offline deterministic simulation fallback.
2. **ByteDance DeerFlow 2.0 Integration**:
   - **Plan-Execute StateGraph**: Decomposes complex missions into milestones and replans dynamically on validation failure.
   - **Dynamic Subagent Swarm**: `Planner` -> `Researcher` -> `Coder` -> `Reviewer` -> `Verifier`.
   - **Long-Term Memory Stream**: Extracts atomic facts from step outputs to maintain cross-task coherence without prompt bloat.
3. **100% Plugin-Native Extensibility**:
   - Every feature is an isolated, hot-pluggable plugin with declarative `manifest.json` and 3-Ring permission levels (`R0_CORE`, `R1_SANDBOX`, `R2_NETWORK`, `R3_UNRESTRICTED`).
4. **Hermes Upstream Sync (`updater.py`)**:
   - Updates `core/hermes-agent` directly from `NousResearch/hermes-agent` while creating timestamped backups and running automated test certifications.

---

## 3. Quick Start & CLI Usage

```bash
cd hermes-super-harness

# 1. Discover all active plugins
python cli.py list-plugins

# 2. Run an autonomous goal using DeerFlow 2.0 workflow
python cli.py run --goal "Build an autonomous Byzantine fault-tolerant consensus simulator"

# 3. Run multi-domain benchmarks (Code, Planning, Security, Consensus)
python cli.py benchmark

# 4. Evolve a prompt instruction with GEPA Pareto optimizer
python cli.py evolve --prompt "Verify AST syntax and type invariants before emitting code"

# 5. Run full automated test suite
pytest tests -v

# 6. 1-Click Update from upstream NousResearch/hermes-agent
python updater.py
```

---

## 4. Test Certification Results

```text
tests/test_deerflow_v2.py::test_deerflow_memory_stream_fact_extraction PASSED [ 11%]
tests/test_deerflow_v2.py::test_deerflow_stategraph_execution PASSED     [ 22%]
tests/test_deerflow_v2.py::test_deerflow_plugin_end_to_end PASSED        [ 33%]
tests/test_plugin_framework.py::test_manifest_validation PASSED          [ 44%]
tests/test_plugin_framework.py::test_plugin_registration_and_lifecycle PASSED [ 55%]
tests/test_plugin_framework.py::test_auto_discovery_of_plugins PASSED    [ 66%]
tests/test_router_and_sandbox.py::test_zero_cost_model_router PASSED     [ 77%]
tests/test_router_and_sandbox.py::test_sandbox_python_execution PASSED   [ 88%]
tests/test_router_and_sandbox.py::test_gepa_evolution_plugin PASSED      [100%]

============================== 9 passed in 5.40s ==============================
```

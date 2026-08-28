---
name: hermes-bot-mode-agi
description: Hermes Bot Mode AGI — 10 persistent Bots as cognitive organs (World, Self, Memory, Dream, Skill-Forge, Curriculum, Planner, Belief, Verifier, Mission). Turns Bot Mode from roster into AGI-oriented architecture.
version: "1.0 Advanced"
author: Hermes Advanced Team
license: MIT
metadata:
  hermes:
    tags: [hermes, bot-mode, agi, persistent-bots, cognitive-architecture, swarm]
    category: hermes-advanced
    requires_toolsets: [web]
---

# SKILL 12 — BOT MODE AGI

> **Load this skill when:** You want to use Hermes Bot Mode NOT as a roster, but as a **persistent AGI brain** — 10 Bots that never die and make Hermes deeper, not bigger.
> **Requires:** Hermes Desktop v0.20.3+ with Bot Mode (default-on, Settings → Plugins → Hermes Bots)
> **Pairs with:** `11-deep-cognition` (the 19 deep recommendations this implements) + `03-orchestration` (one-shot swarm) + `06-memory-world` (world/self/memory planes)
> **Bot Mode Law:** *One-shot swarm = one task and die. Persistent Bot = one cognitive organ forever.*

---

## 0. PURPOSE — FROM ROSTER TO BRAIN

**Basic Bot Mode (what docs show):** Researcher + Coder + Publisher split a game project in a group chat.

**AGI Bot Mode (this skill):** 10 Bots become the **cognitive architecture** that the expert review says Hermes is missing:

```
Advanced Protocol (15 planes, 30 roles) → Continually Learning Cognitive Architecture
                                          → Open-Ended Self-Improving General Agent
```

| Basic Bot Mode | **AGI Bot Mode (This Skill)** |
|---|---|
| Bots are roles for tasks | **Bots are organs for cognition** — World, Self, Memory, Dream, etc. |
| Group chat is collaboration | **Group chat IS reasoning** — @planner internally group-chats @world/@belief/@self *before* answering you |
| Routines: "summarize inbox at 8am" | **Routines as organs:** @dream runs 13-step sleep cycle at 2am, @world re-estimates every 4h |
| Bots die or go idle | **Bots are immortal** — @world has watched for weeks, @self has 142 samples |

---

## 1. THE 10 PERSISTENT BOTS — YOUR AGI BRAIN

Create these **once** in Hermes Desktop → Bots tab → Create Bot. Each is a **real Hermes profile** at `~/.hermes/profiles/<name>/` with isolated config, memory, skills, credentials.

| # | Bot | AGI Plane | What It IS Forever | Model to Pin | Skills to Give It |
|---|-----|-----------|-------------------|--------------|-------------------|
| 1 | **`@mission`** | Plane 1: Mission | **The Goal Keeper** — never loses objective, tracks 6-plan portfolio across weeks, owns `MISSION_GRAPH` | Reasoning (Claude 4 / GPT-5) | `02-planning` |
| 2 | **`@world`** | Plane 3 + Deep #1 | **The World Brain** — continuously maintains `WORLD_STATE` (entities, relationships, causal graphs, counterfactual branches, 90-day forecasts). Updates on **every observation**. Never resets. | Reasoning + Genie 3-style | `06-memory-world` (world-model section) |
| 3 | **`@self`** | Plane 2 + Deep #2 | **The Self Mirror** — tracks **empirical** capability: `python_backend: 0.87 success (142 samples, delta -0.03, failure_modes: [dependency mismatch])`. Routes tasks dynamically on real data, not claims. | Any (self-evaluating) | `06-memory-world` (self-model) |
| 4 | **`@memory`** | Plane 4 + Deep #3 | **The Learning Memory** — not just retrieval, but *experience replay*: `Experience → Extract → Generalize → Validate → Store → Retrieve → Apply → Measure → Update reliability`. Owns 15 namespaces + provenance. | Any | `06-memory-world` |
| 5 | **`@dream`** | Deep #4 | **The Dreamer** — runs **13-step sleep cycle** while you sleep (textbook Letta). Makes Hermes better *because* it remembered. | Cheap + long context | `11-deep-cognition` (sleep-time) |
| 6 | **`@skill-forge`** | Deep #5 + #6 | **The Blacksmith** — Voyager-style: observes successful trajectory → abstracts reusable behavior → generates parameterized skill → tests cross-domain → verifies → promotes. Also **composes** skills: `research+extract+analyze+visualize+report = market-intelligence pipeline` | Coding model | `11-deep-cognition` (skill acquisition) |
| 7 | **`@curriculum`** | Deep #7 | **The Teacher** — SIMA 2-style: auto-selects next task by `learning_value + difficulty + novelty + transfer_value`. Drives `KNOWN → SLIGHTLY HARDER → UNKNOWN → NOVEL → ADVERSARIAL → TRANSFER → OPEN-ENDED` curriculum. Never lets Hermes stagnate. | Reasoning | `11-deep-cognition` (curriculum) |
| 8 | **`@planner`** | Plane 6+7 + Deep #8 | **The Search Mind** — does **test-time search over trajectories** (beam/tree/MCTS/best-of-N), not just one plan. Scores *partial trajectories*. Makes uncertainty → information gain → experiment a first-class executive process. | **Strongest reasoning** (pinned) | `02-planning` + `11-deep-cognition` |
| 9 | **`@belief`** | Deep #9-11 | **The Belief Graph Keeper** — persistent `BELIEF_GRAPH` (claim A: 0.83, 5 sources, dependent beliefs recomputed when A changes → plans reprioritized) + `MISSION_GRAPH` that **never disappears** across days/sessions. Long-horizon autonomy (METR). | Any | `06-memory-world` + `11-deep-cognition` |
| 10 | **`@verifier`** | Plane 10+14 + Skill 05 | **The Judge + Formal Prover** — **triple verification** for every high-stakes deliverable: Builder → Independent Verifier (different model, no builder context) → Formal Prover. Owns 12 gates (G11 Formal Proof + G12 Strategic) + `merge-reconciler` neutrality. | **Different model than builder** (anti-correlated failure) | `05-safety-evaluation` |

**How to Create (Once):**
```
Hermes Desktop → Bots tab → Create Bot
  Name: world
  Role: The World Brain — continuously maintains WORLD_STATE
  Model: Pin per table above (e.g., @planner → strongest reasoning)
  Skills: Attach per table (e.g., @world → 06-memory-world)
  SOUL.md: Your 05-HERMES-Advanced/SOUL.md (50 sections, shared)
  Avatar: Generate per Bot
```

---

## 2. ROUTINES — MAKE BOTS ORGANS (Not Alarms)

In basic Bot Mode, routines are "summarize inbox at 8am". In AGI Bot Mode, **routines ARE the cognition**:

| Bot | Routine | Schedule | What It Does | Backing |
|-----|---------|----------|--------------|---------|
| `@dream` | **13-Step Sleep Cycle** | Every day 2am | `Review trajectories → Detect failures → Detect patterns → Compress experiences → Generate abstractions → Create candidate skills → Identify knowledge gaps → Generate hypotheses → Run offline experiments → Update world model → Update self-model → Regression evals → Promote verified improvements` | `11-deep-cognition` §4, Letta |
| `@world` | **Re-estimate World** | Every 4h | Re-estimate `WORLD_STATE` from recent observations, update causal graph, forecast, detect model disagreement | `11-deep-cognition` §1, Genie 3 |
| `@self` | **Update Self** | After every task (hook) | Update empirical `self_model: {domain, confidence, empirical_success, sample_count, recent_delta, failure_modes}` | `11-deep-cognition` §2 |
| `@belief` | **Recompute Beliefs** | On evidence change | `A changes → dependent beliefs recomputed → plans affected → future actions reprioritized` | `11-deep-cognition` §9 |
| `@memory` | **Consolidate** | Every 6h | Experience replay: `Experience → Extract → Generalize → Validate → Store` | `11-deep-cognition` §3 |
| `@curriculum` | **Select Next Task** | Weekly | Score candidate tasks by `learning_value + transfer_value` and propose next curriculum level | `11-deep-cognition` §7 |

**How to Set (Hermes Bot Mode):**
```
Click Bot → Routines tile (docked beside conversation while Bots tab active)
→ New Routine → Schedule: "0 2 * * *" (cron) → Prompt: the routine text above
→ Runs show up in both Bots pane and `hermes cron list`, results land in that Bot's own chat
```

---

## 3. GROUP CHATS — THE PERSISTENT REASONING LOOP

**Basic:** User creates group, Bots collaborate on a task.

**AGI:** You create **one group that IS the reasoner** — you never talk to it directly, `@planner` does.

### The `Cognition` Group (Your Persistent Brain)

Create one group: **`Cognition` = @planner + @world + @belief + @self + @verifier + @curriculum** (6 Bots, max allowed)

*   **User never talks to `Cognition` directly.** When you ask Hermes anything, `@planner` **internally** group-chats `Cognition` *before* answering you.
*   Caps: **3 rounds, 10 messages per send** — keeps room from spinning.
*   Each Bot keeps its own persistent `Group: Cognition` session underneath the shared room — **room context survives like any Hermes conversation**, so the *group* gets smarter too, not just the Bots.
*   You see **one answer**, but **4-6 Bots deliberated in 3 rounds** behind the scenes.

**How a Deep Answer Happens (User → Cognition → You):**

```
1. You: "Research AI harness architectures 2026 and build best Hermes evidence pipeline"

2. Hermes routes to @planner (not to you directly)

3. @planner group-chats Cognition:
   - @world: "Last 3 harness searches, AVO and DGM highest value, but Genie 3 world models are now P0"
   - @belief: "Claim 'AVO 10.5% over FlashAttention' confidence 0.83, 5 sources, but dependent belief 'AVO generalizes' only 0.61 — need second wave"
   - @curriculum: "This task difficulty 0.7, novelty high, transfer high — worth learning value, select it"
   - @self: "Research on harness: empirical 0.91 (was 0.89, delta +0.02) — @planner is calibrated for this"
   → @planner returns 6-plan portfolio, but now *informed by persistent world/belief/curriculum/self* that have watched for weeks

4. @world spawns research via @memory's past experience:
   - @memory: "Last harness research, query 'agent harness comparison 2026' found 3 sources but missed 'awesome list' — adding that"
   → 5 parallel searches + browser + evidence graph

5. While you sleep that night:
   - @dream reviews this trajectory → detects "harness research always misses 'awesome list'" → generates abstraction → creates candidate skill `harness-research-v2`
   - @self updates: "research on harness: empirical 0.89 (was 0.91, delta -0.02) — recent regression"
   - @world updates causal graph: "awesome list query → +2 sources"

6. Next time you ask similar: Hermes is already better — without you teaching it

7. Verification: @verifier (different model, no builder context) checks not just G1-G12, but also @belief's dependent beliefs and @world's counterfactual branches
```

**Per official docs:**
*   If you **@mention specific Bots** in group, only they respond. If you mention **nobody**, all members decide independently whether to reply or pass — *"Not every Bot replies to every message. Speaking is each member's own choice."*
*   Bots can **escalate to you** via `@user` when judgment needed → group header shows **`needs you` badge**, room pauses for human input (human-in-the-loop).
*   **Cross-machine groups:** Picker shows Bots from every registered connection with **device badge** (`dixie · Mac Mini`) and **disambiguated `@name-device`** handle.

---

## 4. BOT-TO-BOT AS NEURAL SIGNALING

In basic mode, `@researcher have a look at this` hands work to another Bot.

In AGI mode, **Bot-to-bot IS the neural signaling** — Bots message each other *without you*:

```
@planner → @world: "Re-estimate WORLD_STATE for harness domain"
@planner → @belief: "What is confidence on claim A and its dependents?"
@world → @memory: "What past harness research missed awesome list?"
@memory → @skill-forge: "Successful harness research trajectory → candidate skill?"
```

Each handoff is a **persistent per-bot `Bot Chat`** + `message_agent` capability with sender attribution (`Message from @world (@world): ...`), delivered as `hermes -p <bot> chat --in ~ -c "Bot Chat" -Q -q "..."` — your text is **never forwarded verbatim**.

---

## 5. HOW THIS MAPS TO YOUR HERMES ADVANCED STACK

```
Your Current HERMES-Advanced (11 skills, 15 planes):
  - 06-memory-world: World model plane, but as *conceptual* subsystem
  - 11-deep-cognition: 19 deep recommendations as *SKILL.md prose*

This Skill 12 (Bot Mode AGI):
  - Makes them *living Bots* that *stay alive* and *run on schedule*
  - World Model plane → @world Bot that has watched for weeks
  - Self-Model prose → @self Bot with 142 empirical samples
  - Sleep-time permission → @dream Bot running 13-step cycle at 2am
  - Skill Acquisition prose → @skill-forge Bot that actually forges skills while you sleep

Result: docs/08-Deep-Cognitive-Architecture.md "Hermes AGI Stack" target:

                    HERMES
                       |
        +--------------+--------------+ 
     COGNITION      MEMORY         AGENCY
     (@planner,     (@memory,      (@mission,
      @belief)       @dream)        @skill-forge)
        |              |              |
        +--------------+--------------+ 
                       |
                 WORLD MODEL (@world)
                 SELF-MODEL (@self)
                       |
                 LEARNING + SIMULATION + SELF-IMPROVEMENT + EVALUATION + GOVERNANCE
                 (@curriculum, @verifier)
```

---

## 6. CAVEATS — WHAT BOT MODE STILL CAN'T DO (Even for AGI)

*   **No live interruption:** Bot-to-bot is **per-invocation, not live** — receiving Bot sees handoff in inbox **next time it runs**. `@dream` cannot interrupt `@planner` mid-thought. Don't design real-time neural loops that require it. Listed as future work in official docs.
*   **No new safety model:** Each Bot is a **full Hermes agent with real system access** — 10 persistent Bots = **10x the attack surface**. Your `05-safety-evaluation` R0-R6 + 22 invariants must gate **every Bot exactly as before**, but now across 10 persistent profiles. Same scoped-permissions discipline, multiplied.
*   **Coordination overhead unproven at 10:** Official demo was 2-3 Bots on a game. 10-Bot `Cognition` group (6 Bots) has **no public benchmark** — start with 4-6, measure if `Cognition` reliably beats single `@planner` before scaling to 10.
*   **Memory divergence:** 10 Bots with isolated `MEMORY.md` will **diverge** — `@world`'s world ≠ `@self`'s world after a week. You need a **sync routine** (e.g., `@world` broadcasts `WORLD_STATE` summary to all via group chat weekly) or they become 10 strangers.

---

## 7. QUICK START — BUILD THE 10-BOT BRAIN (15 Minutes)

**Prerequisite:** Hermes Desktop v0.20.3+ (Bot Mode default-on, Settings → Plugins → Hermes Bots)

**Step 1: Create the 10 Bots (Once, 10 minutes):**
```
Hermes Desktop → Bots tab → Create Bot (×10):
  For each row in table in §1:
    Name: world (etc.)
    Role: Paste "What It IS Forever" column
    Model: Pin per table (e.g., @planner → strongest reasoning)
    Skills: Attach per table (e.g., @world → 06-memory-world)
    SOUL.md: Your 05-HERMES-Advanced/SOUL.md (50 sections, shared)
```

**Step 2: Wire Routines (5 minutes):**
```
Click each Bot → Routines tile → New Routine:
  @dream → 0 2 * * * → 13-step sleep cycle text from §2
  @world → 0 */4 * * * → Re-estimate WORLD_STATE
  @self → after every task (hook) → Update empirical self_model
  (etc. per §2 table)
```

**Step 3: Create the Cognition Group (1 minute):**
```
Bots tab → New Group Chat → Pick: planner, world, belief, self, verifier, curriculum
Name: Cognition
```

**Test:** Ask Hermes: *"Research AI harness architectures 2026"* — watch `@planner` group-chat `Cognition` before answering. Check `@world`'s `Bot Chat` the next day — it should have re-estimated.

---

## 8. TEMPLATES

---

## 9. PRE-BUILT MASTER PROFILE: `profiles/hermes-asi-master/`

Instead of creating 10 individual profiles manually, you can directly deploy the **Unified Master Profile**:
- **Location:** `05-HERMES-Advanced/profiles/hermes-asi-master/`
- **Internal Engines:** Active Python scripts (`scripts/`) for Bayesian belief updates, empirical self-tracking, 13-step sleep cycles, and formal verification.
- **State Stores:** Live JSON files (`state/`) for `world_state.json`, `self_model.json`, `belief_graph.json`, and `mission_graph.json`.
- **Routines:** Automated cron jobs in `routines/` for nightly Letta dreaming (`01_nightly_dream.json`) and 4-hour world sync (`02_world_sync.json`).

```bash
# Instant Deployment:
cp -r 05-HERMES-Advanced/profiles/hermes-asi-master ~/.hermes/profiles/
hermes -p hermes-asi-master chat
```


- **Bot Creation Checklist:** `templates/bot-creation-checklist.md`
- **Cognition Group Prompt:** `templates/cognition-group-prompt.md`

---

*SKILL 12 — Hermes Bot Mode AGI. Turns Bot Mode from roster into AGI-oriented architecture: 10 persistent Bots as cognitive organs, routines as organs, group chats as reasoning loops. Makes Hermes DEEPER not bigger — the path from Advanced Protocol to Learning Architecture. From expert review dfsdg (19 recommendations) + official Bot Mode docs (PR #87886, v0.20.3).*

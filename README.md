# Hermes ASI Master — Unified Research Division

Unified repository for Hermes ASI cognitive engines, agent frameworks, and learning systems.

## Structure

```
hermes-asi-master/
├── src/                          # Core cognitive engines
│   ├── evolution/                # Bayesian evolution & strategy search
│   └── learning/                 # Phase 7 Learning System
│       ├── curriculum.py        # Personalized learning paths
│       ├── experience_replay.py  # Experience replay for learning
│       ├── self_eval.py          # Self-evaluation engine
│       ├── skill_forge.py        # Skill acquisition forge
│       └── tests/                # Learning system tests
├── libs/
│   ├── debate-room/              # Multi-agent debate & consensus (85 tests)
│   │   └── debate_room/          # Package source
│   └── agentforge-x/             # Core agent framework (91 tests)
│       └── agentforge_x/         # Package source
├── scripts/                      # Operational scripts
├── requirements.txt              # Dependencies
└── README.md
```

## Quickstart

```bash
# Install all dependencies
pip install -r requirements.txt

# Run all tests
pytest libs/debate-room/tests/ libs/agentforge-x/tests/ src/learning/tests/

# Run individual suites
pytest libs/debate-room/tests/          # 85 debate-room tests
pytest libs/agentforge-x/tests/         # 91 agentforge-x tests
pytest src/learning/tests/              # 103 learning system tests
```

## Components

### debate-room (libs/debate-room/)
Multi-agent debate & consensus framework. Three roles (Proposer, Critic, Judge)
engage in structured k-round debates with consensus scoring.

### agentforge-x (libs/agentforge-x/)
Multi-agent fleet framework with six specialized agents (Researcher, Critic,
Coder, Tester, Writer, Ops), rubric-based judging, and YAML presets.

### Phase 7 Learning System (src/learning/)
Self-improving learning system with curriculum engine, experience replay,
self-evaluation, and skill forge. Designed for integration with Hermes ASI
cognitive engines.

## Total Tests: 277+

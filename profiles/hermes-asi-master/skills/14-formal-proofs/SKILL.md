---
name: hermes-formal-proofs
description: Neuro-symbolic theorem proving, formal invariant verification, and Z3/Lean 4 mathematical logic checks.
version: "1.0.0"
author: Hermes Advanced Team
license: MIT
metadata:
  hermes:
    tags: [hermes, formal-verification, z3, lean4, theorem-proving, zero-hallucination]
    category: hermes-advanced
---

# SKILL 14 — NEURO-SYMBOLIC FORMAL PROOFS & Z3

> **Load this skill when:** Validating mission-critical algorithms, cryptography, safety invariants, or mathematical properties.

---

## 1. Formal Proof Workflow

```
Natural Language Spec -> Formal Proposition -> SMT / Lean4 Encoding -> Prover Execution -> Verification Certificate
```

## 2. Invariant Rules
- Code tagged with `R5` or `R6` requires automated SMT solver verification (`G11 Formal Proof Gate`).
- Zero tolerance for simulated or hallucinated proofs; only solver-verified certificates are accepted.

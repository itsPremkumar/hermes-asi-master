# Gates and scoring — getting the split right

Everything else in this harness depends on getting this split right at FRAME time. Get it wrong and the loop either rejects good work over trivial technicalities, or quietly accepts bad work because the score looked fine.

## What makes a good gate

A gate is a hard constraint: binary, checked mechanically wherever possible, and non-negotiable regardless of score.

Good gates share these properties:

- **Binary.** Pass or fail, no partial credit. "Mostly accessible" is not a gate; "meets the required accessibility checks" is.
- **Checkable without judgment.** A test suite passing, a schema validating, a word count under a limit, every citation resolving to a real source — these don't require someone to decide how they feel about the result.
- **Non-negotiable.** If it's tempting to say "well, it failed this gate, but the score is so good," it isn't actually functioning as a gate. Either demote it to a heavily-weighted score dimension, or fix the gate's definition so it means what's actually intended.

Common gates by task:
- Code: existing tests still pass; it builds and runs; no change to a public interface that wasn't asked for.
- Research/writing: every material claim traces to a source actually retrieved this run; no fabricated attribution; stated length or format constraints are met.
- Data work: output matches the expected schema; row counts reconcile; no silent data loss.

## What makes a good score

A score measures degree, for things where more-or-less genuinely applies once the gates are already satisfied.

- Prefer a rubric with named dimensions over a single vibe-based number. "8/10" means little on its own; "rigor 4/5, clarity 3/5, actionability 4/5, weighted to 7.8/10" can actually be argued with.
- Keep the rubric short — three to five dimensions. A twelve-dimension rubric mostly measures how patient the evaluator was that day.
- Tie the score back to the criterion from FRAME explicitly. If the criterion was "benchmark improves >10%," the score is the benchmark's actual output, not a proxy for it.

## The failure mode to watch for

The single most common way this harness produces a bad result: a gate gets treated as a score. Something "almost" passes a hard constraint, the candidate otherwise looks strong, and it gets committed anyway with a mental note to fix the gate issue later. It doesn't get fixed later. Log it as a gate failure and reject it — the discipline only works if it's applied even when the exception feels reasonable in the moment.

## Worked examples

**Task: "make this Python function faster."**
- Gates: existing unit tests pass; output is identical to the original on the existing test fixtures; no new dependency added.
- Score: wall-clock benchmark on the provided input, direction = minimize.
- Execute = actually change the code and actually run the benchmark and the tests via the shell, not "this should be faster because it avoids the extra loop."

**Task: "write a due-diligence memo on a company."**
- Gates: every financial figure cites a source retrieved this run; the memo states its own confidence level per section; no claim presented as fact that was actually inferred.
- Score rubric: coverage of the standard due-diligence categories (3), source quality and recency (3), clarity of the risk section specifically (2), overall actionability (2) — weighted to 10.
- Execute = draft the section; the following EVALUATE pass is a literal re-check of every citation against the source, not a re-read for tone.

**Task: "give me the best tagline for this product."**
- Gates: fits the stated length limit; doesn't reuse a name or phrase asked to be avoided.
- Score: this is the domain where a rubric is weakest — voice and impact are genuinely subjective. Generate several genuinely different candidates rather than iterating one candidate toward a self-assigned score, and let the user pick, with a one-line note on what each one is going for.

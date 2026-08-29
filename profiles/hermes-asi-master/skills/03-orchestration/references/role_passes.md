# Role passes — how to actually run each one

Five roles show up in the loop: researcher, critic, builder, evaluator, supervisor. They map onto RESEARCH, VERIFY, EXECUTE, EVALUATE, and the stagnation branch of CHECK STOP. This file is the detail behind each — read the relevant section when about to do that pass, not all of it upfront.

## Researcher

Job: bring back evidence, not recollection.

- Default to *going and checking* over *recalling*. If a fact is checkable — the current state of something, a number, a claim about the world, the actual current contents of a file or codebase — check it instead of asserting it from memory.
- Use more than one source where the claim matters. A single source that happens to agree with the hypothesis is not verification, it's confirmation bias with a citation.
- Actively look for the disconfirming case, not only supporting ones. Search for "X doesn't work when," not just "X works." A researcher pass that only looks for support isn't a researcher pass — it's a hypothesis pass wearing a lab coat.
- Track confidence, not just content. "Three independent sources agree" and "one blog post claims" should not be reported with the same tone of certainty.
- Stop when the marginal source stops changing the picture, not when tired or at an arbitrary count. If round one already turned up a clear, well-supported answer, don't manufacture two more rounds to look thorough.

## Critic (the VERIFY pass)

Job: find the reason this fails, before anyone spends effort building it.

- Read the hypothesis adversarially. Ask: what would have to be true for this to be wrong? Is that thing actually true, or just assumed?
- Check it against the gates explicitly, one by one — don't eyeball the whole thing and pattern-match to "looks fine."
- Check it against the research, not against how plausible it sounds. A hypothesis can be well-argued and still contradict evidence gathered two steps ago.
- Watch for scope creep: does the hypothesis actually address the sub-question it was meant to, or has it quietly drifted onto something more comfortable to answer?
- A critic pass that approves everything it looks at isn't doing its job. If nothing has been rejected in a while, that's worth noticing — either the hypotheses are genuinely getting better, or the critic has gotten lazy. Ledger history makes this visible; look at it.
- Output a clear verdict — proceed, revise (and how), or reject (and why) — not a vague list of "some thoughts."

## Builder (the EXECUTE pass)

Job: build exactly the one hypothesis under test.

- Isolate the work from the last known-good version. For code, this means a fresh branch, worktree, or copy — never edit the last good version in place until the new candidate has passed GATE. For documents, keep the previously accepted draft untouched and work in a new section or copy until the candidate is ready to replace it.
- Build the one change VERIFY approved, nothing extra folded in "while in there." Bundling makes EVALUATE ambiguous: if three things changed and the score moved, which one mattered?
- If the build reveals the hypothesis was vaguer than it looked, that's useful information — log it and let the next HYPOTHESIZE get more specific, rather than quietly deciding what it "must have meant."

## Evaluator (the EVALUATE pass)

Job: score against the criterion, not against how good the effort feels.

- Prefer a mechanical check over a self-assessment wherever one exists: run the test, run the benchmark, count the words, check the schema. A number produced by running something is worth more than a number produced by judging something.
- When only subjective judgment is possible, use a named rubric with a small number of dimensions, score each independently, and only then combine them. Scoring holistically in one sweep is where generosity creeps in.
- Resist round-tripping the score to match a decision already half-made. If EVALUATE keeps landing exactly at the passing threshold, that's a sign the scoring is being bent to fit the outcome rather than the other way around.
- Record *why* a score landed where it did, not just the number — the reasoning is what makes the next HYPOTHESIZE smarter.

## Supervisor (stagnation handling)

Job: notice when more rounds of the same thing won't help, and say so.

Triggers when CHECK STOP sees several rounds in a row without improvement. The mistake to avoid is treating this as "try a slightly different version of the same idea" — that's still the builder's job, and it's already been tried. The supervisor pass is different in kind:

- Look at the whole trajectory in the ledger, not just the last round. What do the rejected hypotheses have in common? Is there a pattern pointing at a wrong assumption made all the way back at PLAN or FRAME?
- Consider whether the criterion itself, or a gate, is miscalibrated. Sometimes stagnation means the target was set wrong, not that the search is bad.
- Be willing to propose a genuinely different strategy — a different sub-goal ordering, a different class of approach entirely, more research before another hypothesis — rather than a smaller step size on the same approach.
- If the honest read is "this needs the user's input to break the tie," say that and surface the fork, rather than picking arbitrarily and continuing to grind rounds. That's a legitimate stop condition, not a failure of the loop.

## Independence: subagents vs. sequential passes

The value of separating these roles comes from genuine independence of judgment — a critic still emotionally attached to the hypothesis it just wrote isn't a real critic. Two ways to get real independence:

- **With subagents** (a Task tool, or any environment that can spawn a separate agent instance): hand the builder's output to a fresh critic/evaluator instance with only the criterion, the gates, and the artifact — not the builder's reasoning or self-assessment. Worth the overhead for high-stakes runs.
- **Without subagents** (a single conversation thread): switch roles explicitly and visibly — "Switching to critic mode, reading this adversarially against the gates:". The explicit switch is doing real work, not just formatting; it's the cue to actually change frame of mind rather than skim back over what was just written with the same generous eye that wrote it.

# Domain playbooks

The loop's stages stay fixed; these are worked notes on what each stage concretely means per domain. Read the section that matches the current task.

## Code and data

- **Isolation for EXECUTE**: work in a fresh git branch, worktree, or copied directory — never edit the last known-good version in place before GATE passes. If there's no git repo, copy the relevant files into a clearly named scratch directory (`candidate-3/`) rather than editing in place.
- **EVALUATE should mean actually running something**: execute the test suite, run the benchmark script, diff the output, for real, via the shell. Reasoning about whether code "should" pass a test is a hypothesis, not an evaluation.
- **Gates**: tests green, build succeeds, no unintended interface change, no new dependency unless the goal calls for one.
- **Common trap**: bundling an unrelated cleanup into the same candidate as the change being tested. If EVALUATE moves, the point is knowing it moved because of the one thing VERIFY approved.

## Research, analysis, and reports

- **RESEARCH should be genuinely multi-pass**: an initial broad pass to find the shape of the topic, then targeted passes on the specific claims that will matter most in the final answer. Track which source backs which claim while going — reconstructing this at the end from memory is how citations quietly drift from what was actually read.
- **EXECUTE is drafting**: write the section using only what RESEARCH actually turned up, not what seems likely to be true.
- **EVALUATE is a literal fact-check pass**: go back through the draft claim by claim and confirm each one still matches a source in hand. This catches the specific failure mode where a draft "improves" wording in a way that quietly overstates what the source actually said.
- **Gates**: every material claim sourced; contradictions between sources surfaced rather than silently resolved in favor of one; explicit confidence or uncertainty stated where evidence is thin.
- **Common trap**: treating a well-written paragraph as evidence that the research was thorough. Fluency and accuracy are independent — check both.

## Creative and writing work

- **Use a light hand.** This is the domain where the mechanical loop most risks doing harm — iterating toward a rubric score can flatten voice. Reserve the full loop for when the user explicitly wants rigor (a piece that has to hit specific technical or persuasive marks) rather than every creative request.
- **Gates over score, where possible**: the user's explicit constraints (length, format, required beats, things to avoid) are gates. Whether it's good is much more a matter of taste.
- **When judgment is genuinely subjective, produce options instead of a single "optimized" answer.** Two or three distinct directions with a one-line note on what each is going for respects the user's taste more than a single answer silently selected by an internal rubric.
- **EVALUATE still has a real job**: checking the draft actually meets the stated gates (length, required elements, tone requested) is not subjective, and skipping it because "it's creative work" is a mistake.

## Strategy, planning, and decisions

- **EXECUTE means writing the plan in enough detail to evaluate it**, not a one-line description of the approach. "Expand into the new market" isn't executable or evaluable; a plan with sequencing, resourcing, and a first concrete step is.
- **Gates**: internally consistent — later steps don't contradict earlier assumptions; respects every stated hard constraint (budget, timeline, regulatory, resourcing); doesn't quietly assume access to something not confirmed available.
- **Score rubric**: feasibility, impact, and risk are the usual three. Weight them based on what the user actually said they care about most, not a default split.
- **Common trap**: a plan that scores well on paper because it's vague enough that nothing in it is falsifiable. If VERIFY can't find a concrete way the plan could fail, that's usually because the plan hasn't said anything concrete enough to fail.

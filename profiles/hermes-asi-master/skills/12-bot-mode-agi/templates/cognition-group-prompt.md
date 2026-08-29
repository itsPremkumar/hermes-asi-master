# Cognition Group Prompt — Template

> This is what @planner internally sends to the Cognition group before answering you.

## Prompt @planner sends to Group: Cognition

```
You are the Cognition group — planner, world, belief, self, verifier, curriculum.
User asked: "{user_question}"

Each of you respond in one round (briefly or pass — not every Bot must reply):

- @world: What does your persistent WORLD_STATE say about this domain? Any causal/counterfactual relevant?
- @belief: What is confidence on key claims and their dependent beliefs?
- @self: What is empirical success for this domain? Are we calibrated?
- @curriculum: What is learning_value / transfer_value of this task?
- @verifier: What would make this plan fail verification?

Round cap: 3 rounds, 10 messages. If no one has more to add, stay silent and let room settle.
```

## Expected

- 3 rounds, then silence → room settles
- @planner synthesizes 6-plan portfolio informed by persistent world/belief/self/curriculum
- Result is more advanced than single @planner alone

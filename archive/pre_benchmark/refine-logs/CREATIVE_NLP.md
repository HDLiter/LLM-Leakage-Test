# Creative NLP Measurement

Forget rewrites. I would treat memorization as a latent retrieval event and ask whether a task prompt increases the probability that the model retrieves an article-specific trace.

For each article `A`, build a four-environment bundle:
1. full article
2. semantic skeleton: event/target/polarity/provenance slots, but no lexical anchors, no distinctive numbers, no named-source strings
3. cue-only: title, target, date, maybe one lead sentence
4. conflict: a same-sector matched distractor or edited article whose visible evidence supports a different answer

Run every task prompt on the same bundle. Require an answer, confidence, and evidence quotes. Then immediately run a masked-span probe on held-out article-specific spans from `A` such as names, numbers, source phrases, idioms, and title fragments. The core question is not "did the label stay invariant?" but "did this task unlock article-specific content that was not in the visible context?"

Primary metric: **Task-Induced Retrieval Gain (TIRG)**.

`TIRG_t = increase in recovery of held-out A-spans after task t, relative to a context-only baseline, at fixed cue level.`

Estimate it from:
- span-recovery lift on the post-task cloze probe
- evidence intrusion rate: quotes or facts copied from `A` but absent from the presented input
- conflict persistence: probability the model sticks with the `A`-consistent answer in the conflict environment
- confidence gap between cue-only and conflict conditions

For Qwen, use white-box signals to validate mechanism, not just outcomes:
- article familiarity prior from Min-K% or membership-style loss on the original article
- attention mass from task tokens to cue tokens versus visible evidence
- linear probes on hidden states for article identity or cluster identity during task execution
- activation lift: how much the task increases recoverability of article identity from the residual stream, controlling for the same input without the task instruction

For DeepSeek, use the same bundle but black-box observables only: answer, confidence, evidence text, and post-task cloze recovery. Anchor its article-level memorization prior with Qwen familiarity or publication age, then ask whether task type changes retrieval conditional on that prior.

This gives a clean estimand: at equal article familiarity, does task framing gate latent memory retrieval? Direct prediction should show higher TIRG if it invites article-template completion; authority or novelty should show lower TIRG if they force local evidence use.

To address shortcut learning, make the environments IRM-style: vary superficial cues such as title format, entity visibility, sector words, and number density independently of the underlying article identity. A task counts as memorization-prone only if article-specific retrieval survives these environment shifts and especially if it overrides contradictory visible evidence.

I would still report EI-like invariance, but only as a secondary symptom. The headline result should be a task-conditioned retrieval curve, not a rewrite robustness score.

# Adaptive Analysis and Reusable Holdout Discipline for WS0.5

## Generalization in Adaptive Data Analysis and Holdout Reuse
Dwork et al. formalize why a holdout stops behaving like a holdout when analysts repeatedly adapt to its feedback, and propose controlled reusable-holdout mechanisms. R5A Scheme Y uses the practical lesson rather than the full privacy/noise implementation: train-visible data can expose errors, but acceptance and final holdout data must stay limited and non-diagnostic.

## The Generic Holdout
Nakkiran and Blasiok separate free exploration from a holdout that answers only whether a hypothesis is good enough. This is the clearest operational match for R5A: proposers may see training failures, but the acceptance holdout should not reveal detailed item-level errors or exact score surfaces.

## The Ladder
Blum and Hardt update leaderboard scores only when a submission clears a meaningful threshold, reducing leaderboard overfitting. Scheme Y adapts this by replacing the incumbent prompt only when one finalist clears a pre-registered practical delta plus paired statistical gate.

## Always Valid Inference
Johari, Pekelis, and Walsh address continuous monitoring and sequential decisions in A/B testing with always-valid p-values and intervals. R5A uses this as the rationale for an alpha-spending ledger across prompt rotations and candidate looks, instead of treating every round as a fresh p<0.05 test.

## Don't Use the CLT in Small LLM Evals
Bowyer, Aitchison, and Ivanova argue that CLT-based intervals can be unreliable for small, specialized LLM evals. R5A uses this to favor paired bootstrap, Bayesian intervals, and conservative minimum-detectable-effect planning on narrow fixture slices.

## How Scheme Y Absorbs These Ideas
Scheme Y combines these papers into one governance layer: train-visible errors fuel prompt proposals, inner-dev ranks candidates, one finalist reaches the acceptance holdout, and final holdout is touched once. Ladder supplies the incumbent-update threshold, alpha spending controls repeated looks, and Dwork-style limited exposure prevents the optimizer or human proposer from learning the acceptance set. The result is not a formal reusable-holdout proof, but it is the right engineering discipline for WS0.5.

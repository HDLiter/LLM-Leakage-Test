# Prompt Optimization Frameworks for WS0.5

## DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines
Khattab et al. turn prompt-heavy LM systems into declarative programs whose modules can be compiled against task metrics. For R5A WS0.5, this is the clean Scheme X target: topic classification, entity extraction, and signal profiling could become DSPy signatures/modules, but adopting it wholesale would add adapter, serialization, and frozen-prompt export risk during the WS0.5 window.

## MIPRO: Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs
Opsahl-Ong et al. show that instructions and few-shot demonstrations can be optimized jointly with black-box LM calls, minibatch scoring, and surrogate-guided search. Scheme Y borrows MIPRO as a candidate generator idea while keeping acceptance outside the optimizer, because MIPRO can still overfit an exposed validation surface if governance is weak.

## GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning
Agrawal et al. use natural-language reflection, Pareto-frontier preservation, and prompt merging to learn high-level rules from failures. This maps directly to R5A error logs such as missing entity, wrong topic, or schema violation; Scheme Y treats GEPA as the strongest future proposer but wraps it with limited-exposure holdout discipline.

## TextGrad: Automatic "Differentiation" via Text
Yuksekgonul et al. frame textual feedback as gradients over variables in compound AI systems. R5A can use this idea without adopting the full framework by generating structured textual gradients from train-visible failures and turning them into bounded prompt patches.

## ProTeGi / APO: Automatic Prompt Optimization with "Gradient Descent" and Beam Search
Pryzant et al. use minibatches, textual gradients, beam search, and bandit selection to improve prompts. This is the closest algorithmic form of the current Claude/Codex patch loop, so Scheme Y can add a ProTeGi-style proposer to broaden the candidate pool without changing the production prompt format.

## OPRO: Large Language Models as Optimizers
Yang et al. prompt an LLM with prior solutions and scores so it proposes better solutions, including prompts. R5A can use OPRO as a simple low-cost proposer, but WS0.5 explicitly rejects repeatedly exposing one dev set to OPRO until it wins.

## PromptWizard: Task-Aware Prompt Optimization Framework
Agarwal et al. optimize task prompts through feedback-driven critique and synthesis over instructions and in-context examples. It is a plausible black-box alternative if DSPy integration is too heavy, especially for producing human-readable frozen prompts, but Scheme Y still requires an external acceptance gate.

## EvoPrompt: Connecting LLMs with Evolutionary Algorithms
Guo et al. use evolutionary search to maintain and mutate prompt populations. R5A uses this as support for population-based search over one-off patch duels, while treating validation leakage and candidate-count control as the main risk.

## APE: Large Language Models Are Human-Level Prompt Engineers
Zhou et al. generate candidate instructions automatically and select them by measured performance. For R5A, APE is best used for seed prompts or conservative rewrites rather than as the whole tuning loop, because it lacks the later reflective and validation-governance machinery.

## Auto-CoT: Automatic Chain of Thought Prompting
Zhang et al. automatically build diverse chain-of-thought demonstrations. WS0.5 cites it mainly as a boundary condition: R5A extraction/classification tasks should not default to visible CoT unless a named failure cluster benefits and schema errors do not rise.

## Why Scheme Y, not Full DSPy Scheme X
Scheme X is cleaner architecturally, but WS0.5's immediate risk is statistical, not merely optimizer strength: repeated adaptive use of dev slices can accept lucky prompt patches. Scheme Y keeps the current frozen-prompt deliverable, adds a capped candidate pool informed by GEPA/MIPRO/ProTeGi/OPRO, and puts a limited-exposure acceptance gate outside every optimizer. That gives R5A most of the SOTA search benefit without forcing a DSPy migration before the validation protocol is hardened.

Entity masking is **not necessary for EMNLP Findings acceptance** if the paper already adds the **local placebo** and retains **matched-format + sham**. The local placebo repairs a construct-validity problem in the primary metric; entity masking does not. It asks a different, mechanistic question: how much of the suspicious invariance is keyed to visible entity names. That is a good strengthening, but not acceptance-critical.

If you add it, **fold it into Block 3**, not as a new standalone block. Conceptually it belongs with the reviewer-facing falsifications. Operationally, I would keep it as a **Tier1 appendix ablation**, not a full-paper pillar. A separate block makes the paper look like a control battery rather than a result paper.

The paper has too many controls when the reader must track: metric repair, matched-format, sham, entity masking, temporal decay, concordance, plus optional heterogeneity, before the main finding feels stable. At that point the method story is overtaking the empirical claim. For Findings, the center of gravity should remain:
1. fixed-input task ordering,
2. one metric-validity repair,
3. one semantic/format falsification package.

My recommended scope is: **local placebo + entity ablation on Tier1**, not the full `2x2`. The full `2x2` is cleaner scientifically, but it is too expensive relative to what it buys at this stage. You already need the local placebo. A Tier1 masking ablation is enough to answer the obvious reviewer question about entity-triggered recall without multiplying the entire run matrix.

Two cautions. First, the current prompts are explicitly **target-conditioned** (`Target: {target}`, `target_echo`), so masking is not a clean identification device: if the raw target name remains in the prompt, some retrieval cue remains. Second, the current masking code in [`src/masking.py`](D:\GitRepos\LLM-Leakage-Test\src\masking.py) is still blunt placeholder masking (`[实体N]`), which is not obviously a paper-ready primary intervention for evidence-based prompts. That further argues against making masking central. If run, keep it narrow and describe it as a **mechanism probe**, not a rescue of the main estimand.

The **10-week timeline survives** if masking is limited to Tier1 and treated as secondary. It probably does **not** survive a full `2x2` without cutting either Block 4 depth or paper-polish time.

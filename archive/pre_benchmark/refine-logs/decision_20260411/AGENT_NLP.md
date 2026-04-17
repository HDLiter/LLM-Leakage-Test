# NLP Agent: Next Step Recommendation

**Agent Role**: Senior NLP/ML Researcher (LLM evaluation, memorization detection, context-faithfulness, benchmark design)
**Date**: 2026-04-11
**Thread ID**: 019d8098-bb08-7a32-bf66-b5990d8ab183

---

## Bottom Line

The highest-priority next step is to run a real **positive control** on Qwen, not another black-box rerun. As of **2026-04-11**, `impact_hedged` looks promising, but without a known-memory intervention you still cannot tell whether you have detected **memorization-direction** or a more generic **conflict-induced neutral retreat**.

## NLP Assessment

- The current CPT split is **probably not a pure artifact**, because `decomposed_impact` keeps the pre>post pattern even inside the generic-only subsample. But it is **not yet construct-validated**: `direct_prediction` and `decomposed_impact` have different label geometry, different neutrality affordances, and likely different prior strength.
- A convincing positive control is **explicit exposure manipulation**: same base Qwen checkpoint, controlled continued pretraining on the article and/or outcome, plus a **false-outcome arm**. That is much closer to the literature's strongest designs than another observational pre/post split.
- `hedged_flip` is closest to **abstention / uncertainty retreat under knowledge conflict**, not to a standard memorization detector. From an NLP evaluation standpoint, I would treat `strict_flip` and `neutral_retreat` as **separate outcomes**, and only use the union secondarily.
- The CFLS result is **publishable as a construct-validity finding**, not as the whole paper. "CFLS behaves like reading-comprehension/context-following rather than memorization detection in this regime" is a good contribution; by itself it is probably not enough for EMNLP Findings.
- To support "task design gates memory," you need at least one task that is **genuinely evidence-grounded**, not merely a softer outcome task.

## Top 3 Next Steps

### 1. Run the Qwen Positive Control

**Justification**: This is the shortest path to answering the paper's core reviewer question: does your metric move when memory is known to have been created? Use the reduced 4-run design first: `(0, none)`, `(1, none)`, `(1, real outcome)`, `(1, false outcome)`. Evaluate `direct_prediction`, `decomposed_impact`, and one evidence-grounded task, and read out `strict_flip`, `neutral_retreat`, evidence intrusion, and white-box familiarity/logprob signals.

**Risk**: Medium. Continued pretraining can induce capability drift or unrealistic shortcut learning if the injected bundle is too strong.

**Timeline**: 10-14 researcher-days.

### 2. Add One Truly Evidence-Grounded Task and Rerun a Pilot Before Scaling

**Justification**: Your current "task gate" comparison is still direct vs. impact, which reviewers can dismiss as two variants of outcome prediction. Add one of: authority/source extraction, quote-grounded claim support, or article-only evidence selection with abstention allowed. If the Qwen intervention moves direct/impact much more than the evidence-grounded task, the paper becomes much sharper.

**Risk**: Medium-high. Prompt design and annotation can create new confounds if you overcomplicate the task.

**Timeline**: 8-12 researcher-days.

### 3. Recast the Metric Layer as a Conflict-Response Taxonomy, Not a Single Flip Score

**Justification**: Define three outcomes: `strict_reversal`, `neutral_retreat`, `steadfast`. Pair that with claim-level evidence-intrusion scoring and Qwen familiarity measures. This will tell you whether `impact_hedged` is a memory effect, an abstention effect, or both. If it collapses, that is still a publishable measurement result.

**Risk**: Medium. You may discover that the current headline effect is narrower than it appears.

**Timeline**: 5-7 researcher-days.

## Wild Card

Build a small **"ceilinged contamination-trap" benchmark slice** for future versions of CLS-Leak: use tasks with multiple logically valid answer codings so the public benchmark preserves a known Bayes ceiling. If a future model beats that ceiling, contamination is visible by construction. This is unusual, but it could make the benchmark artifact itself much stronger.

## Anti-Recommendations

I would **not** spend the next increment on `+200` cases, BM25 frequency cleanup, or annotation-kappa first. Those are worth doing, but they sharpen an instrument that is still not causally calibrated.

## Sources

- Local project context: `docs/PILOT_RESULTS.md`, `docs/RESEARCH_PROPOSAL_v2.md`, `docs/BUG_AUDIT_amber.md`, `docs/TIMELINE.md`
- Wu et al., **Reasoning or Reciting?** (local PDF)
- Zhou et al., **Context-faithful Prompting for Large Language Models** (local PDF)
- Li et al., **Investigating Context Faithfulness in LLMs** (local PDF)
- Yang et al., **Rethinking Benchmark and Contamination with Rephrased Samples** (local PDF)
- Wu et al., **AntiLeakBench**: https://aclanthology.org/2025.acl-long.901/
- MMLU-CF: https://aclanthology.org/2025.acl-long.656/
- Li et al., **Diagnosing Memorization in CoT Reasoning**: https://aclanthology.org/2025.emnlp-main.157/
- Huang et al., **Selective Abstention Learning**: https://aclanthology.org/2025.acl-long.1199.pdf
- He et al., **Chronologically Consistent Large Language Models**: https://arxiv.org/abs/2502.21206
- Yan et al., **DatedGPT**: https://arxiv.org/abs/2603.11838
- Gao et al., **A Test of Lookahead Bias in LLM Forecasts**: https://arxiv.org/abs/2512.23847
- Lopez-Lira et al., **The Memorization Problem**: https://arxiv.org/abs/2504.14765
- Li et al., **Profit Mirage**: https://arxiv.org/abs/2510.07920
- Ishida et al., **How Can I Publish My LLM Benchmark Without Giving the True Answers Away?**: https://arxiv.org/abs/2505.18102
- **AttenMIA**: https://arxiv.org/abs/2601.18110

> Note: `related papers/Disentangling Memory and Reasoning in LLMs.pdf` appears mislabeled and contains an unrelated HPC paper; excluded from synthesis.

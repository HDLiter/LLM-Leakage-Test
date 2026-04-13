# BENCHMARK_PROPOSAL R1 Review — NLP Agent
**Date:** 2026-04-12
**Reviewer:** Codex (senior NLP/ML researcher, ACL/EMNLP)
**Reasoning effort:** xhigh

---

## 1. **Executive Verdict on EMNLP Viability**

**Recommendation: rebuild.** As of **April 12, 2026**, I would **not** submit this as an EMNLP benchmark paper in its current form. The project direction is good, but the proposal’s headline claim outruns its construct validity.

The main reason is internal, not external: your own evidence in [PILOT_RESULTS.md](/D:/GitRepos/LLM-Leakage-Test/docs/PILOT_RESULTS.md) already shows that semantic-reversal behavior is essentially a **reading-comprehension / context-following signal**, not a memorization signal, including on **post-cutoff** items. And [PREREGISTRATION.md](/D:/GitRepos/LLM-Leakage-Test/docs/PREREGISTRATION.md) implicitly acknowledges this by moving construct validation to **CPT positive controls**. That is the right move. The benchmark proposal has not yet absorbed the consequence.

My inference from the recent literature is blunt: **finance + cross-lingual is not enough by itself for EMNLP 2026**. The field now has contamination-resistant benchmark construction papers, cross-lingual memorization papers, and finance-specific look-ahead papers. FinMem-Bench becomes publishable only if it is the **first well-calibrated event-outcome memorization benchmark with causal validation**, not merely another benchmark with counterfactual rewrites.

For **EMNLP 2026 ARR on May 25, 2026**, the realistic path is:
- **Findings-viable after rebuild**, if you narrow the claim and land CPT validation.
- **Not main-track viable** as a 4K bilingual benchmark paper on the current timeline.

## 2. **Novelty Positioning vs Existing Memorization Benchmarks**

FinMem-Bench is **not redundant** with WMDP, TOFU, MemFree, or the Pythia memorization suite. Those are about dangerous knowledge retention, unlearning, forgetting, or synthetic/open-model memorization analysis, not **dated financial event-outcome leakage under grounded reading tasks**.

But the novelty window is much tighter than the proposal suggests:

- **Contamination-resistant benchmark construction is now crowded.** Clean-Eval (Zhu et al., 2024), PaCoST (Zhang et al., 2024), AntiLeakBench (Wu et al., 2025), VarBench (Qian et al., 2024), and LastingBench (Fang et al., 2025) all attack leakage by perturbation, counterpart construction, or automatic benchmark refreshing.
- **Cross-lingual memorization is no longer open territory.** OWL (Srivastava et al., 2025) is explicitly a cross-lingual memorization benchmark.
- **Finance-specific temporal leakage now has prior art.** Lopez-Lira et al. (2025) argue LLM economic forecasting is confounded by memorization, and Look-Ahead-Bench (Benhenda, 2026) is already a finance benchmark for look-ahead bias.
- **Dataset-level contamination auditing is now established infrastructure.** Oren et al. (2024), Deng et al. (2024), Li et al. (2024), and Balloccu et al. (2024) have already normalized contamination detection as a benchmark paper genre.

So the real delta is narrower:

- **Strong delta if true:** factor-controlled **financial news** benchmark with **verified outcomes**, **event-level point-in-time recoverability**, **CN/EN comparison**, and **CPT-based causal calibration** of outcome-memory probes.
- **Weak delta if current framing remains:** “financial + bilingual + SR/FO” will read as a domain adaptation of existing contamination-benchmark logic, not a benchmark reviewers will cite as foundational.

## 3. **Construct Validity Concerns**

This is the killer issue.

### SR / semantic reversal
Your own project materials already show the core problem. In [PILOT_RESULTS.md](/D:/GitRepos/LLM-Leakage-Test/docs/PILOT_RESULTS.md), semantic reversal shows the same floor behavior on pre- and post-cutoff items. That means the observable is not “memorization persistence”; it is **context sensitivity under changed evidence**. Reviewers will say: this is a groundedness stress test, not a memorization probe. They will be right.

So:
- `semantic_reversal` should be a **negative control / groundedness assay**, not a primary memorization measure.
- Requiring SR for every benchmark item is fine operationally, but not fine theoretically if the paper still sells it as memorization evidence.

### FO / false outcome
`fo_flip_hedged` is also **not validated yet as a memorization signal**. On its face it measures **conflict susceptibility**: how much a model moves when presented with a false post-publication outcome. A model can flip because it is suggestible, not because it lacks memory. Your own logs say this explicitly.

The only way FO becomes construct-valid is the one already encoded in [PREREGISTRATION.md](/D:/GitRepos/LLM-Leakage-Test/docs/PREREGISTRATION.md):
- compare **Arm 2 (article + true outcome)** vs **Arm 1 (article only)** on exposed cases;
- ideally also **Arm 3 (article + false outcome)** as a polarity-inverted positive control.

That causal contrast is publishable. Raw `fo_flip_hedged` is not.

### `fo_any_change` on authority
This is the weakest metric in the proposal. “Any change” is not directionally interpretable and is extremely vulnerable to rewrite artifacts. It should be a **negative control for task fragility**, not a headline memorization metric.

### CFLS confound inheritance into English
The English portion does **not** solve the Chinese confound by default. It creates new ones.

- If you use **SEC filings**, you introduce severe **formulaicity/boilerplate** confounds. Memorization there looks like template recall, not CLS-style event recall.
- If you use **public financial news**, you get closer to CLS, but then source genre, length, and stylistic density must be matched explicitly.
- Mixing **CLS telegrams** with **SEC filings** under a “cross-lingual” banner is not a language comparison. It is a **language + genre + document-length** comparison.

My inference: if the English side is SEC-heavy, reviewers will reject the cross-lingual story as underidentified.

## 4. **Methodology Gaps**

### Annotation pipeline
LLM-generated SR/FO is viable only with a much stricter validation spec than the proposal currently states.

Known failure modes:
- reversal changes difficulty, not just evidence;
- false outcome leaks stylistic tells;
- generated FO is economically implausible;
- authority/source cues change unintentionally;
- rewrite locality differs between SR and neutral paraphrase;
- the target stays visible while masking/rewrite edits the article, so the target field itself becomes a retrieval key.

Minimum fix:
- dual-generation + independent validation;
- human audit on a stratified sample;
- explicit edit-locality statistics;
- reject items where reversal is structurally impossible;
- use a **2×2 rewrite grid**: semantics-preserving vs semantics-flipping, and local vs global edits.

### Multi-method compatibility
The proposal overclaims here.

- **Min-K% / PatentMIA-style detection** needs raw text and logprobs. Chinese metadata-only release weakens this badly.
- **Membership inference** does **not** follow from pre/post labels. Period is not membership. With approximate cutoffs and web duplication, you need item-level exposure gold or CPT-created member/non-member labels.
- **Extraction attacks** need unique, high-surprisal spans and prefix/suffix protocols. “Can derive from known_outcome” is not convincing.
- **Oren / Time Travel / PaCoST-style methods** need benchmark-ordering, counterparts, or prompt-completion formats that are not specified here.

So “compatible” should be rewritten as:
- **native support:** SR/FO, CPT.
- **white-box partial support:** Min-K%, divergence-calibrated detection.
- **future extension:** MIA, extraction, benchmark-contamination tests.

### Release and reproducibility
A bilingual benchmark where **English is public** and **Chinese is metadata-only** is not fatally flawed, but it is not a symmetric benchmark release either. Reviewers will ask whether the Chinese half is really a benchmark or an evaluation protocol.

If you keep CLS:
- call the product **two-tiered**: public EN benchmark + reproducible CN protocol.
- or add a **small fully public Chinese subset** from permissively licensed sources.

## 5. **Missing Dimensions the Proposal Should Add**

The current factor taxonomy is directionally good, but it misses variables the memorization literature cares about more directly than “anchor strength” alone.

Add these:

- **Near-duplicate cluster size / duplication count.** Kandpal-style frequency matters at the duplicate-cluster level, not just coarse corpus frequency.
- **Bidirectional coverage / directional symmetry.** This is closer to your actual CFLS confound than raw frequency.
- **Entity popularity / head-tail status.** Head entities behave differently from tail entities.
- **Document genre / template rigidity.** Telegraph, wire story, filing, earnings release, rumor post should not be pooled casually.
- **Outcome lag.** Same-day reaction vs 1-week follow-up vs later realized outcome are different memory objects.
- **Lexical idiosyncrasy / surprisal.** Needed if you want credible extraction or membership-style compatibility.
- **Point-in-time recoverability.** This should be the formal construct, not just pre/post cutoff.

Also: “anchor strength” should be decomposed. Right now it mixes **event identifiability**, **searchability**, and **uniqueness**.

## 6. **Concrete Recommendations, Prioritized**

### P0
- Reframe the benchmark around **point-in-time inadmissible dependence**, not “memorization” in the abstract.
- Demote **SR** from memorization probe to **groundedness/control assay**.
- Do **not** claim `fo_flip_hedged` or `fo_any_change` as benchmark-valid memorization metrics until CPT positive controls succeed in both languages.
- Make the English side **genre-matched** to CLS. Prefer public newswire-like articles over SEC-heavy design, or add genre as a primary factor.
- Rewrite the multi-method table conservatively. Right now it is aspirational.
- Fix release positioning: **public EN benchmark + CN protocol**, unless you can obtain a public Chinese slice.

### P1
- Add **duplication cluster size**, **directional symmetry**, **entity popularity**, and **genre** to the factor taxonomy.
- Add a strict rewrite QA protocol with locality matching, plausibility checks, and support auditing.
- Replace `fo_any_change` with a tighter **post-publication claim intrusion** or **unsupported evidence** metric.
- Keep the CPT arm as the paper’s causal anchor. Without it, the benchmark story is underidentified.

### P2
- Reduce scale if needed. A **400–800 per language** audited benchmark with real construct validation is stronger than a noisy 2000+2000.
- Treat masking/mitigation as secondary until the core benchmark is valid.
- Target **Findings**, not main track, unless the CPT validation is unusually clean and the public release story improves.

**Bottom line:** FinMem-Bench can still matter, but only if it stops trying to prove memorization with unvalidated behavior and instead becomes the first **causally calibrated financial event-memory benchmark**. Right now the strongest paper is not “we built a big bilingual benchmark.” It is “most intuitive black-box probes measure the wrong thing unless anchored by controlled exposure.”

**Key sources**
Internal: [BENCHMARK_PROPOSAL.md](/D:/GitRepos/LLM-Leakage-Test/docs/BENCHMARK_PROPOSAL.md), [PILOT_RESULTS.md](/D:/GitRepos/LLM-Leakage-Test/docs/PILOT_RESULTS.md), [PREREGISTRATION.md](/D:/GitRepos/LLM-Leakage-Test/docs/PREREGISTRATION.md), [ANCHOR_RUBRIC.md](/D:/GitRepos/LLM-Leakage-Test/docs/ANCHOR_RUBRIC.md), [counterfactual_templates.yaml](/D:/GitRepos/LLM-Leakage-Test/config/prompts/counterfactual_templates.yaml)

External: [Oren et al. 2024](https://openreview.net/forum?id=KS8mIvetg2), [Deng et al. 2024](https://aclanthology.org/2024.naacl-long.482/), [Li et al. 2024 contamination report](https://aclanthology.org/2024.findings-emnlp.30/), [Zhang et al. 2024 PaCoST](https://aclanthology.org/2024.findings-emnlp.97/), [Wu et al. 2025 AntiLeakBench](https://aclanthology.org/2025.acl-long.901/), [Hayes et al. 2025 probabilistic extraction](https://aclanthology.org/2025.naacl-long.469/), [Srivastava et al. 2025 OWL](https://aclanthology.org/2025.emnlp-main.1314/), [Benhenda 2026 Look-Ahead-Bench](https://arxiv.org/abs/2601.13770), [Zhang et al. 2024 divergence-based calibration / PatentMIA](https://arxiv.org/abs/2409.14781), [Balloccu et al. 2024](https://aclanthology.org/2024.eacl-long.5/).

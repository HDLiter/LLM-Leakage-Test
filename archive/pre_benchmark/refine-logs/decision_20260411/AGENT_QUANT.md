# Quant Agent: Next Step Recommendation

**Agent role:** Senior quantitative finance researcher (alpha signals, factor decay, production LLM pipelines)
**Date:** 2026-04-11
**Thread:** 019d8098-7b3c-7931-8586-a5de01a8fc37

---

## Recommendation

Highest priority is to run the **Qwen positive control now**. Adding more cases before that would tighten an observational result, but it would not solve the main problem, which is still identification.

| Priority | Next step | Why now | Main risk | Est. |
|---|---|---|---|---|
| 1 | **Run Phase F on Qwen as a matched positive control**: preferred `2x3` CPT with article exposure `0/1` and outcome state `none/real/false`; acceptable MVP is the reduced 4-run design `[(0,none),(1,none),(1,real),(1,false)]` on `direct_prediction` and `decomposed_impact`. | This is the only step that can turn the current `impact_hedged` OR=`1.95` from an association into a calibrated causal result. It also matches where the literature is going: controlled contamination and time-consistent models, not just black-box probes. | CPT can induce capability drift or an unnatural shortcut if the injected outcome block is too strong. Keep filler corpus, token budget, and held-out sanity checks fixed across arms. | **6-8 researcher-days** for reduced 4-run; **8-12** for full `2x3` |
| 2 | **Add orthogonal triangulation on the existing 606 cases**: Qwen `Min-K%` familiarity + narrow evidence-intrusion labels on the same items. | This is the fastest way to test whether the `impact_hedged` cases are also the ones that look more familiar or leak more post-publication claims. That is more valuable than more N right now. | `Min-K%` is a familiarity prior, not outcome-memory proof; evidence-intrusion labeling can be noisy. Keep the intrusion taxonomy narrow. | **4-6 researcher-days** |
| 3 | **Then do the replication pass**: fix `frequency_class x period`, add about **200 cases**, and rerun the MH analysis. | This is for stability and heterogeneity, not identification. It matters because your current 80% MDE is about OR=`2.4`, above the observed OR=`1.95`. | More N can still replicate a biased design if the confound fix is not done first. Annotation drift is the operational risk. | **6-9 researcher-days** |

---

## Quant Read

- **Is OR=`1.95` economically meaningful?** Yes as a **contamination-control effect**, not yet as an alpha result. A `12.3%` vs `6.8%` false-outcome hedging gap is large enough to distort historical feature validation, but it does not by itself tell you how much live IC or PnL inflation it creates.

- **Best positive control for a quant audience:** the Qwen CPT design above, because it creates a **known contamination dose**. The false-outcome arm is especially persuasive since it separates Type B outcome memory from generic article familiarity.

- **Power vs causal identification:** prioritize **causal identification first**. More cases under the current design mostly buy precision around a result whose construct validity is still partially open.

- **What direct_prediction suggestibility means in production:** treat naked outcome-proximal prompts as **unsafe backtest primitives**. They appear too willing to follow plausible narratives. If used at all, they should be secondary features behind evidence-grounded extraction, PIT models, and adversarial false-outcome stress tests.

- **Venue:** **EMNLP 2026 Findings** is still the right primary target. A finance venue is premature unless you add a clean downstream decay/PIT comparison; right now the contribution is measurement/identification, not a production trading paper.

---

## Wild Card

Run a **dose-response calibration** on Qwen: inject each event bundle `0/1/2/5` times, fit a curve from known contamination dose to `impact_hedged`, then map DeepSeek's observed OR onto an **implied contamination-equivalent dose**. That would give quant readers a much more interpretable statement than "there is some memorization-direction signal."

---

## Sources

### Internal
- [PILOT_RESULTS.md](docs/PILOT_RESULTS.md)
- [RESEARCH_PROPOSAL_v2.md](docs/RESEARCH_PROPOSAL_v2.md)
- [BUG_AUDIT_amber.md](docs/BUG_AUDIT_amber.md)
- [TIMELINE.md](docs/TIMELINE.md)
- [Assessing Look-Ahead Bias GPT Sentiment.pdf](related%20papers/Assessing%20Look-Ahead%20Bias%20GPT%20Sentiment.pdf)
- [Memorization Problem LLMs Economic Forecasts.pdf](related%20papers/Memorization%20Problem%20LLMs%20Economic%20Forecasts.pdf)
- [Counterfactual Memorization in Neural Language Models.pdf](related%20papers/Counterfactual%20Memorization%20in%20Neural%20Language%20Models.pdf)
- [Detecting Pretraining Data from Large Language Models.pdf](related%20papers/Detecting%20Pretraining%20Data%20from%20Large%20Language%20Models.pdf)
- [Profit_Mirage_Revisiting_Information_Leakage_in_LL.pdf](related%20papers/Profit_Mirage_Revisiting_Information_Leakage_in_LL.pdf)

### Web (2024-2026)
- Chronologically Consistent Large Language Models (2025): https://arxiv.org/abs/2502.21206
- The Impact of Post-training on Data Contamination (2026): https://arxiv.org/abs/2601.06103
- All Leaks Count, Some Count More (2026): https://arxiv.org/abs/2602.17234
- Chronologically Consistent Generative AI (2025): https://arxiv.org/abs/2510.11677
- Overestimation in LLM Evaluation (2025): https://arxiv.org/abs/2501.18771
- Reasoning or Reciting? Exploring the Capabilities and Limitations of Language Models Through Counterfactual Tasks (2024): https://arxiv.org/abs/2307.02477

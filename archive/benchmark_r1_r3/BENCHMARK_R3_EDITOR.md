# BENCHMARK MVP R3 Decision Check — Editor Agent
**Date:** 2026-04-13
**Reviewer:** Codex (senior EMNLP area chair, continuing R1+R2 persona)
**Reasoning effort:** xhigh
**Source:** docs/DECISION_20260413_mvp_direction.md
**R1/R2 references:** BENCHMARK_R1_EDITOR.md, BENCHMARK_R2_EDITOR.md

---

1. **Per-decision verdicts**

- **Decision 1: OK-with-concern.** Deferring the final rhetorical frame is more honest than forcing a taxonomy-first story before seeing whether partitions actually separate. The danger is not "framing later"; the danger is letting "framing later" become "claim later." Freeze the allowed paper shell now: a Findings-style resource/evaluation paper on factor-conditioned detector behavior. Do not leave open a later jump back to probe-validity, causal intervention, or tooling.
- **Decision 2: OK-with-concern.** Point-in-time market mechanics are useful as covariates and partition fields. The coupling risk is venue drift: intraday bars, abnormal returns, and exchange-calendar logic can pull the paper toward quant-finance if they become the centerpiece. For EMNLP, these fields must stay in service of the NLP question, not become the novelty claim.
- **Decision 3: OK.** One case per event cluster is exactly the right anti-bloat discipline. It reduces duplication, leakage, and paper sprawl.
- **Decision 4: OK.** Computing realized outcomes from raw fields instead of freezing labels is editorially defensible. It keeps the release more reusable and avoids label ossification. The only discipline needed is one clearly pre-registered primary horizon.
- **Decision 5: NEEDS-REWORK.** Directionally correct, but not yet legally or editorially clean enough. Reprint replacement helps; the current wording still overclaims with "public domain" and still leaves an awkward mixed benchmark if CLS-only cases remain inside the main artifact.
- **Decision 7: NEEDS-REWORK.** LLM-first annotation with disagreement review is a reasonable production workflow, but not yet a credible gold-benchmark validation plan. Two LLMs can agree and still be wrong in correlated ways. You need explicit random human audit, versioned prompts/models, and a rule for what portion of the final benchmark is human-validated.
- **Decision 9/10 coupling:** No objection in principle. Decision 9 is good discipline. Decision 10 only becomes dangerous if "economic/linguistic/statistical meaning" is used to justify too many factors.

2. **Decision 5: legal/editorial opinion on the reprint strategy**

This addresses my R2 licensing-fatal concern **partially, not fully**.

Replacing a CLS telegram with the original SSE/SZSE announcement, when the CLS item is substantively just a repost/transcription of that official disclosure, is a much better rights position than redistributing the CLS text. Editorially, that is the right direction. But do not call those exchange disclosures "public domain" unless counsel confirms that under the relevant law. Publicly accessible is not the same as public domain, and official exchange sites themselves assert copyright notices. What you can say safely is: these are **official public disclosures intended for equal public access**, which is a much cleaner benchmark source than a proprietary newswire or terminal-like feed.

The closest NLP precedent is not "ACL venues bless mixed-rights news redistribution." The closer precedent is the opposite: when news rights are messy, dataset papers either work from controlled/public sources or avoid redistributing full text. Older news datasets often released IDs/URLs or derived features when rights were unclear; when authors did redistribute text, it was usually because the source was controlled, public, or treated as clearly reusable. Finance-specific precedent exists, e.g. FIRE used publicly accessible financial news plus SEC filings, but ACL acceptance is not legal clearance.

Editorially, if the reprint-replacement rate is **60%+**, then yes, that can become the **public benchmark core** I wanted, but only if the paper is explicit:

- Primary artifact: `FinMem-Bench-Public`, fully releasable text, all main benchmark tables here.
- Secondary artifact: `FinMem-Bench-Licensed` or `FinMem-Bench-Extended`, non-public or access-restricted, clearly not required for reproducing the core claims.

What I would not submit is a single benchmark described as one resource where **60% has releasable text and 40% is metadata-only** and then run the headline analysis on the combined set. Reviewers will say, correctly, that you did not release the benchmark you evaluated.

If you insist on including the 40%, the editorial workaround is strict: all primary claims and detector comparisons run on the public core; the non-public remainder is secondary robustness only, or omitted from the submission version entirely. If licensing is still unresolved by **April 19-20, 2026**, the safer submission strategy is a **fully public-only core** built entirely from SSE/SZSE/company/gov disclosures and to drop the CLS-heavy expansion from the May submission.

Also: do not build the paper around "small-volume fair use." That is not a serious benchmark-release strategy for ARR/EMNLP.

3. **Decision 7: reviewer-defense strategy for LLM annotation**

"LLM-annotated benchmark" can survive at EMNLP Findings or a Datasets/Benchmarks track, but only under a narrow pattern: **LLMs propose; humans verify; the released evaluation set is not presented as unreviewed silver.**

Recent accepted precedent supports that pattern, not a pure LLM-gold pattern. WebWalkerQA (ACL 2025) used GPT-4o to generate initial QA pairs and then human annotators to verify and refine the final set. LongCite / LongBench-Cite (Findings ACL 2025) used automated LLM construction, but backed the evaluation story with human checks showing the automatic judge correlated with humans. NuNER (EMNLP 2024) and Multi-News+ (EMNLP 2024) show EMNLP is comfortable with LLM-annotated data for training, pretraining, or cleansing. The cautionary side is equally clear: Annolexical (Findings NAACL 2025) had to validate downstream on human-labeled benchmarks, and "Just Put a Human in the Loop?" (Findings ACL 2025) shows LLM suggestions can shift label distributions even when humans review them.

The strongest objections are:

- **Quality / correlated error:** most fatal for a benchmark. Claude and Codex agreeing is not proof.
- **Circularity:** second most fatal if annotation LLMs are close cousins of evaluated models.
- **Reproducibility:** real, but easier to neutralize with prompt/version release.

Pre-emption strategy:

- Release prompts, model versions, dates, and adjudication rules.
- Treat LLM outputs as proposals, not gold.
- Human-review **all disagreements** and a **random sample of agreements**.
- Report human-LLM agreement, LLM-LLM agreement, and an error taxonomy.
- If possible, keep the benchmark's final evaluation core human-adjudicated.

My editorial threshold: **5% is too low. 10% is borderline. 20% random audit plus 100% of disagreements is the minimum credible plan.** For a 500-800 case benchmark, the cleaner answer is stronger: fully human-verify the final public evaluation split.

4. **Realistic timeline assessment**

**May 25, 2026: no as the base plan.** It remains a stretch scenario, not a realistic operating plan.

Bluntly: with R4/R5/R6 still pending, the public-core licensing path still unsettled, schema freeze not fully complete, annotation pilot not yet run, and the paper frame still intentionally deferred, you do not have enough slack for a clean ARR May submission unless three things happen by **April 19-20, 2026**: licensing path fixed, paper shell fixed, and pilot launched immediately. If those do not happen by then, stop pretending May 25 is the plan. The honest target becomes **August 3, 2026** or later.

5. **Minimum publishable plan: placeholder abstract**

This paragraph is honest only under one narrowed submission plan: **public-core primary, licensed extension secondary, Findings-style resource/evaluation paper**.

*We present FinMem-Bench, a factor-annotated Chinese financial-text audit set for studying when memorization detectors surface higher outcome-memory risk. The benchmark is organized at the event-cluster level and links publicly releasable official-source texts to key entities, announcement timestamps, point-in-time market mechanics, and verified realized outcomes computed from raw market data. Rather than introducing a new detector, we evaluate whether existing memorization scores vary systematically across economically and linguistically defined news regimes, and whether these differences are stable across models and tasks. To preserve reproducibility and releaseability, we distinguish a fully public benchmark core from any larger licensed extension and run primary analyses on the public core. FinMem-Bench is intended as a Findings-style resource and evaluation substrate for factor-conditioned auditing of memorization risk in Chinese financial news.*

6. **Priority fixes before R4 launch**

1. Resolve the release policy by **April 19-20, 2026**: what counts as public-core text, what does not, and stop using the phrase "public domain" unless verified.
2. Freeze the paper shell now: Findings resource/evaluation, public core primary, licensed extension secondary.
3. Upgrade Decision 7 into a real validation protocol: random human audit of agreement cases, all disagreements adjudicated, prompt/model versioning frozen.
4. State explicitly that all headline results must be reproducible from the released public core.
5. Keep Decision 2 subordinate to the NLP claim so the paper does not drift into a quant event-study submission.

Relevant precedents consulted: WebWalkerQA / WebWalker (ACL 2025) https://aclanthology.org/2025.acl-long.508/ ; LongCite / LongBench-Cite (Findings ACL 2025) https://aclanthology.org/2025.findings-acl.264/ ; NuNER (EMNLP 2024) https://aclanthology.org/2024.emnlp-main.660/ ; Multi-News+ (EMNLP 2024) https://aclanthology.org/2024.emnlp-main.2/ ; Annolexical paper (Findings NAACL 2025) https://aclanthology.org/2025.findings-naacl.75/ ; "Just Put a Human in the Loop?" (Findings ACL 2025) https://aclanthology.org/2025.findings-acl.1323/ ; FIRE (Findings NAACL 2024) https://aclanthology.org/2024.findings-naacl.230/ ; MIND (ACL 2020) https://aclanthology.org/2020.acl-main.331/ ; SSE disclosure-access references https://english.sse.com.cn/news/newsrelease/c/4947425.shtml and SZSE fair-disclosure reference https://www.szse.cn/disclosure/notice/general/t20060810_499657.html

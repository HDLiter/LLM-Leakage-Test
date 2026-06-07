---
role: Editor / narrative and venue-fit
session: R5A Temporal Cue Design
thread_id: 019d93f5-e59d-76b0-9981-2b9dd04c8fbd
model_reasoning_effort: xhigh
generated: 2026-04-15
---

## Block A

The underlying annotation should be **multi-dimensional**, but the paper should expose a **collapsed reviewer-facing version**. A raw 6-level ladder in the main text is too much for a 9-page paper; it will read like ontology work.

- Main-text view: use `explicit`, `indirect`, `none` as the paper-facing bins.
- Keep two appendix flags: `closed-reference lookup` and `removable (adjunct) vs irreducible (subject)`.
- Full L4/L3/L2/L0.5/L0/L1 can live in supplement as the operational map behind those bins.

I would not merge L2 and L0.5. Both need inference, but only `L0.5` makes the **date lookup itself** the likely memorization signal. `L3` should count as in-text, not lookup-heavy; resolving a missing year from local context is not the same construct as retrieving `WAIC 5th edition -> 2022` from memory. `subject-type vs adjunct-type` is a separate axis, because it governs **manipulability**, not clarity.

- For articles with multiple cues, store a **cue inventory vector**.
- For observational analysis, derive `highest usable cue`.
- For D11 eligibility, derive `highest removable cue`; that is the only summary that matters for intervention.

Annotation should be **hybrid**: rules for obvious L4/L3/L1 cases, LLM assist for L2/L0.5/L0 and subject-vs-adjunct, human adjudication on disagreements. Reuse the existing `time anchor` idea from the anchor rubric rather than inventing a totally new ontology. Editorially, I would want `alpha/kappa >= 0.80` on the collapsed paper bins and `>= 0.70` on fine appendix subtypes.

For reviewer accessibility, the one-sentence gloss should be: **temporal-cue clarity measures how much the text itself tells the model when the event happened.**

## Block B

Recommendation: **both**, but asymmetrically.

As a factor, temporal-cue clarity should be a **secondary** factor, not spine. It strengthens the paper only if framed as the **text-side counterpart to Cutoff Exposure**: exposure asks whether a model could have seen the event; cue clarity asks how easily the input can reactivate that memory. If you elevate it to spine, the paper risks sounding like a chronology benchmark rather than a finance memorization benchmark.

- Best placement: Bloc 0, with an explicit caveat that Bloc 0 now contains both a case×model temporal variable and a text-level temporal accessibility variable.
- Better name for methods prose: `Temporal Cue Accessibility`; `clarity` is fine as informal shorthand.
- Construct caveat: it measures **retrieval accessibility from the input**, not true event time and not chronology reasoning in general.
- Literature provenance: `PARTIAL` for surrounding chrono-control work, `NOVEL` as a benchmark factor operationalization.

As a manipulation, it is more valuable. The dose-response edit is one of the few additions that could become a remembered methodological hook, because it reads like an identification strategy rather than another detector. But that only holds if adjunct-type coverage is real. Right now there is **no estimate** in the repo, so editorially I would require a fast coverage audit before selling this as headline design.

Observation and manipulation are complementary, not redundant. The factor gives breadth; the manipulation gives causal-style leverage on a subset. That combination also differentiates FinMem-Bench from `MemGuard-Alpha`, `Profit Mirage`, `Look-Ahead-Bench`, and `LiveTradeBench`, which do not isolate **text-side temporal trigger strength** this directly.

## Block C

Recommendation: **split conceptually into D4a and D4b, but do not spend two detector slots on them**.

`D4a` and `D4b` are distinct constructs. `D4a` is text-prompt temporal conflict; `D4b` is prompt-level chronology compliance after text cues are removed. That distinction is real. But from a paper-shape perspective, this should be **one ADG family with two sub-measurements**, not two headline detectors.

- `D4a` is the more legible one for reviewers.
- `D4b` is the more redundant one once D11 exists, because it lives on the same time-masked input regime.
- Relative to `CMMD`, ADG is complementary in principle but still secondary in narrative priority. CMMD remains the main temporal detector.

I would not give ADG major main-text space unless D11 is dropped. The full split version is too detector-zoo-like for the main paper, and its prompt-engineering flavor is weaker for finance venues than a text-intervention story. Default editorial placement: **appendix or one compact sensitivity panel**.

- The `matching as-of date` condition for `D4a` is a necessary control; without it, the contradiction result is underidentified.
- The full `76,800`-call split design is not justified as main-text budget.

## Block D

Recommendation: **adopt, but reshape**. D11 should not be a standalone detector slot; it should be a **temporal stress-test module** applied to a small number of core detectors.

That is the version with the cleanest narrative. As a standalone detector, D11 is too meta and bloats the result tables. As a scoped intervention module, it becomes memorable: FinMem-Bench can weaken time anchors by minimal edits and observe whether memorization signals decay.

- Run it on 2 core detectors, not the whole pool.
- My editorial choice would be one temporal detector (`CMMD`) and one text-conflict detector (`D5 SR/FO` or `D3`), then stop.
- Main success condition: detector scores attenuate monotonically as time cues are removed, and the attenuation is stronger on pre-cutoff / high-anchor / closed-reference cases than on controls.
- Dominant failure mode: generic information loss or answerability loss. You must report `coverage/abstention` alongside the score change and include a matched non-temporal deletion control.
- Subject-type L0.5 cases stay in the observational factor analysis but are excluded from the intervention arm.
- If manipulable coverage is low, or subject-type share is above roughly the brief's `>30%` concern zone, D11 becomes appendix-only.

D11 and D4 are not the same intervention. D11 manipulates the **text**; ADG manipulates the **prompt**. But D11 does largely eat `D4b`'s lunch from a narrative standpoint. If D11 is adopted, `D4b` should be folded into appendix sensitivity, not kept as a separate main-text story.

Abstract/intro sell snippet:

> FinMem-Bench exploits a distinctive property of financial news: temporal anchors can often be weakened by minimal edits without changing the underlying event. We construct time-attenuated variants of the same CLS article and test whether memorization signals decay as explicit temporal cues disappear. This temporal dose-response separates detector reliance on retrievable time anchors from generic event understanding, a control absent from prior finance leakage benchmarks.

That snippet is clean enough to justify keeping D11 in some form.

## Block E

Presentation-wise, this should be a **pre-registered primary-vs-sensitivity split**, not a new within-case crossover dimension across all perturbation detectors.

- Global default for primary analyses: **preserve original temporal cues**.
- Rationale: otherwise D5/D6/D7 each become two interventions at once, and the tables become unreadable.

Per detector:

- `D5 SR/FO`: preserve the original date in primary analysis. Removing time changes more than one slot and muddies the construct.
- `D6 FinMem-NoOp`: the inserted clause should ideally contain **no new temporal cue**; if fluency requires one, it should be generic and time-consistent with the source item, never deliberately mismatched in the primary run.
- `D7 EAD`: do **not** expand to a 2x2x2 main taxonomy. Time masking can be a small appendix sensitivity, not a benchmark-wide eight-cell design.

Without pilots, the principled choice is simple: keep time preserved in the main detector definitions, and preregister one limited sensitivity branch where time is masked. That is much easier to explain than another crossed design axis.

## Cross-Block Synthesis

The clean narrative is not "FinMem-Bench adds yet another detector." It is: **memorization depends on both exposure opportunity and retrieval cue accessibility**, and temporal cues give the benchmark a rare way to observe the latter and experimentally weaken it.

- Best paper-facing design: a **collapsed 3-bin taxonomy plus two appendix flags**, temporal cue as a **secondary factor**, D11 as a **scoped intervention module**, and ADG as an **appendix or compact sensitivity family**.
- That keeps the central claim intact. Temporal cue handling strengthens the paper if it sharpens the exposure story; it dilutes the paper if it becomes a second ontology plus two more detector slots.
- This is also the clearest differentiation story: `MemGuard-Alpha` has detector stacking, `Profit Mirage` / `Look-Ahead-Bench` / `LiveTradeBench` have point-in-time or evaluation-scheme leakage control, but FinMem-Bench can show **text-level temporal trigger dependence** by minimal intervention.
- Tension with Step 1: the editor ceiling still matters. If D11 is promoted, it must consume **module space**, not **detector-slot space**. ADG cannot also expand into two headline detectors.
- Questions for other lenses: can NLP annotate `closed-reference` and `subject vs adjunct` reliably; can Stats define the minimum manipulable-coverage threshold and monotonicity/control test that makes D11 publishable; can Quant price a reduced D11 run on 2 detectors rather than full-pool expansion.
- Paper-space cost: the **recommended** package adds about **1 compact taxonomy table, 1 dose-response figure, and 4-5 short paragraphs** total. The **full** package adds roughly **1 taxonomy table, 2 additional figures, and 6-8 paragraphs**, which is about **2 main-text pages** and too expensive for a 9-page paper.

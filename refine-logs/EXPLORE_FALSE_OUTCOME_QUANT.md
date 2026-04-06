# False-Outcome CPT: Quant View

False-outcome continued pretraining does **not** make counterfactual (CF) article rewrites fully redundant. It can become the cleanest **causal mechanism** test: hold article semantics fixed, randomize which outcome memory is injected, and ask whether direct prediction follows the planted label while authority extraction remains stable. That would be strong evidence that outcome memory drives prediction and that task design gates that channel. But it does **not** replace a test of whether a deployed model actually follows article semantics when the article changes.

## 1. Are CF rewrites redundant for the core claim?

For the narrow claim, **"task design blocks injected outcome memory,"** false-outcome CPT is sufficient and arguably stronger than CF rewrites. For the broader claim, **"the model is reasoning from article semantics rather than recalled outcomes,"** CF rewrites are still necessary.

## 2. Unique contribution of each test

- **False-outcome CPT** uniquely gives causal identification. Randomized exposure means a shift toward the false planted label is direct evidence that parametric outcome memory can control prediction.
- **CF article rewrites** uniquely test semantic responsiveness and context-faithfulness at inference time. If economically meaningful edits do not flip the answer, the model is not following visible text, regardless of how its memory was formed.

They are therefore **complementary**, not duplicates: CPT tests the memory channel; CF tests text-grounding.

## 3. Which matters more for production signal validation?

From a quant production perspective, **CF rewrites are more relevant**. Signal validation asks whether the live model responds correctly to economically meaningful changes in the article. False-outcome CPT is mainly a lab mechanism experiment and a strong paper-quality causal anchor, not the main production audit.

## 4. How to structure the CPT corpus

Use matched **event bundles** with a fixed template:

- **Article block**: original article only.
- **Outcome block**: structured post-event summary for the target and horizon, e.g. `T+1` and `T+5` signed return, bucket, plus one short rationale sentence.

Create three arms:

- `article only`
- `article + true outcome`
- `article + false outcome`

Keep formatting, length, horizon, and style identical across arms. False outcomes should be **sign-flipped or materially altered but still market-plausible**, not absurd. Hold evaluation events fully out of CPT and balance exposure by event type, prominence, and date.

## 5. Main risk

Yes, false-outcome training can break the comparison if it changes more than memory:

- It may degrade general market priors or calibration.
- It may teach the model to overweight the appended outcome block versus article semantics.
- It may create distributional artifacts that reveal the arm from style.
- Large dosage may cause broad interference rather than event-specific memory.

Mitigation: keep exposure small (`100-200` bundles), mix with a large clean corpus, equalize formatting, use plausible false labels, and run sanity checks on general financial instruction-following plus held-out text-grounded tasks.

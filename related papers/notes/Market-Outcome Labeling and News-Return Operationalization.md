# Market-Outcome Labeling & News-Return Operationalization

*Literature basis for the R-1k/l/m market (quote-driven) case-label factors: F_mktdir (direction),
F_mktmag (magnitude), F_mktcap (size). Collected 2026-06-04 via two Codex search passes + two
verification workflows (citation-integrity + adversarial refutation). Cite counts: OpenAlex/Semantic
Scholar, retrieved 2026-06-04.*

## Framing
Real A-share returns are used as **case labels** (descriptive outcome tags answering "what kind of
outcome-case gets memorized more"), **NOT** as a prediction target and **NOT** as a causal
event-study CAR. This framing decides every operational choice below.

## Headline conclusion (confirmed across two rounds + adversarial verification)
- **Return window: task-dependent convention, not a settled standard.** No survey prescribes a
  canonical "news-reaction" return window. Event-study uses CAR over symmetric windows; NLP
  prediction uses short windows (+20min / next-day / t→t+1); each self-defines.
- **Direction encoding: convention, not settled.** Event studies keep returns continuous; NLP uses
  binary up/down or self-defined 3-class.
- **Neutral-band threshold: NO authoritative numeric anchor.** An adversarial agent actively
  hunted for a standard and failed; the instances found are mutually contradictory (see below),
  which positively confirms "each dataset self-defines."
- **Raw vs abnormal: depends on purpose.** For a descriptive label, raw return is the realized
  outcome; abnormal/market-adjusted is a causal-inference tool → raw primary, adjusted robustness.
- **A-share price limits → censoring flag**; direction stays usable (limit direction = true
  direction), magnitude is censored.

## Per-paper roles (cite counts retrieved 2026-06-04)

| Paper | cites | Role for our factors |
|---|---:|---|
| **Lopez-Lira & Tang 2023** (arXiv:2304.07619) `Lopez-Lira ChatGPT Stock Returns.pdf` | 327 (S2) | **Window mapping** (verbatim, US): pre-6:00 = same-day open→close; 6:00–close = same-day close→next close; after close = next open→next close. Also itself uses **raw** next-day return as primary, abnormal (CAPM/FF5) only in robustness Table 9. **NB: 6 a.m./close are US clock — we transfer the LOGIC and re-set cutoffs to A-share hours (open 9:30, close 15:00).** |
| **Astock / Zou et al. 2022** (FinNLP@EMNLP) `Astock A-Share Stock-Specific News Dataset.pdf` | 26 (S2) | **A-share 3-class quantile precedent** (Eq.1, verbatim): a/b/c/d = 20/40/60/20 → top20%=up, mid40-60%=neutral, bottom20%=down; **discards ~40% (20-40, 60-80) to take strongest signal**. We borrow the "3-class on returns" form but **reject** the discard + use a fixed band, not quantile. |
| **StockNet / Xu & Cohen 2018** (ACL) `StockNet Stock Movement Prediction from Tweets.pdf` | 384 (OpenAlex) | **Most-cited fixed-threshold precedent** (US): README "labeled as up and down when movement percent ≥0.55% or ≤−0.5%", middle discarded. The ~0.5% is the canonical "too-small-to-distinguish" noise-floor magnitude → **our primary band anchor, symmetrized to ±0.5%**. |
| **CMIN / Luo et al. 2023** (ACL) `CMIN Causality-Guided Stock Movement Prediction.pdf` | 17 (OpenAlex) | Covers **CSI300 (A-share, 2018-2021)** + US top110. **CORRECTION: CMIN is BINARY** (§3 verbatim: "binary classification ... ŷ=1 rise, ŷ=0 fall") — the earlier-claimed "CMIN ±1% 3-class" was a citation error. So CMIN is **not** a fixed-±1% precedent; it shows binary on A-shares. |
| **FNSPID 2024** (arXiv:2402.06698) `FNSPID Financial News Dataset Time Series.pdf` | 37 (OpenAlex) | Large-scale benchmark; **binary UP/DOWN, no neutral band** — a contradictory data point for "no threshold standard". |
| **Roll 1984** (JF 39(4):1127-1139) `Roll 1984 Implicit Bid-Ask Spread.pdf` | 2651 (S2) | **Mechanistic basis for the neutral band** (abstract, verbatim): "trading costs induce negative serial dependence in successive observed market price changes ... Spread = 2√(−cov)". Near-zero observed returns ≈ bid-ask bounce noise → justify neutralizing them. |
| **Qi 2023** (PLOS ONE, e0287548) `Qi 2023 Price Limits China ChiNext.pdf` | 2 (OpenAlex) | China ChiNext 10%→20% reform; confirms **delayed price discovery / volatility spillover / trading interference** near limits → why limit-hit magnitude is a censored lower bound. |

**Referenced-only (paywalled / book, in INDEX without PDF):** MacKinlay 1997 JEL (~4600, abnormal=actual−normal,
event-study estimand); Kothari & Warner 2007 (short vs long horizon); Barber & Odean 2008 RFS (~4000,
news-day/attention window precedent); FFJR 1969 IER (~7000, event-study origin); Chen et al. 2008
China Economic Review (SSE limit magnet effect); López de Prado 2018 (triple-barrier, vol-scaled);
surveys Loughran-McDonald 2016 (2187)/2020 (254), Kearney-Liu 2014, Xing-Cambria-Welsch 2018,
Kumar-Ravi 2016, Du-Xing-Mao-Cambria ACM CSUR 2024 — **financial-NLP background only, NOT authorities
for window / threshold / limits**.

## Locked operationalization (→ R1k/R1l/R1m DECISIONS)
- **Window**: Lopez-Lira mapping on A-share clock (open 9:30, close 15:00, lunch 11:30-13:00 → intraday
  bucket); 6 a.m. cutoff retained (user-approved, US open ≈ A-share open). Daily raw primary; 15-min
  (baostock) secondary **only if coverage audit passes** (else missingness bias). robustness [t,t+1].
- **Series / coherence**: ONE return series r drives both factors. F_mktdir = sign(r) + zero-centered
  band; F_mktmag = |r|. Adjust both together (raw → r−market / r−industry) for robustness; subtraction,
  no cross-sectional ranking (cross-sectional rank decouples direction from magnitude — rejected).
- **Direction band**: **fixed symmetric ±0.5% primary** (|r| < 0.5% = neutral), anchored directly to
  StockNet's ~0.5% noise-floor magnitude (most-cited, 384; their ±0.55/−0.5% asymmetry was US-drift
  class-balance — we symmetrize). Robustness band set = **{0% (no neutral = pure binary, cf.
  CMIN/FNSPID), ±1%, ±1.5%}**. **No authoritative anchor** — pre-registered design choice. Do NOT
  justify a wider band by "A-shares more volatile": return volatility ≠ microstructure noise floor (the
  band filters Roll bid-ask-bounce noise, not real-move size); whether A-shares need a wider band is
  answered empirically by the robustness set + a Roll effective-spread estimate on pilot data.
- **Magnitude**: continuous |r| (log as robustness if right-skewed). Limit-hit **included** in primary
  (case set consistent with direction), censored flag carried; **excluded** as robustness.
- **F_mktcap**: point-in-time market cap at event date (avoid ex-post), log; not return-based; check
  collinearity vs F_salience.
- **Honest boundary (for prereg)**: window / band / limit legitimacy = convention + institutional fact
  + Roll microstructure, NOT survey endorsement.

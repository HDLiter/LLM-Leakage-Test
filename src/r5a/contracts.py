"""Typed data contracts for the R5A pilot.

Contracts are frozen *structurally* in WS0; field semantics map directly to
the plan and operator schema. Implementation modules (operators, perturbations,
estimands) must import these models rather than re-declaring records inline.

Authority:
- plans/phase7-pilot-implementation.md  §§5.2, 5.3, 5.4, 5.4A, 5.5A, 6, 8.1A, 10
- config/prompts/R5A_OPERATOR_SCHEMA.md §§3.4, 4.4, 5.4
- refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md §§1, 7
"""

from __future__ import annotations

import math
from datetime import date, datetime
from enum import Enum
from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class AccessTier(str, Enum):
    WHITE_BOX = "white_box"
    BLACK_BOX = "black_box"


class OperatorId(str, Enum):
    P_PREDICT = "p_predict"
    P_LOGPROB = "p_logprob"
    P_EXTRACT = "p_extract"
    P_SCHEMA = "p_schema"


class PerturbationVariant(str, Enum):
    BASELINE = "baseline"
    C_CO = "c_co"
    C_NOOP = "c_noop"
    C_NOOP_PLACEBO = "c_noop_placebo"
    C_SR = "c_sr"
    C_ANON = "c_anon"
    C_TEMPORAL = "c_temporal"
    C_ADG = "c_adg"


class RequestStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    RETRYABLE = "retryable"
    TERMINAL_SKIPPED = "terminal_skipped"


class HostCategory(str, Enum):
    POLICY = "policy"
    CORPORATE = "corporate"
    INDUSTRY = "industry"
    MACRO = "macro"


class FOSlotTopology(str, Enum):
    SINGLE_POINT = "single-point"
    MULTI_POINT_LINKED = "multi-point-linked"
    NARRATIVE_ENTAILED = "narrative-entailed"


class SeedSupport(str, Enum):
    YES = "yes"
    NO = "no"
    BEST_EFFORT = "best-effort"


class Direction(str, Enum):
    UP = "up"
    DOWN = "down"
    NEUTRAL = "neutral"


# ---------------------------------------------------------------------------
# Article and pilot manifest
# ---------------------------------------------------------------------------


class ArticleRecord(BaseModel):
    """Authoritative pilot article unit. Fed to operators verbatim."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    text: str
    target: str
    target_type: Literal["company", "sector", "index", "macro", "other"]
    publish_date: date
    event_type: str
    host_category: HostCategory
    metadata: dict[str, Any] = Field(default_factory=dict)


class PilotCase(BaseModel):
    """One row of the frozen pilot manifest. Carries factor bins and
    perturbation eligibility flags decided at sampling time."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    source: str  # e.g. "cls_v3", "seed_test_cases_v3"
    publish_date: date
    target: str
    target_type: Literal["company", "sector", "index", "macro", "other"]
    event_type: str
    host_category: HostCategory
    pre_cutoff: bool
    factor_bins: dict[str, str]  # factor_id -> bin label, frozen at manifest freeze
    fo_eligible: bool
    fo_verified_outcome: bool
    fo_slotable: bool
    noop_eligible: bool
    article_hash: str  # sha256 of `text`
    notes: str | None = None


class PilotManifest(BaseModel):
    """Frozen pilot case manifest written to disk and hashed for prereg."""

    model_config = ConfigDict(extra="forbid")

    manifest_id: str
    created_at: datetime
    sampling_config_hash: str
    cases: list[PilotCase]
    manifest_hash: str  # sha256 over the canonical JSON of `cases`


# ---------------------------------------------------------------------------
# Perturbation artifacts
# ---------------------------------------------------------------------------


class SpanEdit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    span_start: int
    span_end: int
    kind: Literal["replace", "insert", "delete"]
    original_text: str
    replaced_text: str


class PerturbationArtifact(BaseModel):
    """Output of C_CO / C_NoOp generators. Audited rows feed P_predict on
    perturbed text. Reserved metadata keys are listed in plan §5.4A."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    perturbation_id: str
    variant: PerturbationVariant
    event_type: str
    eligible: bool
    source_text: str
    perturbed_text: str
    edit_spans: list[SpanEdit]
    rationale: str
    generator_version: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    # Reserved keys (validated by perturbation modules, see §5.4A):
    #   verified_outcome, fo_slotable, fo_slot_topology, slot_span,
    #   ineligible_reason, host_category, noop_bank_id,
    #   noop_eligibility_rule_id, placebo_variant


# ---------------------------------------------------------------------------
# Operator outputs
# ---------------------------------------------------------------------------


class EvidenceQuote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quote: str
    supports: Literal["direction"]


class RequestFingerprint(BaseModel):
    """Normalized fingerprint per plan §10.3."""

    model_config = ConfigDict(extra="forbid")

    provider: str
    model_id: str
    system_fingerprint: str | None = None
    response_id: str | None = None
    route_hint: str | None = None
    ts: datetime
    seed_requested: int | None = None
    seed_supported: SeedSupport
    seed_effective: bool | None = None  # filled in only after duplicate rerun


class PredictRecord(BaseModel):
    """P_predict output row. Per plan §5.3 + operator schema §3.4."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    model_id: str
    variant: PerturbationVariant
    prompt_version: str
    target_echo: str
    direction: Direction
    confidence: int = Field(ge=0, le=100)
    explicit_memory_reference: bool
    explicit_memory_reference_heuristic: bool
    evidence: list[EvidenceQuote] = Field(min_length=1, max_length=2)
    parse_status: Literal["ok", "repaired", "failed"]
    retry_count: int = Field(ge=0)
    fingerprint: RequestFingerprint
    cache_key: str
    cache_hit: bool
    raw_response_sha256: str


LOGPROB_TRACE_SCHEMA_VERSION = "v2.0"


class LogProbTrace(BaseModel):
    """P_logprob output row. Per plan §5.2, operator schema §4.4, and the
    2026-04-27 amendment in `docs/DECISION_20260427_pcsg_redefinition.md`.

    Schema versioning: bump `schema_version` whenever a new field is
    added so that downstream consumers can detect and refuse mismatched
    artifacts. v2.0 introduces per-position alternative-token logprobs,
    `quant_scheme`, `weight_dtype`, `vllm_image_digest`,
    `hidden_states_uri`, and the integrity validators. v1.0 (in-flight
    pre-2026-04-27) traces are NOT readable under v2.0 — none have been
    written yet, so this is forward-only.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["v2.0"] = "v2.0"

    case_id: str
    model_id: str
    tokenizer_family: str
    tokenizer_sha: str
    hf_commit_sha: str
    quant_scheme: str  # e.g. "AWQ-INT4", "fp16"; recorded for cross-precision sanity
    weight_dtype: str | None = None  # "float16" / "bfloat16" / "float32" / null for INT4
    vllm_image_digest: str | None = None  # Docker image SHA256 if backend was vLLM

    article_token_count: int = Field(ge=1)
    raw_token_ids: list[int]
    token_logprobs: list[float]

    # Per-position alternative-token logprobs from vLLM's top_logprobs.
    # Stored as a ragged list[list[float]] because Parquet handles it
    # natively. Outer length == article_token_count; inner length is
    # bounded by top_logprobs_k (typically 5) but may be 0 at the first
    # position (vLLM returns null there). Token-string identifiers of
    # the alternatives are NOT persisted: Min-K%++ scoring only needs
    # the logprob values, and the OpenAI-compatible top_logprobs field
    # exposes token strings, not token IDs.
    top_alternative_logprobs: list[list[float]] = Field(default_factory=list)
    top_logprobs_k: int = Field(ge=0, default=0)

    # Special-token / prefix bookkeeping: how many tokens at the head of
    # `raw_token_ids` are model-injected prefix (e.g. GLM's `[gMASK]<sop>`)
    # rather than article content. Downstream analysis MUST skip these for
    # E_CTS / E_PCSG so that comparisons stay article-content-only.
    prefix_token_count: int = Field(ge=0, default=0)

    # Optional pointer to a separately-stored hidden-state tensor file
    # (.safetensors). Populated only when WS6 hidden-state extraction
    # was requested at scoring time.
    hidden_states_uri: str | None = None

    thinking_mode: Literal["off"]
    backend: Literal["vllm_completion", "offline_hf"]
    fingerprint: RequestFingerprint

    @model_validator(mode="after")
    def _check_consistency(self) -> "LogProbTrace":
        n = len(self.raw_token_ids)
        if n != len(self.token_logprobs):
            raise ValueError(
                "raw_token_ids and token_logprobs must have equal length; "
                f"got {n} vs {len(self.token_logprobs)}"
            )
        if n != self.article_token_count:
            raise ValueError(
                f"article_token_count ({self.article_token_count}) != "
                f"len(raw_token_ids) ({n})"
            )
        if any(t < 0 for t in self.raw_token_ids):
            raise ValueError("raw_token_ids contains negative values")
        if any(not math.isfinite(lp) for lp in self.token_logprobs):
            raise ValueError("token_logprobs contains non-finite values")

        if self.top_alternative_logprobs:
            if len(self.top_alternative_logprobs) != n:
                raise ValueError(
                    "top_alternative_logprobs must align with raw_token_ids"
                )
            if self.top_logprobs_k > 0:
                for i, lps in enumerate(self.top_alternative_logprobs):
                    if lps and len(lps) > self.top_logprobs_k:
                        raise ValueError(
                            f"top_alternative_logprobs at position {i} has "
                            f"{len(lps)} entries; declared k={self.top_logprobs_k}"
                        )

        if self.prefix_token_count > self.article_token_count:
            raise ValueError(
                f"prefix_token_count ({self.prefix_token_count}) exceeds "
                f"article_token_count ({self.article_token_count})"
            )

        return self


# ---------------------------------------------------------------------------
# Audit records (plan §9)
# ---------------------------------------------------------------------------


class CueFailFlags(BaseModel):
    model_config = ConfigDict(extra="forbid")

    temporal_cue: bool = False
    numeric_density_mismatch: bool = False
    diction_register_shift: bool = False
    entity_salience_leak: bool = False
    discourse_marker_shift: bool = False
    style_boilerplate_drift: bool = False


class AuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    perturbation_id: str
    variant: PerturbationVariant
    reviewer_id: str
    role: Literal["quant", "nlp", "editor", "stats"]
    ts: datetime
    natural_cls_style: Literal["pass", "fail", "uncertain"]
    target_local_edit: Literal["pass", "fail", "uncertain"]
    economic_consistency: Literal["pass", "fail", "uncertain"]
    no_unintended_cues: Literal["pass", "fail", "uncertain"]
    cue_fail_flags: CueFailFlags
    overall_pass: bool
    comment: str | None = None


# ---------------------------------------------------------------------------
# Run-state lineage (plan §5.5A)
# ---------------------------------------------------------------------------


class RunStateRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str  # uuid4
    case_id: str
    model_id: str
    operator: OperatorId
    perturbation_variant: PerturbationVariant
    status: RequestStatus
    retry_count: int = Field(ge=0)
    fingerprint: RequestFingerprint | None = None
    response_id: str | None = None
    ts_start: datetime
    ts_end: datetime | None = None


RUNSTATE_TABLE_NAME: Final[str] = "request_runstate"
"""SQLite table name for the runstate DB.

Forward-declared contract: the Phase 7 orchestration writer (see
`plans/phase7-pilot-implementation.md` §5.5A) must create the
``data/pilot/runstate.db`` table by this name with columns matching
``RunStateRow`` fields plus the seed-triplet columns
(``seed_requested``, ``seed_supported``, ``seed_effective``).

Used by:
- ``scripts/ws1_finalize_run_manifest.py`` confirmatory hard-fail
  (read-only sqlite check for orphan ``pending`` / ``retryable`` rows).

Defining the name here lets the gate ship before the writer exists;
when the writer lands it must conform to this constant rather than
introduce a new table-naming branch.
"""


# ---------------------------------------------------------------------------
# Run manifest (plan §10.4)
# ---------------------------------------------------------------------------


class RunManifest(BaseModel):
    """Run-level provenance record (plan §10.4 + DECISION_20260427 §3.2 +
    DECISION_20260429_gate_removal §2.6 + DECISION_20260429_llama_addition §3.2).

    Six fields beyond the base provenance set were added 2026-04-29:

    - `cutoff_observed`: per-model empirical cutoff dates produced by Path E
      knee detection. None for models where the knee detector rejected the
      fit (CI width > 3 months OR drop CI lower bound <= 0.05).
    - `cutoff_date_yaml`: per-model `cutoff_date` values copied from the
      fleet YAML at run time. Pairing with `cutoff_observed` lets downstream
      analyses estimate exposure-misclassification when the two disagree.
    - `quant_scheme`: per-model `quant_scheme` snapshot. Required for the
      AWQ-vs-fp16 calibration audit (Stage 2.8) and for §8.2 random-effects
      interpretation under cross-precision pooling.
    - `pcsg_pair_registry_hash`: SHA256 of the canonicalized `pcsg_pairs`
      block from the fleet YAML. Pinning the registry separately from the
      whole-fleet hash means PCSG analysis can detect pair-set drift even
      if a non-pair-related fleet edit changed `fleet_config_hash`.
    - `hidden_state_subset_hash`: SHA256 over the sorted list of `case_id`s
      used for WS1 Stage 2.7 hidden-state extraction. Lets WS6 detect that
      the analysis layer is reading the same 30-case subset that was
      written to disk.
    - `quality_gate_thresholds`: realized strict-majority denominator
      values per gate name (`e_extract_main_text`, `e_extract_confirmatory`,
      etc.). Per `docs/DECISION_20260429_gate_removal.md` §2.6 the K is
      derived from N at run time, so the manifest must record what K
      ended up being.

    2026-04-30 R2 amendments (cross-ref
    `refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/DECISIONS.md`):

    - decision #1 — `mode: Literal["confirmatory", "dev"]` field added.
      Confirmatory finalize enforces an 11-clause hard-fail framework
      in `scripts/ws1_finalize_run_manifest.py` (originally 8 clauses;
      Tier-R2-0 PR1 step 7 added hidden-states-dir + runstate-db
      clauses and renumbered end-to-end). Dev mode (set via the
      finalizer's `--allow-tbd` flag) skips the framework.
    - decision #2 — split-tier roster fields `fleet_p_predict_eligible`
      and `fleet_p_logprob_eligible` record the realized eligibility sets
      so downstream analysis can detect drift from the YAML view.
    - decision #5 — `cutoff_observed` renamed to
      `exposure_horizon_observed`. The field carries Path-E empirical
      exposure-horizon dates (knee-detector output); `cutoff_date_yaml`
      keeps its name as it mirrors the operator-declared YAML value.
    - decision #11 — `pcsg_pair_registry_hash` is now required (no
      default); WS6 quality_gate_thresholds keys are dropped at the
      finalizer (`scripts/ws1_finalize_run_manifest.py`), not the schema.
    """

    model_config = ConfigDict(extra="forbid")

    run_id: str
    created_at: datetime
    git_commit_sha: str
    fleet_config_hash: str
    runtime_config_hash: str
    sampling_config_hash: str
    prompt_versions: dict[str, str]  # operator_id -> prompt version tag
    model_fingerprints: dict[str, dict[str, str]]  # model_id -> fingerprint fields
    white_box_checkpoint_shas: dict[str, str]  # model_id -> hf_commit_sha
    runtime_caps: dict[str, int]  # provider -> max_concurrency
    seed_policy: dict[str, Any]
    runstate_db_path: str
    runstate_db_hash: str | None = None  # filled at run close
    article_manifest_hash: str
    perturbation_manifest_hash: str | None = None
    audit_manifest_hash: str | None = None

    # Operational provenance (plan §10.1) — populated by ws1_pin_fleet
    # and ws1_finalize_run_manifest. tokenizer_shas mirrors fleet YAML
    # at run time for white-box models; vllm_image_digest is pinned per
    # cloud session.
    #
    # tokenizer_sha is defined per DECISIONS.md decision #4 as the
    # SHA-256 of `tokenizer.json` byte content as resolved at load
    # time. This matches HF's blob-store filename for LFS-tracked
    # tokenizers but NOT for git-tracked ones (HF uses git-blob SHA1
    # for non-LFS); the divergence is intentional, and `tokenizer_sha`
    # MUST NOT be used as a cache lookup key.
    tokenizer_shas: dict[str, str] = Field(default_factory=dict)
    vllm_image_digest: str | None = None
    gpu_dtype: str | None = None  # e.g. "bf16", "fp16"; reflects backend launch flag
    launch_env: dict[str, str] = Field(default_factory=dict)  # CUDA_VISIBLE_DEVICES, vLLM args, etc.

    # 2026-04-29 Tier-0 additions (DECISION_20260427 §3.2 +
    # DECISION_20260429_gate_removal §2.6); 2026-04-30 R2 amendments
    # (DECISIONS.md decisions #1, #2, #5, #11) renamed `cutoff_observed`
    # to `exposure_horizon_observed`, tightened `pcsg_pair_registry_hash`
    # to required, and added `mode` + the two split-tier roster fields.
    exposure_horizon_observed: dict[str, date | None] = Field(default_factory=dict)
    cutoff_date_yaml: dict[str, date] = Field(default_factory=dict)
    quant_scheme: dict[str, str] = Field(default_factory=dict)
    pcsg_pair_registry_hash: str
    hidden_state_subset_hash: str | None = None
    quality_gate_thresholds: dict[str, int] = Field(default_factory=dict)
    mode: Literal["confirmatory", "dev"] = "confirmatory"
    fleet_p_predict_eligible: list[str] = Field(default_factory=list)
    fleet_p_logprob_eligible: list[str] = Field(default_factory=list)

    # Tier-R2-0 PR1 (refine-logs/reviews/R5A_TIER_R2_0_IMPL_REVIEW_20260502
    # IMPLEMENTATION_NOTE.md §PR1 step 3): SHA-256 of analyzer JSON consumed
    # via `--exposure-horizon` and SHA-256 per `*__pilot.parquet` byte
    # content. Together they bind Path-E provenance end-to-end:
    # finalizer → analyzer JSON → per-model trace parquet. `| None` /
    # empty default supports dev / `--allow-tbd` mode where Path-E is
    # absent; confirmatory hard-fail rejects None / empty for the
    # P_logprob roster.
    exposure_horizon_source_sha256: str | None = None
    pilot_trace_shas: dict[str, str] = Field(default_factory=dict)


__all__ = [
    "AccessTier",
    "ArticleRecord",
    "AuditRecord",
    "CueFailFlags",
    "Direction",
    "EvidenceQuote",
    "FOSlotTopology",
    "HostCategory",
    "LogProbTrace",
    "OperatorId",
    "PerturbationArtifact",
    "PerturbationVariant",
    "PilotCase",
    "PilotManifest",
    "PredictRecord",
    "RequestFingerprint",
    "RUNSTATE_TABLE_NAME",
    "RequestStatus",
    "RunManifest",
    "RunStateRow",
    "SeedSupport",
    "SpanEdit",
]

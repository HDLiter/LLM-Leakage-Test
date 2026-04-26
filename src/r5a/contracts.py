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

from datetime import date, datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


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
    C_FO = "c_fo"
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
    """Output of C_FO / C_NoOp generators. Audited rows feed P_predict on
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


class LogProbTrace(BaseModel):
    """P_logprob output row. Per plan §5.2 + operator schema §4.4."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    model_id: str
    tokenizer_family: str
    tokenizer_sha: str
    hf_commit_sha: str
    article_token_count: int
    raw_token_ids: list[int]
    token_logprobs: list[float]
    thinking_mode: Literal["off"]
    backend: Literal["vllm_completion", "offline_hf"]
    fingerprint: RequestFingerprint


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


# ---------------------------------------------------------------------------
# Run manifest (plan §10.4)
# ---------------------------------------------------------------------------


class RunManifest(BaseModel):
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
    "RequestStatus",
    "RunManifest",
    "RunStateRow",
    "SeedSupport",
    "SpanEdit",
]

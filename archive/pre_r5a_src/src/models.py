"""Pydantic data models for the leakage test bench."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Direction(str, Enum):
    UP = "up"
    DOWN = "down"
    NEUTRAL = "neutral"


class NewsCategory(str, Enum):
    POLICY = "policy"          # 政策类
    CORPORATE = "corporate"    # 企业类
    INDUSTRY = "industry"      # 行业类
    MACRO = "macro"            # 宏观类


class VariantType(str, Enum):
    REVERSE_OUTCOME = "reverse_outcome"  # deprecated; use SEMANTIC_REVERSAL
    ALTER_NUMBERS = "alter_numbers"  # deprecated; retained for backward compatibility
    SEMANTIC_REVERSAL = "semantic_reversal"
    PROVENANCE_SWAP = "provenance_swap"
    NOVELTY_TOGGLE = "novelty_toggle"
    NEUTRAL_PARAPHRASE = "neutral_paraphrase"
    SHAM_EDITS = "sham_edits"
    FALSE_OUTCOME_CPT = "false_outcome_cpt"

    @classmethod
    def active_counterfactuals(cls) -> tuple["VariantType", ...]:
        """Counterfactual variants backed by frozen YAML templates."""
        return (
            cls.SEMANTIC_REVERSAL,
            cls.PROVENANCE_SWAP,
            cls.NOVELTY_TOGGLE,
            cls.NEUTRAL_PARAPHRASE,
            cls.SHAM_EDITS,
        )

    @classmethod
    def deprecated_counterfactuals(cls) -> tuple["VariantType", ...]:
        """Legacy counterfactual variants kept only for compatibility."""
        return (cls.REVERSE_OUTCOME, cls.ALTER_NUMBERS)

    @property
    def is_deprecated(self) -> bool:
        """Whether this enum value is a legacy counterfactual type."""
        return self in self.deprecated_counterfactuals()


class MaskDimension(str, Enum):
    YEAR = "year"
    ENTITY = "entity"
    NUMBERS = "numbers"
    SECTOR = "sector"


class OutputFormat(str, Enum):
    BINARY = "binary"
    SCALAR = "scalar"
    FIVE_BIN = "5-bin"
    FREE_TEXT = "free-text"


class ProbeType(str, Enum):
    PRICE_QUERY = "price_query"
    TREND_PREDICTION = "trend_prediction"
    EVENT_IMPACT = "event_impact"
    MARKET_PERFORMANCE = "market_performance"


# --- Core data models ---

class NewsSample(BaseModel):
    id: str
    title: str
    content: str
    publish_time: datetime
    category: NewsCategory
    source: str = "cls_telegraph"


class TestCase(BaseModel):
    id: str
    news: NewsSample
    known_outcome: str = Field(description="已知的后续市场结果")
    outcome_date: str = Field(description="结果发生日期")
    sector: str = Field(description="相关板块")
    key_entities: list[str] = Field(default_factory=list)
    key_numbers: list[str] = Field(default_factory=list)
    expected_direction: Direction
    subcategory: str = Field(default="", description="细分类别")
    memorization_likelihood: str = Field(default="medium", description="high|medium|low")
    target: str = Field(default="", description="Primary entity/ticker/index being predicted about")
    target_type: str = Field(default="", description="company|sector|index")


class MaskingConfig(BaseModel):
    """Which masking / prompt strategies are active."""
    mask_year: bool = False
    mask_entity: bool = False
    mask_numbers: bool = False
    mask_sector: bool = False
    role_play: bool = False
    cot_forced: bool = False
    extraction_constraint: bool = False
    mask_mode: str = Field(default="rule", description="rule | llm")

    @property
    def label(self) -> str:
        parts = []
        if self.mask_year: parts.append("Y")
        if self.mask_entity: parts.append("E")
        if self.mask_numbers: parts.append("N")
        if self.mask_sector: parts.append("S")
        if self.mask_mode == "llm": parts.append("LLM")
        if self.role_play: parts.append("R")
        if self.cot_forced: parts.append("C")
        if self.extraction_constraint: parts.append("X")
        return "+".join(parts) or "baseline"


class CounterfactualVariant(BaseModel):
    original_case_id: str
    variant_type: VariantType
    modified_title: str
    modified_content: str
    modification_description: str = ""


class FiveBinDistribution(BaseModel):
    strong_bear: int = Field(ge=0, le=100)
    weak_bear: int = Field(ge=0, le=100)
    neutral: int = Field(ge=0, le=100)
    weak_bull: int = Field(ge=0, le=100)
    strong_bull: int = Field(ge=0, le=100)

    @property
    def direction(self) -> Direction:
        bull = self.weak_bull + self.strong_bull
        bear = self.weak_bear + self.strong_bear
        if bull > bear + 10:
            return Direction.UP
        elif bear > bull + 10:
            return Direction.DOWN
        return Direction.NEUTRAL

    def as_prob_array(self) -> list[float]:
        total = self.strong_bear + self.weak_bear + self.neutral + self.weak_bull + self.strong_bull
        if total == 0:
            return [0.2] * 5
        return [v / total for v in [self.strong_bear, self.weak_bear, self.neutral, self.weak_bull, self.strong_bull]]


class LLMResponse(BaseModel):
    model: str
    prompt_hash: str = ""
    raw_response: str
    parsed_direction: Optional[Direction] = None
    parsed_confidence: Optional[float] = None
    parsed_distribution: Optional[FiveBinDistribution] = None
    reasoning: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    logprobs: Optional[list[dict]] = None


class ProbeResult(BaseModel):
    probe_type: str
    test_case_id: str
    masking_config: MaskingConfig
    output_format: OutputFormat
    original_response: LLMResponse
    cf_responses: dict[str, LLMResponse] = Field(default_factory=dict, description="variant_type -> response")
    pc: Optional[float] = None
    ci: Optional[float] = None
    ids: Optional[float] = None


class MemorizationProbe(BaseModel):
    id: str
    probe_type: ProbeType
    question: str
    ground_truth: str
    tolerance: str = Field(default="", description="e.g. ±1% for price queries")


# --- Strategy presets ---

STRATEGY_PRESETS: dict[str, MaskingConfig] = {
    "baseline": MaskingConfig(),
    "thales_v1": MaskingConfig(mask_year=True, role_play=True, cot_forced=True),
    "full_mask": MaskingConfig(mask_year=True, mask_entity=True, role_play=True, cot_forced=True, extraction_constraint=True),
    "year_only": MaskingConfig(mask_year=True),
    "entity_only": MaskingConfig(mask_entity=True),
    "role_only": MaskingConfig(role_play=True),
    "cot_only": MaskingConfig(cot_forced=True),
    "constraint_only": MaskingConfig(extraction_constraint=True),
    "llm_mask": MaskingConfig(mask_year=True, mask_entity=True, mask_mode="llm"),
    "llm_full": MaskingConfig(
        mask_year=True, mask_entity=True, mask_numbers=True, mask_sector=True,
        mask_mode="llm", role_play=True, cot_forced=True,
    ),
}

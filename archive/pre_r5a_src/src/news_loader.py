"""News loader: load from embedded samples or CLS telegraph JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .models import NewsSample, TestCase, CounterfactualVariant, MemorizationProbe

_PROJECT_ROOT = Path(__file__).parent.parent
_SAMPLES_DIR = _PROJECT_ROOT / "data" / "samples"
_TEST_CASES_PATH = _PROJECT_ROOT / "data" / "seed" / "test_cases.json"
_MEMORIZATION_PROBES_PATH = _PROJECT_ROOT / "data" / "seed" / "memorization_probes.json"
_COUNTERFACTUAL_VARIANTS_PATH = _PROJECT_ROOT / "data" / "generated" / "counterfactual_variants.json"


def load_test_cases(path: Optional[Path] = None) -> list[TestCase]:
    """Load test cases from JSON file."""
    p = path or _TEST_CASES_PATH
    if not p.exists():
        raise FileNotFoundError(f"Test cases not found: {p}")
    raw = json.loads(p.read_text(encoding="utf-8"))
    return [TestCase(**tc) for tc in raw["test_cases"]]


def load_memorization_probes(path: Optional[Path] = None) -> list[MemorizationProbe]:
    """Load memorization probe questions."""
    p = path or _MEMORIZATION_PROBES_PATH
    if not p.exists():
        raise FileNotFoundError(f"Probes not found: {p}")
    raw = json.loads(p.read_text(encoding="utf-8"))
    return [MemorizationProbe(**item) for item in raw["probes"]]


def load_counterfactual_variants(path: Optional[Path] = None) -> list[CounterfactualVariant]:
    """Load pre-generated counterfactual variants."""
    p = path or _COUNTERFACTUAL_VARIANTS_PATH
    if not p.exists():
        return []
    raw = json.loads(p.read_text(encoding="utf-8"))
    return [CounterfactualVariant(**v) for v in raw["variants"]]


def load_cls_telegraphs(cls_dir: str | Path) -> list[NewsSample]:
    """Load raw CLS telegraph JSON files (development mode).

    Expected format per file: list of dicts with keys:
    id, title, content, ctime (unix timestamp), ...
    """
    from datetime import datetime

    cls_path = Path(cls_dir)
    if not cls_path.exists():
        raise FileNotFoundError(f"CLS directory not found: {cls_path}")

    samples = []
    for f in sorted(cls_path.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("data", [])
        for item in items:
            try:
                samples.append(NewsSample(
                    id=str(item.get("id", "")),
                    title=item.get("title", ""),
                    content=item.get("content", item.get("title", "")),
                    publish_time=datetime.fromtimestamp(item["ctime"]) if "ctime" in item else datetime.fromisoformat(item.get("publish_time", "2024-01-01")),
                    category="macro",
                    source="cls_telegraph",
                ))
            except (KeyError, ValueError):
                continue
    return samples


def save_test_cases(cases: list[TestCase], path: Optional[Path] = None) -> None:
    """Save test cases to JSON."""
    p = path or _TEST_CASES_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {"test_cases": [tc.model_dump(mode="json") for tc in cases]}
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def save_counterfactual_variants(variants: list[CounterfactualVariant], path: Optional[Path] = None) -> None:
    """Save counterfactual variants to JSON."""
    p = path or _COUNTERFACTUAL_VARIANTS_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {"variants": [v.model_dump(mode="json") for v in variants]}
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

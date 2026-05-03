from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from src.r5a.contracts import ArticleRecord


SMOKE_FIXTURE = Path("data/pilot/fixtures/smoke_30.json")


def test_ws1_smoke_fixture_is_committed_and_contract_valid() -> None:
    assert SMOKE_FIXTURE.exists()
    rows = json.loads(SMOKE_FIXTURE.read_text(encoding="utf-8"))

    records = [ArticleRecord.model_validate(row) for row in rows]

    assert len(records) == 30
    assert Counter((r.metadata or {}).get("period") for r in records) == {
        "pre_cutoff": 24,
        "post_cutoff": 6,
    }
    assert Counter(r.host_category.value for r in records) == {
        "corporate": 10,
        "industry": 7,
        "macro": 6,
        "policy": 7,
    }
    assert [r.case_id for r in records[:5]] == [
        "v3_h_028",
        "v3_h_120",
        "tc_008",
        "tc_004",
        "v3_h_074",
    ]
    assert (
        hashlib.sha256(SMOKE_FIXTURE.read_bytes()).hexdigest()
        == "1862e4e7a6286a6b49a635f246366120d4f5a51b3143725cdb4eedc0fbdf1576"
    )

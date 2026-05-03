"""Unit tests for src.r5a.io_utils.

Per Tier-R2-0 PR1 step 1 / step 17: the atomic-write helper is now
shared between the pinner and the finalizer; a regression here would
silently allow half-written fleet YAML or RunManifest JSON on disk
after a crash, breaking the WS1 provenance contract.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.r5a.io_utils import atomic_write_json, atomic_write_text


def test_atomic_write_text_creates_target_with_content(tmp_path: Path):
    target = tmp_path / "out.txt"
    atomic_write_text(target, "hello\n")
    assert target.read_text(encoding="utf-8") == "hello\n"
    # No `.tmp` siblings should be left over after success.
    assert not list(tmp_path.glob("out.txt.*.tmp"))


def test_atomic_write_text_creates_parent_dirs(tmp_path: Path):
    target = tmp_path / "nested" / "deeper" / "out.txt"
    atomic_write_text(target, "x")
    assert target.read_text(encoding="utf-8") == "x"


def test_atomic_write_text_overwrites_existing(tmp_path: Path):
    target = tmp_path / "out.txt"
    target.write_text("old", encoding="utf-8")
    atomic_write_text(target, "new")
    assert target.read_text(encoding="utf-8") == "new"


def test_atomic_write_text_cleanup_on_mid_write_failure(
    tmp_path: Path, monkeypatch
):
    """Verifies the except / finally cleanup path under an in-process
    exception: when `os.replace` raises after the temp file has been
    written and synced, the target stays at its pre-write content and
    the `.tmp` sibling is removed.

    Scope (C2 / Tier-R2-0 PR2 step 12): SIGKILL recovery is a
    PROCESS-level concern (no `finally` runs after a kill -9) and is
    out of scope for this unit test. Validating it would require a
    subprocess + restart harness; the helper relies on `os.replace`
    being atomic on POSIX/NTFS so a partial swap cannot land on disk
    even without `finally` cleanup.
    """
    import os

    target = tmp_path / "out.txt"
    target.write_text("pre-existing", encoding="utf-8")

    def boom(*_a, **_k):
        raise RuntimeError("simulated kill mid-write")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(RuntimeError, match="simulated kill mid-write"):
        atomic_write_text(target, "new content")
    # Target untouched.
    assert target.read_text(encoding="utf-8") == "pre-existing"
    # Temp file cleaned up.
    leftovers = list(tmp_path.glob("out.txt.*.tmp"))
    assert not leftovers, f"unexpected leftover temp file(s): {leftovers}"


def test_atomic_write_json_round_trip(tmp_path: Path):
    target = tmp_path / "out.json"
    payload = {"k": [1, 2, 3], "s": "z"}
    atomic_write_json(target, payload)
    import json

    assert json.loads(target.read_text(encoding="utf-8")) == payload

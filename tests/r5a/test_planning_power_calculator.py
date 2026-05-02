"""Unit tests for scripts/planning_power_calculator.py.

Per R2 Tier-0 Block F.36. Anchors closed-form SE numerics + verifies
Block E cleanup (no MC SE keys, E_OR label rename, removed --b-outer
side effects).
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

planner = importlib.import_module("scripts.planning_power_calculator")


def test_pcsg_se_anchor():
    se = planner._se_pcsg_pair(2048, 2, 0.98, 4.5)
    assert se == pytest.approx(0.0710, abs=5e-4)


def test_cmmd_se_case_level_after_fix():
    args = argparse.Namespace(
        n_case_pilot=80,
        n_case_bl2_post=350,
        n_case_main_total=2560,
        cmmd_inflation=[1.0],
        effects=[0.20],
        scenarios=["unweighted_pilot"],
        family_states=["S20"],
        pcsg_eligibility=[0.98],
        n_case_main_pre=2048,
    )
    rows = planner._simulate_estimand_powers(args)
    cmmd_rows = [r for r in rows if r["estimand"] == "E_CMMD_beta_cutoff"]
    assert cmmd_rows, "no E_CMMD rows produced"
    se_pilot_expected = 1.0 / (430 ** 0.5)
    se_main_expected = 1.0 / (2560 ** 0.5)
    assert cmmd_rows[0]["se_pilot"] == pytest.approx(se_pilot_expected, abs=1e-4)
    assert cmmd_rows[0]["se_main"] == pytest.approx(se_main_expected, abs=1e-4)
    # Ratio: SE_pilot / SE_main = sqrt(n_main / n_pilot)
    assert cmmd_rows[0]["se_pilot"] / cmmd_rows[0]["se_main"] == pytest.approx(
        (2560 / 430) ** 0.5, abs=0.01
    )
    # Per E.30 sub-step 1: n_models / n_families dropped from E_CMMD rows.
    assert "n_models" not in cmmd_rows[0]
    assert "n_families" not in cmmd_rows[0]


def test_wy_power_anchor_points():
    assert planner._wy_power(0.0, 1.0, z_wy=2.8) == pytest.approx(0.005110, abs=1e-6)
    assert planner._wy_power(0.2, 0.071, z_wy=2.8) == pytest.approx(0.5067, abs=1e-3)
    assert planner._wy_power(0.3, 0.071, z_wy=2.8) == pytest.approx(0.9230, abs=1e-3)


def test_no_mc_se_in_output_rows(tmp_path: Path, monkeypatch):
    output = tmp_path / "planning.json"
    monkeypatch.setattr(
        sys, "argv",
        ["planning_power_calculator.py", "--output", str(output)],
    )
    planner.main()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["rows"], "rows missing"
    for row in data["rows"]:
        assert "power_pilot_mc_se" not in row
        assert "power_main_mc_se" not in row
        assert "power_pilot_ci95_low" not in row
        assert "power_main_ci95_high" not in row
    # E.32 sub-step 2: b_outer removed from output config.
    assert "b_outer" not in data["config"]


def test_estimand_label_renamed_to_e_or():
    args = argparse.Namespace(
        n_case_pilot=80,
        n_case_bl2_post=350,
        n_case_main_total=2560,
        cmmd_inflation=[1.0],
        effects=[0.20],
        scenarios=["unweighted_pilot"],
        family_states=["S20"],
        pcsg_eligibility=[0.98],
        n_case_main_pre=2048,
    )
    rows = planner._simulate_estimand_powers(args)
    labels = {r["estimand"] for r in rows}
    assert "E_OR_E_NoOp_beta_cutoff" in labels
    assert "E_FO_E_NoOp_beta_cutoff" not in labels

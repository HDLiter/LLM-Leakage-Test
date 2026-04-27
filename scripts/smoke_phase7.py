"""Phase 7 smoke harness.

WS0 deliverable per plan §5.1 step 6. Runs in two modes:

  --check-config   Validate fleet and runtime YAMLs. Always supported.
  --operator p_predict --variant baseline --smoke-cases 20
                   9-model P_predict feasibility gate (plan §5.1 step 7,
                   WS0 exit criterion: >= 95% strict-JSON parse success).
                   Requires WS2 adapters; stubbed at WS0 freeze.

Per CLAUDE.md project notes, the runtime defaults the script enforces
are: DeepSeek concurrency = 20, vLLM concurrency = 16, trust_env=false,
proxy=none on both. Setting NO_PROXY for localhost / DeepSeek must be
done in the calling shell before invoking this script (plan §14.3).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.r5a.fleet import load_fleet  # noqa: E402
from src.r5a.runtime import load_runtime  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 7 WS0 smoke harness")
    parser.add_argument(
        "--fleet",
        default="config/fleet/r5a_fleet.yaml",
        help="path to fleet YAML",
    )
    parser.add_argument(
        "--runtime",
        default="config/runtime/r5a_runtime.yaml",
        help="path to runtime YAML",
    )
    parser.add_argument(
        "--operator",
        choices=["p_predict", "p_logprob"],
        help="operator to probe (WS2/WS1 implementation)",
    )
    parser.add_argument(
        "--variant",
        default="baseline",
        help="perturbation variant (baseline only at WS0 freeze)",
    )
    parser.add_argument(
        "--smoke-cases",
        type=int,
        default=20,
        help="number of cases for the feasibility gate",
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="exit after validating fleet and runtime configs",
    )
    return parser.parse_args()


def report_fleet(fleet) -> None:
    white_box = fleet.white_box_ids()
    black_box = fleet.black_box_ids()
    print(f"fleet_version: {fleet.fleet_version}")
    print(f"yaml_sha256:   {fleet.raw_yaml_sha256[:12]}...")
    print(f"white_box ({len(white_box)}): {', '.join(white_box)}")
    print(f"black_box ({len(black_box)}): {', '.join(black_box)}")
    # Post-2026-04-27 expansion: 10 white-box (5 Qwen2.5 + 4 Qwen3 + 1 GLM)
    # and 4 black-box. See docs/DECISION_20260427_pcsg_redefinition.md.
    if len(white_box) != 10 or len(black_box) != 4:
        print(
            "WARNING: fleet does not match the post-expansion 10+4 split "
            "(docs/DECISION_20260427_pcsg_redefinition.md)",
            file=sys.stderr,
        )


def report_runtime(rt) -> None:
    print(f"runtime.seed:           {rt.runtime.seed}")
    print(f"runtime.retry_max:      {rt.runtime.retry_max}")
    print(f"runtime.timeout_s:      {rt.runtime.timeout_seconds}")
    print(f"runtime.cache_enabled:  {rt.runtime.cache_enabled}")
    print(f"runtime.runstate_db:    {rt.runtime.runstate_db}")
    for name, prov in rt.providers.items():
        print(
            f"providers.{name}: max_concurrency={prov.max_concurrency} "
            f"trust_env={prov.trust_env} proxy={prov.proxy}"
        )


def main() -> int:
    args = parse_args()

    fleet = load_fleet(args.fleet)
    runtime = load_runtime(args.runtime)

    print("== fleet ==")
    report_fleet(fleet)
    print()
    print("== runtime ==")
    report_runtime(runtime)

    if args.check_config:
        return 0

    if args.operator is None:
        # No operator requested; configs validated, that's all WS0 promises.
        return 0

    # Operator probes are intentionally not wired up at WS0 freeze.
    # WS1 implements P_logprob backends and an offline smoke;
    # WS2 implements P_predict backends + the 9-model 20-case gate.
    print(
        f"\n[stub] --operator {args.operator} requires backend adapters "
        "that land in WS1/WS2; rerun this script after the matching "
        "workstream is implemented.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

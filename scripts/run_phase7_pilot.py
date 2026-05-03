"""Phase 7 pilot orchestration entry point placeholder.

The full request loop is WS4 work. This stub wires the runstate writer at
the location the eventual orchestrator will use, so cloud preflight can
initialize `data/pilot/runstate.db` without duplicating schema code.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.r5a.orchestration.runstate import RunStateWriter  # noqa: E402
from src.r5a.runtime import load_runtime  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 7 pilot orchestrator")
    parser.add_argument(
        "--runtime",
        default="config/runtime/r5a_runtime.yaml",
        help="runtime YAML path; supplies default runstate DB path",
    )
    parser.add_argument(
        "--runstate-db",
        default=None,
        help="SQLite runstate path; default = runtime.runstate_db",
    )
    parser.add_argument(
        "--init-runstate-only",
        action="store_true",
        help="initialize the runstate DB and exit",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runtime = load_runtime(args.runtime)
    db_path = args.runstate_db or runtime.runtime.runstate_db
    writer = RunStateWriter(db_path)

    if args.init_runstate_only:
        writer.init_db()
        print(f"initialized runstate DB: {db_path}")
        return 0

    # TODO(WS4): build the full Phase 7 request loop here. Each planned
    # request must first write `pending`, then move to `success`,
    # `retryable`, or `terminal_skipped` through RunStateWriter.
    raise SystemExit(
        "full Phase 7 orchestration is not implemented yet; use "
        "--init-runstate-only for the runstate preflight."
    )


if __name__ == "__main__":
    raise SystemExit(main())

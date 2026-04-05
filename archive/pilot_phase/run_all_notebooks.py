"""Run all notebooks in sequential order, saving outputs in-place.

Usage:
    python run_all_notebooks.py              # normal run
    python run_all_notebooks.py --clear-cache  # delete data/cache,generated,results before running
    python run_all_notebooks.py --clear-output # only clear notebook outputs, don't execute
"""

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

NOTEBOOKS = [
    "notebooks/00_data_prep.ipynb",
    "notebooks/01_memorization_audit.ipynb",
    "notebooks/02_counterfactual.ipynb",
    "notebooks/03_ablation.ipynb",
    "notebooks/04_output_format.ipynb",
    "notebooks/05_mitigation_compare.ipynb",
    "notebooks/06_prompt_optimization.ipynb",
]

REGENERABLE_DIRS = [
    PROJECT_ROOT / "data" / "cache",
    PROJECT_ROOT / "data" / "generated",
    PROJECT_ROOT / "data" / "results",
]


def clear_cache() -> None:
    deleted = 0
    for d in REGENERABLE_DIRS:
        if d.exists():
            count = sum(1 for _ in d.iterdir())
            shutil.rmtree(d)
            print(f"Deleted: {d} ({count} files)")
            deleted += count
    if not deleted:
        print("No regenerable data directories found")


def clear_outputs() -> None:
    """Clear outputs from all notebooks without executing."""
    for nb in NOTEBOOKS:
        path = PROJECT_ROOT / nb
        if not path.exists():
            continue
        subprocess.run(
            [sys.executable, "-m", "jupyter", "nbconvert",
             "--clear-output", "--inplace", str(path)],
            capture_output=True, text=True,
        )
    print(f"Cleared outputs from {len(NOTEBOOKS)} notebooks")


def run_notebook(path: str) -> bool:
    print(f"\n{'='*60}")
    print(f"Running: {path}")
    print(f"{'='*60}")
    start = time.time()
    result = subprocess.run(
        [
            sys.executable, "-m", "jupyter", "nbconvert",
            "--to", "notebook",
            "--execute",
            "--inplace",
            "--ExecutePreprocessor.timeout=-1",
            "--ExecutePreprocessor.kernel_name=python3",
            "--KernelManager.shutdown_wait_time=5",
            path,
        ],
        capture_output=True,
        text=True,
    )
    elapsed = time.time() - start
    if result.returncode == 0:
        print(f"  OK  ({elapsed:.0f}s)")
        return True
    else:
        print(f"  FAIL ({elapsed:.0f}s)")
        print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all experiment notebooks")
    parser.add_argument("--clear-cache", action="store_true",
                        help="Delete data/cache, data/generated, and data/results before running")
    parser.add_argument("--clear-output", action="store_true",
                        help="Only clear notebook outputs, don't execute")
    args = parser.parse_args()

    if args.clear_output:
        clear_outputs()
        return

    if args.clear_cache:
        clear_cache()

    os_start = time.time()
    passed, failed = [], []

    for nb in NOTEBOOKS:
        nb_path = PROJECT_ROOT / nb
        if not nb_path.exists():
            print(f"  SKIP (not found): {nb}")
            failed.append(nb)
            break
        ok = run_notebook(str(nb_path))
        (passed if ok else failed).append(nb)
        if not ok:
            print(f"\nStopping: {nb} failed.")
            break

    total = time.time() - os_start
    print(f"\n{'='*60}")
    print(f"Done in {total:.0f}s  |  passed: {len(passed)}  failed: {len(failed)}")
    if failed:
        print(f"Failed: {failed}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

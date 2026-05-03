"""WS1 RunManifest finalizer.

Per Tier-0 #4 (`refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/SYNTHESIS.md`)
+ Operational §6: a confirmatory cloud run is non-reproducible without
a single artifact joining together pinned fleet + main traces + Path E
output + pcsg_pairs hash + Docker digest + sub-artifact hashes. This
script writes that artifact (`RunManifest`).

2026-04-30 R2 amendments
(`refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/DECISIONS.md`):

  - decision #1 — confirmatory mode runs an 8-clause hard-fail check
    (`_confirmatory_hard_fail`) before constructing the manifest. Each
    failed clause is reported in a single multi-line `SystemExit`
    message prefixed with `[clause N]` so operators see the full
    failure set, not just the first one. `--allow-tbd` switches mode
    to `dev` and skips the framework.
  - decision #2 — manifest records the realized split-tier rosters via
    `fleet_p_predict_eligible` and `fleet_p_logprob_eligible`.
  - decision #5 — `--cutoff-observed` renamed to `--exposure-horizon`;
    field on the manifest is `exposure_horizon_observed`.
  - decision #10 — `quality_gate_thresholds` keys `e_fo_*` renamed to
    `e_or_*`; `C_FO` references in this docstring renamed to `C_CO`.
  - decision #11 — `quality_gate_thresholds` no longer carries the
    WS6 mechanistic keys (mooted by gate removal).

Pilot trace row-count invariant (Tier-R2-0 PR1, IMPLEMENTATION_NOTE.md
§PR1 step 4 / S5): every per-model `*__pilot.parquet` must contain
exactly `len(--article-manifest)` rows (one row per article × case).
The article manifest is required to be a JSON list of
`ArticleRecord`-shaped entries; mismatch (or 0-byte / corrupt parquet)
raises `SystemExit` in confirmatory mode and is also enforced for any
parquet that exists in dev mode.

Inputs (file paths; missing optional inputs are recorded as `None`):

  --fleet              pinned fleet YAML (no `<TBD>` allowed)
  --runtime            runtime YAML
  --traces-dir         directory containing per-model `*__pilot.parquet`
  --exposure-horizon   JSON output of scripts/run_exposure_horizon_analysis.py
  --hidden-states-dir  directory of WS6 hidden-state .safetensors files
  --article-manifest   pilot article manifest JSON
  --sampling-config    YAML defining the pilot sampling protocol; SHA-256
                       hashed into RunManifest.sampling_config_hash so that
                       hash is independent of article_manifest_hash
  --perturbation-manifest   (optional) C_CO/C_NoOp output manifest
  --audit-manifest     (optional) audit manifest
  --vllm-image-digest  Docker image digest used for the run
  --gpu-dtype          backend launch dtype (e.g. "bf16", "fp16")
  --launch-env         JSON file with the run's environment snapshot
                       (CUDA_VISIBLE_DEVICES, vLLM args, NO_PROXY, etc.)
  --output             RunManifest JSON output path

Quality-gate thresholds are computed at run time using the
strict-majority rule from `docs/DECISION_20260429_gate_removal.md`
§2.6: K = ⌊N/2⌋ + 1 for "majority" gates, K = ⌈N/3⌉ for the "minority
sufficient" E_extract main-text rule. The realized K values are
recorded so downstream analysis is unambiguous about which fleet basis
was used.

Run order on cloud instance after pilot completes:

    python scripts/run_exposure_horizon_analysis.py ...
    python scripts/ws1_finalize_run_manifest.py \\
        --fleet config/fleet/r5a_fleet.yaml \\
        --runtime config/runtime/r5a_runtime.yaml \\
        --traces-dir data/pilot/logprob_traces \\
        --exposure-horizon data/pilot/exposure_horizon/horizon_observed.json \\
        --hidden-states-dir data/pilot/hidden_states \\
        --article-manifest data/pilot/manifests/pilot_articles.json \\
        --sampling-config config/pilot_sampling.yaml \\
        --vllm-image-digest sha256:... \\
        --gpu-dtype bf16 \\
        --launch-env data/pilot/.launch_env.json \\
        --output data/pilot/run_manifest.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
import subprocess
import sys
import uuid
from datetime import date as Date, datetime, timezone
from pathlib import Path
from typing import Literal

import pyarrow.parquet as pq

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.r5a.contracts import RUNSTATE_TABLE_NAME, RunManifest  # noqa: E402
from src.r5a.fleet import FleetConfig, load_fleet  # noqa: E402
from src.r5a.io_utils import atomic_write_text  # noqa: E402
from src.r5a.runtime import load_runtime  # noqa: E402


VLLM_IMAGE_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WS1 RunManifest finalizer")
    p.add_argument("--fleet", default="config/fleet/r5a_fleet.yaml")
    p.add_argument("--runtime", default="config/runtime/r5a_runtime.yaml")
    p.add_argument(
        "--traces-dir",
        default="data/pilot/logprob_traces",
        help="directory of per-model trace parquet files",
    )
    p.add_argument("--exposure-horizon", default=None)
    p.add_argument("--hidden-states-dir", default=None)
    p.add_argument("--article-manifest", required=True)
    p.add_argument(
        "--sampling-config",
        default="config/pilot_sampling.yaml",
        help="YAML defining the pilot sampling protocol; SHA-256 hashed "
        "into RunManifest.sampling_config_hash (R2 decision #15 / R2-C2 #5).",
    )
    p.add_argument("--perturbation-manifest", default=None)
    p.add_argument("--audit-manifest", default=None)
    p.add_argument("--vllm-image-digest", default=None)
    p.add_argument("--gpu-dtype", default=None)
    p.add_argument("--launch-env", default=None)
    p.add_argument(
        "--seed-policy",
        default=None,
        help="JSON file describing seed policy; default reads from runtime",
    )
    p.add_argument(
        "--prompt-versions",
        default=None,
        help="JSON file mapping operator_id to prompt version tag",
    )
    p.add_argument(
        "--runstate-db",
        default=None,
        help="path to runstate sqlite; default = runtime.runstate_db",
    )
    p.add_argument("--output", required=True)
    p.add_argument("--run-id", default=None)
    p.add_argument(
        "--allow-tbd",
        action="store_true",
        help=(
            "permit `<TBD>` placeholders in the fleet (smoke / dev only); "
            "sets manifest.mode='dev' and skips the 8-clause confirmatory "
            "hard-fail framework. Confirmatory runs MUST run "
            "scripts/ws1_pin_fleet.py first and OMIT this flag."
        ),
    )
    return p.parse_args()


def _git_commit_sha() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        )
        return out.decode("ascii").strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "0" * 40


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(64 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _hash_strings(items: list[str]) -> str:
    """SHA256 of `\\n`-joined sorted strings."""
    payload = "\n".join(sorted(items)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _parquet_rowcount_or_error(path: Path) -> int | str:
    """Return parquet row count, or a string describing the open / read error.

    Uses `pyarrow.parquet.read_metadata` so the file is not fully loaded.
    Wraps 0-byte / truncated / corrupt files into the same diagnostic
    surface as a row-count mismatch (Tier-R2-0 PR1 step 4).
    """
    try:
        return pq.read_metadata(str(path)).num_rows
    except Exception as exc:  # pragma: no cover - exact error class is libarrow-version-dependent
        return f"failed to read parquet metadata: {exc!r}"


def _validate_traces_dir(
    traces_dir: Path,
    expected_models: list[str],
    *,
    mode: Literal["confirmatory", "dev"],
    expected_n_articles: int | None = None,
) -> dict[str, str]:
    """Return mapping `model_id -> trace_path` for the realized set.

    Layout convention (matches `scripts/ws1_run_logprob.py`
    `_resolve_output_paths` for `--pilot`): `{traces_dir}/{model_id}__pilot.parquet`.

    In `dev` mode missing traces (or a missing directory) are tolerated
    so `--allow-tbd` smoke-finalize still runs against partial data.
    In `confirmatory` mode every `expected_models` entry must exist on
    disk AND no extra `*__pilot.parquet` files may be present; both
    classes are reported in a single multi-line `SystemExit`.

    Row-count gate (Tier-R2-0 PR1 step 4 / S5): when
    `expected_n_articles` is provided, every parquet that resolves to
    an `expected_models` entry is opened via
    `pyarrow.parquet.read_metadata` and its row count compared to
    `expected_n_articles`. Mismatch / 0-byte / corrupt parquet → fail.
    """
    expected_set = set(expected_models)
    out: dict[str, str] = {}

    if not traces_dir.exists():
        if mode == "dev":
            return out
        raise SystemExit(
            f"--traces-dir {traces_dir} does not exist; "
            f"confirmatory finalize requires per-model `*__pilot.parquet` files."
        )

    on_disk: dict[str, Path] = {}
    for parquet in sorted(traces_dir.glob("*__pilot.parquet")):
        # Strip the `__pilot.parquet` suffix to recover model_id.
        model_id = parquet.name[: -len("__pilot.parquet")]
        on_disk[model_id] = parquet

    rowcount_problems: list[str] = []

    def _check_rowcount(model_id: str, parquet_path: Path) -> None:
        if expected_n_articles is None:
            return
        result = _parquet_rowcount_or_error(parquet_path)
        if isinstance(result, str):
            rowcount_problems.append(
                f"  {model_id} ({parquet_path.name}): {result}"
            )
        elif result != expected_n_articles:
            rowcount_problems.append(
                f"  {model_id} ({parquet_path.name}): row count {result} "
                f"!= expected {expected_n_articles}"
            )

    if mode == "dev":
        for mid, path in on_disk.items():
            if mid in expected_set:
                out[mid] = str(path)
                _check_rowcount(mid, path)
        if rowcount_problems:
            raise SystemExit(
                "pilot trace row count does not match article-manifest:\n"
                + "\n".join(rowcount_problems)
            )
        return out

    missing = sorted(expected_set - set(on_disk))
    extras = sorted(set(on_disk) - expected_set)
    if missing or extras:
        msg_lines = [
            f"--traces-dir {traces_dir} does not match P_logprob fleet roster:"
        ]
        if missing:
            msg_lines.append(f"  missing: {missing}")
        if extras:
            msg_lines.append(f"  unexpected files for: {extras}")
        raise SystemExit("\n".join(msg_lines))

    for mid in sorted(expected_set):
        out[mid] = str(on_disk[mid])
        _check_rowcount(mid, on_disk[mid])

    if rowcount_problems:
        raise SystemExit(
            "pilot trace row count does not match article-manifest "
            f"(expected {expected_n_articles} per model):\n"
            + "\n".join(rowcount_problems)
        )
    return out


def _pilot_trace_shas(traces: dict[str, str]) -> dict[str, str]:
    """Compute SHA-256 of each pilot trace parquet's byte content.

    Populates `RunManifest.pilot_trace_shas` (Tier-R2-0 PR1 #9 E SHA
    half). Paired with `_validate_traces_dir`'s row-count gate this
    closes the half-written / 0-byte / wrong-N / mix-batch parquet hole.
    """
    return {mid: _sha256_file(Path(path)) for mid, path in traces.items()}


_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def _validate_exposure_horizon_payload(
    payload: object,
    path: Path,
    fleet: FleetConfig,
) -> None:
    """Path-E source-JSON shape gate (Tier-R2-0 PR1 step 5).

    Enforces that the analyzer JSON binds analyzer-side trace SHAs and
    probe-set SHA into the finalizer's view, so a stale or malformed
    file cannot silently masquerade as a valid Path-E result.

    Required at the top level:
      - ``trace_shas``: ``dict[str, str]`` whose keys equal the fleet
        ``p_logprob_eligible_ids()`` set and whose values are non-empty
        lower-case 64-hex SHA-256 digests.
      - ``probe_set_sha256``: a non-empty lower-case 64-hex SHA-256.

    Any deviation (missing key, wrong type, empty value, malformed hex,
    or roster mismatch) raises ``SystemExit`` with a single multi-line
    message naming each violation.
    """
    if not isinstance(payload, dict):
        raise SystemExit(
            f"--exposure-horizon {path} top-level JSON is "
            f"{type(payload).__name__}; expected object."
        )

    failures: list[str] = []

    # trace_shas
    if "trace_shas" not in payload:
        failures.append(
            "--exposure-horizon JSON is missing 'trace_shas' "
            "(produced by run_exposure_horizon_analysis.py)."
        )
    else:
        trace_shas = payload["trace_shas"]
        if not isinstance(trace_shas, dict):
            failures.append(
                f"--exposure-horizon 'trace_shas' is "
                f"{type(trace_shas).__name__}; expected object."
            )
        else:
            expected_roster = set(fleet.p_logprob_eligible_ids())
            actual_roster = set(trace_shas)
            if actual_roster != expected_roster:
                missing = sorted(expected_roster - actual_roster)
                extras = sorted(actual_roster - expected_roster)
                failures.append(
                    "--exposure-horizon 'trace_shas' roster does not match "
                    f"P_logprob fleet (missing={missing}, unexpected={extras})."
                )
            for mid, sha in trace_shas.items():
                if not isinstance(sha, str) or not sha:
                    failures.append(
                        f"--exposure-horizon 'trace_shas[{mid}]' is empty "
                        f"or non-string ({sha!r})."
                    )
                elif not _SHA256_RE.match(sha):
                    failures.append(
                        f"--exposure-horizon 'trace_shas[{mid}]'={sha!r} "
                        "does not match SHA-256 lower-hex pattern."
                    )

    # probe_set_sha256
    if "probe_set_sha256" not in payload:
        failures.append(
            "--exposure-horizon JSON is missing 'probe_set_sha256'."
        )
    else:
        probe_sha = payload["probe_set_sha256"]
        if not isinstance(probe_sha, str) or not probe_sha:
            failures.append(
                f"--exposure-horizon 'probe_set_sha256' is empty or "
                f"non-string ({probe_sha!r})."
            )
        elif not _SHA256_RE.match(probe_sha):
            failures.append(
                f"--exposure-horizon 'probe_set_sha256'={probe_sha!r} "
                "does not match SHA-256 lower-hex pattern."
            )

    if failures:
        raise SystemExit(
            f"Path-E source JSON shape verification failed for {path}:\n  "
            + "\n  ".join(failures)
        )


def _read_exposure_horizon(
    path: Path,
    fleet: FleetConfig,
    *,
    mode: Literal["confirmatory", "dev"],
) -> tuple[dict[str, Date | None], list[str]]:
    """Read scripts/run_exposure_horizon_analysis.py output.

    The analysis JSON's `summary[model_id]` carries `horizon_observed`
    (renamed from the pre-R2 `cutoff_observed` per DECISIONS.md
    decision #5). In `confirmatory` mode every fleet P_logprob model
    must appear with either an ISO date or `null` (rejected horizon),
    and an invalid date string raises `SystemExit`. In `dev` mode an
    invalid date silently becomes `None` so iteration on the analyzer
    is not blocked.

    Top-level shape (`trace_shas`, `probe_set_sha256`) is validated
    via :func:`_validate_exposure_horizon_payload` regardless of mode
    (Tier-R2-0 PR1 step 5).
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    _validate_exposure_horizon_payload(payload, path, fleet)
    summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
    out: dict[str, Date | None] = {}
    msgs: list[str] = []
    for model_id, row in summary.items():
        # Schema-strict parse (Tier-R2-0 PR1 step 6, #4 A): a row without
        # `horizon_observed` is malformed regardless of mode and is not
        # equivalent to `horizon_observed: null` (which is "knee detector
        # rejected the fit"). Mode does not soften this — a stale or
        # truncated analyzer run must not silently land as "rejected
        # horizon" for every model.
        if "horizon_observed" not in row:
            raise SystemExit(
                f"--exposure-horizon {path} summary[{model_id!r}] is missing "
                f"'horizon_observed' key (got keys {sorted(row)!r}). "
                "Re-run scripts/run_exposure_horizon_analysis.py."
            )
        co = row["horizon_observed"]
        if co is None:
            out[model_id] = None
            msgs.append(f"  {model_id}: horizon rejected ({row.get('notes')})")
            continue
        try:
            out[model_id] = Date.fromisoformat(co)
            msgs.append(
                f"  {model_id}: horizon_observed={co} "
                f"CI={row.get('horizon_ci_lower')}..{row.get('horizon_ci_upper')} "
                f"({row.get('horizon_ci_width_months')} months wide)"
            )
        except ValueError:
            if mode == "confirmatory":
                raise SystemExit(
                    f"invalid horizon date {co!r} for {model_id} in {path}"
                )
            out[model_id] = None
            msgs.append(f"  {model_id}: invalid horizon date {co!r}")

    if mode == "confirmatory":
        eligible = set(fleet.p_logprob_eligible_ids())
        present = set(out)
        missing = sorted(eligible - present)
        extras = sorted(present - eligible)
        if missing or extras:
            msg_lines = [
                f"--exposure-horizon {path} does not match P_logprob fleet roster:"
            ]
            if missing:
                msg_lines.append(f"  missing: {missing}")
            if extras:
                msg_lines.append(f"  unexpected: {extras}")
            raise SystemExit("\n".join(msg_lines))

    return out, msgs


def _hidden_state_subset_hash(
    hidden_states_dir: Path,
    expected_models: list[str],
    expected_case_count: int = 30,
    *,
    mode: Literal["confirmatory", "dev"],
) -> tuple[str | None, int]:
    """Hash the WS6 hidden-state subset.

    On-disk layout `{hidden_states_dir}/{case_id}__{model_id}.safetensors`
    is COUPLED to `OfflineHFBackend._save_hidden_states`
    (`src/r5a/backends/offline_hf.py` line ~260). If the layout
    convention is ever updated, both this function AND the backend
    writer MUST change together — F.35 #7 fixture is constructed
    directly (does not exercise the backend) and will not catch
    drift between writer and reader.
    """
    if not hidden_states_dir.exists():
        if mode == "dev":
            return None, 0
        raise SystemExit(
            f"--hidden-states-dir {hidden_states_dir} does not exist; "
            f"confirmatory finalize requires the WS6 subset on disk."
        )

    per_model: dict[str, set[str]] = {}
    for f in hidden_states_dir.glob("*.safetensors"):
        stem = f.stem  # `{case_id}__{model_id}`
        if "__" not in stem:
            continue
        case_id, _, model_id = stem.rpartition("__")
        per_model.setdefault(model_id, set()).add(case_id)

    if not per_model:
        if mode == "dev":
            return None, 0
        raise SystemExit(
            f"--hidden-states-dir {hidden_states_dir} contains no "
            f"`{{case_id}}__{{model_id}}.safetensors` files; expected "
            f"{expected_case_count} per model in {expected_models!r}."
        )

    if mode == "confirmatory":
        problems: list[str] = []
        # Establish the canonical case set from the first expected model that has data.
        canonical: set[str] | None = None
        for mid in expected_models:
            if mid in per_model:
                canonical = per_model[mid]
                break
        if canonical is None:
            raise SystemExit(
                f"hidden-state subset has no entries for any expected model "
                f"{expected_models!r}; got models {sorted(per_model)!r}"
            )
        for mid in expected_models:
            cases = per_model.get(mid, set())
            if len(cases) != expected_case_count:
                problems.append(
                    f"  {mid}: have {len(cases)} cases, expected {expected_case_count}"
                )
            missing = sorted(canonical - cases)
            if missing:
                problems.append(f"  {mid}: missing case_ids {missing}")
        if problems:
            raise SystemExit(
                "hidden-state subset incomplete:\n" + "\n".join(problems)
            )

    # Use the canonical case set (first model present) for the hash so that
    # the value is stable regardless of which model was sampled.
    case_ids: set[str] = set()
    for mid in expected_models:
        if mid in per_model:
            case_ids = per_model[mid]
            break
    if not case_ids:
        return None, 0
    return _hash_strings(sorted(case_ids)), len(case_ids)


def _strict_majority(n: int) -> int:
    return n // 2 + 1


def _one_third_minimum(n: int) -> int:
    return math.ceil(n / 3)


def _quality_gate_thresholds(
    n_p_predict: int, n_p_logprob: int
) -> dict[str, int]:
    """Per `docs/DECISION_20260429_gate_removal.md` §2.6 +
    `docs/DECISION_20260429_llama_addition.md` §2.6.

    R2 decision #11 drops the WS6 mechanistic keys; R2 decision #10
    source-side renames the `e_fo_*` keys to `e_or_*`. The argument
    `n_p_logprob` is retained in the signature because
    `_confirmatory_hard_fail` clause #6 enforces that the realized
    P_logprob roster equals the fleet view, so callers can still pass
    it for documentation / future use.
    """
    del n_p_logprob  # currently unused; retained for signature stability
    return {
        # E_extract reserve thresholds (R5A_FROZEN_SHORTLIST §4)
        "e_extract_main_text_promotion_n_p_predict": n_p_predict,
        "e_extract_main_text_threshold": _one_third_minimum(n_p_predict),
        "e_extract_confirmatory_promotion_n_p_predict": n_p_predict,
        "e_extract_confirmatory_threshold": _strict_majority(n_p_predict),
        # Behavioral E_OR / E_NoOp gate condition 3 has been REMOVED
        # (gate_removal §2.1). Recorded here as informational so future
        # reanalysis can compare against the gate that *would* have
        # applied if it were still in force.
        "e_or_e_noop_informational_n_p_predict": n_p_predict,
        "e_or_e_noop_informational_threshold": _strict_majority(n_p_predict),
    }


def _model_fingerprints(fleet: FleetConfig) -> dict[str, dict[str, str]]:
    """Build a model_id -> fingerprint-fields mapping for the manifest.

    For confirmatory runs the operator-side fingerprint (system_fingerprint,
    response_id, ...) is captured per request; this manifest-level summary
    just records what was *expected* per fleet config.
    """
    fps: dict[str, dict[str, str]] = {}
    for mid, cfg in fleet.models.items():
        fp = {
            "provider": cfg.provider,
            "family": cfg.family,
            "access": cfg.access.value,
        }
        if cfg.api_model_name:
            fp["api_model_name"] = cfg.api_model_name
        if cfg.hf_repo:
            fp["hf_repo"] = cfg.hf_repo
        if cfg.cutoff_source:
            fp["cutoff_source"] = cfg.cutoff_source
        fps[mid] = fp
    return fps


def _confirmatory_hard_fail(
    args: argparse.Namespace,
    fleet: FleetConfig,
    traces: dict[str, str],
    exposure_horizon: dict[str, Date | None],
    launch_env: dict[str, str],
    sampling_config_path: Path,
    runstate_db_path: str | None,
) -> None:
    """11-clause confirmatory-mode hard-fail (decision #1 + Lens A major #8;
    Tier-R2-0 PR1 step 7 added hidden-states-dir + runstate clauses and
    renumbered end-to-end so each check has a unique ``[clause N]``).

    Raises a single ``SystemExit`` carrying a multi-line message; each
    failed clause is on its own line, prefixed with ``[clause N]`` so
    the operator sees every failure (not just the first) and tests can
    assert on the exact clause set without coincidental substring
    matches in unrelated text.

    Two clauses are normally enforced inside helpers that run **before**
    this collector (so the failure surfaces at the call site, not here):

    - the exposure-horizon-roster check is enforced inside
      :func:`_read_exposure_horizon`;
    - the trace-roster + per-parquet row-count checks are enforced
      inside :func:`_validate_traces_dir`.

    Both are re-checked here so that any future caller that bypasses
    those helpers still sees the same gate. Tests asserting on those
    failure modes (the exposure-horizon-roster check or the trace-roster
    check) must call the helper directly; the multi-line collector
    here is reachable only when the helper is bypassed. Clause numbers
    can shift across releases, so this docstring deliberately avoids
    naming them — see the in-body comments for current numbering.
    """
    failures: list[str] = []
    placeholder_set = {None, "", "<TBD>"}

    # Clause 1 — git_commit_sha must be a real SHA, not the all-zero fallback.
    git_sha = _git_commit_sha()
    if git_sha == "0" * 40:
        failures.append(
            "[clause 1] git_commit_sha is all-zero (run from a non-git checkout?); "
            "cannot record provenance."
        )

    # Clause 2 — vllm_image_digest must match sha256:<64-hex>.
    digest = args.vllm_image_digest
    if not digest:
        failures.append(
            "[clause 2] --vllm-image-digest is required in confirmatory mode."
        )
    elif not VLLM_IMAGE_DIGEST_RE.match(digest):
        failures.append(
            f"[clause 2] --vllm-image-digest {digest!r} does not match "
            "sha256:<64-hex>."
        )

    # Clause 3 — sampling-config path must exist.
    if not sampling_config_path.exists():
        failures.append(
            f"[clause 3] --sampling-config {sampling_config_path} does not exist; "
            "confirmatory finalize cannot hash it into sampling_config_hash."
        )

    # Clause 4 — every P_logprob model has non-placeholder tokenizer_sha and
    # white-box checkpoint sha.
    p_logprob_ids = fleet.p_logprob_eligible_ids()
    for mid in p_logprob_ids:
        cfg = fleet.get(mid)
        if cfg.tokenizer_sha in placeholder_set:
            failures.append(
                f"[clause 4] tokenizer_sha is {cfg.tokenizer_sha!r} for {mid} — "
                "run scripts/ws1_pin_fleet.py."
            )
        if cfg.hf_commit_sha in placeholder_set:
            failures.append(
                f"[clause 4] hf_commit_sha is {cfg.hf_commit_sha!r} for {mid} — "
                "run scripts/ws1_pin_fleet.py."
            )

    # Clause 5 — every black-box has a non-placeholder api_model_name.
    for mid in fleet.black_box_ids():
        cfg = fleet.get(mid)
        if cfg.api_model_name in placeholder_set:
            failures.append(
                f"[clause 5] api_model_name is {cfg.api_model_name!r} for "
                f"black-box {mid}."
            )

    # Clause 6 — exposure_horizon keys must equal the P_logprob fleet roster.
    # Normally short-circuited inside _read_exposure_horizon; mirrored here
    # so a caller that bypasses the helper still sees the gate.
    expected = set(p_logprob_ids)
    eh_keys = set(exposure_horizon)
    if eh_keys != expected:
        missing = sorted(expected - eh_keys)
        extras = sorted(eh_keys - expected)
        failures.append(
            "[clause 6] exposure_horizon roster mismatch "
            f"(missing={missing}, unexpected={extras})."
        )

    # Clause 7 — traces dir mapping must cover every P_logprob model.
    # Normally short-circuited inside _validate_traces_dir; mirrored here.
    trace_keys = set(traces)
    if trace_keys != expected:
        missing = sorted(expected - trace_keys)
        extras = sorted(trace_keys - expected)
        failures.append(
            "[clause 7] traces-dir roster mismatch "
            f"(missing={missing}, unexpected={extras})."
        )

    # Clause 8 — launch_env must record CUDA_VISIBLE_DEVICES and VLLM_VERSION.
    for required_key in ("CUDA_VISIBLE_DEVICES", "VLLM_VERSION"):
        if required_key not in launch_env:
            failures.append(
                f"[clause 8] launch_env is missing required key {required_key!r}; "
                "supply it via --launch-env JSON."
            )

    # Clause 9 — gpu_dtype must be set (e.g. "bf16").
    if args.gpu_dtype in placeholder_set:
        failures.append(
            f"[clause 9] --gpu-dtype is {args.gpu_dtype!r}; required in "
            "confirmatory mode (e.g. \"bf16\", \"fp16\")."
        )

    # Clause 10 — --hidden-states-dir must be supplied (PR1 step 7 / #1 B).
    # The directory's contents (subset hash) are checked inside
    # _hidden_state_subset_hash; this clause guards the upstream "operator
    # forgot the flag entirely" case so it does not silently degrade to
    # `hidden_state_subset_hash=None` in the manifest.
    if args.hidden_states_dir is None:
        failures.append(
            "[clause 10] --hidden-states-dir is required in confirmatory mode; "
            "WS6 subset hash cannot be computed without it."
        )

    # Clause 11 — runstate.db must be initialized and have no orphan
    # `pending` / `retryable` rows (PR1 step 7 / MED-2 + S2 forward-
    # declared RUNSTATE_TABLE_NAME contract). Read-only `mode=ro&immutable=1`
    # so a missing file does not silently get created.
    if runstate_db_path is None:
        failures.append(
            "[clause 11] runstate.db path is empty; runtime.runstate_db or "
            "--runstate-db must point at the orchestration database."
        )
    else:
        rs_path = Path(runstate_db_path)
        try:
            conn = sqlite3.connect(
                f"file:{rs_path.as_posix()}?mode=ro&immutable=1", uri=True
            )
        except sqlite3.OperationalError:
            failures.append(
                f"[clause 11] runstate.db at {rs_path} not initialized; "
                "Phase 7 orchestration must run before confirmatory finalize."
            )
        else:
            try:
                with conn:
                    try:
                        cur = conn.execute(
                            f"SELECT COUNT(*), GROUP_CONCAT("
                            f"case_id || ':' || model_id, '; ') "
                            f"FROM {RUNSTATE_TABLE_NAME} "
                            f"WHERE status IN ('pending', 'retryable')"
                        )
                        count, sample = cur.fetchone()
                    except sqlite3.OperationalError as exc:
                        failures.append(
                            f"[clause 11] runstate.db at {rs_path} is missing "
                            f"table {RUNSTATE_TABLE_NAME!r} or expected columns "
                            f"({exc!s}); Phase 7 orchestration writer must "
                            "create it per RUNSTATE_TABLE_NAME contract."
                        )
                    else:
                        if count and count > 0:
                            sample_str = sample or ""
                            truncated = sample_str[:200] + (
                                "..." if len(sample_str) > 200 else ""
                            )
                            failures.append(
                                f"[clause 11] runstate has {count} orphan "
                                f"pending/retryable rows: {truncated}"
                            )
            finally:
                conn.close()

    if failures:
        raise SystemExit(
            "fleet not ready for confirmatory finalize:\n  "
            + "\n  ".join(failures)
        )


def main() -> int:
    args = parse_args()
    fleet = load_fleet(args.fleet)
    runtime = load_runtime(args.runtime)

    mode: Literal["confirmatory", "dev"] = "dev" if args.allow_tbd else "confirmatory"

    article_manifest_path = Path(args.article_manifest)
    article_manifest_hash = _sha256_file(article_manifest_path)

    # S5 (IMPLEMENTATION_NOTE.md): pilot trace row count must equal article
    # manifest entry count, per model. Read with shape assertion so a
    # malformed manifest cannot silently masquerade as the empty list.
    manifest_payload = json.loads(
        article_manifest_path.read_text(encoding="utf-8")
    )
    if not isinstance(manifest_payload, list):
        raise SystemExit(
            f"--article-manifest {article_manifest_path} is not a JSON list "
            f"(got {type(manifest_payload).__name__}); expected list of "
            f"ArticleRecord-shaped entries."
        )
    expected_n_articles = len(manifest_payload)

    sampling_config_path = Path(args.sampling_config)
    if sampling_config_path.exists():
        sampling_config_hash = _sha256_file(sampling_config_path)
    else:
        if mode == "confirmatory":
            # The hard-fail framework will report this as part of its
            # collected message; raising here would short-circuit the
            # multi-clause collection contract.
            sampling_config_hash = ""
        else:
            sampling_config_hash = ""

    perturbation_manifest_hash: str | None = None
    if args.perturbation_manifest:
        perturbation_manifest_hash = _sha256_file(Path(args.perturbation_manifest))

    audit_manifest_hash: str | None = None
    if args.audit_manifest:
        audit_manifest_hash = _sha256_file(Path(args.audit_manifest))

    exposure_horizon: dict[str, Date | None] = {}
    if args.exposure_horizon:
        exposure_horizon, lines = _read_exposure_horizon(
            Path(args.exposure_horizon), fleet, mode=mode
        )
        print("exposure_horizon loaded:")
        for ln in lines:
            print(ln)

    cutoff_date_yaml = {mid: cfg.cutoff_date for mid, cfg in fleet.models.items()}
    quant_scheme = {
        mid: (cfg.quant_scheme or "")
        for mid, cfg in fleet.models.items()
        if cfg.quant_scheme is not None or cfg.is_white_box()
    }

    pcsg_hash = fleet.pcsg_pair_registry_hash()

    p_logprob_ids = fleet.p_logprob_eligible_ids()
    p_predict_ids = fleet.p_predict_eligible_ids()
    n_p_predict = len(p_predict_ids)
    n_p_logprob = len(p_logprob_ids)

    traces = _validate_traces_dir(
        Path(args.traces_dir),
        p_logprob_ids,
        mode=mode,
        expected_n_articles=expected_n_articles,
    )
    pilot_trace_shas = _pilot_trace_shas(traces)

    exposure_horizon_source_sha256: str | None = None
    if args.exposure_horizon:
        exposure_horizon_source_sha256 = _sha256_file(Path(args.exposure_horizon))

    hs_hash, hs_n = (None, 0)
    if args.hidden_states_dir:
        hs_hash, hs_n = _hidden_state_subset_hash(
            Path(args.hidden_states_dir),
            p_logprob_ids,
            mode=mode,
        )
        print(
            f"hidden_state_subset: {hs_n} cases, hash="
            + (hs_hash[:12] + "..." if hs_hash else "<none>")
        )

    quality_gate_thresholds = _quality_gate_thresholds(n_p_predict, n_p_logprob)

    tokenizer_shas = {
        mid: (cfg.tokenizer_sha or "")
        for mid, cfg in fleet.models.items()
        if cfg.is_white_box() and cfg.tokenizer_sha
    }
    white_box_checkpoint_shas = {
        mid: (cfg.hf_commit_sha or "")
        for mid, cfg in fleet.models.items()
        if cfg.is_white_box() and cfg.hf_commit_sha
    }

    runtime_caps = {name: prov.max_concurrency for name, prov in runtime.providers.items()}

    seed_policy: dict[str, object]
    if args.seed_policy:
        loaded = _load_json(Path(args.seed_policy))
        if not isinstance(loaded, dict):
            raise SystemExit("--seed-policy JSON must be an object")
        seed_policy = dict(loaded)
    else:
        seed_policy = {
            "strategy": "fixed",
            "seed": runtime.runtime.seed,
        }

    prompt_versions: dict[str, str] = {}
    if args.prompt_versions:
        loaded = _load_json(Path(args.prompt_versions))
        if not isinstance(loaded, dict):
            raise SystemExit("--prompt-versions JSON must be an object")
        prompt_versions = {str(k): str(v) for k, v in loaded.items()}

    launch_env: dict[str, str] = {}
    if args.launch_env:
        loaded = _load_json(Path(args.launch_env))
        if not isinstance(loaded, dict):
            raise SystemExit("--launch-env JSON must be an object")
        launch_env = {str(k): str(v) for k, v in loaded.items()}

    runstate_db_path = args.runstate_db or runtime.runtime.runstate_db
    runstate_db_hash: str | None = None
    if runstate_db_path:
        rs_path = Path(runstate_db_path)
        if rs_path.exists():
            runstate_db_hash = _sha256_file(rs_path)

    if mode == "confirmatory":
        _confirmatory_hard_fail(
            args=args,
            fleet=fleet,
            traces=traces,
            exposure_horizon=exposure_horizon,
            launch_env=launch_env,
            sampling_config_path=sampling_config_path,
            runstate_db_path=runstate_db_path,
        )

    manifest = RunManifest(
        run_id=args.run_id or uuid.uuid4().hex,
        created_at=datetime.now(timezone.utc),
        git_commit_sha=_git_commit_sha(),
        fleet_config_hash=fleet.raw_yaml_sha256,
        runtime_config_hash=runtime.raw_yaml_sha256,
        sampling_config_hash=sampling_config_hash,
        prompt_versions=prompt_versions,
        model_fingerprints=_model_fingerprints(fleet),
        white_box_checkpoint_shas=white_box_checkpoint_shas,
        runtime_caps=runtime_caps,
        seed_policy=seed_policy,
        runstate_db_path=runstate_db_path,
        runstate_db_hash=runstate_db_hash,
        article_manifest_hash=article_manifest_hash,
        perturbation_manifest_hash=perturbation_manifest_hash,
        audit_manifest_hash=audit_manifest_hash,
        tokenizer_shas=tokenizer_shas,
        vllm_image_digest=args.vllm_image_digest,
        gpu_dtype=args.gpu_dtype,
        launch_env=launch_env,
        exposure_horizon_observed=exposure_horizon,
        cutoff_date_yaml=cutoff_date_yaml,
        quant_scheme=quant_scheme,
        pcsg_pair_registry_hash=pcsg_hash,
        hidden_state_subset_hash=hs_hash,
        quality_gate_thresholds=quality_gate_thresholds,
        mode=mode,
        fleet_p_predict_eligible=p_predict_ids,
        fleet_p_logprob_eligible=p_logprob_ids,
        exposure_horizon_source_sha256=exposure_horizon_source_sha256,
        pilot_trace_shas=pilot_trace_shas,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = manifest.model_dump(mode="json")
    # Atomic write (MED-3 / Tier-R2-0 PR1 step 14): a crash mid-write
    # would otherwise leave a half-written manifest that downstream
    # readers might still try to parse.
    atomic_write_text(
        out_path,
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True),
    )
    print(f"\nwrote {out_path}")
    print(f"  mode                   = {mode}")
    print(f"  fleet_version          = {fleet.fleet_version}")
    print(f"  fleet_config_hash      = {fleet.raw_yaml_sha256[:12]}...")
    print(f"  pcsg_pair_registry_hash= {pcsg_hash[:12]}...")
    print(f"  n_p_predict (eligible) = {n_p_predict}")
    print(f"  n_p_logprob (eligible) = {n_p_logprob}")
    print(f"  exposure_horizon (n_ok)= "
          f"{sum(1 for v in exposure_horizon.values() if v is not None)}"
          f"/{len(exposure_horizon)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""WS1 RunManifest finalizer.

Per Tier-0 #4 (`refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/SYNTHESIS.md`)
+ Operational §6: a confirmatory cloud run is non-reproducible without
a single artifact joining together pinned fleet + main traces + Path E
output + pcsg_pairs hash + Docker digest + sub-artifact hashes. This
script writes that artifact (`RunManifest`).

Inputs (file paths; missing optional inputs are recorded as `None`):

  --fleet              pinned fleet YAML (no `<TBD>` allowed)
  --runtime            runtime YAML
  --traces-dir         directory containing per-model `*__pilot.parquet`
  --cutoff-observed    JSON output of scripts/run_cutoff_probe_analysis.py
  --hidden-states-dir  directory of WS6 hidden-state .safetensors files
  --article-manifest   pilot article manifest JSON
  --perturbation-manifest   (optional) C_FO/C_NoOp output manifest
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

    python scripts/run_cutoff_probe_analysis.py ...
    python scripts/ws1_finalize_run_manifest.py \\
        --fleet config/fleet/r5a_fleet.yaml \\
        --runtime config/runtime/r5a_runtime.yaml \\
        --traces-dir data/pilot/logprob_traces \\
        --cutoff-observed data/pilot/cutoff_probe/cutoff_observed.json \\
        --hidden-states-dir data/pilot/hidden_states \\
        --article-manifest data/pilot/manifests/pilot_articles.json \\
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
import subprocess
import sys
import uuid
from datetime import date as Date, datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.r5a.contracts import RunManifest  # noqa: E402
from src.r5a.fleet import load_fleet  # noqa: E402
from src.r5a.runtime import load_runtime  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WS1 RunManifest finalizer")
    p.add_argument("--fleet", default="config/fleet/r5a_fleet.yaml")
    p.add_argument("--runtime", default="config/runtime/r5a_runtime.yaml")
    p.add_argument(
        "--traces-dir",
        default="data/pilot/logprob_traces",
        help="directory of per-model trace parquet files",
    )
    p.add_argument("--cutoff-observed", default=None)
    p.add_argument("--hidden-states-dir", default=None)
    p.add_argument("--article-manifest", required=True)
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
            "confirmatory runs MUST run scripts/ws1_pin_fleet.py first"
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


def _read_cutoff_observed(path: Path) -> tuple[dict[str, Date | None], list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
    out: dict[str, Date | None] = {}
    msgs: list[str] = []
    for model_id, row in summary.items():
        co = row.get("cutoff_observed")
        if co is None:
            out[model_id] = None
            msgs.append(f"  {model_id}: cutoff rejected ({row.get('notes')})")
        else:
            try:
                out[model_id] = Date.fromisoformat(co)
                msgs.append(
                    f"  {model_id}: cutoff_observed={co} "
                    f"CI={row.get('cutoff_ci_lower')}..{row.get('cutoff_ci_upper')} "
                    f"({row.get('cutoff_ci_width_months')} months wide)"
                )
            except ValueError:
                out[model_id] = None
                msgs.append(f"  {model_id}: invalid cutoff date {co!r}")
    return out, msgs


def _hidden_state_subset_hash(hidden_states_dir: Path) -> tuple[str | None, int]:
    """SHA256 over sorted case_ids extracted from hidden-state filenames.

    Layout convention: `<hidden_states_dir>/<model_id>/<case_id>.safetensors`.
    Path E hidden-state coverage is per-model identical (same 30 cases),
    so we use any one model's case set.
    """
    if not hidden_states_dir.exists():
        return None, 0
    case_ids: set[str] = set()
    for model_dir in hidden_states_dir.iterdir():
        if not model_dir.is_dir():
            continue
        for f in model_dir.glob("*.safetensors"):
            case_ids.add(f.stem)
        if case_ids:
            break  # Use the first model's set; subset is supposed to be identical
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
    `docs/DECISION_20260429_llama_addition.md` §2.6."""
    return {
        # E_extract reserve thresholds (R5A_FROZEN_SHORTLIST §4)
        "e_extract_main_text_promotion_n_p_predict": n_p_predict,
        "e_extract_main_text_threshold": _one_third_minimum(n_p_predict),
        "e_extract_confirmatory_promotion_n_p_predict": n_p_predict,
        "e_extract_confirmatory_threshold": _strict_majority(n_p_predict),
        # WS6 mechanistic discriminative analysis (now unconditional, but
        # the per-fleet K is still recorded so analysis can cite it.)
        "ws6_mechanistic_n_white_box": n_p_logprob,
        "ws6_mechanistic_threshold": _strict_majority(n_p_logprob),
        # Behavioral E_FO / E_NoOp gate condition 3 has been REMOVED
        # (gate_removal §2.1). Recorded here as informational so future
        # reanalysis can compare against the gate that *would* have
        # applied if it were still in force.
        "e_fo_e_noop_informational_n_p_predict": n_p_predict,
        "e_fo_e_noop_informational_threshold": _strict_majority(n_p_predict),
    }


def _model_fingerprints(fleet) -> dict[str, dict[str, str]]:
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


def main() -> int:
    args = parse_args()
    fleet = load_fleet(args.fleet)
    runtime = load_runtime(args.runtime)

    placeholders: list[str] = []
    for mid, cfg in fleet.models.items():
        if cfg.is_white_box():
            if cfg.tokenizer_sha in {None, "<TBD>"}:
                placeholders.append(f"{mid}.tokenizer_sha")
            if cfg.hf_commit_sha in {None, "<TBD>"}:
                placeholders.append(f"{mid}.hf_commit_sha")
        if cfg.access.value == "black_box":
            if cfg.api_model_name in {None, "<TBD>"}:
                placeholders.append(f"{mid}.api_model_name")
    if placeholders and not args.allow_tbd:
        raise SystemExit(
            "fleet still carries `<TBD>` placeholders for: "
            + ", ".join(placeholders)
            + ". Run scripts/ws1_pin_fleet.py before finalizing the manifest, "
            "or pass --allow-tbd for non-confirmatory runs."
        )

    article_manifest_path = Path(args.article_manifest)
    article_manifest_hash = _sha256_file(article_manifest_path)

    perturbation_manifest_hash: str | None = None
    if args.perturbation_manifest:
        perturbation_manifest_hash = _sha256_file(Path(args.perturbation_manifest))

    audit_manifest_hash: str | None = None
    if args.audit_manifest:
        audit_manifest_hash = _sha256_file(Path(args.audit_manifest))

    cutoff_observed: dict[str, Date | None] = {}
    if args.cutoff_observed:
        cutoff_observed, lines = _read_cutoff_observed(Path(args.cutoff_observed))
        print("cutoff_observed loaded:")
        for ln in lines:
            print(ln)

    cutoff_date_yaml = {mid: cfg.cutoff_date for mid, cfg in fleet.models.items()}
    quant_scheme = {
        mid: (cfg.quant_scheme or "")
        for mid, cfg in fleet.models.items()
        if cfg.quant_scheme is not None or cfg.is_white_box()
    }

    pcsg_hash = fleet.pcsg_pair_registry_hash()

    hs_hash, hs_n = (None, 0)
    if args.hidden_states_dir:
        hs_hash, hs_n = _hidden_state_subset_hash(Path(args.hidden_states_dir))
        print(
            f"hidden_state_subset: {hs_n} cases, hash="
            + (hs_hash[:12] + "..." if hs_hash else "<none>")
        )

    n_p_predict = len(fleet.p_predict_eligible_ids())
    n_p_logprob = len(fleet.p_logprob_eligible_ids())
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

    manifest = RunManifest(
        run_id=args.run_id or uuid.uuid4().hex,
        created_at=datetime.now(timezone.utc),
        git_commit_sha=_git_commit_sha(),
        fleet_config_hash=fleet.raw_yaml_sha256,
        runtime_config_hash=runtime.raw_yaml_sha256,
        sampling_config_hash=article_manifest_hash,
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
        cutoff_observed=cutoff_observed,
        cutoff_date_yaml=cutoff_date_yaml,
        quant_scheme=quant_scheme,
        pcsg_pair_registry_hash=pcsg_hash,
        hidden_state_subset_hash=hs_hash,
        quality_gate_thresholds=quality_gate_thresholds,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = manifest.model_dump(mode="json")
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    print(f"\nwrote {out_path}")
    print(f"  fleet_version          = {fleet.fleet_version}")
    print(f"  fleet_config_hash      = {fleet.raw_yaml_sha256[:12]}...")
    print(f"  pcsg_pair_registry_hash= {pcsg_hash[:12]}...")
    print(f"  n_p_predict            = {n_p_predict}")
    print(f"  n_p_logprob            = {n_p_logprob}")
    print(f"  cutoff_observed (n_ok) = "
          f"{sum(1 for v in cutoff_observed.values() if v is not None)}"
          f"/{len(cutoff_observed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

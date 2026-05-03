"""WS1 fleet provenance pinner.

Per Tier-0 #2 (`refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/SYNTHESIS.md`)
+ plan §10.1: confirmatory runs MUST NOT carry `<TBD>` placeholders for
`tokenizer_sha` or `hf_commit_sha`. Run this script after
`huggingface-cli download` finishes for each white-box model on the
cloud instance; it discovers actual SHAs from the HF cache layout and
writes them back into `config/fleet/r5a_fleet.yaml`.

Discovery sources (precedence: explicit overrides > HF cache > leave
as-is):

  1. `--pin-json PATH` — JSON map `{model_id: {hf_commit_sha,
     tokenizer_sha, [revision]}}` for cases where auto-discovery fails
     (e.g., no HF cache available because models are pre-baked into the
     Docker image). Unknown model_ids in the JSON are rejected so a
     typo cannot silently no-op a confirmatory pinning run.

  2. `--hf-cache DIR` — HuggingFace hub cache root (default precedence:
     `$HF_HUB_CACHE` env var, then `$HF_HOME/hub`, then
     `~/.cache/huggingface/hub`). Each model's snapshot is at
     `models--<owner>--<repo>/snapshots/<sha>/`. The tokenizer SHA is
     the SHA-256 of `tokenizer.json` byte content as resolved at load
     time (DECISIONS.md decision #4). NOTE this matches HF's blob-store
     filename ONLY for LFS-tracked tokenizers; non-LFS tokenizers are
     stored under their git-blob SHA1 in the HF cache. Do NOT use
     `tokenizer_sha` as a cache lookup key.

When the HF cache contains multiple snapshots for one repo (typical
after retried downloads on AutoDL bring-up), the pinner refuses to
silently pick the newest mtime — the operator MUST disambiguate via
`--pin-json` `revision` field so the pinned `hf_commit_sha` is the one
that was actually loaded.

The script is purely textual on the YAML file: it walks the model
section line-by-line, locates `<TBD>` values for the chosen model, and
replaces them in place. This preserves the file's leading comments and
PCSG pair registry (which is the SHA-256 input for
`pcsg_pair_registry_hash` so a careless round-trip would silently
invalidate prior RunManifests). Before any fleet write, an existing
pinning log must parse as a JSON array; a corrupt or non-array log
raises, and the operator must reconcile it before retry. The fleet YAML
and pinning log are both replaced atomically via `os.replace`.

Usage:

    python scripts/ws1_pin_fleet.py \\
        --fleet config/fleet/r5a_fleet.yaml \\
        --hf-cache /root/.cache/huggingface/hub \\
        --vllm-image-digest sha256:deadbeef... \\
        --bump-version r5a-v2.1-2026-04-29.pinned-1

    # dry run
    python scripts/ws1_pin_fleet.py --fleet config/fleet/r5a_fleet.yaml --check

The `--vllm-image-digest` value is NOT written into the fleet YAML
(it's a per-run, not per-model, field; recorded in RunManifest by
`scripts/ws1_finalize_run_manifest.py`). It is required for non-`--check`
runs and must match the regex `sha256:<64-hex>`; recorded into
`data/pilot/.fleet_pinning_log.json`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.r5a.fleet import ModelConfig, load_fleet  # noqa: E402
from src.r5a.io_utils import atomic_write_json, atomic_write_text  # noqa: E402


PLACEHOLDER = "<TBD>"
VLLM_IMAGE_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WS1 fleet provenance pinner")
    p.add_argument(
        "--fleet",
        default="config/fleet/r5a_fleet.yaml",
        help="fleet YAML path (edited in place unless --output is set)",
    )
    p.add_argument(
        "--output",
        default=None,
        help="output YAML path; default = --fleet (in place)",
    )
    p.add_argument(
        "--hf-cache",
        default=None,
        help=(
            "HuggingFace hub cache root; default = "
            "$HF_HUB_CACHE, then $HF_HOME/hub, then ~/.cache/huggingface/hub"
        ),
    )
    p.add_argument(
        "--pin-json",
        default=None,
        help=(
            "JSON file with explicit per-model overrides; unknown model_ids "
            "are rejected with a non-zero exit"
        ),
    )
    p.add_argument(
        "--vllm-image-digest",
        required=False,
        default=None,
        help=(
            "Docker image digest used during pinning; required for non-check "
            "runs (must match sha256:<64-hex>); recorded in pinning log"
        ),
    )
    p.add_argument(
        "--bump-version",
        default=None,
        help="new fleet_version string; defaults to <current>+pinned-<UTC>",
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="dry run; report what would change without writing",
    )
    p.add_argument(
        "--log-path",
        default="data/pilot/.fleet_pinning_log.json",
        help="JSON log file recording each pinning run",
    )
    return p.parse_args()


def _sha256_file_content(content: bytes) -> str:
    """SHA-256 of `tokenizer.json` byte content as resolved at load time.

    Matches HF cache `blobs/<hash>` filename for LFS-tracked tokenizers
    but NOT for git-tracked ones (HF uses git-blob SHA1 for non-LFS).
    Do NOT use this value as a cache lookup key.
    """
    return hashlib.sha256(content).hexdigest()


def _default_hf_cache() -> Path | None:
    """Resolve the HF cache directory from env and standard locations.

    Per `MED-4` (Tier-R2-0 PR1 step 11): when ``HF_HUB_CACHE`` is
    explicitly set but the path does not exist, fail loudly rather
    than silently falling through to the next candidate (which would
    lead to a cache-miss "no snapshot" diagnostic far from the real
    misconfiguration). Only the unset case falls back.
    """
    env_cache = os.environ.get("HF_HUB_CACHE")
    if env_cache is not None:
        candidate = Path(env_cache)
        if not candidate.exists():
            raise SystemExit(
                f"HF_HUB_CACHE={env_cache!r} is set but the directory does "
                "not exist; unset the env var or fix the path."
            )
        return candidate
    hf_home = os.environ.get("HF_HOME")
    if hf_home:
        candidate = Path(hf_home) / "hub"
        if candidate.exists():
            return candidate
    candidate = Path.home() / ".cache" / "huggingface" / "hub"
    if candidate.exists():
        return candidate
    return None


def _hf_cache_repo_dir(cache: Path, hf_repo: str) -> Path:
    """`Qwen/Qwen2.5-7B-Instruct-AWQ` -> `cache/models--Qwen--Qwen2.5-7B-Instruct-AWQ`."""
    name = "models--" + hf_repo.replace("/", "--")
    return cache / name


def _pick_snapshot(
    repo_dir: Path,
    model_id: str,
    *,
    requested_revision: str | None,
) -> Path | None:
    """Return the snapshot directory for `model_id`.

    Refuses to silently choose between multiple snapshots — when the HF
    cache has more than one (typical after retried `huggingface-cli
    download` on AutoDL bring-up), the operator MUST pass the desired
    `hf_commit_sha` via `--pin-json` `revision` field. This eliminates
    the "wrong-snapshot-pinned" hazard (R2-C5 #2 / Lens A major #5).
    """
    snaps = repo_dir / "snapshots"
    if not snaps.exists():
        return None
    candidates = [p for p in snaps.iterdir() if p.is_dir()]
    if not candidates:
        return None

    if requested_revision is not None:
        target = snaps / requested_revision
        if not target.exists():
            raise SystemExit(
                f"{model_id}: --pin-json revision {requested_revision!r} "
                f"not found under {snaps}; have {[c.name for c in candidates]}"
            )
        return target

    if len(candidates) == 1:
        return candidates[0]

    raise SystemExit(
        f"{model_id}: HF cache has multiple snapshots {[c.name for c in candidates]} "
        f"under {snaps}; refusing to silently pick newest. Pass "
        f"--pin-json with `\"{model_id}\": {{\"revision\": \"<commit_sha>\"}}` "
        "to disambiguate."
    )


def _discover_from_cache(
    cfg: ModelConfig,
    cache: Path,
    *,
    requested_revision: str | None,
) -> tuple[str | None, str | None, str]:
    """Return (hf_commit_sha, tokenizer_sha, note)."""
    if not cfg.hf_repo:
        return None, None, "no hf_repo in fleet entry"
    repo_dir = _hf_cache_repo_dir(cache, cfg.hf_repo)
    if not repo_dir.exists():
        return None, None, f"cache miss: {repo_dir} not found"
    snapshot = _pick_snapshot(
        repo_dir, cfg.model_id, requested_revision=requested_revision
    )
    if snapshot is None:
        return None, None, f"no snapshot under {repo_dir}/snapshots"
    commit_sha = snapshot.name
    tok_path = snapshot / "tokenizer.json"
    if not tok_path.exists():
        return commit_sha, None, f"snapshot at {snapshot} has no tokenizer.json"
    real = tok_path.resolve()
    try:
        content = real.read_bytes()
    except OSError as exc:  # pragma: no cover
        return commit_sha, None, f"failed reading {real}: {exc!r}"
    # tokenizer.json content-validity check (#6 D / Tier-R2-0 PR1 step
    # 12): a corrupt or partial download is silently SHA-hashable but
    # not loadable; rejecting non-JSON here surfaces the error at pin
    # time rather than at first vLLM launch.
    try:
        json.loads(content)
    except json.JSONDecodeError as exc:
        return (
            commit_sha,
            None,
            f"tokenizer.json at {real} is not valid JSON: {exc!s}",
        )
    tok_sha = _sha256_file_content(content)
    return commit_sha, tok_sha, "ok"


# ----------------------------------------------------------------------
# YAML in-place patcher (preserves comments + PCSG-pair byte order)
# ----------------------------------------------------------------------


_MODEL_HEADER_RE = re.compile(r"^  ([A-Za-z0-9_.\-]+):\s*(?:#.*)?$")


def _patch_model_block(
    yaml_text: str,
    model_id: str,
    *,
    hf_commit_sha: str | None,
    tokenizer_sha: str | None,
) -> tuple[str, list[str]]:
    """Replace `<TBD>` for `tokenizer_sha` and `hf_commit_sha` inside the
    block of `model_id`. Returns the new text and a list of human-
    readable change descriptions.

    Implementation: find the `model_id:` header at indent 2, then walk
    forward until the next 2-space-indent key (next model or pcsg_pairs
    section). Within that span, replace the targeted lines. Both the
    raw `<TBD>` placeholder and a quoted `"<TBD>"` are accepted as
    "needs pinning" so YAML files that quoted the placeholder for
    portability still get patched on first run (R2-C5 #4).
    """
    lines = yaml_text.splitlines(keepends=True)
    n = len(lines)
    start: int | None = None
    end: int = n
    for i, line in enumerate(lines):
        if line.startswith("  ") and not line.startswith("    "):
            m = _MODEL_HEADER_RE.match(line.rstrip("\n"))
            if m and start is None and m.group(1) == model_id:
                start = i + 1
                continue
            if start is not None and not line.startswith("    "):
                if line.strip() and not line.lstrip().startswith("#"):
                    end = i
                    break
        if start is not None and not line.startswith("  "):
            if line.strip() and not line.lstrip().startswith("#"):
                end = i
                break
    if start is None:
        return yaml_text, [f"{model_id}: not found in YAML; skipped"]

    changes: list[str] = []
    field_re = lambda key: re.compile(  # noqa: E731
        rf"^(    {re.escape(key)}:\s*)(\S+.*?)(\s*(?:#.*)?)$"
    )
    field_pairs = (
        ("tokenizer_sha", tokenizer_sha),
        ("hf_commit_sha", hf_commit_sha),
    )
    quoted_placeholder = f'"{PLACEHOLDER}"'
    for j in range(start, end):
        line = lines[j].rstrip("\n")
        for key, new_value in field_pairs:
            if new_value is None:
                continue
            mm = field_re(key).match(line)
            if not mm:
                continue
            raw_current = mm.group(2).strip()
            # Strip surrounding quotes before equality check (LOW-1).
            # Without this an idempotent rerun against a YAML that
            # quoted the SHA (e.g. `"abc..."`) reports a misleading
            # SKIP "already pinned with conflicting" instead of a no-op.
            if (
                len(raw_current) >= 2
                and raw_current[0] == raw_current[-1]
                and raw_current[0] in ('"', "'")
            ):
                current = raw_current[1:-1]
            else:
                current = raw_current
            if (
                current == PLACEHOLDER
                or current == new_value
            ):
                if current == new_value:
                    continue
                replacement = f'{mm.group(1)}"{new_value}"{mm.group(3)}'
                lines[j] = replacement + ("\n" if lines[j].endswith("\n") else "")
                changes.append(f"{model_id}.{key}: {PLACEHOLDER} -> {new_value}")
            elif raw_current == quoted_placeholder:
                # Defensive: pre-strip equality already covers this, but
                # keep an explicit branch for clarity.
                replacement = f'{mm.group(1)}"{new_value}"{mm.group(3)}'
                lines[j] = replacement + ("\n" if lines[j].endswith("\n") else "")
                changes.append(f"{model_id}.{key}: {PLACEHOLDER} -> {new_value}")
            else:
                changes.append(
                    f"{model_id}.{key}: SKIP (already pinned to {current!r}; "
                    f"would have set {new_value!r})"
                )

    return "".join(lines), changes


def _bump_fleet_version(yaml_text: str, new_version: str) -> tuple[str, str | None]:
    pat = re.compile(r'^(fleet_version:\s*)(["\'])(.*?)\2(\s*(?:#.*)?)$', re.MULTILINE)
    m = pat.search(yaml_text)
    if not m:
        return yaml_text, None
    old = m.group(3)
    new_text = pat.sub(rf'\g<1>"{new_version}"\g<4>', yaml_text, count=1)
    return new_text, old


def main() -> int:
    args = parse_args()

    if not args.check:
        if not args.vllm_image_digest:
            raise SystemExit(
                "--vllm-image-digest is required for non-check pinning runs"
            )
        if not VLLM_IMAGE_DIGEST_RE.match(args.vllm_image_digest):
            raise SystemExit(
                f"--vllm-image-digest must match sha256:<64-hex>; "
                f"got {args.vllm_image_digest!r}"
            )

    fleet_path = Path(args.fleet)
    if not fleet_path.exists():
        raise SystemExit(f"fleet YAML not found: {fleet_path}")
    fleet = load_fleet(fleet_path)
    yaml_text = fleet_path.read_text(encoding="utf-8")

    overrides: dict[str, dict[str, str]] = {}
    if args.pin_json:
        overrides = json.loads(Path(args.pin_json).read_text(encoding="utf-8"))
        unknown = sorted(set(overrides) - set(fleet.models))
        if unknown:
            raise SystemExit(
                f"--pin-json contains model IDs not in fleet: {unknown}; "
                "check config/fleet/r5a_fleet.yaml `models:` keys"
            )

    cache: Path | None = None
    if args.hf_cache:
        cache = Path(args.hf_cache)
        if not cache.exists():
            raise SystemExit(f"--hf-cache directory not found: {cache}")
    else:
        cache = _default_hf_cache()

    # Pre-validate the existing pinning log BEFORE any fleet mutation
    # (#5 A / Tier-R2-0 PR1 step 8): a corrupt or wrong-shape log must
    # fail the run so the operator can reconcile it; otherwise the
    # fleet would be silently rewritten while the audit trail breaks.
    log_path = Path(args.log_path)
    prior_log: list = []
    if not args.check and log_path.exists():
        try:
            prior_log = json.loads(log_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SystemExit(
                f"existing pinning log {log_path} is corrupt: {exc!r}; "
                "operator must inspect and either fix or move it aside "
                "before re-running pinner. Fleet file unchanged."
            )
        if not isinstance(prior_log, list):
            raise SystemExit(
                f"existing pinning log {log_path} is not a JSON array; "
                "operator must inspect and either fix or move it aside "
                "before re-running pinner. Fleet file unchanged."
            )

    all_changes: list[str] = []
    pinned_records: dict[str, dict[str, str]] = {}
    skipped_records: dict[str, dict[str, str]] = {}

    for model_id, cfg in fleet.models.items():
        if not cfg.is_white_box() or not cfg.hf_repo:
            continue
        ovr = overrides.get(model_id, {})
        commit_sha = ovr.get("hf_commit_sha")
        tok_sha = ovr.get("tokenizer_sha")
        revision = ovr.get("revision")
        note = "override"
        if (commit_sha is None or tok_sha is None) and cache is not None:
            disc_commit, disc_tok, disc_note = _discover_from_cache(
                cfg, cache, requested_revision=revision
            )
            commit_sha = commit_sha or disc_commit
            tok_sha = tok_sha or disc_tok
            note = "override+cache" if ovr else f"cache:{disc_note}"
        if commit_sha is None and tok_sha is None:
            all_changes.append(f"{model_id}: NO PINNING — no override, no cache hit")
            continue
        yaml_text, changes = _patch_model_block(
            yaml_text,
            model_id,
            hf_commit_sha=commit_sha,
            tokenizer_sha=tok_sha,
        )
        all_changes.extend(changes)
        # Split semantics (MED-5 / Tier-R2-0 PR1 step 10): a model is
        # "pinned" only if the patch actually replaced a `<TBD>`
        # placeholder for at least one field; SKIP'd entries (existing
        # value differs from override and is not a placeholder) go to
        # `models_skipped` so the log does not falsely claim the run
        # changed bytes that it left untouched.
        record = {
            "hf_commit_sha": commit_sha or "",
            "tokenizer_sha": tok_sha or "",
            "source": note,
        }
        replaced = any(
            c.startswith(f"{model_id}.") and "->" in c and "SKIP" not in c
            for c in changes
        )
        skipped = any(
            c.startswith(f"{model_id}.") and "SKIP" in c for c in changes
        )
        if replaced:
            pinned_records[model_id] = record
        if skipped:
            skipped_records[model_id] = record

    new_version: str = fleet.fleet_version
    any_field_changed = any(
        ("->" in c)
        and not c.startswith("fleet_version:")
        and "SKIP" not in c
        for c in all_changes
    )

    if not args.check:
        if args.bump_version:
            new_version = args.bump_version
            yaml_text, old_version = _bump_fleet_version(yaml_text, new_version)
            if old_version is not None:
                all_changes.append(f"fleet_version: {old_version} -> {new_version}")
            else:
                all_changes.append("fleet_version: pattern not matched; not bumped")
        elif any_field_changed:
            now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            new_version = f"{fleet.fleet_version}+pinned-{now}"
            yaml_text, old_version = _bump_fleet_version(yaml_text, new_version)
            if old_version is not None:
                all_changes.append(f"fleet_version: {old_version} -> {new_version}")
            else:
                all_changes.append("fleet_version: pattern not matched; not bumped")
        else:
            all_changes.append("fleet_version: no field changes; not bumped")

    if not args.check:
        from io import StringIO

        import yaml

        try:
            parsed = yaml.safe_load(StringIO(yaml_text))
            from src.r5a.fleet import FleetConfig, _normalize_models

            FleetConfig.model_validate(_normalize_models(parsed))
        except Exception as exc:
            raise SystemExit(
                f"patched YAML failed re-validation: {exc!r}. "
                "Fleet file unchanged."
            )

        out_path = Path(args.output) if args.output else fleet_path
        atomic_write_text(out_path, yaml_text)
        print(f"wrote {out_path}")

    print("changes:")
    for c in all_changes:
        print(f"  {c}")

    if not args.check:
        log_entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "fleet_version_old": fleet.fleet_version,
            "fleet_version_new": new_version,
            "vllm_image_digest": args.vllm_image_digest,
            "models_pinned": pinned_records,
            "models_skipped": skipped_records,
            "changes": all_changes,
        }
        prior_log.append(log_entry)
        atomic_write_json(log_path, prior_log)
        print(f"appended pinning log -> {log_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

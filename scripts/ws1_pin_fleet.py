"""WS1 fleet provenance pinner.

Per Tier-0 #2 (`refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/SYNTHESIS.md`)
+ plan §10.1: confirmatory runs MUST NOT carry `<TBD>` placeholders for
`tokenizer_sha` or `hf_commit_sha`. Run this script after
`huggingface-cli download` finishes for each white-box model on the
cloud instance; it discovers actual SHAs from the HF cache layout and
writes them back into `config/fleet/r5a_fleet.yaml`.

Discovery sources (precedence: explicit overrides > HF cache > leave
as-is):

  1. `--pin-json PATH` — JSON map `{model_id: {hf_commit_sha, tokenizer_sha}}`
     for cases where auto-discovery fails (e.g., no HF cache available
     because models are pre-baked into the Docker image).

  2. `--hf-cache DIR` — HuggingFace hub cache root (defaults to
     `$HF_HOME/hub` or `~/.cache/huggingface/hub`). Each model's
     snapshot is at `models--<owner>--<repo>/snapshots/<sha>/`. The
     tokenizer SHA is computed as the git-blob SHA1 of
     `tokenizer.json` (matches HF's own blob-store filename, but works
     on Windows where the blobs/ symlinks become real files).

The script is purely textual on the YAML file: it walks the model
section line-by-line, locates `<TBD>` values for the chosen model, and
replaces them in place. This preserves the file's leading comments and
PCSG pair registry (which is the SHA-256 input for
`pcsg_pair_registry_hash` so a careless round-trip would silently
invalidate prior RunManifests).

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
`scripts/ws1_finalize_run_manifest.py`). It is required here only to
record alongside the pinning so the operator has a single source of
truth for what was running when SHAs were captured; the value is
echoed into `data/pilot/.fleet_pinning_log.json`.
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


PLACEHOLDER = "<TBD>"


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
            "$HF_HOME/hub or ~/.cache/huggingface/hub"
        ),
    )
    p.add_argument(
        "--pin-json",
        default=None,
        help="JSON file with explicit per-model overrides",
    )
    p.add_argument(
        "--vllm-image-digest",
        required=False,
        default=None,
        help="Docker image digest used during pinning; recorded in pinning log",
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


def _git_blob_sha1(content: bytes) -> str:
    """Compute git's `blob` SHA1: `sha1("blob <size>\\0" + content)`.

    Matches the filename used by the HF hub cache `blobs/` store, which
    is the git-blob SHA1 of each file. Works on Windows even when the
    cache copied the file (no symlinks) because the hash is content-
    addressed.
    """
    h = hashlib.sha1()
    h.update(f"blob {len(content)}\0".encode("ascii"))
    h.update(content)
    return h.hexdigest()


def _default_hf_cache() -> Path | None:
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


def _pick_snapshot(repo_dir: Path) -> Path | None:
    snaps = repo_dir / "snapshots"
    if not snaps.exists():
        return None
    candidates = [p for p in snaps.iterdir() if p.is_dir()]
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _discover_from_cache(
    cfg: ModelConfig, cache: Path
) -> tuple[str | None, str | None, str]:
    """Return (hf_commit_sha, tokenizer_sha, note)."""
    if not cfg.hf_repo:
        return None, None, "no hf_repo in fleet entry"
    repo_dir = _hf_cache_repo_dir(cache, cfg.hf_repo)
    if not repo_dir.exists():
        return None, None, f"cache miss: {repo_dir} not found"
    snapshot = _pick_snapshot(repo_dir)
    if snapshot is None:
        return None, None, f"no snapshot under {repo_dir}/snapshots"
    commit_sha = snapshot.name
    tok_path = snapshot / "tokenizer.json"
    if not tok_path.exists():
        return commit_sha, None, f"snapshot at {snapshot} has no tokenizer.json"
    # Resolve symlink target on Linux; read content directly otherwise
    real = tok_path.resolve()
    try:
        content = real.read_bytes()
    except OSError as exc:  # pragma: no cover
        return commit_sha, None, f"failed reading {real}: {exc!r}"
    tok_sha = _git_blob_sha1(content)
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
    section). Within that span, replace the targeted lines.
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
                # Could be next model header at same indent; stop the block
                if line.strip() and not line.lstrip().startswith("#"):
                    end = i
                    break
        if start is not None and not line.startswith("  "):
            # Top-level key (e.g. `pcsg_pairs:`); end of models section
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
    for j in range(start, end):
        line = lines[j].rstrip("\n")
        for key, new_value in field_pairs:
            if new_value is None:
                continue
            mm = field_re(key).match(line)
            if not mm:
                continue
            current = mm.group(2).strip()
            if current == PLACEHOLDER or current == new_value:
                if current == new_value:
                    continue
                # Quote unconditionally to avoid YAML interpreting hex
                # values as numbers/floats by accident.
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
    fleet_path = Path(args.fleet)
    if not fleet_path.exists():
        raise SystemExit(f"fleet YAML not found: {fleet_path}")
    fleet = load_fleet(fleet_path)
    yaml_text = fleet_path.read_text(encoding="utf-8")

    overrides: dict[str, dict[str, str]] = {}
    if args.pin_json:
        overrides = json.loads(Path(args.pin_json).read_text(encoding="utf-8"))

    cache: Path | None = None
    if args.hf_cache:
        cache = Path(args.hf_cache)
        if not cache.exists():
            raise SystemExit(f"--hf-cache directory not found: {cache}")
    else:
        cache = _default_hf_cache()

    all_changes: list[str] = []
    pinned_records: dict[str, dict[str, str]] = {}

    # Iterate in YAML order; only act on white-box models with hf_repo.
    for model_id, cfg in fleet.models.items():
        if not cfg.is_white_box() or not cfg.hf_repo:
            continue
        ovr = overrides.get(model_id, {})
        commit_sha = ovr.get("hf_commit_sha")
        tok_sha = ovr.get("tokenizer_sha")
        note = "override"
        if (commit_sha is None or tok_sha is None) and cache is not None:
            disc_commit, disc_tok, disc_note = _discover_from_cache(cfg, cache)
            commit_sha = commit_sha or disc_commit
            tok_sha = tok_sha or disc_tok
            note = f"override+cache" if ovr else f"cache:{disc_note}"
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
        pinned_records[model_id] = {
            "hf_commit_sha": commit_sha or "",
            "tokenizer_sha": tok_sha or "",
            "source": note,
        }

    # Bump fleet_version unless explicitly told not to.
    new_version: str = fleet.fleet_version  # default for --check / log
    if not args.check:
        if args.bump_version:
            new_version = args.bump_version
        else:
            now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            new_version = f"{fleet.fleet_version}+pinned-{now}"
        yaml_text, old_version = _bump_fleet_version(yaml_text, new_version)
        if old_version is not None:
            all_changes.append(f"fleet_version: {old_version} -> {new_version}")
        else:
            all_changes.append("fleet_version: pattern not matched; not bumped")

    # Re-validate by parsing the patched YAML through pydantic before
    # writing — refuses to commit a malformed result.
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
        out_path.write_text(yaml_text, encoding="utf-8")
        print(f"wrote {out_path}")

    print("changes:")
    for c in all_changes:
        print(f"  {c}")

    if not args.check:
        log_path = Path(args.log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "fleet_version_old": fleet.fleet_version,
            "fleet_version_new": new_version,
            "vllm_image_digest": args.vllm_image_digest,
            "models_pinned": pinned_records,
            "changes": all_changes,
        }
        prior: list = []
        if log_path.exists():
            try:
                prior = json.loads(log_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                prior = []
        prior.append(log_entry)
        log_path.write_text(
            json.dumps(prior, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"appended pinning log -> {log_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

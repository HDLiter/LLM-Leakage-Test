"""Capture non-Docker vLLM runtime provenance for WS1 AutoDL runs.

AutoDL container instances are themselves Docker-isolated environments and
do not support nested Docker. For that deployment path, WS1 records a
`sha256:<64-hex>` digest over a canonical JSON payload describing the host
runtime (Python, CUDA/GPU, vLLM/Torch package versions, pip freeze, selected
non-secret environment variables, and repo commit). The existing
`vllm_image_digest` trace/manifest field stores this runtime digest.

The timestamp is written beside the payload for operator auditability, but it
is intentionally excluded from the digest so rerunning the capture against an
unchanged environment produces the same digest.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SECRET_KEY_PARTS = ("TOKEN", "KEY", "SECRET", "PASSWORD", "CREDENTIAL")
SELECTED_ENV_KEYS = (
    "CUDA_VISIBLE_DEVICES",
    "DATA_ROOT",
    "HF_ENDPOINT",
    "HF_HOME",
    "HF_HUB_CACHE",
    "NO_PROXY",
    "no_proxy",
    "VLLM_PIP_SPEC",
    "WS1_SKIP_VLLM_INSTALL",
)
PACKAGE_NAMES = (
    "vllm",
    "torch",
    "transformers",
    "huggingface-hub",
    "pydantic",
    "httpx",
    "pyarrow",
    "pandas",
    "numpy",
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Capture WS1 non-Docker vLLM runtime provenance"
    )
    p.add_argument(
        "--output",
        required=True,
        help="JSON file to write, e.g. /data/vllm_runtime_provenance.json",
    )
    p.add_argument(
        "--sha-output",
        default=None,
        help=(
            "optional text file for the sha256:<64-hex> digest; defaults "
            "to not writing a separate digest file"
        ),
    )
    p.add_argument(
        "--repo-root",
        default=None,
        help="repo root used for git commit provenance; default = cwd",
    )
    return p.parse_args()


def _run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 30) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        return {
            "cmd": cmd,
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
        }
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": _redact_text(proc.stderr.strip()),
    }


def _redact_text(value: str) -> str:
    # Keep this conservative: token-like strings must not leak into
    # provenance JSON copied back into the repo.
    import re

    return re.sub(r"hf_[A-Za-z0-9]{20,}", "[HF_TOKEN_REDACTED]", value)


def _redact_env(env: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key in SELECTED_ENV_KEYS:
        if key not in env:
            continue
        if any(part in key.upper() for part in SECRET_KEY_PARTS):
            out[key] = "[REDACTED]"
        else:
            out[key] = _redact_text(env[key])
    out["HF_TOKEN_present"] = str(bool(env.get("HF_TOKEN")))
    return out


def _package_versions() -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for name in PACKAGE_NAMES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def _pip_freeze() -> list[str]:
    result = _run([sys.executable, "-m", "pip", "freeze"], timeout=120)
    if result["returncode"] != 0:
        return []
    return sorted(
        _redact_text(line.strip())
        for line in result["stdout"].splitlines()
        if line.strip()
    )


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return None


def _canonical_digest(payload: dict[str, Any]) -> str:
    raw = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def build_runtime_payload(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    git_rev = _run(["git", "rev-parse", "HEAD"], cwd=repo_root)
    git_status = _run(["git", "status", "--short"], cwd=repo_root)
    data_readlink = _run(["readlink", "-f", "/data"])
    nvidia_query = _run(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader",
        ]
    )
    vllm_version = _run([sys.executable, "-m", "vllm.entrypoints.openai.api_server", "--version"])

    return {
        "schema_version": "ws1-runtime-provenance-v1",
        "runtime_kind": "autodl_container_non_docker",
        "python": {
            "executable": sys.executable,
            "version": sys.version,
            "implementation": platform.python_implementation(),
        },
        "platform": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "os_release": _read_text(Path("/etc/os-release")),
        },
        "repo": {
            "root": str(repo_root),
            "git_commit_sha": git_rev["stdout"] if git_rev["returncode"] == 0 else None,
            "git_status_short": git_status["stdout"] if git_status["returncode"] == 0 else None,
        },
        "gpu": {
            "nvidia_smi_query": nvidia_query,
        },
        "packages": {
            "versions": _package_versions(),
            "pip_freeze": _pip_freeze(),
            "vllm_version_command": vllm_version,
        },
        "paths": {
            "data_root_resolved": data_readlink["stdout"] if data_readlink["returncode"] == 0 else None,
        },
        "environment": _redact_env(os.environ),
    }


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()
    runtime = build_runtime_payload(repo_root)
    digest = _canonical_digest(runtime)
    payload = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime_digest": digest,
        "runtime": runtime,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if args.sha_output:
        sha_path = Path(args.sha_output)
        sha_path.parent.mkdir(parents=True, exist_ok=True)
        sha_path.write_text(digest + "\n", encoding="utf-8")
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

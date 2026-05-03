"""Shared filesystem helpers for R5A scripts.

`atomic_write_text` and `atomic_write_json` write a file via a sibling
temp file followed by ``os.replace``, so a process crash mid-write
cannot leave a half-written file on disk. The temp file lives in the
same directory as the target so ``os.replace`` is a same-filesystem
rename across both POSIX and Windows.

Used by:
    scripts/ws1_pin_fleet.py        (fleet YAML write, pinning log)
    scripts/ws1_finalize_run_manifest.py  (RunManifest JSON write)
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def atomic_write_text(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` atomically via tempfile + os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_str = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    tmp = Path(tmp_str)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise


def atomic_write_json(path: Path, payload: Any) -> None:
    """JSON-serialize ``payload`` and write atomically to ``path``."""
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    atomic_write_text(path, text)

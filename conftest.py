"""Pytest collection-time hook: put repo root on `sys.path` so tests
can `from src.r5a.* import ...` without setting PYTHONPATH externally.

This avoids touching tests/ layout or adding a pyproject.toml just for
test discovery. Mirrors the smoke-script pattern in scripts/.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

"""LLM Leakage Detection & Mitigation Test Bench."""

from .masking import extract_json_robust

DEFAULT_CONCURRENCY: int = 50


def set_seed(seed: int = 42) -> None:
    import random
    import numpy as np
    random.seed(seed)
    np.random.seed(seed)

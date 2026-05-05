"""Tests for WS1 non-Docker runtime provenance capture."""

from __future__ import annotations

from scripts import ws1_capture_runtime_provenance as prov


def test_runtime_digest_is_canonical_and_stable():
    payload_a = {"b": [2, 1], "a": {"x": "y"}}
    payload_b = {"a": {"x": "y"}, "b": [2, 1]}
    digest = prov._canonical_digest(payload_a)
    assert digest == prov._canonical_digest(payload_b)
    assert digest.startswith("sha256:")
    assert len(digest) == len("sha256:") + 64


def test_runtime_provenance_env_redacts_secret_values():
    env = {
        "HF_TOKEN": "hf_" + "a" * 40,
        "HF_ENDPOINT": "https://hf-mirror.com",
        "NO_PROXY": "localhost,127.0.0.1",
    }
    out = prov._redact_env(env)
    assert out["HF_TOKEN_present"] == "True"
    assert out["HF_ENDPOINT"] == "https://hf-mirror.com"
    assert "HF_TOKEN" not in out
    assert "hf_" + "a" * 40 not in repr(out)


def test_redact_text_removes_hf_token_shape():
    token = "hf_" + "b" * 40
    assert token not in prov._redact_text(f"Bearer {token}")
    assert "[HF_TOKEN_REDACTED]" in prov._redact_text(f"Bearer {token}")

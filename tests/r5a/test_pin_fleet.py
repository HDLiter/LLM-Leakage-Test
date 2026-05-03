"""Unit tests for scripts/ws1_pin_fleet.py.

Per R2 Tier-0 Block F.34. Covers Block B hardening: SHA-256 file content
hash, pin-json unknown rejection, vllm-image-digest format gate,
quoted-`<TBD>` patching, idempotent fleet_version, multi-snapshot
rejection, corrupt-log refusal.

All tests use `tmp_path` for I/O and call `main()` after monkeypatching
`sys.argv` (avoids subprocess flakiness on Windows).
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import the script as a module.
pin_fleet = importlib.import_module("scripts.ws1_pin_fleet")


MINIMAL_FLEET_YAML = """\
fleet_version: "test-v1"

models:

  qwen2.5-7b:
    family: qwen
    access: white_box
    provider: vllm
    cutoff_date: 2023-10-31
    cutoff_source: vendor_stated
    tokenizer_family: qwen
    hf_repo: Qwen/Qwen2.5-7B-Instruct-AWQ
    quant_scheme: AWQ-INT4
    tokenizer_sha: <TBD>
    hf_commit_sha: <TBD>
    p_logprob:
      thinking_control: default_off
      prompt_overlay_policy: none
      route_lock_required: hf_commit_sha
      echo_supported: true
    p_predict:
      thinking_control: default_deployed
      prompt_overlay_policy: baseline_only

  deepseek-v3:
    family: deepseek
    access: black_box
    provider: deepseek
    cutoff_date: 2024-07-31
    cutoff_source: community_paraphrase
    api_model_name: deepseek-chat
    p_predict:
      thinking_control: default_deployed
      prompt_overlay_policy: baseline_only
      route_lock_required: provider_model_id

pcsg_pairs: []
"""


def _write_minimal_fleet(tmp_path: Path) -> Path:
    p = tmp_path / "fleet.yaml"
    p.write_text(MINIMAL_FLEET_YAML, encoding="utf-8")
    return p


def _make_hf_cache(tmp_path: Path, hf_repo: str, snapshots: dict[str, bytes]) -> Path:
    """Build a minimal `models--<owner>--<repo>/snapshots/<sha>/tokenizer.json`
    layout. `snapshots` maps commit_sha -> tokenizer.json bytes."""
    cache = tmp_path / "hf_cache"
    repo_dir = cache / ("models--" + hf_repo.replace("/", "--"))
    snaps = repo_dir / "snapshots"
    snaps.mkdir(parents=True, exist_ok=True)
    for sha, content in snapshots.items():
        snap = snaps / sha
        snap.mkdir()
        (snap / "tokenizer.json").write_bytes(content)
    return cache


def _run_pin_fleet_cli(monkeypatch, *args: str) -> None:
    monkeypatch.setattr(sys, "argv", ["ws1_pin_fleet.py", *args])
    pin_fleet.main()


def _digest(suffix: str = "0") -> str:
    return "sha256:" + suffix * 64


def test_patch_model_block_pins_only_target_model():
    new_text, changes = pin_fleet._patch_model_block(
        MINIMAL_FLEET_YAML,
        "qwen2.5-7b",
        hf_commit_sha="a" * 40,
        tokenizer_sha="b" * 64,
    )
    assert any("qwen2.5-7b.tokenizer_sha" in c for c in changes)
    assert any("qwen2.5-7b.hf_commit_sha" in c for c in changes)
    # deepseek block must be untouched.
    assert "deepseek-chat" in new_text
    assert "deepseek-v3" in new_text
    # placeholder must be replaced inside the qwen block.
    assert "tokenizer_sha: <TBD>" not in new_text


def test_pin_json_unknown_model_is_rejected(tmp_path: Path, monkeypatch):
    fleet_path = _write_minimal_fleet(tmp_path)
    pin_json = tmp_path / "pin.json"
    pin_json.write_text(
        json.dumps({"not-in-fleet": {"hf_commit_sha": "x" * 40}}),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit) as exc:
        _run_pin_fleet_cli(
            monkeypatch,
            "--fleet", str(fleet_path),
            "--pin-json", str(pin_json),
            "--vllm-image-digest", _digest("a"),
            "--log-path", str(tmp_path / "pin_log.json"),
        )
    assert "not-in-fleet" in str(exc.value)


def test_pin_fleet_check_mode_does_not_write(tmp_path: Path, monkeypatch):
    fleet_path = _write_minimal_fleet(tmp_path)
    before = fleet_path.read_bytes()
    _run_pin_fleet_cli(
        monkeypatch,
        "--fleet", str(fleet_path),
        "--check",
    )
    after = fleet_path.read_bytes()
    assert before == after


def test_pin_fleet_validates_hash_invariant_and_idempotency(tmp_path: Path, monkeypatch):
    fleet_path = _write_minimal_fleet(tmp_path)
    pin_json = tmp_path / "pin.json"
    pin_json.write_text(
        json.dumps(
            {
                "qwen2.5-7b": {
                    "hf_commit_sha": "a" * 40,
                    "tokenizer_sha": "b" * 64,
                }
            }
        ),
        encoding="utf-8",
    )
    log_path = tmp_path / "pin_log.json"
    _run_pin_fleet_cli(
        monkeypatch,
        "--fleet", str(fleet_path),
        "--pin-json", str(pin_json),
        "--vllm-image-digest", _digest("c"),
        "--bump-version", "test-v1.pinned-1",
        "--log-path", str(log_path),
    )
    first = fleet_path.read_bytes()
    _run_pin_fleet_cli(
        monkeypatch,
        "--fleet", str(fleet_path),
        "--pin-json", str(pin_json),
        "--vllm-image-digest", _digest("c"),
        "--bump-version", "test-v1.pinned-1",
        "--log-path", str(log_path),
    )
    second = fleet_path.read_bytes()
    assert first == second, "second pin run must be byte-identical to first"


def test_pin_fleet_quoted_tbd_is_patched():
    yaml_with_quoted = MINIMAL_FLEET_YAML.replace(
        "tokenizer_sha: <TBD>", 'tokenizer_sha: "<TBD>"'
    )
    new_text, changes = pin_fleet._patch_model_block(
        yaml_with_quoted,
        "qwen2.5-7b",
        hf_commit_sha=None,
        tokenizer_sha="b" * 64,
    )
    assert any("qwen2.5-7b.tokenizer_sha" in c and "->" in c for c in changes)
    assert '"<TBD>"' not in new_text
    assert "b" * 64 in new_text


def test_pin_fleet_sha256_file_content():
    # Anchor: SHA-256 of b"abc" is well-known.
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert pin_fleet._sha256_file_content(b"abc") == expected


@pytest.mark.parametrize(
    "digest, ok",
    [
        (None, False),
        ("<TBD>", False),
        ("sha256:short", False),
        ("sha256:" + "f" * 64, True),
    ],
)
def test_pin_fleet_image_digest_validation(
    tmp_path: Path, monkeypatch, digest, ok
):
    fleet_path = _write_minimal_fleet(tmp_path)
    args: list[str] = ["--fleet", str(fleet_path), "--log-path", str(tmp_path / "log.json")]
    if digest is not None:
        args.extend(["--vllm-image-digest", digest])
    if ok:
        # Pinning should succeed without raising on the digest check.
        _run_pin_fleet_cli(monkeypatch, *args)
    else:
        with pytest.raises(SystemExit):
            _run_pin_fleet_cli(monkeypatch, *args)


def test_pin_fleet_multi_snapshot_rejected_without_revision(
    tmp_path: Path, monkeypatch
):
    fleet_path = _write_minimal_fleet(tmp_path)
    cache = _make_hf_cache(
        tmp_path,
        "Qwen/Qwen2.5-7B-Instruct-AWQ",
        {
            "a" * 40: b'{"version": 1}',
            "b" * 40: b'{"version": 2}',
        },
    )
    with pytest.raises(SystemExit) as exc:
        _run_pin_fleet_cli(
            monkeypatch,
            "--fleet", str(fleet_path),
            "--hf-cache", str(cache),
            "--vllm-image-digest", _digest("d"),
            "--log-path", str(tmp_path / "pin_log.json"),
        )
    msg = str(exc.value)
    assert "qwen2.5-7b" in msg
    assert "multiple snapshots" in msg


def test_pin_fleet_corrupt_log_rejected(tmp_path: Path, monkeypatch):
    fleet_path = _write_minimal_fleet(tmp_path)
    log_path = tmp_path / "pin_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("{not valid json", encoding="utf-8")
    pin_json = tmp_path / "pin.json"
    pin_json.write_text(
        json.dumps(
            {
                "qwen2.5-7b": {
                    "hf_commit_sha": "a" * 40,
                    "tokenizer_sha": "b" * 64,
                }
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit) as exc:
        _run_pin_fleet_cli(
            monkeypatch,
            "--fleet", str(fleet_path),
            "--pin-json", str(pin_json),
            "--vllm-image-digest", _digest("e"),
            "--log-path", str(log_path),
        )
    assert "corrupt" in str(exc.value).lower()


def test_pin_fleet_corrupt_log_leaves_fleet_unchanged(tmp_path: Path, monkeypatch):
    """#5 A / Tier-R2-0 PR1 step 8: log validation must run BEFORE the
    fleet is rewritten, so a corrupt log fails the run with the fleet
    file byte-identical to its pre-run state.
    """
    fleet_path = _write_minimal_fleet(tmp_path)
    fleet_before = fleet_path.read_bytes()
    log_path = tmp_path / "pin_log.json"
    log_path.write_text("{not valid json", encoding="utf-8")
    pin_json = tmp_path / "pin.json"
    pin_json.write_text(
        json.dumps(
            {
                "qwen2.5-7b": {
                    "hf_commit_sha": "a" * 40,
                    "tokenizer_sha": "b" * 64,
                }
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit):
        _run_pin_fleet_cli(
            monkeypatch,
            "--fleet", str(fleet_path),
            "--pin-json", str(pin_json),
            "--vllm-image-digest", _digest("f"),
            "--log-path", str(log_path),
        )
    assert fleet_path.read_bytes() == fleet_before, (
        "fleet YAML must not be mutated when the existing log is corrupt"
    )

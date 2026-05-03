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


# MED-13 fixture upgrade (Tier-R2-0 PR2 step 1): minimum realistic shape
# is >=2 white-box + >=1 black-box + >=1 pcsg_pair, with SHAs that satisfy
# the #7 D Pydantic validators (40/64 lower-hex or `<TBD>`).
#   - qwen2.5-7b keeps `<TBD>` placeholders so pinning tests can exercise
#     the replace-`<TBD>`-with-override path against a known target.
#   - qwen3-8b ships pre-pinned with valid SHAs; its only role is to make
#     the pcsg_pair valid (PCSGPair `early`/`late` must both be P_logprob-
#     eligible) and to give the fleet >1 white-box model.
#   - deepseek-v3 covers the black-box arm.
#   - temporal_qwen_cross_version pcsg_pair mirrors the real fleet.
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

  qwen3-8b:
    family: qwen
    access: white_box
    provider: vllm
    cutoff_date: 2025-01-31
    cutoff_source: operator_inferred
    tokenizer_family: qwen3
    hf_repo: Qwen/Qwen3-8B-AWQ
    quant_scheme: AWQ-INT4
    tokenizer_sha: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    hf_commit_sha: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    p_logprob:
      thinking_control: append_no_think_sentinel
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

pcsg_pairs:
  - id: temporal_qwen_cross_version
    role: temporal
    early: qwen2.5-7b
    late: qwen3-8b
    tokenizer_compat: qwen2_class
    max_token_id_inclusive: 151664
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


def test_pin_fleet_replaces_tbd_with_override(tmp_path: Path, monkeypatch):
    """#10 B / Tier-R2-0 PR2 step 2: a single pinner run with overrides
    must (a) remove `<TBD>` placeholders for the targeted model, (b)
    write the override SHA-256 / SHA-1 values into the YAML, and (c)
    bump `fleet_version` to the requested string. The previous
    combined "hash invariant + idempotency" test only asserted byte
    equality across two runs, which would also pass if the pinner
    silently ignored `--pin-json` entirely.
    """
    fleet_path = _write_minimal_fleet(tmp_path)
    before = fleet_path.read_text(encoding="utf-8")
    assert "tokenizer_sha: <TBD>" in before
    assert "hf_commit_sha: <TBD>" in before
    assert 'fleet_version: "test-v1"' in before

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
    _run_pin_fleet_cli(
        monkeypatch,
        "--fleet", str(fleet_path),
        "--pin-json", str(pin_json),
        "--vllm-image-digest", _digest("c"),
        "--bump-version", "test-v1.pinned-1",
        "--log-path", str(tmp_path / "pin_log.json"),
    )
    after = fleet_path.read_text(encoding="utf-8")

    # qwen2.5-7b's `<TBD>` placeholders are gone, override values landed.
    qwen_block = after.split("qwen2.5-7b:")[1].split("qwen3-8b:")[0]
    assert "<TBD>" not in qwen_block
    assert "a" * 40 in qwen_block
    assert "b" * 64 in qwen_block

    # qwen3-8b's pre-pinned (non-`<TBD>`) values must be untouched —
    # the override only names qwen2.5-7b.
    qwen3_block = after.split("qwen3-8b:")[1].split("deepseek-v3:")[0]
    assert "b" * 40 in qwen3_block

    # fleet_version bumped to the requested string.
    assert 'fleet_version: "test-v1.pinned-1"' in after


def test_pin_fleet_is_idempotent(tmp_path: Path, monkeypatch):
    """#10 B / Tier-R2-0 PR2 step 2: re-running the pinner with the
    same overrides on a YAML that already carries those SHAs must be
    byte-identical to the post-first-run state. Pairs with
    `test_pin_fleet_replaces_tbd_with_override`, which proves the first
    run actually wrote the overrides (without that pair, byte-equality
    alone would also be satisfied by a pinner that silently no-op'd).
    """
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


def test_pin_fleet_default_auto_bump_appends_distinct_timestamp(
    tmp_path: Path, monkeypatch
):
    """MED-10 / Tier-R2-0 PR2 step 3: when `--bump-version` is omitted
    and at least one field changed, the pinner appends an UTC
    `+pinned-<timestamp>` suffix to the existing `fleet_version`. Two
    runs with `any_field_changed=True` and a >=1s gap must therefore
    yield distinct fleet_version strings (the auto-bump path is
    second-resolution per `%Y%m%dT%H%M%SZ`).

    F.34 idempotency masked this because both prior runs explicitly
    passed `--bump-version`, which short-circuits the auto-bump branch.
    """
    import datetime as dt_mod

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

    fixed_times = iter(
        [
            dt_mod.datetime(2026, 5, 2, 10, 0, 0, tzinfo=dt_mod.timezone.utc),
            dt_mod.datetime(2026, 5, 2, 10, 0, 0, tzinfo=dt_mod.timezone.utc),
            dt_mod.datetime(2026, 5, 2, 10, 0, 1, tzinfo=dt_mod.timezone.utc),
            dt_mod.datetime(2026, 5, 2, 10, 0, 1, tzinfo=dt_mod.timezone.utc),
        ]
    )

    class _DT:
        @staticmethod
        def now(tz=None):
            del tz
            return next(fixed_times)

    monkeypatch.setattr(pin_fleet, "datetime", _DT)

    log_path = tmp_path / "pin_log.json"
    _run_pin_fleet_cli(
        monkeypatch,
        "--fleet", str(fleet_path),
        "--pin-json", str(pin_json),
        "--vllm-image-digest", _digest("c"),
        "--log-path", str(log_path),
    )
    yaml_after_first = fleet_path.read_text(encoding="utf-8")
    first_version = next(
        ln for ln in yaml_after_first.splitlines() if ln.startswith("fleet_version:")
    )
    assert "+pinned-20260502T100000Z" in first_version

    # Re-run on a freshly reset fixture so `any_field_changed` is True
    # again on the second invocation (otherwise the no-change branch
    # would skip the auto-bump entirely and the test would assert on a
    # path that did not execute).
    _write_minimal_fleet(tmp_path)
    _run_pin_fleet_cli(
        monkeypatch,
        "--fleet", str(fleet_path),
        "--pin-json", str(pin_json),
        "--vllm-image-digest", _digest("c"),
        "--log-path", str(log_path),
    )
    yaml_after_second = fleet_path.read_text(encoding="utf-8")
    second_version = next(
        ln for ln in yaml_after_second.splitlines() if ln.startswith("fleet_version:")
    )
    assert "+pinned-20260502T100001Z" in second_version
    assert first_version != second_version


def test_pin_fleet_explicit_revision_picks_targeted_snapshot(
    tmp_path: Path, monkeypatch
):
    """MED-11 / Tier-R2-0 PR2 step 4: when the HF cache holds multiple
    snapshots for one repo, `--pin-json` must let the operator name the
    desired commit via `revision`, and the pinner must read THAT
    snapshot's `tokenizer.json` (not the other one). Existing tests
    only covered the multi-snapshot REJECTION path; the happy-path
    `revision`-resolves branch was untested.
    """
    fleet_path = _write_minimal_fleet(tmp_path)

    # Two snapshots; tokenizer.json content differs so SHA-256 differs.
    sha_a = "a" * 40
    sha_b = "b" * 40
    cache = _make_hf_cache(
        tmp_path,
        "Qwen/Qwen2.5-7B-Instruct-AWQ",
        {
            sha_a: b'{"snapshot": "a"}',
            sha_b: b'{"snapshot": "b"}',
        },
    )
    expected_tok_sha = pin_fleet._sha256_file_content(b'{"snapshot": "a"}')

    pin_json = tmp_path / "pin.json"
    pin_json.write_text(
        json.dumps({"qwen2.5-7b": {"revision": sha_a}}),
        encoding="utf-8",
    )
    _run_pin_fleet_cli(
        monkeypatch,
        "--fleet", str(fleet_path),
        "--hf-cache", str(cache),
        "--pin-json", str(pin_json),
        "--vllm-image-digest", _digest("e"),
        "--bump-version", "test-v1.pinned-rev",
        "--log-path", str(tmp_path / "pin_log.json"),
    )

    after = fleet_path.read_text(encoding="utf-8")
    qwen_block = after.split("qwen2.5-7b:")[1].split("qwen3-8b:")[0]
    assert sha_a in qwen_block, "hf_commit_sha must be the requested revision"
    assert sha_b not in qwen_block, "the un-requested snapshot SHA must not leak in"
    assert expected_tok_sha in qwen_block, (
        "tokenizer_sha must hash the tokenizer.json from the requested snapshot, "
        "not the other one"
    )


def test_default_hf_cache_set_but_missing_raises(tmp_path: Path, monkeypatch):
    """C3 (PR1 cross-review defer) / Tier-R2-0 PR2 step 13 (a):
    `_default_hf_cache()` must hard-fail when `HF_HUB_CACHE` is set to a
    nonexistent directory rather than silently falling through to
    `HF_HOME` / `~/.cache/huggingface/hub` (MED-4).
    """
    missing = tmp_path / "does_not_exist"
    assert not missing.exists()
    monkeypatch.setenv("HF_HUB_CACHE", str(missing))
    with pytest.raises(SystemExit) as exc:
        pin_fleet._default_hf_cache()
    msg = str(exc.value)
    assert "HF_HUB_CACHE" in msg
    # The message renders the path via `repr()`, which doubles backslashes
    # on Windows; match a stable substring instead.
    assert "does_not_exist" in msg
    assert "does not exist" in msg


def test_discover_from_cache_invalid_tokenizer_json_returns_note(
    tmp_path: Path,
):
    """C3 (PR1 cross-review defer) / Tier-R2-0 PR2 step 13 (b):
    `_discover_from_cache` must surface the malformed-tokenizer.json
    case as a `(commit_sha, None, note)` triple where the note flags
    the file as not valid JSON, rather than silently SHA-hashing the
    bytes (#6 D residual). A bytes-only SHA on corrupt content would
    still pin a "valid"-looking SHA that fails on first vLLM launch.
    """
    fleet_path = _write_minimal_fleet(tmp_path)
    fleet = pin_fleet.load_fleet(fleet_path)
    cfg = fleet.get("qwen2.5-7b")

    cache = _make_hf_cache(
        tmp_path,
        "Qwen/Qwen2.5-7B-Instruct-AWQ",
        {"a" * 40: b"this is not { valid json"},
    )

    commit_sha, tok_sha, note = pin_fleet._discover_from_cache(
        cfg, cache, requested_revision=None
    )
    assert commit_sha == "a" * 40
    assert tok_sha is None
    assert "not valid JSON" in note

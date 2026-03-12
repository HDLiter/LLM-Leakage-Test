"""
DeepSeek API 并发性能测试脚本
扫描多个并发度，找到最优并行数（吞吐量拐点 / rate-limit 天花板）。
"""

import asyncio
import os
import time

import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-chat"

# 20 个短 prompt，足够暴露 rate-limit 但不会太贵
N_PROMPTS = 20
TEST_PROMPTS = [
    ("你是一个金融分析师。", f"用一句话分析：央行降准对A股的影响。(编号{i})")
    for i in range(N_PROMPTS)
]

CONCURRENCY_LEVELS = [1, 5, 10, 15, 20, 30, 50]


def _build_body(system: str, user: str) -> dict:
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.0,
        "max_tokens": 128,
    }


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


# ── asyncio sweep ────────────────────────────────────────────────

async def _async_single(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    system: str,
    user: str,
) -> dict:
    """Single request with semaphore-controlled concurrency."""
    async with semaphore:
        resp = await client.post(
            f"{BASE_URL}/chat/completions",
            headers=_headers(),
            json=_build_body(system, user),
        )
        resp.raise_for_status()
        return resp.json()


async def _run_level(
    prompts: list[tuple[str, str]],
    concurrency: int,
) -> tuple[float, int, int]:
    """Run all prompts at a given concurrency level.

    Returns (elapsed_seconds, success_count, error_count).
    """
    semaphore = asyncio.Semaphore(concurrency)
    successes = 0
    errors = 0

    async with httpx.AsyncClient(timeout=120.0) as client:
        tasks = [
            _async_single(client, semaphore, s, u)
            for s, u in prompts
        ]
        t0 = time.perf_counter()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.perf_counter() - t0

    for r in results:
        if isinstance(r, Exception):
            errors += 1
        elif isinstance(r, dict) and "choices" in r:
            successes += 1
        else:
            errors += 1

    return elapsed, successes, errors


def run_benchmark():
    n = len(TEST_PROMPTS)
    print(f"=== DeepSeek API 并发度扫描 ({n} prompts × {len(CONCURRENCY_LEVELS)} levels) ===\n")

    rows: list[dict] = []

    for level in CONCURRENCY_LEVELS:
        label = f"concurrency={level}"
        print(f"  [{label}] ...", end="", flush=True)
        elapsed, ok, err = asyncio.run(_run_level(TEST_PROMPTS, level))
        throughput = ok / elapsed if elapsed > 0 else 0
        rows.append({
            "concurrency": level,
            "elapsed": elapsed,
            "success": ok,
            "errors": err,
            "throughput": throughput,
        })
        print(f"  {elapsed:6.2f}s  {ok}/{n} ok  {throughput:.1f} req/s"
              f"{'  ⚠ errors!' if err else ''}")

    # ── 汇总表 ──
    print(f"\n{'='*65}")
    print(f"{'并发度':>8}  {'耗时':>8}  {'成功':>6}  {'错误':>6}  {'吞吐量':>10}  {'加速比':>8}")
    print(f"{'-'*65}")

    baseline = rows[0]["elapsed"]
    best = max(rows, key=lambda r: r["throughput"])

    for r in rows:
        speedup = baseline / r["elapsed"] if r["elapsed"] > 0 else 0
        marker = " ◀ best" if r["concurrency"] == best["concurrency"] else ""
        print(
            f"{r['concurrency']:>8}  "
            f"{r['elapsed']:>7.2f}s  "
            f"{r['success']:>5}/{n}  "
            f"{r['errors']:>5}  "
            f"{r['throughput']:>8.1f}/s  "
            f"{speedup:>7.2f}x"
            f"{marker}"
        )

    print(f"{'='*65}")
    print(f"\n推荐并发度: {best['concurrency']}  "
          f"(吞吐量 {best['throughput']:.1f} req/s, "
          f"加速比 {baseline / best['elapsed']:.1f}x)")

    if best["errors"] > 0:
        print(f"  ⚠ 最优并发度有 {best['errors']} 个错误，建议降低一级")
        # 找最高无错误的
        no_err = [r for r in rows if r["errors"] == 0]
        if no_err:
            safe_best = max(no_err, key=lambda r: r["throughput"])
            print(f"  安全推荐: concurrency={safe_best['concurrency']}  "
                  f"({safe_best['throughput']:.1f} req/s)")


if __name__ == "__main__":
    run_benchmark()

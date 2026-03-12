"""
DeepSeek API 并发性能测试脚本
测试三种策略: 顺序调用 / asyncio 并发 / ThreadPoolExecutor
"""

import asyncio
import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-chat"

# 测试用的 prompts — 简短问题，减少 token 消耗
TEST_PROMPTS = [
    ("你是一个金融分析师。", f"用一句话分析：央行降准对A股的影响。(编号{i})") for i in range(10)
]


def build_body(system: str, user: str) -> dict:
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.0,
        "max_tokens": 128,
    }


def headers() -> dict:
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


# ── 策略 1: 顺序调用 ──────────────────────────────────────────────

def test_sequential(prompts: list[tuple[str, str]]) -> list[dict]:
    results = []
    with httpx.Client(timeout=120.0) as client:
        for system, user in prompts:
            resp = client.post(
                f"{BASE_URL}/chat/completions",
                headers=headers(),
                json=build_body(system, user),
            )
            resp.raise_for_status()
            results.append(resp.json())
    return results


# ── 策略 2: asyncio + httpx.AsyncClient ────────────────────────────

async def _async_single(client: httpx.AsyncClient, system: str, user: str, semaphore: asyncio.Semaphore) -> dict:
    async with semaphore:
        resp = await client.post(
            f"{BASE_URL}/chat/completions",
            headers=headers(),
            json=build_body(system, user),
        )
        resp.raise_for_status()
        return resp.json()


async def _test_async(prompts: list[tuple[str, str]], max_concurrency: int) -> list[dict]:
    semaphore = asyncio.Semaphore(max_concurrency)
    async with httpx.AsyncClient(timeout=120.0) as client:
        tasks = [_async_single(client, s, u, semaphore) for s, u in prompts]
        return await asyncio.gather(*tasks)


def test_async(prompts: list[tuple[str, str]], max_concurrency: int = 5) -> list[dict]:
    return asyncio.run(_test_async(prompts, max_concurrency))


# ── 策略 3: ThreadPoolExecutor ─────────────────────────────────────

def _thread_single(system: str, user: str) -> dict:
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(
            f"{BASE_URL}/chat/completions",
            headers=headers(),
            json=build_body(system, user),
        )
        resp.raise_for_status()
        return resp.json()


def test_threadpool(prompts: list[tuple[str, str]], max_workers: int = 5) -> list[dict]:
    results = [None] * len(prompts)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_thread_single, s, u): i for i, (s, u) in enumerate(prompts)}
        for future in as_completed(futures):
            idx = futures[future]
            results[idx] = future.result()
    return results


# ── 运行 benchmark ─────────────────────────────────────────────────

def run_benchmark():
    n = len(TEST_PROMPTS)
    print(f"=== DeepSeek API 并发性能测试 ({n} 个请求) ===\n")

    # 1) 顺序
    print("[1/4] 顺序调用 ...")
    t0 = time.perf_counter()
    seq_results = test_sequential(TEST_PROMPTS)
    t_seq = time.perf_counter() - t0
    print(f"  耗时: {t_seq:.2f}s  平均: {t_seq/n:.2f}s/req\n")

    # 2) asyncio concurrency=5
    print("[2/4] asyncio 并发 (max_concurrency=5) ...")
    t0 = time.perf_counter()
    async5_results = test_async(TEST_PROMPTS, max_concurrency=5)
    t_async5 = time.perf_counter() - t0
    print(f"  耗时: {t_async5:.2f}s  平均: {t_async5/n:.2f}s/req  加速比: {t_seq/t_async5:.2f}x\n")

    # 3) asyncio concurrency=10
    print("[3/4] asyncio 并发 (max_concurrency=10) ...")
    t0 = time.perf_counter()
    async10_results = test_async(TEST_PROMPTS, max_concurrency=10)
    t_async10 = time.perf_counter() - t0
    print(f"  耗时: {t_async10:.2f}s  平均: {t_async10/n:.2f}s/req  加速比: {t_seq/t_async10:.2f}x\n")

    # 4) ThreadPool
    print("[4/4] ThreadPoolExecutor (max_workers=5) ...")
    t0 = time.perf_counter()
    tp_results = test_threadpool(TEST_PROMPTS, max_workers=5)
    t_tp = time.perf_counter() - t0
    print(f"  耗时: {t_tp:.2f}s  平均: {t_tp/n:.2f}s/req  加速比: {t_seq/t_tp:.2f}x\n")

    # 汇总
    print("=" * 50)
    print(f"{'策略':<30} {'总耗时':>8} {'加速比':>8}")
    print("-" * 50)
    print(f"{'顺序调用':<28} {t_seq:>7.2f}s {'1.00x':>8}")
    print(f"{'asyncio (concurrency=5)':<28} {t_async5:>7.2f}s {t_seq/t_async5:>7.2f}x")
    print(f"{'asyncio (concurrency=10)':<28} {t_async10:>7.2f}s {t_seq/t_async10:>7.2f}x")
    print(f"{'ThreadPool (workers=5)':<28} {t_tp:>7.2f}s {t_seq/t_tp:>7.2f}x")
    print("=" * 50)

    # 验证结果完整性
    for label, res in [("seq", seq_results), ("async5", async5_results), ("async10", async10_results), ("tp", tp_results)]:
        ok = sum(1 for r in res if r and "choices" in r)
        print(f"  {label}: {ok}/{n} 成功")


if __name__ == "__main__":
    run_benchmark()

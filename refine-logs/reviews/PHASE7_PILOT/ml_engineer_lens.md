---
lens: ML Engineer (feasibility gate)
reviewer: Codex xhigh via sub-agent
date: 2026-04-17
reviewed_doc: plans/phase7-pilot-implementation.md
threadId: 019d9eda-274e-7db3-9836-51610431dcee
---

# Phase 7 ML Engineer Feasibility Gate Review

## 1. 总体判断

**GO-WITH-FIXES**

截至 **2026-04-17**，这个 Phase 7 plan 工程上能落地，但还没过 WS0 infra gate。真正危险的不在统计，而在 6 个工程缺口：`P_logprob` 请求契约没写到可执行粒度、thinking policy 在 plan / operator schema 内部互相打架、seed 被写得比现实更“可复现”、resume 还是 run-level 不是 request-level、`src/r5a` 没 packaging 方案、audit app 只定义了 UI 没定义协作形态。先补这些，再进 WS1-WS3；否则会出现先写代码、后返工协议。

## 2. Feasibility summary table

| WS | 工程动作 | 可行性 | 估时 (wall-clock) | 主要风险 |
|---|---|---|---|---|
| WS0 | `src/r5a` scaffold、manifest、runtime/fleet config | 可行，但必须先补 packaging / deps / source-of-truth | 2-3 天 | thinking policy 冲突、缺依赖、import 纪律不清 |
| WS1 | `P_logprob` on 5 WB | 可行，但当前 plan 低估了接口细节 | 4-6 天 | vLLM prompt logprobs 契约、Qwen3/GLM thinking-off、HF fallback |
| WS2 | `P_predict` on 9 fleet | 可行 | 3-4 天 | OpenRouter 路由锁、fingerprint 映射、JSON repair |
| WS3 | `C_FO`/`C_NoOp` + audit | 可行 | 4-6 天 + 审核工时 | Streamlit 只适合本地渲染，不等于协作方案 |
| WS4 | pilot orchestration | 可行，前提是 WS1-WS3 都已 smoke 绿灯 | 2-3 天 | item-level resume / partial failure / duplicate 诊断 |
| WS5 | stats + prereg 产物 | 可行 | 2-3 天 | 上游数据 shape 漂移导致分析脚本返工 |

单人现实总工期不是 plan 表里的线性和，而是 **15-22 个工作日** 更可信；如果 cloud GPU、provider key、双审人手都在 2026-04-17 当天 ready，才能压到 **10-14 个工作日**。

## 3. 问题 (Blocking / Major / Minor)

- `B1` - `P_logprob` 请求契约还不够可执行。plan 只写“completion endpoint”，但 vLLM prompt-side logprobs 不是天然返回的，必须把 `echo=true + max_tokens=0 + prompt_logprobs=k` 这类请求语义写死。风险是 WS1 做完才发现拿到的是 completion logprobs 或 token 对不齐。修法：在 `docs/DECISION_20260417_phase7_interfaces.md` 和 `src/r5a/backends/vllm_logprob.py` 同时冻结 request/response contract；30-case smoke 先做 token-id / BOS-EOS / first-token-nullability 校验，不通过立即切 HF forward scorer。

- `B2` - thinking policy 的 source of truth 冲突。plan 说 `P_predict` 用 default deployed mode；但 [config/prompts/R5A_OPERATOR_SCHEMA.md](</D:/GitRepos/LLM-Leakage-Test/config/prompts/R5A_OPERATOR_SCHEMA.md:423>) 又把 Qwen3/GLM4 写成 OFF，且同一文档后面又说 `P_predict/P_extract/P_schema` 用 default。风险是 pilot 内同一模型被两种 runtime 混跑。修法：别再用 prose 规则，改成 `fleet.yaml` 里的 per-model × per-operator `thinking_control` 矩阵。

- `B3` - reproducibility 对 seed 的表述过头。DeepSeek 官方 chat API 文档没有 `seed`；OpenRouter 虽有 `seed` 参数，但 provider support 是可变的；vLLM 官方也明确说 `vllm serve` 在线服务不保证可复现。风险是 run manifest 看起来 deterministic，实际不是。修法：统一记录 `seed_requested / seed_supported / seed_effective / scheduler_nondeterministic`，把 duplicate rerun 和 fingerprint drift 当主诊断，seed 只当附加元数据。

- `B4` - resume 粒度不够。当前 plan 只有 “checkpointed resume”；而 legacy [src/pilot.py](</D:/GitRepos/LLM-Leakage-Test/src/pilot.py:1222>) 还是 case-level incremental save。风险是 2.3k-2.5k calls 的 pilot 一旦半路失败，无法精确重放、duplicate 与正常请求混 cache。修法：把最小执行单元改成 request item；每个 `(case, model, operator, variant, prompt_version, runtime_fingerprint)` 生成稳定 `request_id`，状态机至少有 `pending/success/retryable/terminal_skipped`。

- `M1` - 如果复用 legacy `LLMClient`，proxy 约束会漏。同步 client 只在 [src/pilot.py](</D:/GitRepos/LLM-Leakage-Test/src/pilot.py:1430>) 被补成 `proxy=None, trust_env=False`，但异步 [src/llm_client.py](</D:/GitRepos/LLM-Leakage-Test/src/llm_client.py:249>) 还是默认 `httpx.AsyncClient(timeout=120.0)`。风险是公司代理或系统代理接管 OpenRouter / localhost 流量。修法：`src/r5a/backends/*` 不要包 legacy client；若必须复用，sync/async 两条路径都显式关代理继承。

- `M2` - 依赖清单不完整。[requirements.txt](</D:/GitRepos/LLM-Leakage-Test/requirements.txt:1>) 里没有 `streamlit`、`pyyaml`、`pyarrow`/`fastparquet`，但现有 [src/pilot.py](</D:/GitRepos/LLM-Leakage-Test/src/pilot.py:1366>) 已经 `import yaml`，Phase 7 还要写 Streamlit 和 Parquet。风险是“在你机器上能跑”。修法：WS0 先补 `pyproject.toml` 或 `environment.yml`，显式 pin Phase 7 依赖。

- `M3` - `src/r5a` 与 legacy `src/` 共存本身没问题，真正问题是没有 packaging discipline。当前 repo 没 `pyproject.toml`，`src/r5a` 也还不存在。风险是 `pytest`、脚本入口、IDE 三套 import 行为不一致。修法：保留 legacy `src` 不搬家，新增 `src/r5a/__init__.py`，所有新代码一律 `from src.r5a...`，并在 `rag_finance` 里做 editable install。

- `m4` - 并发上限有泄漏风险。[src/__init__.py](</D:/GitRepos/LLM-Leakage-Test/src/__init__.py:5>) 里 `DEFAULT_CONCURRENCY=50`，和 plan 的 DeepSeek=20 / vLLM=16 冲突。修法：R5A 后端不要读 legacy default；provider semaphore 只从 `config/runtime/r5a_runtime.yaml` 取值。

## 4. 十个必答问题

1. **Q1**
   不一致。Qwen3 的官方/生态支持是 `enable_thinking=False` 这种硬开关；`/no_think` 只是当 thinking 已开启时的软提示，不适合 `P_logprob`，因为会污染被计分文本。Qwen2.5 本身就是非 reasoning instruct，通常不需要 toggle；GLM-4-9B-0414 不能假设和 Qwen3 同一 API 语义。结论：plan 只覆盖了 Qwen3，一半对；GLM-4 需要 WS0 先实测并写入 `thinking_control` 枚举。

2. **Q2**
   没有完全 address。vLLM 官方实现里，只有在 completion 路径下 `echo=true` 且 `max_tokens=0` 时，才会把 prompt token ids 和 prompt logprobs 直接回传；单写 `top_logprobs` 不够，`min_tokens` 对这个场景基本无关。结论：WS1 必须把 request contract 写成代码常量，而不是留在说明文字里。

3. **Q3**
   如果是 **DeepSeek direct**，fingerprint 可行，seed 不可行。官方 chat completion 文档有 `id`、`created`、`model`、`system_fingerprint`，还有 prompt cache hit/miss 统计；但没有 `seed` 请求字段。若经 **OpenRouter** 调 DeepSeek，gateway 可以收 `seed`，但要把 `seed_supported=false` 当正常结果处理，不能假设真的生效。

4. **Q4**
   OpenRouter 的 provider routing lock 是可实现的，不是伪需求。官方支持 `provider.order`、`allow_fallbacks=false`、`only`、`require_parameters=true`；要 pin 到具体 endpoint slug 也可以。真正缺的是审计链：completion 返回的 `id` 还不够，最好再查 `/api/v1/generation`，把 `provider_name` 和 `upstream_id` 落盘。

5. **Q5**
   现在不建议把 legacy 直接改成 `src/legacy_v0/`，那会把 WS0 变成重命名工程。Phase 7 最低风险方案是：保留现有 `src` 作为包名，新增 `src/r5a/` 子包，加 `pyproject.toml` 和所有 `__init__.py`，然后禁止任何新代码写 `from pilot import ...` 这类裸导入。这样不会有真正的 module name collision，只有 import 纪律问题。

6. **Q6**
   Streamlit 在 Windows 本地跑，适合作为“本地审阅前端”，不适合作为“多人协作后端”。如果是你本人或同一局域网一两个人看，`--server.address 0.0.0.0` 就够；如果是外部协作者，私有 Streamlit Community Cloud 才有基本分享/鉴权，但那意味着文本离开本地环境。对这个 benchmark，我更建议每个 reviewer 本地跑同一个 app，输出各自 `labels_{reviewer}.jsonl`，再统一 merge。

7. **Q7**
   14B bf16 的现实门槛不是“能不能装下权重”，而是“能不能带着 KV cache 和 vLLM 调度余量稳定跑”。实践上 **48GB VRAM 是单模型可用下限，80GB 更稳**；如果你的本地 GPU 只有 24GB/32GB，这个 plan 不能把 14B bf16 white-box 当本地 baseline。云上建议优先 **RunPod A100-80GB** 或 **Modal A100-80GB/H100**；Vast.ai 最便宜，但 host/driver/磁盘/网络方差最大，不适合 reproducibility-first 的 pilot。

8. **Q8**
   plan 提到了 checkpointed resume，但没有把“失败重试”和“断点续跑”设计成 request-level idempotent orchestration。缺的有三项：稳定 `request_id`、per-item 状态机、diagnostic duplicate 的独立 lineage。没有这三项，`scripts/run_phase7_pilot.py` 到 2k+ calls 时就会退化成“遇错重跑一大片”。

9. **Q9**
   plan 还没给出统一 fingerprint 映射，所以现在答案是“还不够”。至少要统一到一张 schema：`gateway`、`request_model`、`response_model`、`gateway_request_id`、`provider_name`、`provider_endpoint_slug`、`upstream_request_id`、`system_fingerprint`、`usage_native_tokens`、`cached_tokens`、`seed_requested`、`seed_supported`、`docker_digest`、`hf_model_sha`、`tokenizer_sha`。否则 DeepSeek / OpenRouter / vLLM 的证据链会碎成三套。

10. **Q10**
    plan 的**运行时长**大体可信，**工程工期**偏乐观。按单人 + 1 张本地 GPU + 远端白盒租 GPU 的现实基线，从 **2026-04-17** 算，较可信的完成窗口是 **2026-05-08 到 2026-05-21**；更中心的预测是 **2026-05-13 到 2026-05-16**。所以总体判断是：runtime 估时约 1x，engineering wall-clock 约 **1.5x-2x**。

## 5. 必须在 WS0 先确认的 infra 项

- `rag_finance` 环境里先补齐并 pin `streamlit`、`pyyaml`、`pyarrow`，再做任何 Phase 7 脚本。
- 明确 `P_predict` 的 thinking source of truth，解决 `plan` 与 `R5A_OPERATOR_SCHEMA` 的冲突。
- 对 5 个 WB 模型逐个做 `P_logprob` smoke：请求、token 数、BOS/EOS、thinking-off、trace 对齐。
- 确认 white-box 服务跑在 **Linux GPU 节点 / Docker**，Windows 只做 orchestration，不直接承担 benchmark-grade vLLM serving。
- 固定 vLLM image digest、HF model SHA、tokenizer SHA、CUDA/driver/GPU SKU。
- 对 OpenRouter 每个模型先拿到实际 provider slug，并验证 `/generation` metadata 可读。
- 把 provider semaphore 从 runtime config 读取，彻底隔离 legacy `DEFAULT_CONCURRENCY=50`。
- 建 request-level cache / manifest / resume 三件套，再写 operator 主逻辑。
- 先演练一轮 audit batch 的双 reviewer merge，再决定 Streamlit 是否够轻。
- 验证所有 `httpx` 调用都显式 `proxy=None`、`trust_env=False`、`NO_PROXY` 包含 `localhost,127.0.0.1,host.docker.internal`。

## 6. 建议的 repo 布局 (final form)

我建议 **Phase 7 final form** 用“最小扰动”方案，不搬 legacy：

```text
pyproject.toml
environment.yml
requirements.txt
config/
  fleet/r5a_fleet.yaml
  runtime/r5a_runtime.yaml
  models/*.yaml
  perturbations/*.yaml
  pilot_sampling.yaml
src/
  __init__.py
  llm_client.py
  pilot.py
  ...
  r5a/
    __init__.py
    contracts.py
    fleet.py
    runtime.py
    manifests.py
    cache.py
    fingerprints.py
    resume.py
    backends/
      __init__.py
      vllm_logprob.py
      openrouter_chat.py
      deepseek_chat.py
    operators/
      __init__.py
      p_logprob.py
      p_predict.py
    perturbations/
      __init__.py
      c_fo.py
      c_noop.py
      shared.py
    audit/
      __init__.py
      schema.py
      merge.py
    analysis/
      __init__.py
      logprob_metrics.py
      pilot_effects.py
scripts/
  smoke_phase7.py
  sample_phase7_pilot.py
  run_phase7_pilot.py
  build_perturbation_audit_batch.py
  merge_perturbation_audit.py
  audit_app.py
tests/
  r5a/
```

`pyproject.toml` 最低限度建议：

```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "llm-leakage-test"
version = "0.1.0"
requires-python = ">=3.12,<3.13"

[tool.setuptools.packages.find]
where = ["."]
include = ["src", "src.*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

关键规则只有两条：
- 新代码只允许 `from src.r5a...`
- `scripts/*.py` 一律通过 editable install 或仓库根目录执行，禁止临时 `sys.path` hack

## 7. 跨 lens 信号

- `P_predict` 的 thinking policy 现在不是“未定”，而是**互相矛盾**：同一份 operator schema 里既写了 Qwen3/GLM OFF，又写了 `P_predict` 用 default。
- legacy 全局并发默认值是 **50**，和 plan 的 DeepSeek=20 / vLLM=16 不兼容；任何“顺手复用”都会越界。
- 现有代码只在同步 client 侧显式关代理，异步批量路径没有；这和 plan 的 proxy discipline 直接冲突。
- plan 把 Streamlit 当“最轻量审计方案”，但它其实只是最轻量 UI，不是最轻量协作协议。

**参考的官方文档**
- vLLM prompt logprobs / completion echo 逻辑: https://docs.vllm.ai/en/v0.10.1/api/vllm/entrypoints/openai/serving_completion.html
- vLLM Qwen3 reasoning / `enable_thinking=False`: https://docs.vllm.ai/en/v0.18.2/features/reasoning_outputs/
- Qwen3 官方 model card 关于 hard switch 与 `/no_think`: https://huggingface.co/Qwen/Qwen3-235B-A22B/blob/main/README.md
- vLLM reproducibility 说明: https://docs.vllm.ai/en/v0.11.2/usage/reproducibility/
- DeepSeek Chat Completions: https://api-docs.deepseek.com/api/create-chat-completion
- OpenRouter provider routing: https://openrouter.ai/docs/features/provider-routing
- OpenRouter generation metadata: https://openrouter.ai/docs/api-reference/get-a-generation/~explorer
- OpenRouter prompt caching / sticky routing: https://openrouter.ai/docs/features/prompt-caching
- Streamlit sharing / private app: https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app
- Modal GPU options: https://modal.com/docs/reference/modal.gpu
- RunPod pod selection / VRAM guidance: https://docs.runpod.io/pods/choose-a-pod
- Vast.ai docs: https://docs.vast.ai/

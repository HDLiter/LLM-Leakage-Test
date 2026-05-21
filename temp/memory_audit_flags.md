# Memory 严谨性审查 — Codex

## 过时条目

- `MEMORY.md` / "Direction Pivot ... binary contrast + evidence intrusion + Qwen CPT as causal anchor": 当前真相为 Phase 5 后的 factor-driven cross-model benchmark；`docs/TIMELINE.md` 记载 2026-04-12 已 pivot 到 factor-controlled cross-model benchmark，`section_01.md` 确认当前贡献是 benchmark 本身。
- `MEMORY.md` / "Codex MCP Patterns ... use mode 3" 与 "Codex Parallelism ... wrap each Codex MCP call": 与 `_GLOBAL_CLAUDE.md` 的当前指令冲突，后者写明 Codex 调用走 `/codex-run`，CLI `codex exec` 取代 MCP sub-agent 作为默认。
- `project_setup.md` / "Codex MCP configured globally"、"Don't suggest ... reconfiguring Codex MCP": 与 `_GLOBAL_CLAUDE.md` 当前默认 `/codex-run` / CLI `codex exec` 不一致。
- `project_setup.md` / "Codex conda workaround: AGENTS.md ..." 与 "relying on AGENTS.md instead": 当前 repo 根目录无 `AGENTS.md`，仅 `archive/pre_benchmark/root/AGENTS.md`；该设置不属于当前活跃根配置。
- `project_setup.md` / "tracks `.claude/CLAUDE.md` and `.claude/settings.json`": 当前 `.gitignore` 忽略的是 `.claude/settings.local.json`，`git ls-files .claude` 仅显示 `.claude/CLAUDE.md`。
- `project_setup.md` / "vLLM instance: Docker container running Qwen 2.5 7B": 当前 fleet 已是 split-tier 16 模型，`section_05.md` 和 `docs/DECISION_20260429_llama_addition.md` 确认 12 个 P_logprob-eligible 白盒 + 4 个黑盒，不再是单一 Qwen 2.5 7B 白盒参照。
- `project_direction_pivot.md` / "New thesis: Outcome-proximal tasks amplify contamination"、"Binary contrast: direct prediction vs authority": 与 `section_01.md` 当前研究问题冲突；当前定位是 characterizing factor-driven memorization benchmark，非 task-design 机制论文。
- `project_direction_pivot.md` / "Continued pretraining on Qwen 7B as causal anchor": 当前 R5A/Phase 7 scope 未含继续预训练；`R5A_FROZEN_SHORTLIST.md` 当前 confirmatory family 是 5 estimand × 4 factor。
- `project_direction_pivot.md` / "Benchmark shrunk from 1000 to 300-500 well-audited clusters": 与 `section_01.md` 的 main run N=2,560、`pending_items.md` 的 pilot 80 pre + 700 post = 780 冲突。
- `project_direction_pivot.md` / "Use this as the basis for revised EXPERIMENT_PLAN.md": 当前下一步是重开 R-1..R-6 后组装中文 `docs/RESEARCH_PROPOSAL.md`，见 `project_status.md` 与 `section_07.md`。
- `project_cfls_generalization_confound.md` / "Diagnostic 2 (in progress)": `docs/TIMELINE.md` 已把 192-case diagnostic 与 Phase 3/4 作为历史阶段记录，当前项目已进入 Phase 7 / Pass-1 后重开。
- `project_cfls_generalization_confound.md` / "This gap ... is the key finding for the paper": 当前 `section_01.md` 明确论文贡献是 factor-driven memorization benchmark；CFLS 诊断不是当前 paper key finding。
- `infra_capabilities.md` / "Role: grey/black-box target model"、"Role: white-box reference model"、"Use Qwen ... DeepSeek ... Cross-validate between the two": 当前 `section_05.md` / `docs/DECISION_20260503_blackbox_refresh.md` 确认为 16-model split-tier fleet，DeepSeek 只是 4 个黑盒之一，Qwen 也不是唯一白盒。
- `lit_landscape.md` / "Model: DeepSeek (understudied) + Qwen white-box": 当前 fleet 为 12 白盒 + 4 黑盒；`section_05.md` 列出 DeepSeek V4 Pro / GPT-4.1 / GPT-5.1 / Claude Sonnet 4.6 等，不再是 DeepSeek+Qwen 双模型定位。
- `project_english_expansion.md` / "Factor-level comparison: do Template Rigidity, Entity Salience, Event Burst ...": 存疑；当前 4 个因子为 Cutoff Exposure、Historical Family Recurrence、Target Salience、Template Rigidity，`section_03.md` 未列 Event Burst，Target Salience 已是连续 `log1p` 提及数。
- `feedback_annotation.md` / "Tier 1 anchor set, 300 cases"、"DeepSeek (the model under test)": 当前 `section_05.md` / `pending_items.md` 的 pilot 是 780，main run 是 2,560，模型对象是 16-model fleet；DeepSeek 不再是唯一被测模型。
- `feedback_annotation.md` / "Send batches to Claude (via Agent tool) and Codex (via MCP)": 与 `_GLOBAL_CLAUDE.md` 当前 Codex 默认 `/codex-run` / CLI `codex exec` 不一致。
- `feedback_agent_roles.md` / "4 Codex domain agents ... participate in all conceptual discussions"、"mcp__codex__codex-reply": 存疑；R5A 多 agent 角色是历史工作流，当前 `pending_items.md` 的 R-1..R-6 强制方法是 clean-room-first，且 `_GLOBAL_CLAUDE.md` 已把默认 Codex 调用改为 `/codex-run`。
- `feedback_codex_mcp.md` / "delegate heavy reasoning ... to Codex MCP"、"launch parallel `mcp__codex__codex` calls": 与 `_GLOBAL_CLAUDE.md` 当前 Codex 调用默认不一致。
- `feedback_codex_parallelism.md` / "wrap each call inside its own Agent ... mcp__codex__codex": 与 `_GLOBAL_CLAUDE.md` 当前默认 `/codex-run` / CLI `codex exec` 不一致。
- `feedback_concurrency.md` / "Use concurrency=20 for DeepSeek-chat API calls": `docs/DECISION_20260503_blackbox_refresh.md` 明确 `deepseek-chat` 是 mutable compatibility route 且不再是稳定 fleet pin，当前 DeepSeek 选择为 `deepseek-v4-pro`。
- `feedback_doc_for_llm_context.md` / "Codex MCP for design/review": 存疑；该处作为 2026-05-02 工作流背景可理解为历史，但若当作当前方法，则与 `_GLOBAL_CLAUDE.md` 的 `/codex-run` 默认冲突。
- `feedback_four_layer_framework.md` / "L1 Factor — dataset classification": 存疑；`pending_items.md` flag ⑦ 已确认旧定义与 Cutoff Exposure 的 case×model 性质存在张力，因子定义需写为 case-level 或 case×model。

## 自相矛盾

- `_GLOBAL_CLAUDE.md` / "走 `/codex-run` ... CLI `codex exec` 取代 MCP sub-agent 作为默认" 与 `feedback_codex_mcp.md`、`feedback_codex_parallelism.md`、`feedback_agent_roles.md`、`feedback_annotation.md`、`project_setup.md`、`MEMORY.md` 中的 Codex MCP 默认工作流相冲突。
- `project_setup.md` / "tracks `.claude/CLAUDE.md` and `.claude/settings.json`" 与当前 repo 文件状态冲突；`.gitignore` 忽略 `.claude/settings.local.json`，`git ls-files .claude` 仅跟踪 `.claude/CLAUDE.md`。
- `project_status.md` / "16 模型 pin"、`section_05.md` / "14 P_predict-eligible ... 12 P_logprob-eligible" 与 `infra_capabilities.md` / "Qwen ... white-box reference model"、`lit_landscape.md` / "DeepSeek + Qwen white-box" 的双模型叙述冲突。
- `feedback_four_layer_framework.md` / "L1 Factor ... dataset classification" 与 `pending_items.md` flag ⑦ 冲突；当前已确认 Cutoff Exposure 是 case×model 因子，不满足单纯 case-level/dataset classification 定义。

## 描述已被取代方向 / 未标历史

- `project_direction_pivot.md`: 描述 2026-04-05 的 task-design / evidence-intrusion / Qwen continued-pretraining 方向，并在 "How to apply" 中仍要求作为新计划基础；`docs/TIMELINE.md` 记载 2026-04-12 Phase 5 已 pivot 到 factor-controlled cross-model benchmark。
- `project_cfls_generalization_confound.md`: 把 CFLS/Diagnostic 1-2 的旧诊断线写成 paper key finding；当前 `section_01.md` 的论文贡献已转为 factor-driven benchmark。
- `feedback_annotation.md`: 300-case anchor set + DeepSeek 单目标的标注策略属于旧实验形态；当前 `pending_items.md` 的 ground truth/收益使用问题归 R-6 重开调查。
- `infra_capabilities.md`: 仍按 DeepSeek 黑盒 + Qwen 白盒两模型研究架构叙述可行方法；当前 `section_05.md` / `docs/DECISION_20260429_llama_addition.md` 是 16-model split-tier fleet。
- `lit_landscape.md`: "Our Unique Position" 仍按 2026-04-04 的 DeepSeek+Qwen / sentiment task 定位写当前贡献，未标明它早于 Phase 5 benchmark pivot 与后续 fleet refresh。
- `MEMORY.md`: 索引仍把 `project_direction_pivot.md`、`feedback_annotation.md`、`infra_capabilities.md`、`feedback_codex_mcp.md` 等旧方向/旧工具默认作为普通 current memory 暴露，未在索引层标明历史或被取代。

## 判定为当前 / 无问题的条目

- `feedback_clean_room_first.md`
- `feedback_decision_text_drift.md`
- `feedback_precommit_flexibility.md`
- `feedback_review_complexity.md`
- `feedback_review_triage_priority.md`
- `project_plan_naming.md`
- `project_status.md`
- `thales_connection.md`
- `user_profile.md`

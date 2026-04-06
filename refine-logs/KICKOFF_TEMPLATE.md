# Session Kickoff Template

> Copy and adapt this as the opening message for a new Claude Code session on this project.

---

## For Proposal v2 Review Session

```
继续 LLM Leakage 项目。

背景：
- 上一轮 session (2026-04-05) 经过 8 轮 4-agent 讨论，从 EXPERIMENT_PLAN v1 演化到 RESEARCH_PROPOSAL v2
- 完整讨论记录：refine-logs/DISCUSSION_LOG_20260405.md
- 待审阅文档：docs/RESEARCH_PROPOSAL_v2.md（459行，含 9 个 [OPTION] 决策点）
- Agent 角色和流程定义：见 memory 中的 feedback_agent_roles.md

任务：对 RESEARCH_PROPOSAL_v2.md 进行多 agent 审阅。

流程：
1. Round 1：4 个 domain agent（Quant/NLP/Stats/Editor）并行独立审阅 proposal v2
   - 每人给出：score /10, verdict, strengths, weaknesses, 对 [OPTION] 的建议
   - 写入各自文件，互不可见
2. Claude 汇总 Round 1：识别收敛点、分歧点、新问题
3. Round 2（如有分歧）：agents 看到彼此观点，聚焦未解决的点
4. 收敛后 → ML Engineer 审可行性
5. 每轮结果写入 DISCUSSION_LOG_{date}.md

注意：
- Agent 只拿到角色提示 + 文件索引，让他们自己读文件
- 不要给预设选项，让他们自由评价
- Claude 是 orchestrator，不参与实质判断
- 所有 Codex 调用用 danger-full-access + xhigh reasoning
```

## For Implementation Session

```
继续 LLM Leakage 项目，进入实施阶段。

背景：
- Proposal v2 已审阅通过：docs/RESEARCH_PROPOSAL_v2.md
- [OPTION] 决策已确定（见 DISCUSSION_LOG_{date}.md）
- 讨论历史：refine-logs/DISCUSSION_LOG_*.md

任务：[具体实施任务，例如：]
- 构建 CLS-Leak benchmark 的数据 pipeline
- 重写 src/metrics.py 实现 CFLS 和 evidence intrusion
- 设计 continued pretraining 的训练脚本

流程：
1. ML Engineer agent 先做可行性评估和技术方案
2. Claude Code 执行实现
3. 如遇设计问题 → 拉 domain agents 讨论
```

## For Focused Debate Session

```
继续 LLM Leakage 项目，需要针对特定问题进行讨论。

背景：
- 完整项目状态：docs/RESEARCH_PROPOSAL_v2.md
- 讨论历史：refine-logs/DISCUSSION_LOG_*.md

议题：[具体问题]

流程：
1. Round 1：4 domain agents 并行独立思考（不给预设选项）
2. Claude 汇总收敛/分歧
3. Round 2+：聚焦分歧，交叉讨论直到收敛
4. 如涉及实施 → ML Engineer gate
5. 结果归档到 DISCUSSION_LOG_{date}.md
```

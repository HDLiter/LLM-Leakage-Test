# Project: LLM 数据泄露检测与消除测试台

## 概述
研究 LLM 在金融新闻情感分析任务中的训练数据泄露问题。当前以 DeepSeek-chat 为实验对象，84 条 A 股新闻为测试集。

## 项目结构
- `src/` — 核心模块（LLM 客户端、masking、metrics、prompts、experiment runners）
- `notebooks/` — 实验 notebook（00-06 已完成初步探究）
- `data/seed/` — 测试用例和记忆探针
- `data/results/` — 实验结果（JSON + PNG）
- `data/cache/` — API 响应缓存
- `related papers/` — 参考论文 PDF
- `config/settings.yaml` — 实验配置

## 当前阶段
初步探究已完成，方法论仍在探索中。文献尚未充分收集，实验设计有待深化。不要假设研究方向已确定。

## 约束
- 当前阶段在 DeepSeek-chat 上迭代，暂不扩展到其他模型
- conda 环境：rag_finance（Python 3.12）
- API key 在 .env 中，不要提交到 git
- 所有文档、代码注释、notebook markdown 均使用英文（用户对话可用中文）

## Rate limit handling
如果 Codex MCP 调用因 rate limit 失败：
1. 等待 30 秒后重试，最多 3 次（排除网络抖动）
2. 若 3 次均失败，视为 API 配额耗尽，用 `/loop 30m` 设置 cronjob 每 30 分钟检查 Codex MCP 是否恢复，恢复后自动继续任务

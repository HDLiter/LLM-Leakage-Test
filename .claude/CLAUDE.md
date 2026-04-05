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
开题报告已完成并通过 3 轮多视角审阅（8/10），prompt schema 已冻结。下一步：在 pilot 数据上验证 prompt，然后构建 1000-case benchmark。
- `docs/RESEARCH_PROPOSAL.md` — 正式开题报告（审阅后修订版）
- `config/prompts/` — 冻结的 prompt schema（9 个 task prompt + 5 个 counterfactual 模板）
- `AUTO_REVIEW.md` — 审阅记录

## 约束
- 当前阶段在 DeepSeek-chat 上迭代，暂不扩展到其他模型
- conda 环境：rag_finance（Python 3.12）
- API key 在 .env 中，不要提交到 git
- 所有文档、代码注释、notebook markdown 均使用英文（用户对话可用中文）

## Network / Proxy
- 本机使用代理，连接 DeepSeek API 和 vLLM (Docker) 时需设置 NO_PROXY
- 在代码中发起请求前确保环境变量正确，或在 httpx/requests 中显式设置 proxy=None

## 可用模型
- DeepSeek-chat: 通过 API（灰/黑盒）
- Qwen 2.5 7B: Docker vLLM 本地部署（白盒，可获取 logprobs）

## 数据资源
- 84 条 A 股新闻测试集（data/seed/）
- 财联社电报语料 ~100万+ 条（源：D:\GitRepos\Thales\datasets\cls_telegraph_raw）

## Codex MCP 使用指南

### 角色分工（模式三）
- **Codex MCP**：重思考（方案设计、审阅、文献分析、prompt 起草、长上下文推理）— 用户 token 多
- **Claude Code**：轻执行（写文件、改代码、跑命令、orchestration）— 用户 token 少
- 原则：Codex 输出内容 → Claude Code 落地写入文件，不要让 Claude Code 做 Codex 能做的推理工作

### Sandbox 限制（重要）
- `mcp__codex__codex` 的 `sandbox` 参数（`read-only` / `workspace-write` / `danger-full-access`）控制 Codex 能否写入文件
- **实测 `workspace-write` 在 Windows 上不可靠**：创建新目录、`apply_patch` 均可能被拦截
- **解法**：用 `sandbox: "danger-full-access"` 并指定 `cwd: "D:\\GitRepos\\LLM-Leakage-Test"` — 已验证可以创建目录和写文件
- 如果不想给 full access，则让 Codex 在回复中输出完整文件内容，由 Claude Code 用 Write 工具落地（但会浪费 Claude Code token）

### 对话上下文管理
- 首次调用 `mcp__codex__codex` 会返回 `threadId`，保存它
- 后续用 `mcp__codex__codex-reply` + `threadId` 继续同一对话，GPT 保留完整上下文
- 多视角审阅时可以并行发多个 `mcp__codex__codex` 调用（各自独立 threadId）
- 每个 thread 是独立的，不同 thread 之间没有共享上下文

### 推理深度
- 始终使用 `config: {"model_reasoning_effort": "xhigh"}` 获取最高推理深度
- 默认推理深度可能不够，尤其是审阅和方案设计任务

### Prompt 编写技巧
- 给 Codex 完整上下文：把需要读的文件内容直接粘贴在 prompt 里，而不是让它自己去读（减少工具调用开销）
- 但如果文件太多/太大，可以让 Codex 自己读（指定 `cwd` 和文件路径）
- 明确告诉 Codex 输出格式（"输出完整文件内容"、"输出 YAML" 等）
- 给角色设定（"你是资深量化研究员"）比泛泛要求效果好得多

### Rate limit handling
如果 Codex MCP 调用因 rate limit 失败：
1. 等待 30 秒后重试，最多 3 次（排除网络抖动）
2. 若 3 次均失败，视为 API 配额耗尽，用 `/loop 30m` 设置 cronjob 每 30 分钟检查 Codex MCP 是否恢复，恢复后自动继续任务

### 典型工作流
```
1. Claude Code 读取项目文件，整理上下文
2. Claude Code 调用 mcp__codex__codex，把上下文 + 任务发给 Codex
3. Codex 返回设计方案 / 代码 / 审阅意见（纯文本）
4. Claude Code 解析 Codex 输出，用 Write/Edit 工具写入文件
5. Claude Code 跑验证命令确认结果
```

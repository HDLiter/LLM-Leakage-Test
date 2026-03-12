# LLM 数据泄露检测与消除测试台

检测和量化 LLM（DeepSeek）在 A 股新闻评估任务中的数据泄露程度，并评估各种 prompt 工程策略的消除效果。

## 背景

LLM 在预训练阶段已经"读过"历史新闻及后续市场走势。当回测时给 LLM 一条 2024 年的新闻，它可能在"回忆"而非"分析"——即 Profit Mirage 论文所说的"利润海市蜃楼"。

## 方法论

基于四篇论文的方法：
- **Profit Mirage** (Li et al., 2025): PC/CI/IDS 三指标量化泄露
- **A Test of Lookahead Bias** (Gao et al., 2026): LAP 成员推断攻击
- **All Leaks Count** (Zhang et al., 2026): Claim-level 分析 + Shapley-DCLR
- **Your AI, Not Your View** (Lee et al., 2025): LLM 偏好偏差控制

## 快速开始

```bash
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY
jupyter notebook
```

## 批量运行

```bash
# 顺序执行全部 notebook（每个 notebook 使用独立内核）
python run_all_notebooks.py

# 清除 API 缓存后重新运行（强制重新调用 LLM）
python run_all_notebooks.py --clear-cache

# 仅清空 notebook 输出（不执行）
python run_all_notebooks.py --clear-output
```

## 项目结构

```
config/settings.yaml     # 实验配置
src/                     # 核心模块
  models.py              # Pydantic 数据模型
  llm_client.py          # DeepSeek API 客户端
  masking.py             # 掩码与反事实生成
  metrics.py             # PC, CI, IDS, OLR 等指标
  prompts.py             # Prompt 模板
  news_loader.py         # 数据加载
notebooks/               # 实验 Notebook
  00_data_prep.ipynb     # 数据准备
  01_memorization_audit  # 记忆审计
  02_counterfactual      # 反事实攻击
  03_ablation            # 消融 + 安慰剂测试
  04_output_format       # 输出格式影响
  05_mitigation_compare  # 消除策略对比
  06_prompt_optimization # DSPy 自动优化
data/                    # 数据与结果
```

## 核心指标

| 指标 | 公式 | 含义 |
|------|------|------|
| PC | (1/N)·Σ I[ŷ_orig = ŷ_cf] | 高 = 高泄露 |
| CI | 1 - (1/M)·Σ\|s_orig - s_cf\| | →1 = 高泄露 |
| IDS | (1/N)·Σ D_KL(P_orig ∥ P_cf) | 高 = 低泄露 |
| L | α·PC + β·CI - γ·IDS | 综合泄露分数 |

# Codex 连贯性审查 — Pass 1 walk-through

## 自相矛盾

1. 第 2 章 / “L1 | Factor 因子 | 给每个案例打的标签,用于分层与交互分析 | 案例 → 类别/数值标签”、“不提任何模型/文本变换能描述它 → 因子”；第 3 章 / “Cutoff Exposure(Bloc 0 — 时间暴露;case×model 连续)”、“case×model:既依赖案例日期,也依赖模型 cutoff。” 第 2 章把因子定义为 case-only 且可不提模型,但第 3 章把 confirmatory 因子 Cutoff Exposure 定义为 case×model。
2. 第 4 章 / “P_predict(黑盒即可):文章 + 冻结任务 prompt → 方向/置信度 + 记忆标记 + 证据引用”；第 5 章 / “P_predict 仅输出方向(涨/跌/中性 + 0-100 信心)”。同一个冻结 P_predict 输出字段在两处不一致；这不同于已知的“是否挂钩真实收益/alpha”问题。

## 逻辑断点 / 缺口

无。

## 追溯不到研究问题的步骤

无。

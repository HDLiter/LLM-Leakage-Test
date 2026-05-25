# R-4a Methodology Audit — final decisions

**Status**: LOCKED 2026-05-23
**Audit trail**(下游 agent 不需要读;只在需要 debate / 看推导过程时翻):
- `whiteboard_analysis.md` —— 阶段 1 白板独立分析 + 阶段 2 对照
- `subfield_lit_scan.md` —— 15 篇 2022-2026 子领域代表作扫描

---

## 1. Framework-level locks (8 条)

### 1. 主报路径 = effect size + 95% CI
- 每个 estimand 走自己的混合模型 + 聚类稳健 SE;主报形式 = effect size + 95% CI per coefficient
- Claim type = **人群层面 characterization**(随因子分层的效应描述)
- 子领域 reference layer:Carlini 用 fraction extractable + log-linear scaling;Shi 用 AUC + ablation;Duan 用 1,000-bootstrap AUC;LiveBench 用 95% bootstrap CI on leaderboard

### 2. Tier labels = main / primary / supporting / robustness / appendix
- 五层标签的 evidence-tier 角色分工:
  - **main / primary**:承担论文主张的 estimand × 因子格子
  - **supporting**:帮助解释或校验主信号
  - **robustness**:检查混杂(同-cutoff pair、协变量稳健性等)
  - **appendix**:细节 / 探索性 / 边缘结果
- 子领域同行通用 label set:Carlini 用 primary / alternate / Appendix;Shi 用 main / analysis / ablation;LiveBench 用 score / ablation / quality control;AntiLeakBench 用 main / human verification

### 3. Pre-registration 路径 = design memo + sealed split + transparency artifact
- **Stage 1 design memo**(pilot 前 commit SHA-locked markdown):研究问题 / 候选 estimand / 候选因子 / 扰动 inventory / 模型 fleet / 案例准入规则 / pilot 后允许修订项 / pilot 后禁止修订项
- **Sealed pilot / test split**:pilot N=780 与 main run N=2,560 0 重叠;pilot 80 pre-cutoff 承载主因子分析,700 post-cutoff 承载 BL2 负对照
- **Stage 2 transparency artifact**(pilot 后 commit-locked update):看到了什么 / 改了什么 / 改动归属 Stage 1 declared allowed / main 开跑前最终锁了什么
- 论文措辞模板:"the final analysis plan was committed at commit Y prior to running the main experiment, with the diff from commit X documenting all pilot-driven refinements."
- 子领域 reference:Shi 2024 WikiMIA pre-2017 / post-2023 sealed split;LiveBench monthly 1/6 private slice;AntiLeakBench post-cutoff 自动构造

### 4. 每个 estimand 独立建模
- Estimand-specific analysis unit:`E_CMMD = case-level fleet aggregate`,`E_PCSG = case×pair`,`E_CTS = case×model`,`E_FO / E_NoOp = case×model eligible subset`
- 聚类按 estimand unit 配:case / model / pair clustering 各自适配
- Case-level aggregate(E_CMMD)走 case-level inference / bootstrap 或 case-cluster CI
- 每个 estimand 独立 fit + 独立报 coefficient table

### 5. 扰动质量审计 = Gwet's AC1 + accuracy
- per-perturbation × event-type 矩阵报 Gwet's AC1 + accuracy
- 质量数字的 reporting role = 透明度 + 方法节 caveat;case-level admissibility / exclusion 决策走 R-5 admissibility 路径
- Gwet's AC1 选择理由:prevalence 高场景下比 Cohen's kappa 稳定(避免 kappa paradox)
- 子领域 reference:AntiLeakBench 2025(3-annotator + Gwet's AC1 + accuracy)

### 6. baseline_confidence / model_capability 走 sensitivity
- 报告 slot = sensitivity / robustness analysis,在 primary model 之外另报
- Reading 角色 = robustness check(主系数在协变后稳定性)
- baseline_confidence 自身可能承载 memorization 信号 → sensitivity slot 是合适的报告位置(避免与主信号 confound)

### 7. TOST / SESOI = 0.15 服务 BL2 等价检验
- Use scope:BL2 post-cutoff "效应应近零" 主张 + 同-cutoff 证伪对的近零 claim
- SESOI = 0.15(标准化效应);通过条件 = 95% CI 完全落在 [-0.15, +0.15]
- 主系数路径 = effect size + 95% CI(per Lock 1)

### 8. Scenario-based MC power simulation
- 基于 pilot 估计的 effect size / 方差 / eligibility / 缺失结构模拟 main run power
- Simulation 必须含 split-tier fleet / eligibility / missingness / pilot-to-main reweighting / conservative shrinkage
- Simulation target = primary family 区间精度 + 检出率(走 effect-size / CI 路径,per Lock 1)

---

## 2. E_CMMD definition

**E_CMMD = Cross-Model Cutoff-Monotone Disagreement**。

E_CMMD 是 case-level 跨模型行为信号;主张层与 memorization 解释**解耦**。Reading 路径:
- E_CMMD 单独成立 → cutoff-consistent behavioral divergence(描述层 reading)
- E_CMMD 与 E_PCSG / E_FO 在同一因子方向上**收敛** → memorization characterization(inference 层 reading)

---

## 3. Negative-control concrete handling

R-4a 锁的负对照具体处理(R-3 范围内的设计决定):

| 负对照 | 处理方式 | 通过 / caveat reading |
|---|---|---|
| **BL2 post-cutoff** | TOST 等价检验,SESOI = 0.15 | 通过 = 95% CI 完全落在 [-0.15, +0.15] |
| **同-cutoff 证伪对**(GLM-4-9B ↔ GPT-4.1)| 主 estimand 上的差异 ratio(主信号占整体信号的份额)| ratio ≤ 0.5 → cutoff-driven reading 维持;ratio > 0.5 → architecture-noise early-warning caveat 附在结果上 |
| **BL1 元数据 / text-light challenger** | grouped-CV-by-case 交叉验证 | 同一原文派生的多行 share fold,grouped-by-case 保证 row-level train/eval disjoint |

C_NoOp_placebo / BL3 中文非金融语料的具体设计留 R-3 session。

---

## 4. R-4a scope boundary

R-4a 锁的层级 = **框架级**方法论。Component-level 项目由对应 session + pilot 数据决定:

| 项目 | Decided by |
|---|---|
| Estimand 清单(哪些进 primary)| R-1e + pilot 数据 |
| Primary family 大小(S8 / S10 / S12 / S20 等)| R-1e + pilot 数据 |
| Confirmatory 因子总数 + 具体身份 | R-1e + pilot 数据 |
| Confirmatory 扰动选哪几个 | R-2 |
| C_FO 机制(就地换值 vs T+1/T+5 真实收益)| R-2 + R-6 |
| P_predict 输出 schema(direction / + confidence / + memory_flag / + evidence)| R-6 + WS2 |

**R-4a → R-6 容量接口**:R-6 加新 estimand 走两条路径之一 — (a) 替换现有 primary 格子,(b) 开新 design memo。Framework 留 estimand 数量给 pilot 数据决定。

---

## 5. R-4b open scope

R-4b(pilot 后具体数字 / 实施细节)仍 **open**,等 R-1e / R-2 / R-3 / R-5 落定后开跑:

- Power 计算具体数字 + n_eff 矩阵
- 混合模型具体规格落地(每个 estimand 的 random effects 结构 / link function)
- Bootstrap 实施(case-level / cluster bootstrap;轮数;CI 类型)
- Path E cutoff probe 实施细节(白盒部分;月度冲击风险修复)
- Scenario-based MC power simulation 实施

R-4b 工作面 = implementation-side;framework-side 8 条由 R-4a 锁(§1)。

---

## 6. Downstream session anchor

| Session | R-4a constraint |
|---|---|
| **R-1b** ✔ closed → `../R1b_recurrence/R1b_DECISIONS.md` | 标签语言 main/primary/supporting/robustness/appendix;factor metrics 严在 operators 之前(L1↔L3 边界);log1p(0)=0 / no-dedup / article cluster traceability;provenance + layer-view hash discipline |
| R-1c | 同 R-1b |
| R-1d | 同 R-1b;额外 — Template Rigidity metric definition 限定在 L1↔L3 边界内;从文献起设计 |
| R-1e | Primary 因子选择 = 在 primary factor slot 池里替换 / 调整;相近因子合并入单一 primary 维度,fine-grained 拆分放 supporting;factor 数量留 pilot 数据决定 |
| R-2 | Primary 扰动池容量与 primary estimand 容量耦合(新增 primary 扰动 = 替换池中现有项目);C_NoOp 路由 = supporting(reading 为 template-brittleness / robustness 信号);C_FO 是最直接 memorization 证据的扰动 |
| R-3 | BL2 走 TOST/SESOI=0.15;同-cutoff pair 走 early-warning ratio reading;BL1 走 grouped-CV-by-case;C_NoOp_placebo 落 supporting diagnostic slot |
| R-4b | 见 §5 |
| R-5 | 采样支撑 per-factor × per-estimand cell 有效样本;反直觉 / 难预测案例的 exclusion 走 predeclared population restriction 路径 |
| R-6 | 真实收益的合法接口 = difficulty covariate / 过滤审计 / auxiliary validation;新 confirmatory estimand 走 framework-level 替换 / 新 design memo 路径(per §4)|

---

## 7. Meta-narrative pointer

R-4a 元层结论(ratchet 论双源坐实 / clean-room-first 协议有效性再坐实 / Codex frozen 与 subfield lit scan 双源汇聚)= **methodology highlights**,放 `../../WALKTHROUGH_PASS1/pending_items.md` R-4a closed 块。

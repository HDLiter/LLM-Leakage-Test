# R-0 + R-4a Reverse Consolidation Report

**Date**: 2026-05-25
**Operator**: Claude Code (CC,本次任务由 Claude 跑,非 Codex)
**Scope**: Retroactively produce time-static `R{X}_DECISIONS.md` for R-0 (closed 2026-05-23 PM late) and R-4a (closed 2026-05-23), and reduce scattered lock-in to pointer + orthogonal content per project documentation convention (memory `feedback_doc_for_llm_context`, locked 2026-05-24 at R-1b close).

---

## §1 Inventory

每个散落源文档按 (a) time-static lock-in 候选(进 DECISIONS.md) / (b) methodology meta(留 pending_items 类 audit) / (c) out-of-scope (不动) 分类。

### R-0 sources

| Source | Time-static lock-in 候选(进 R0_DECISIONS.md) | Methodology meta(留 pending_items) | 其它 |
|---|---|---|---|
| **WS0.5 memo §4.5**(`docs/DECISION_20260518_ws0_5_thales_alignment.md` lines 588-836)| §4.5.0 TL;DR / §4.5.A 4 层模型 / §4.5.B 6 阶段 pipeline + 6 hard constraints / §4.5.C Pool inventory / §4.5.D Cross-cutting principles / §4.5.F downstream session input | 顶部 "Reopen origin" 块(R-0 提升来由)+ "Authority" 块 + audit trail pointer | §4.5.E "Supersession of earlier memo prose" — 是 history-style supersession 记录;其正向 content(provenance hash 要求)已抽进 R0_DECISIONS.md §9。supersession 本身留 §4.5 body 作 audit trail |
| **pending_items.md R-0 closed 块**(lines 50-105)| 5 个 numbered 架构 lock-ins(4-layer / 6-stage / universal admissibility / Pool inventory / supersession)——**全部** duplicate §4.5 | arch-vs-session 锁原则诞生过程 + Codex Pass A vs user walkthrough 双源收敛 + clean-room-first 协议再次坐实 + 下游解锁清单 | — |
| **worktable.md §1 R-0 closed 段**(lines 50-72)+ §2 R-0 行(line 85)| 整段 architecture 描述均 duplicate §4.5 | "元层观察"段(双源收敛 + clean-room-first)| — |
| **RESEARCH_PROPOSAL.md §4 顶部 R-0 anchor**(lines 146-159)+ §4.7 R-0 容器描述(lines 290-317)| 4 层 / 6 阶段 / Pool inventory / admissibility 描述均 duplicate §4.5 | — | 学术叙事的"为什么有这个架构容器"段 — 留 §4 / §4.7 body 简化版,服务读者无须离开 proposal 即能读懂上下文 |
| `whiteboard_analysis.md`(R0_corpus_arch/)| — | — | Audit trail file;DECISIONS.md 引用,本身不动 |

### R-4a sources

| Source | Time-static lock-in 候选(进 R4a_DECISIONS.md) | Methodology meta(留 pending_items) | 其它 |
|---|---|---|---|
| **RESEARCH_PROPOSAL.md §4.4**(lines 207-253)| 8 框架级 locks(逐条)+ E_CMMD 重命名 + R-1/R-2/R-6 待定清单(R-4a 不锁项)+ R-4b 仍开放清单 | — | 候选 estimand 池清单(non-R-4a content)— 留 §4.4 body |
| **RESEARCH_PROPOSAL.md §4.5**(lines 255-275 负对照)| BL2 TOST/SESOI=0.15 / 同-cutoff ratio reading / BL1 grouped-CV-by-case 处理细节 | — | C_NoOp_placebo / BL3 提及(R-3 范围,non-R-4a)— 留 §4.5 body |
| **pending_items.md R-4a closed 块**(lines 147-180)| 8 框架级 locks 数字 + E_CMMD 重命名 + R-4b open scope + R-6 解封 | "元层结论 ratchet 论坐实"段 + clean-room 与 lit scan 双源收敛 + E_CMMD 重命名的具体理由过程 + 子领域 lit scan 主导做法摘要(0/15 multiplicity 等)| — |
| **worktable.md §1 R-4a closed 段**(lines 37-48)+ §2 R-4a 行(line 84)| 8 locks 总览 | "元层结论 ratchet 论双源坐实"句 | — |
| `whiteboard_analysis.md` + `subfield_lit_scan.md`(R4_methodology_audit/)| — | — | Audit trail files;DECISIONS.md 引用,本身不动 |

---

## §2 R0_DECISIONS.md 落地

**File**: `refine-logs/reviews/REOPEN_R1_R6/R0_corpus_arch/R0_DECISIONS.md`(195 行)

**结构**(沿用 R1b_DECISIONS.md pattern):
1. Four-layer model(S0 / L1 / L2 / L3)+ row unit + required/optional columns + bundle handling + non-tradable rows 客体 vs 主体区分
2. Pipeline order(mermaid 流程图 + 6 hard constraints)
3. Universal admissibility(三条 boolean 与 L3 base view 物化)
4. Sampling pool inventory(Pool B sole base + G/H/I optional + D/E/F 扩展位)
5. Cross-cutting principles(`log1p(0)=0` legal / no-dedup legal / article cluster traceability / counts and identities not locked)
6. R-0 scope boundary(不锁清单 + arch-vs-session 锁原则)
7. Downstream session input table(R-1a / R-1b ✔ closed / R-1c / R-1d / R-2 / R-5 / B-2)
8. R-1c session anchor(沿用 R1b §5 两档制 pattern:必须遵守 / 选择空间 / discriminant check)
9. B-2 provenance hash requirements(R-0 引入的 8 项 hash)
10. Downstream notes(B-2 / R-2 / R-5 / R-4b)

**Time-static 自查通过**:无 reviewer-chain verdict、无 v0.2/v0.3 版本标记、无 "originally / changed to" 语、无 "(not X)" 历史对比;non-tradable rows 与 anti-survivorship 的辨析使用正向定义。

**Ambiguous 点**:无 — R-0 容器层的内容在 §4.5 中已是相对干净 time-static 形态,只需 reorganize + 去 history 框架(如"R-1b kickoff 走查衍生"这种 origin 描述)。

---

## §3 R4a_DECISIONS.md 落地

**File**: `refine-logs/reviews/REOPEN_R1_R6/R4_methodology_audit/R4a_DECISIONS.md`(~110 行)

**结构**:
1. Framework-level locks(8 条,每条只讲当前状态)
2. E_CMMD definition(name + reading 路径)
3. Negative-control concrete handling(BL2 / 同-cutoff / BL1 表)
4. R-4a scope boundary(不锁项 by decided-by)
5. R-4b open scope
6. Downstream session anchor(R-1b ✔ / R-1c / R-1d / R-1e / R-2 / R-3 / R-4b / R-5 / R-6 / B-2)
7. Meta-narrative pointer(指向 pending_items 的 ratchet / clean-room highlights)

**Time-static 自查通过(经用户 push-back 后重写,2026-05-25)**:
- 去掉所有"取消 / 替换 / 退出 / 不绑 / 不扩散 / 解绑 / 不再 / 取代"等历史动词
- Lock 1 主报路径写"effect size + 95% CI"正向描述,不写"不做 multiplicity correction"
- Lock 3 写"design memo + sealed split + transparency artifact 三件套",不写"取代正式预注册"
- Lock 5 写"质量数字 reporting role = 透明度",不写"取消 hard gate"
- Lock 6 写"走 sensitivity slot",不写"退出 primary"
- Lock 7 写"Use scope = BL2 + 同-cutoff",不写"不扩散主系数"
- Lock 8 写"Simulation target = primary family 区间精度",不写"解绑 Westfall-Young"
- §2 E_CMMD 只写当前 name + reading 路径,不写"原 Memorization Disagreement"
- §3 负对照通过 / caveat 用正向 reading 描述,如"ratio ≤ 0.5 → cutoff-driven reading 维持"

**Ambiguous 点**:无 — R-4a 锁的 8 条与负对照具体处理在 §4.4 / §4.5 已清晰列出。

---

## §4 散落处 cleanup edits

| File | 改动 | 关键决策点选项 |
|---|---|---|
| `docs/DECISION_20260518_ws0_5_thales_alignment.md` §4.5 | 顶部加 ⚠ STATUS banner 指向 R0_DECISIONS.md;§4.5.A–§4.5.F body 保留作 audit trail | **选 (a) banner-only**(默认,同 WS0.5 §5 对 R-1b 的处理 pattern)。理由:§4.5 body ~250 行,内含 R-0 closure 当时的整段推理与措辞;若整体迁出则失去 WS0.5 memo 自身的演进 audit value,且 WS0.5 memo 是 design memo 类文档,history-style content 在此 doc class 合法 |
| `refine-logs/reviews/WALKTHROUGH_PASS1/pending_items.md` R-0 closed 块 | 5 个 numbered 架构 lock-ins 整段删除并替换为 pointer 行;保留并改名为 "方法论 highlights"(arch-vs-session 锁原则诞生 + Codex Pass A vs user walkthrough 双源收敛);下游解锁清单保留作"下游解锁"标准 bullet | — |
| `refine-logs/reviews/WALKTHROUGH_PASS1/pending_items.md` R-4a closed 块 | 8 框架 locks 整段删除并替换为 pointer 行;E_CMMD 重命名数字 detail 移至"方法论 highlights"段(讲过程不讲历史 lock);新增"子领域 lit scan 主导做法"摘要 highlight(0/15 数字);保留 ratchet 论双源坐实段;R-4b open / R-6 解封作"下游解锁"标准 bullet | — |
| `plans/worktable.md` §1 R-0 + R-4a closed 段 | 两段都缩到单一 pointer 句(canonical lock-in path + methodology highlights → pending_items)| — |
| `plans/worktable.md` §2 R-0 + R-4a 行 | 工作项栏简化(去掉框架 8 条 inline);可动?栏改为 `✔ closed → DECISIONS.md path` | — |
| `docs/RESEARCH_PROPOSAL.md` §4 顶部 R-0 anchor 块 | 缩到 ~6 行 — 保留学术叙事(四层 / 六阶段 / Pool B / R-X session 在容器内自决)+ pointer 到 R0_DECISIONS.md;架构 detail 不再罗列 | — |
| `docs/RESEARCH_PROPOSAL.md` §4.4 | 缩到学术叙事 + pointer 到 R4a_DECISIONS.md;保留候选 estimand 池清单(non-R-4a content);8 locks 概览段简化为一句"覆盖面"句 | — |
| `docs/RESEARCH_PROPOSAL.md` §4.5 负对照段 | 三条负对照各自处理保留(BL2 / 同-cutoff / BL1)用正向 reading 描述;顶部加 pointer 到 R4a_DECISIONS.md §3 | — |
| `docs/RESEARCH_PROPOSAL.md` §4.7 | 缩到学术叙事(R-0 在采样层做了什么 + non-tradable 处理)+ pointer 到 R0_DECISIONS.md;Pool inventory 不再 inline 罗列 | — |
| `docs/RESEARCH_PROPOSAL.md` §9 待重开项一览表 | R-0 / R-4a 行从"框架 8 条 inline"改为"pointer 到 DECISIONS.md" | — |

**未动的内部交叉引用**:
- WS0.5 memo §3.3.1 / §5.2 / §6.2 / §6.3 内的 "R-0 supersession note" 块 — 这些本身是 §4.5 closure 时记录的 in-memo cross-references,与 §4.5 banner 形成自洽的 audit chain;不更新指向 R0_DECISIONS.md 以保持 §4.5 body 的 audit trail 完整性。
- R-1b 相关文件(`R1b_DECISIONS.md` / `whiteboard_analysis.md` / `construct_*.md` / `bch_*.md`)— 与本任务正交,不动。
- `refine-logs/reviews/CROSS_SYNTH_20260523/synthesis_findings.md` — cross-synth 文件,与本任务正交;其中 R-0 / R-4a 引用本身就是 history-style audit,不动。

---

## §5 待 CC 同步(memory)

memory 文件在 sandbox 外,本次任务未改;CC 接走查后同步以下条目:

- **`project_status.md`**(`MEMORY.md` 索引行:"Pass-1 走查完成;R-4a + R-0(2026-05-23 PM late)closed;R-1b/R-1c/R-5/B-2 解锁可动")— 内容上已是 pointer-style,无需改;但若 R-1b 已 closed 2026-05-24,可顺手把"R-1b/R-1c/R-5/B-2 解锁可动"更新为"R-1b ✔ closed 2026-05-24,R-1c/R-5/B-2 可动",这与本 consolidation 任务无关、属于 routine status update。
- **`feedback_doc_for_llm_context.md`** 里 "Retroactive scope" 段(line ~55)现在写 "已 closed 的 R-0 / R-4a 不补 DECISIONS.md (它们的 lock-in 已经在 `docs/DECISION_20260518_ws0_5_thales_alignment.md §4.5` 和 `pending_items.md` closed 块里以 DECISIONS-style 形式存在,风格 already 符合 convention)。从 R-1b 起新会话全部按此 pattern 产出。" — **本任务推翻了这条 retroactive scope** 的判断:经审视 §4.5 与 pending_items 的混合 narrative 形态确实没达到 "single canonical entry per session" 的 convention,因此本任务把 R-0 / R-4a 反向 consolidate。memory 这一段应改为:"已 closed 的 R-0 / R-4a 已于 2026-05-25 反向 consolidate 出 `R0_DECISIONS.md` 与 `R4a_DECISIONS.md`,与 R-1b 起的 forward-pattern 一致。从 R-1b 起新会话全部按此 pattern 产出。"

---

## §6 Resolved questions (owner 2026-05-25 拍 — 都选 a)

1. **WS0.5 memo §4.5 处理选项** → **(a) banner-only**。§4.5 body 整段保留作 audit trail(同 WS0.5 §5 对 R-1b 的处理 pattern);banner 已落。无 follow-up edit。
2. **R0 §10 Tier B 备份内容校准措辞** → **(a) 留着不动**。"Entity-first ordering 移除了 §4.5.E 提到的 §5.2 Phase R1 full-CLS topic-classify 成本驱动 → Tier B 备份内容相应重新校准" 保留 — 给 B-2 工程师 implementation context;DECISIONS.md §10 Downstream notes 性质与 §1-§5 framework lock 略异。无 follow-up edit。
3. **pending_items.md R-4a "子领域 lit scan 主导做法"段** → **(a) 留 pending_items**。0/15 数字是 R-4a 8 条的论证根据,属 audit trail;DECISIONS.md 内子领域 reference 已用 Carlini / Shi / Duan / LiveBench / AntiLeakBench style 嵌入。无 follow-up edit。
4. **R4a §6 downstream session anchor 的 B-2 行** → **(a) 删除**。Provenance + layer-view hash discipline 由 R-0 §9 锁,R-4a → B-2 接口几乎为空;§6 表删 B-2 行。Follow-up edit 已 apply(2026-05-25)。

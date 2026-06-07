---
lens: Editor
reviewer: Codex xhigh via sub-agent
date: 2026-04-17
reviewed_doc: plans/phase7-pilot-implementation.md
threadId: 019d9ed8-f24c-7542-a80a-f3ca7e0c7053
---

# Phase 7 Editor Lens Review

## 1. 总体判断
**GO-WITH-FIXES**。

这份 plan 的主干是能落地的：critical path 清楚，workstream 切分合理，freeze discipline 强，且已经明显在为最终论文叙事做铺垫。问题不在“方向错”，而在四个 reviewer 会立刻追问的缺口还没封口：reserve promotion 路径其实不可执行、Stage 1 sign-in 证据链不够硬、Phase 8 gate 第 9 条仍有解释空间、人审资源假设偏乐观。补完这四点，这份文档就能从“内部好文档”升到“外部可审计的操作文档”。

## 2. 强项 (作为操作文档)
- confirmatory core 没有乱长。Phase 7 实施核心仍是 `P_logprob`/`P_predict`、5 个 frozen confirmatory estimands、4 个 core factors，与 frozen shortlist 一致。
- `WS0 -> (WS1+WS2+WS3) -> WS4 -> WS5` 的 critical path 清楚，且把 `src/r5a/` 与旧单模型遗产切开，这对 scope hygiene 很重要。
- `N=100` 被定义成 default arbitration point，而不是随手可扩张的 pilot 起点，这一点对 anti-scope-creep 很有价值。
- manifest/hash/fingerprint/cache/rerun policy 写得比一般研究计划更像真正要跑的东西，操作性强。
- §826 明确说 gate 关心的是 measurement readiness，不是 pilot 必须“显著为正”，这给最终论文保留了 null-friendly 的合法空间。

## 3. 问题 (Blocking / Major / Minor)
**Blocking**
- reserve promotion 在文字上保留了，但在执行上没有被设计出来。[plan §2.2/§7.2](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:47) 允许 Stage 2 根据 frozen triggers 决定 reserve promotion，但 plan 没有任何 workstream、owner、budget、artifact 去实际跑 `E_ADG/E_extract/E_schema_cont`，这与 [R5A reserve rules](D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md:100) 形成“名义保留、实际收缩”。
- Stage 1 prereg 的 sign-in 证据链不够硬。[plan §7.1](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:474) 只说 `committed`、`dated and signed`，但没定义谁签、签在哪、怎样形成不可回写的时间戳。外部 reviewer 不会把“本地 markdown 文件 + 本地 commit”当成充分 prereg evidence。
- Phase 8 gate 第 9 条不够判定。[plan §13](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:811) 里的 “acceptable”“reasonable planning target”“more than one retained confirmatory estimand” 都留有裁量空间，而且没说到底看 `beta1` 还是各 factor model 的“primary coefficient”。
- human audit 资源模型过于乐观。[plan §9/§11](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:631) 设计的是 150-160 个 perturbation artifact 全量双审再 adjudication，但预算只有 6-10 reviewer-hours，且默认有 4 个独立 reviewer。若实际只有你本人或 1-2 位协作者，这个 IAA 设计会直接失真。

**Major**
- quality gate 没有在本 plan 里完整落地。Frozen shortlist 的 gate 是 3 条件：audit pass、eligible coverage、baseline delta non-degeneracy；本 plan 主要写清了 audit 与部分 coverage，但没有把完整数值门槛直接钉死在主文中，导致执行时仍要回查上游文档。
- Stage 2 允许更新 “final prompt wording” 与前文的 “freeze semantics, not deployment adapters” 存在张力。若不限定为 adapter-layer wording，而是 semantic prompt wording，就会形成隐性 scope drift。
- risk register 没覆盖几个真实失败模式：单侧 perturbation demotion、`N=100` 无法满足 quota matrix 但 rebalancing 又会引入 cherry-picking、same-cutoff consistency check 只在 risk 里出现却没有对应执行步骤、reviewer shortage、prereg evidence dispute。
- documentation overhead 偏重。14 节正文 + 5 个 workstreams + 5 个 decision memos + prereg skeleton + appendix/runbook 细节，已经开始逼近 pilot 本身的工作量。

**Minor**
- Exit gate 4 的 “acceptable parse rates” 和 gate 7 的 “not directionally contradictory” 应直接继承 WS2/BL2 的数值标准，而不是留成自然语言。
- §1 用 `prove` 稍强，操作文档里更稳的是 `demonstrate operational executability`。
- `signed`、`committed`、`approved` 在文中混用，证据语义不统一。

## 4. 七个必答问题
1. **Q1**  
没有看到暗中扩大 frozen confirmatory scope 的情况。没有新增 confirmatory estimand / factor / operator；`BL1/BL2/B1/C1/M2` 都是 analysis 或 validity layer，不是 confirmatory family 扩张。真正的问题反而是**暗中收缩 executable scope**：reserve promotion 仍被保留为 Stage 2 选项，但 plan 没有为其准备可执行路径。

2. **Q2**  
第 9 条目前**不够判定**。争议会出现在：只有 1 个 estimand 达到 80%；第 2 个在 78-79%；demotion/regrouping 后 “retained confirmatory estimands” 还剩几个；以及“primary temporal-exposure coefficient”到底指 `beta1` 还是各 model 的 primary term。建议改成硬规则：  
自动 GO 仅在“最终 retained family 上，至少 2 个 retained confirmatory estimands 的预注册 primary coefficient 的 simulated power >= 0.80”时成立；否则一律进入 explicit review。若最终 retained family 少于 2 个，则按定义不能自动 GO。

3. **Q3**  
有 anti-scope-creep 机制，但还不够。已有的护栏是对的：single default `N=100`、先 rebalance 后扩张、扩张需 decision memo、Stage 2 allowed edits 冻结。缺的是：最多允许几次扩张、谁批准、扩张前允许看哪些 pilot readout、扩张上限是多少。现在仍可能滑向“先跑小 pilot，再因为不满意而自然长成大 pilot”。

4. **Q4**  
plan 对 human bottleneck 有意识，但认识还不够硬。WS3 知道 audit 是关键依赖，也知道必须全量双审；问题在于时间预算明显按“4 个独立 reviewer 同天到位”来写，而不是按真实协作约束来写。若实际没有 4 位独立人审，这个 plan 就应明确降级为“2-reviewer + 1 adjudicator”模式，并承认 IAA 解释力下降。

5. **Q5**  
以 pilot 文档来说，documentation overhead **偏重**。可精简的不是 prereg 本身，而是“主计划里重复出现的 runbook 细节”。最该合并的是：5 个 decision memos 合成一个 `Phase7_DECISION_LOG.md`；`§10 + §14` 合成 ops appendix；各 WS 的 deliverable path 表可压成一个总表；Stage 2 skeleton 可降为模板附录，不必占主文核心位置。

6. **Q6**  
目前没写清谁签、签在哪、什么算 sign-in。外部 reviewer 最想看到的是：  
具名 signatories、Stage 1 prereg 的 git commit SHA、远端时间戳证据（merged PR、signed tag、或至少 push 到受保护远端的 commit）、与 pilot manifest 的 hash 绑定、以及 Phase 8 go/no-go memo 对这些证据的回链。OSF 不是必须，但“只有本地 commit”通常不够硬。

7. **Q7**  
论文 narrative **可以**在 null pilot 下站住，但 plan 还没把这条后路写成显式分支。现在只有一句“Null pilot findings are allowed”，这还不够形成 paper fallback。建议在 go/no-go memo 模板里预设 3 条 narrative branch：positive、heterogeneous、null-but-informative。null 情况下主张应是“在严格审计、冻结 scope 的 benchmark 下，temporal-exposure-correlated signal 弱/异质/不稳定”，而不是被迫转向追加 scope 来“找信号”。

## 5. 文档结构建议
- 把 `§3-§5` 合并成一个 **Execution Plan**：每个 WS 只保留 owner、input、output、exit gate、blocking dependency。
- 把 `§10` 和 `§14` 合并成 **Ops Appendix / Runbook**，命令、yaml keys、路径表都移过去。
- 把 5 个 `DECISION_20260417_*` 合成一个 **Decision Log**，按触发条件开条目，不必每个都独立成文。
- 单独加一个 **Evidence Package** 小节，明确 prereg sign-in、manifest freeze、Phase 8 gate 各自需要什么审计证据。
- 对 reserve promotion 二选一：要么加一个真正可执行的 `WS6-lite`；要么在本计划里明确“Phase 7 不评估 reserve promotion，若触发则另开 Phase 7b”。

## 6. Claim-framing 一致性
整体上，这份 plan 比多数研究计划更克制，已经尽量站在 “characterizing” 而不是 “proving leakage” 的一侧。需要再收紧的地方有三处：  
- 把 `prove that the frozen measurement stack can be executed` 改成更操作性的表述。  
- 把 same-cutoff pair、BL2、model_capability covariate 明确写成 consistency / falsification checks，而不是 causal identification。  
- 若后续文稿继续用 “memorization/leakage”，应始终绑在 “temporal-exposure-correlated behavior under this benchmark” 上，避免暗示机制已被识别。

## 7. 跨 lens 信号
这份 plan 对 Challenger A3/B2/C1 和 Cold Reader F4/M2/M3/BL2/BL4 的回应是到位的，所以它与 R5A freeze 和最终论文之间已经有了一条可走通的主叙事。剩余缺口恰好也对应此前最危险的批评点：C2/F3 的 consistency-check 没真正落地，M1 的“框架会不会压过研究本身”在文档体量上重新出现，null fallback narrative 还不够显式。换句话说，问题不是研究逻辑散，而是**操作边界与证据边界还差最后一层硬化**。

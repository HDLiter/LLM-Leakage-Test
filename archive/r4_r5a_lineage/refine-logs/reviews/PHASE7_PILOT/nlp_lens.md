---
lens: NLP
reviewer: Codex xhigh via sub-agent
date: 2026-04-17
reviewed_doc: plans/phase7-pilot-implementation.md
threadId: 019d9ed8-022b-7403-8732-269de7bf0bc8
---

# Phase 7 NLP Lens Review

## 1. 总体判断
`GO-WITH-FIXES`。整体架构是对的：把 `C_FO/C_NoOp` 先做成可审计的 text perturbation，再用统一 `P_predict` 吃 baseline/variant，且要求全量人工 audit、按 perturbation × event type 报通过率，这些都抓住了要害，见 [plans/phase7-pilot-implementation.md](/D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:263)、[R5A_OPERATOR_SCHEMA.md](/D:/GitRepos/LLM-Leakage-Test/config/prompts/R5A_OPERATOR_SCHEMA.md:90)、[MEASUREMENT_FRAMEWORK.md](/D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md:120)。但从 NLP lens 看，当前 draft 还有 5 个 launch 前必须补齐的空洞：`C_FO` 的 slotability 还没落到可执行 taxonomy，`C_NoOp` 的 clause bank 还没 host-aware，`P_predict` baseline 与 `E_ADG` 的 prompt 边界没彻底切干净，`explicit_memory_reference` 只有“布尔字段 + 几个 regex”级别，“no unintended cues” 也还没被操作化。若不先补，`≥85%` 人工通过与 effect purity 都没有把握。

## 2. 强项
- 把 `C_FO/C_NoOp` 的 confirmatory 身份绑在质量门上，而不是先默认它们有效，这是正确的治理顺序。
- `C_FO` 明确要求 rule-based slot editing、clean localization 失败就拒绝生成，避免“为了凑覆盖率而放松编辑规则”。
- `C_NoOp` 要求 deterministic bank、medial insertion、记录 insertion index，至少给后续审计留下了可追溯面。
- 全量 audit 而非抽样 audit，很适合中文金融短文本这种高脆弱度场景。
- `P_predict` 语义层要求跨 9 模型统一，部署层单独适配，这对 effect comparability 是必要条件。
- cache bypass duplicate rerun 与 provider fingerprint logging 对黑盒行为测量很关键，能防止把 API 抖动误读成 memorization signal。

## 3. 问题

### Blocking
- `NLP-B1` - 问题：plan 实际上把“verified known outcome”近似成了“有 cleanly localizable 的 `C_FO` slot”。风险：很多 case 有已知后验 outcome，但原文里没有单一、局部、可替换的 outcome slot，尤其是政策讲话、市场综述、多标的异动、产业催化汇总。这样会同时伤覆盖率和自然度。具体修法：在 pilot sampling 前先冻结 `fo_slot_topology` taxonomy，只允许“单结果、单目标、单句内可定位”的 super-type；预标 `slot_span / agreement_span / max_changed_char_ratio / ineligible_reason`，把“已知 outcome”与“可做 FO”分开建字段。[plans/phase7-pilot-implementation.md](/D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:300)
- `NLP-B2` - 问题：`C_NoOp` 目前只有“8-16 字、medial position、deterministic bank”，没有 host sentence grammar。风险：在 CLS 电报里，`此外/另外/同时` 这类 connective 一旦没有并列前提会非常假；即便语法通，source/authority/time/certainty 也可能被无意改掉。具体修法：把 clause bank 改成 host-aware insertion library，按“parenthetical fragment / appositive / parallel clause”分层；禁止无支撑 connective、代词回指、时间锚、来源锚、确定性增强词；每条 bank 项显式记录 `entity_disjoint / cluster_disjoint / no_polarity / no_authority_shift` 证明。
- `NLP-B3` - 问题：4 维 rubric 里的 `no unintended cues` 只给了名字，没有 fail criteria。风险：IAA 会虚高地集中在 style 维度，真正决定 gate 成败的 cue leakage 会在 adjudication 时爆炸。具体修法：不改 4 大维度，但给第 4 维补 6 个强制子检查：新时间锚、新来源/权威锚、新确定性/证据性标记、新方向/幅度词、新 target salience shift、异常具体数字/代码/英文缩写；每类给 pass/fail 示例表。[plans/phase7-pilot-implementation.md](/D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:660)

### Major
- `NLP-M1` - 问题：`P_predict` 语义层并未真正冻结。prompt body 仍 pilot-iterable，few-shot 数量未定，而且 schema 文本一边说 baseline 统一，一边又说 `as_of_date` 可注入同一 semantic layer。风险：baseline、`E_FO/E_NoOp`、`E_ADG` 的 effect 被 prompt envelope 混住。具体修法：Stage 1 prereg 里先冻结 baseline 为 zero-shot 或“纯格式示例、非金融、无日期”的 schema-only 示例；`E_ADG` 必须是单独 overlay，不得把 date slot 偷留在 baseline 模板里。[R5A_OPERATOR_SCHEMA.md](/D:/GitRepos/LLM-Leakage-Test/config/prompts/R5A_OPERATOR_SCHEMA.md:53)
- `NLP-M2` - 问题：`explicit_memory_reference` 目前还是“self-report bool + 少量 heuristic phrase”。风险：9 模型跨风格一致性会很差，中文模型更可能说“印象中/似乎见过/据我已有知识”，而不是“训练数据”。具体修法：以 regex/lexicon 为主，不用 LLM-as-judge 做 primary;把它明确定义成 supplementary lower-bound signal，并在 pilot 上做人审 precision audit。
- `NLP-M3` - 问题：CLS 文本对 `P_logprob` 的数码密度、英文缩写、标题模板、dateline boilerplate 偏差没有进入计划。风险：`E_CTS` 可能部分在测 token class mix，而不是 memorization。具体修法：Stage 1 prereg 加 token-class diagnostics 与 raw vs boilerplate-masked sensitivity;`E_PCSG` 还能靠 same-tokenizer pairing 缓一点，`E_CTS` 更需要这层护栏。

### Minor
- `NLP-m1` - 问题：`explicit_memory_reference` 指令 + “必须给 quote evidence” 会把模型往 article-grounding 推。风险：不是污染方向，而是系统性压低 effect size。具体修法：拿 10-20 个 held-out calibration cases 跑一个 shadow sensitivity，估计这个 prompt intervention 的衰减幅度。
- `NLP-m2` - 问题：`8-16 字 clause` 这个说法本身不稳。风险：8-16 字对“片语/插入成分”可以，对“完整分句”往往太短。具体修法：把术语改成 `inserted fragment`;若要完整短句，放宽到约 `10-22` 字并绑定标点模板。

## 4. 六个必答问题

**Q1. `C_FO` 能稳定产出 `≥85%` 人工通过吗？哪些 event type 最可能失败？**  
有条件可达，但前提是把它收缩成“slot topology 清晰”的子集，而不是泛 event type。  
我抽看了现有 [test_cases_v3.json](/D:/GitRepos/LLM-Leakage-Test/data/seed/test_cases_v3.json:1) 的 682 条 seed：正文长度中位数约 224 字，已有 `known_outcome` 的 only 192 条，其中 `corporate+industry` 占 163 条。这说明 pool 够，但能做 `C_FO` 的多半会集中在单结果 corporate/industry 事件。最稳的类型是：获批/未获批、立案/撤案、中标/失标、回购/减持比例、融资/分红/利率/产能等单一数值 slot。最容易失败的是：市场综述、板块异动、政策会议表态、产业催化汇总、研究机构预测、以及“原文讲事件，known outcome 其实是后验股价反应”的 case。后者尤其危险，因为它有 verified outcome，却没有 article-internal replaceable outcome slot。

**Q2. `C_NoOp` 在中文新闻里会不会因 discourse connectives 显得不自然？clause bank 够吗？**  
会，而且这是当前 plan 最大的自然度风险之一。CLS 电报非常省字，连接词高度带前提;`此外/另外/同时` 一旦没有明确并列框架，读者一眼就能看出是硬插。仅有 versioned clause bank 不够，必须 host-aware。我的建议是：只有在宿主句已经形成并列结构时才允许 connective;默认优先插 parenthetical/appositive 片段;任何 bank 项都不得引入新来源、时间、证据强度、主语切换或新的数字锚。否则 `C_NoOp` 很容易从“无操作”变成“语篇失真”或“信息加权变化”。

**Q3. `P_predict` 的 frozen prompt schema 会不会污染 effect 测量，并与 `E_ADG` 互相污染？**  
会，主要是“衰减型污染”而不是“反向造假型污染”。当前 prompt 强制“只能用文内信息”、要求 evidence quote、还要求显式自报 memory reference，这会把模型推向自我监控和文本 grounding，结果通常是把真实 memorization effect 压小。对 `E_FO/E_NoOp` 来说，这更像 lower-bound bias。更麻烦的是 [R5A_OPERATOR_SCHEMA.md](/D:/GitRepos/LLM-Leakage-Test/config/prompts/R5A_OPERATOR_SCHEMA.md:165) 明说 `as_of_date` 可注入同一 semantic layer，但 baseline prompt body里并没有明示这个 slot 的边界;再加上 few-shot 仍未定，确实有和 `E_ADG` 混层的风险。结论是：baseline template、ADG overlay、few-shot policy 必须在 Stage 1 先切干净。

**Q4. `explicit_memory_reference` flag 的跨模型一致性如何？regex 还是 LLM-as-judge？plan 是否 underspecified？**  
目前明显 underspecified。跨模型一致性我只给“低到中等”预期。原因不是 parser，而是语言行为本身：有些模型会忠实填 bool，有些会永远不给 self-incriminating 表达，有些会用“印象中/根据既有知识/这件事我似乎见过”这种弱显式语。主方案应是 regex/lexicon，不是 LLM-as-judge;后者会引入二次模型偏见，而且把“显式”变成“被别的模型推断”。我建议把它明确定义为 supplementary signal，并把 heuristic 词表扩展到中文 paraphrase family，再拿 pilot 子样本做人审 precision/recall 估计。

**Q5. Human audit 的 4 维 rubric 足够 cover corner cases 吗？尤其第 4 维？**  
四个大框是对的，但第 4 维现在不够。最容易被 reviewer 挑战的盲区有五类：  
1. edit 没改方向词，但改了 evidentiality 或 certainty，等于偷偷改了可信度。  
2. insert/rewrite 没改 target 本身，却改了 target salience 和句法焦点。  
3. 新引入时间、来源、机构简称、产品代码、英文缩写，触发 event recall。  
4. `C_FO` 改 slot 后，为了语法通顺连带改动若干 agreement words，结果超出“target-local”。  
5. `C_NoOp` 虽然 target-irrelevant，但改变了 wire 的节奏和新闻编辑常规，造成 style cue。  
所以 rubric 不是要加第 5 维，而是要给第 4 维一张 fail taxonomy。

**Q6. CLS 电报特征对 `P_logprob` 的 Min-K++/CTS 会不会造成系统性偏差？plan 是否考虑？**  
会，而且 plan 目前几乎没正面处理。现有 682 条 seed 里，正文长度中位数约 224 字，阿拉伯数字中位数约 23 个，约 83% 含 Latin uppercase/缩写。CLS 还有强模板前缀，如 `【标题】财联社X月X日讯/电`。这些因素会让 tail tokens 既可能被 boilerplate 拉低 surprise，也可能被罕见代码、缩写、产品名、比例数字拉高 surprise。`E_PCSG` 因为 same-tokenizer paired contrast，风险相对可控;`E_CTS` 更容易吃 style mix 偏差。当前 plan 只做了 tokenizer pinning 和 same-tokenizer pairing，还没把 token-class decomposition、length/digit normalization、boilerplate sensitivity 写进 prereg，所以这块我判定为“已意识到 tokenizer 问题，但未覆盖 CLS-specific lexical bias”。

## 5. 对 Stage 1 prereg skeleton 的 NLP 侧建议
- 先冻结 `P_predict` 是否 zero-shot;若不是 zero-shot，只能用非金融、无日期、纯格式示例。
- 把 `C_FO` eligibility 预注册成 slot-topology 规则，不要只写“verified outcome”。
- 把 `C_NoOp` bank 预注册成 host-aware insertion classes，并明令禁用 unsupported connective。
- 把 `explicit_memory_reference` 明写成 supplementary signal，不得作为主要结果解释支柱。
- 给 audit rubric 附 cue taxonomy、正反例、以及“agreement words 允许改到哪”为止。
- 给 `P_logprob` 加 prereg diagnostics：digit ratio、Latin uppercase ratio、ticker/code ratio、boilerplate share。
- 预注册一个小型 prompt-sensitivity shadow set，专门测 evidence/self-report 行是否压缩 delta。

## 6. 跨 lens 信号
- 如果按我建议收紧 `C_FO` super-type，coverage `≥60%` 会比 pass rate 更可能先成为瓶颈，这会直接影响 Quant/Stats 侧的 confirmatory 保留概率。
- 如果 `C_NoOp` 改成 host-aware bank，ML 工程工作量会上升一点，但远小于 pilot 后整批重做的成本。
- 如果 `P_logprob` diagnostics 显示 strong token-class bias，paper 叙事里应把 `E_CTS` 降为“raw familiarity proxy”，把更强解释权交给 `E_PCSG`。
- 如果 `explicit_memory_reference` 继续维持当前 underspecified 状态，Editor 侧不应让它承担“模型承认自己记得”的 headline 叙事。

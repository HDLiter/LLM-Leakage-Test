# P0 审计记录 —— 推理 / 红队 / 权衡

> **status**:audit trail。决策正本在 `P0_DECISIONS.md`(干净、无历史)。
> 本文留"为什么这么定"+ 权衡过的东西,供日后追溯;下游拿 DECISIONS 即可。
> **方法**:clean-room-first 多 agent workflow —— 四问(Q1–Q4)各跑独立白板分析
> (Q1 三视角面板:测量效度 / 红队 / 统计识别力)→ 对抗性红队漂移审计 → 综合
> 对照既往 reviewer。11 agent。红队对四问均判 `holds_up=true`、`landmine_violations=[]`。

---

## Q1 → P0_DECISIONS §1(主量 + 主张射程)

**核心推理**:"扰动后不变"不止两种来源。至少四种:(A) case 结局记忆;(B) 一般方向先验;(C) 能力不足 / 算子退化的无关不变;(D) 扰动没生效。真正威胁主 claim 的是 C/D(假阳性 resistance),不是 A/B —— A、B 已由 D1 并入"记忆"构念,A/B 之分只是亚型读数。

**三件工具分工(不能误并成三把都能切 A/B 的刀)**:
- 分层 null = floor / 可证伪锚(post 抵抗若=pre,case 信号被淹);
- 会聚效度 = 杀 C(算子伪迹),不分 A/B;
- 截止点前后 × 因子 = 唯一做 A/B 子集级分离的环节,但靠的是"前后差的差"二阶量。

**链的硬度分层**:撑得住"resistance = 广义记忆(A+B 一族)";撑得偏软的是"把 A 单独量化"——它是二阶差、信噪比低、pilot 仅 80 条 pre 样本,且 pre/post 案例非同源(事件类型 / regime / 文风系统性不同,平行趋势无保证)。

**owner 定调(超过 workflow 推荐)**:
- 主 claim 取广义记忆;"A 单独量化"**不预注册**,推到结果分析期判(workflow 原提"三道 pilot 升格闸门",owner 收敛为"实验没跑、现在不确定、分析时看",更简)。
- **owner 纠正显著度的特殊化**:workflow(承 kickoff Q1 + 红队"显著度是中性曝光量、选错方向旋钮")仍把 `F_salience` 拎出来当分离旋钮讨论;owner 判定**实验前任何单一因子都一视同仁,P0 不预派分离旋钮**。这条盖过"换 `F_entval`"的修法——根子是别在数据前指定旋钮。

**红队补充(留作分析期注意)**:会聚效度"两通道独立"本身是隐含前提(若两通道都被同一批高频实体带动,会聚=同一曝光混杂的两次显影);截止点软 floor(TempoMed-Bench 2605.13045 渐变非阶跃)。

## Q2 → P0_DECISIONS §2(false-alpha 桥)

**核心**:桥是纯论证,红线宾语恒为"记忆 / 抗扰动指纹"。

**红队两处加固(已并入决策)**:
- **措辞陷阱**:clean-room 用"记忆抬升代理 / memorization-lift proxy"当承重宾语,把 `memory_lift` 与 resistance 划等号 —— `memory_lift` 血统是 lift-over-prior(pre/post 抬升,PAM 2602.18733),会把已溶解的范式张力召回。修:承重词只用 resistance,lift 留 `P_logprob` 通道。
- **差分纪律**:桥承重的应是"pre 抵抗 − post 抵抗(扣本底)= 归 case 记忆的增量",不是整段 pre-cutoff 抵抗(后者仍混一般先验);这与 Q1 判"A 单独量化是软的"咬合,桥不能比识别走得更远。

**owner 定调**:给出 false-alpha 三通道(截止点前后表现差 / 语义反转抵抗 / 因子过度反应),定位为**结果分析期 checklist**,非现下因果主张。通道 1 是动机侧;测量侧不把前后准确率差当主指标(守雷区 2)。三通道引文备用:LAP 2512.23847 / alpha-decay 2601.13770 / PAM 2602.18733。

## Q3 → P0_DECISIONS §3(prediction-lift 角色)

**核心**:真实涨跌对照维持 pilot 旁证级别,不单立常设 exploratory estimand。

**owner 定调(悲观,理由成立)**:单条短新闻 vs 真实市场无数变量,"涨了且模型也说涨"不证明充分推理 —— 可能蒙中无关侧面利好,非股价真实推手。故 pilot 看一眼印证悲观即可,不寄望。

**红队佐证**:clean-room 声称的"独有价值"未经推导,且承载价值的量(PAM lift-over-prior)落在 `memory_lift` 地盘,"两把不同尺子"卖点软。

**连带**:不开 confirmatory 角色 → novelty 复活闸门不触发 → novelty 维持非主因子、归宿 P5。

## Q4 → P0_DECISIONS §4(§4.6)

**核心**:§4.6 不动。

**owner 原则**:与真实收益相关内容不进指标、最多进因子;§4.6"正式指标不碰收益"本就一致。

**注**:§4.6 整段挂 [R-6 重开中],终将重写,"不动"站得住;只读该节者的误读窗口低风险,R-6 重写时写明"收益不进指标、可进因子"即消。

---

## 并行查证

- **directional-label 查证** → `directional_label_probe.md`:语料有现成方向标注 `expected_direction`(~730–750 例),但标注者是 GPT 家族(Codex),fleet 含 GPT-5.1 / Claude Sonnet 4.6,"外部 judge 须非 fleet 模型"只部分成立 —— 合法性是因子扩展 decision 要拍的真判断,非自动可用。

## 既往 reviewer 对照(净结论)

clean-room 结论与 `R4_construct_validity_decisions.md`(D1–D9)、`algorithm_deepaudit.md` §4/§5、codex fpscope review 高度一致;差异都是"本轮定调已修正既往 lean"(resistance 正名、两范式溶解、null 分层)而非新冲突。clean-room 从 resistance 实存主量出发,绕过了 E_FO 命名漂移这个假争议源头。

---

## 后修:曝光-privilege 漂移检测(2026-06-01)

owner 发现 `P0_DECISIONS.md` §1 会聚效度写成"两通道都过锚、**都随曝光升**"——与同节决策1"曝光只是诸多因子之一、不预派分离旋钮"自相矛盾。开 3 视角 + 综合 drift-check workflow(`wf_ad5f8a04-dc0`,4 agent),三视角一致 `drift_confirmed=true`,且无新漂移、未误伤 cutoff 锚。

**判定**:
- 关键区分 = **cutoff 锚(上帝视角验证锚,享特殊地位合法)** vs **曝光类因子(`F_salience`/`F_recur`,peer,不享)**。"过锚"该留;"随曝光升"是把 peer 因子抬成验证轴 = 真漂移。
- 会聚效度真正的第二条腿 = **两通道在同一批 case 上一致指向记忆、且该一致不被同一共同混杂(如高频实体)带动(= 通道独立性:来源不同源、非统计独立)**;"随曝光升"非 load-bearing,且暗藏共因伪迹口子(高频实体同时拉高两通道 = 同一混杂的两次显影,非会聚)。
- **根在上游 D4**:`R4_construct_validity_decisions.md` D4 + `four_layer_candidate_pools.md` §5 原话即"都随曝光升"(血统 `algorithm_deepaudit.md` §3(b) 把"曝光梯度 = recurrence/salience"坐实为 peer)。已给两处加非破坏性校正注(不改拍板正文),指向 `P0_DECISIONS.md` §1。

**改动**:`P0_DECISIONS.md` §1(会聚效度第二条腿)+ §5 pilot ②(独立性检查去曝光锁定)+ §5 P2(F_temporal 与 cutoff 锚分家);D4 + four_layer §5 加校正注。

---

## 框架收紧:两信号模型(2026-06-01)

owner 指出"验证锚看 A 截有没有如期归零" + "pre−post 落差正是泄露信号" = **over-claim**(没数据、且不假设能拆 A/B、不假设能测出 A 归没归零)。**改成两信号模型:**
- **信号一 = 抗扰动族(主量)= 成见型记忆**;**跨 cutoff 是强是弱不预测,不给它安 post-cutoff 归零判据**。它靠扰动设计本身立(抵抗反事实改写 = 用缓存而非读文本)。
- **信号二 = E_PCSG / E_CTS(熟悉度类)= 确切结局记忆**;**干净的 cutoff 锚落这条**。
- **不假设能合成两者**;"pre−post 抵抗能照出确切结局记忆" = **假说之一**,留结果分析期看。
- **会聚效度不当预设判据**,降为"两条各测一面、互相佐证、事后看相关线索"。

→ **本文件上面"落差=正信号 / memory_lift→0"等表述据此降级为假说**(非 over-claim 时的确信)。正本 `P0_DECISIONS.md` §0/§1/§5-P2;canonical D2/D4 已加"按 P0 收紧"注。术语:白话主量名 = **抗扰动族**(不叫"指纹");P_logprob 通道白话 = **熟悉度/眼熟**(不叫"惊讶度")。


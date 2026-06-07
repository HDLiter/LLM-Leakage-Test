# LLM 记忆派生偏见 catalog(本地文献调研,2026-05-30/31)

> **status**:文献调研产物,登记备查(用户:不强求全覆盖)。喂 P0–P7 辩论 + 因子/扰动设计。
> **来源**:25 篇本地论文(`related papers/`)结构化抽取 → 16 族 dedup。整场调研由 workflow
> 跑出(25/25 读到、0 失败、127 原始条目);本文件是人工精简的决策版。
> **诚信注**:合成时发现两篇被标错(本地 "Disentangling Memory and Reasoning" PDF 实为 HPC
> 压缩论文;MIT "Model Belief" 讲测量效率无行为偏见),已剔除,余 ~22 篇有效。

---

## 0. 核心结论(consilient)

十几篇从不同角度切入,**底层是同一个机制**:模型不看眼前文章,而是**拿语料里学到的先验
顶替眼前文章作答**。名字十几个,结构一样:**预测被语料分布驱动,不被这条具体新闻驱动。**

按 **cutoff 后归不归零**干净分两堆 —— 这正是本项目"各测量指标的无记忆基线不同"的外部坐实:
- **A 堆 = exact 记忆**(cutoff 后该读 ~0,验证锚正面证据):输入不敏感(Profit Mirage PC/CI/IDS)、
  数字→标签指纹、近重复污染、embedding 记日期→行情。
- **B 堆 = 养成偏见**(cutoff 后不归零,项目决定并入构念):下表。

---

## 1. 偏见 catalog(按"对我们是危害/灰色/跨模型 caveat"分类)

### ① 纯危害 / 杂讯 —— 必须扣掉,否则 cutoff 后假装有信号
| 族 | 是什么 | cutoff 后 | 我们的钩子 | 关键文献 |
|---|---|---|---|---|
| 基准率 / 多数类先验 | 涨样本占多→无脑猜涨;无法回忆时退到标签边缘分布 | 持续 | 验证锚(raw_score null≠0 主因);AUC 非 accuracy | Levy 2024;Didisheim 2025;Lopez-Lira 2025 |
| 乐观 / 正面框架 | 系统性偏判"正面/涨";summarization 把中性压成正面 | 持续 | p_predict 类别失衡;C_SR | Chen Brain-Scan 2026(baseline 64.5% 正面);Kong 2026 |
| 格式/选项顺序/弃答 | 选项顺序翻答案、过度弃答 | 持续 | 自身 prompt 设计 nuisance(随机化选项/对称标签) | Li-Zhou 2025;Wongchamcharoen 2025 |
| 拍马屁 sycophancy | 迎合 prompt 暗示的立场;陈述句/肯定语气/第一人称/情绪触发 | 持续 | C_SR;NoOp;prompt 中性化 | Dubois 2026;Wang 2025;Ibrahim 2026 |

> ⚠️ 对**本中文语料尤其危险**:CLS 电报天生陈述句+语气肯定+情绪重(触发 sycophancy);叠加
> 外国乐观(对中国公司)+ 基准率涨 → 语料本身偏"涨"。须 prompt 严格中性 + 扣基准率/乐观后再读信号。

### ② 灰色 / 模棱两可 —— 真本事 or 过期偏见(P0 + B2 争论核心)
| 族 | 是什么 | cutoff 后 | 我们的钩子 | 关键文献 |
|---|---|---|---|---|
| 功能性/事后诸葛 look-ahead | 打分**函数**被"后来发生什么"污染,哪怕输入只有 t 前信息 | 持续(headline) | cutoff 分层(定义为持续残差);p_predict lift | Lopez-Lira 2025;Levy 2024 |
| 知识冲突(旧记忆压新证据) | 文本与先验冲突时吐先验、无视眼前文本;MR=P原/(P原+P替) | 持续(override 倾向) | **C_FO 直接对应**(注入矛盾结局看跟不跟);C_SR | Li-Zhou;Zhou-Zhang;Longpre;Jin;Wang-causal;Gaotang-Li |
| 确认偏见/过度自信 | 抱住先验抗反证;置信度=先验强度非输入信息量 | 持续 | **C_FO/C_SR 测抵抗**(决策翻转率=resistance 模板) | Lee 2025;Lopez-Lira 2025;Kong 2026 |
| 按常见情形猜(canonical) | 对常规猜对(本事),对意外新闻系统性猜错(危害最贵) | 持续 | F_recur(常见家族);C_FO 注反常结局 | Wu 2023;Wongchamcharoen 2025 |
| 风格/因子先验(规模/价值/动量/板块) | 文本固定下按公司特征类系统性偏方向 | 持续 | F_salience 近邻;需公司特征协变量;C_SR | Nakagawa 2024(符号跨模型翻转);Lee 2025;Kong 2026 |
| 共现/表面捷径 | 编码 token 共现而非因果关联;否定盲、反转差 | 持续 | C_SR(否定盲);F_template;C_NoOp | Zhang 2024;Wang-causal;Chen Brain-Scan;McCoy RAVEN |
| 只看语气不看数字 | 几乎只靠语言 tone,弱化数值(beat/miss 幅度) | 持续 | C_SR 改数值/符号看动不动;F_template | Chen Brain-Scan;Levy 2024 |
| 时间/近因先验 | 时间线索(日期/"今天"/近因)驱动判断而非内容 | 混合 | F_cutoff 近端;C_temporal;C_NoOp 改日期 | Chen;Lopez-Lira §5.8;Wongchamcharoen;Didisheim |

### ③ 跨模型 caveat —— cutoff 切不掉,16 模型对比时单独控
| 族 | 是什么 | 我们的钩子 | 关键文献 |
|---|---|---|---|
| 地域/外国偏见 | 美国训练模型对中国公司系统性更乐观(语料地域覆盖不均) | fleet 组成(对同一中文 case 比各模型"涨"占比);per-model 混杂 | Kong 2026(引 Cao 2025);Didisheim 2025 |

### 已知不重列(项目已纳入)
episodic 结局记忆(cutoff-gated);实体/人气偏见(持续,已决定并入构念)。

---

## 2. 第一性原理上该有、本地库未覆盖的缺口(标注:合成 agent 推断)

> 用户 2026-05-31 裁决:**中文语料专属先验不拿出来看**(对英文语料也不够了解,无从对比);
> 年/日历 + 事件类型先验**挪因子扩展 decision**;其余登记备查。以下仅存档。

1. [INFER] 中文语料专属先验(状态媒体措辞/`政策``监管`关键词→方向/`涨停``跌停`语言)—— **本轮不看**。
2. [INFER] 市场状态(牛熊/危机)条件化方向先验 —— 半 gated 半持续。
3. [INFER] 事件类型→方向先验(并购/回购/`减持`/监管调查)—— Janus-Q(2602.19919)有现成 taxonomy;挪因子扩展。
4. [INFER] 日历/季节性(年关/春节/财报季)—— 挪因子扩展。
5. [INFER] 基准集内部故事续集泄露(post-cutoff 一条的结局可从同集更早 post-cutoff 文章推出)—— 构造风险,记着。
6. [INFER] 中文情感词饱和(对 `利好/利空` 过度反应)—— 本轮不看。
7. [INFER] 多个持续偏见在 cutoff 后**叠加**(外国乐观+基准率涨+迎合)——要扣一摞不是一个。

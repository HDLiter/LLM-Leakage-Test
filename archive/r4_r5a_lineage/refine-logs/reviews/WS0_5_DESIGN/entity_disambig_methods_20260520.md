# 中文金融实体别名生成与匹配/消歧方法调研

日期: 2026-05-20

任务背景: 在约 120 万条财联社中文金融快讯中，对 80-430 个目标实体统计“被提及的文章数”。目标实体均为可交易 A 股上市公司、指数或板块，且有唯一证券/指数代码。语料已由 LLM 抽取 salient entities，当前问题不是构建完整知识库，而是为一组已知目标做高精度、可复现的文章级计数。

核心判断: 这个场景是“封闭目标集 + 强主数据 + 已有 mention 抽取 + 文章级计数”，不应按开放域 Wikipedia EL 的复杂度来做。业界标准 pipeline 仍然适用，但应简化成: 权威主数据构建 alias table -> 确定性候选生成 -> 类型/代码/日期/上下文规则消歧 -> 少量长尾人工或 LLM 审计。

## 1. 标准 EL pipeline

Entity linking / named entity disambiguation 的标准结构通常分三层:

1. mention detection: 从文本中识别实体提及 span 与类型。传统方法是 CRF/BiLSTM-CRF/BERT 序列标注；金融中文近年也常用 BERT、MRC 或增强特征模型。已有研究指出中文金融 NER 的难点包括公司简称、金融术语、中文英文数字混合名、简称多样化等，见 Information Sciences 的中文金融 NER 研究摘要: https://www.sciencedirect.com/science/article/abs/pii/S0020025522015444 。本项目已经有 LLM 抽取出的 salient entities，因此不需要从原文重做完整 mention detection；只需把抽取出的 entity string 归一化和链接。

2. candidate generation: 对每个 mention 生成可能实体集合。工业实现通常依赖 KnowledgeBase + alias table + prior probability。spaCy 的 EntityLinker 文档就是这个结构: 对已标注 mention，从 KB 生成 plausible candidates，再用模型结合 prior/context 选择实体，且候选 `(alias, entity)` 带 prior probability: https://spacy.io/api/entitylinker 和 https://spacy.io/api/kb/ 。开放域系统常从 Wikipedia redirect、anchor text、disambiguation page 生成 alias；企业/金融场景则应从内部主数据、公司名、证券代码、工商/交易所信息、历史更名记录生成 alias。

3. ranking / disambiguation: 在候选中选择实体，或输出 NIL/unknown。代表性做法包括:

- Prior-only / popularity prior: 用 `P(entity | alias)` 选最常见实体。优点是快、可解释；缺点是对“中信”“平安”“苹果”这类多义名会偏向热门实体。
- Local context ranker: 用 mention 周围词、标题、实体类型、候选描述、字符串相似度、行业/地区等特征训练 LR/SVM/GBDT，或用 BERT cross-encoder 打分。优点是对短文本上下文有效；缺点是需要标注数据或可迁移训练集。
- Global / collective disambiguation: AIDA/Hoffart et al. 2011 用 mention-entity graph，把 mention-entity prior/context similarity 与 entity-entity coherence 结合，选择全局一致的实体集合。AIDA 论文明确讨论了 prior、context similarity、coherence 和 graph algorithm: https://www.hoffart.ai/wp-content/papercite-data/pdf/hoffart-2011a.pdf 。优点是适合一篇文章中多个实体相互约束；缺点是复杂、依赖 KB 图谱，对财联社短电报常常收益有限。
- Dense retrieval + reranking: BLINK/Wu et al. 2020 用 bi-encoder 先从大规模实体描述中召回，再用 cross-encoder 重排，见 https://arxiv.org/abs/1911.03814 。适合开放域、实体规模百万级、需要 zero-shot 的场景；对本项目 80-430 个目标过重。
- Generative retrieval: GENRE/De Cao et al. 2021 直接生成唯一实体名，见 https://arxiv.org/abs/2010.00904 。优点是可把实体检索转成 constrained generation；缺点是模型依赖强，可复现性和可审计性弱于 deterministic alias table。
- 企业金融 KG linking: J.P. Morgan 的 JEL 工作强调 Wikipedia-tuned EL 很难直接泛化到企业关心的公司实体，使用公司 KG、字符与语义特征匹配金融新闻 mention: https://arxiv.org/abs/2411.02695 。这对本项目的启示是: 金融实体链接应以领域主数据为中心，而不是让通用 LLM 或通用 Wikipedia EL 决定实体身份。

方法取舍:

- 开放域 EL 追求“任意 mention -> 任意 KB 实体”，因此需要复杂 candidate generation 和 neural ranking。
- 本项目只追求“给定目标是否在文章中被提及”，且目标有代码，最重要的是 precision、审计性、可复现性。
- 因此应保留标准 pipeline 的结构，但把模型复杂度降到主数据 alias table + deterministic rules + 小规模人工/LLM 审计。

## 2. 中文金融实体可利用结构

中文 A 股/指数/板块实体有非常强的结构化约束，这是本任务相对开放域 EL 的最大优势。

1. 证券主数据天然提供 canonical id。

- A 股上市公司有交易所代码和证券代码。Tushare `stock_basic` 明确提供 `ts_code`、`symbol`、`name`、`fullname`、`cnspell`、`market`、`exchange`、`list_status`、`list_date`、`delist_date`、`is_hs` 等字段: https://tushare.pro/document/2?doc_id=25 。
- 上交所有官方“股票列表”“暂停/终止上市公司”“地区行业分类”等入口: https://www.sse.com.cn/assortment/stock/ 。
- 巨潮资讯网作为深交所法定信息披露平台，也在页面上展示代码、简称、公告等结构化入口，并说明平台定位: https://www.cninfo.com.cn/?lang=en 。
- AKShare 提供 A 股代码简称、上交所股票列表、股票更名等接口。其文档中 `stock_info_change_name` 指向“新浪财经-股票曾用名”，`stock_info_sz_change_name` 指向深交所名称变更数据: https://akshare.akfamily.xyz/data/stock/stock.html 。

2. 历史曾用名是金融实体链接的必要信息，不是 LLM 该自由生成的内容。

- Tushare `namechange` 接口描述为历史名称变更记录，输出 `ts_code`、`name`、`start_date`、`end_date`、`ann_date`、`change_reason`: https://tushare.pro/document/2?doc_id=100 。
- 财联社语料覆盖 2020-2026，期间 A 股改名、ST 摘帽/戴帽、重组更名很常见。历史简称和曾用名必须进 alias table，并记录生效日期。

3. 指数/板块也有主数据。

- Tushare `index_basic` 覆盖中证、上证、深证、申万等指数基础信息；文档样例中有 `801010.SI 农林牧渔 SW 申万 一级行业指数`: https://tushare.pro/document/2?doc_id=94 。
- Tushare `index_member_all` 可按申万三级分类提取行业成分，字段包括一级/二级/三级行业代码和股票代码: https://tushare.pro/document/2?doc_id=335 。
- 中证指数官网是宽基/主题/行业指数的重要官方来源: https://www.csindex.com.cn/ 。

4. `ST/*ST`、临时前缀和扩位简称需要当作证券简称规则处理。

- 交易所上市规则中，退市风险警示通常在股票简称前冠以 `*ST`，其他风险警示冠以 `ST`。这一点可从上交所股票上市规则摘录看到: https://flfgsc.cn/law/%E4%B8%8A%E6%B5%B7%E8%AF%81%E5%88%B8%E4%BA%A4%E6%98%93%E6%89%80%E8%82%A1%E7%A5%A8%E4%B8%8A%E5%B8%82%E8%A7%84%E5%88%99-2024%E5%B9%B44%E6%9C%88%E4%BF%AE%E8%AE%A2-2024%E5%B9%B4/block735 。
- 对匹配而言，`*ST左江`、`ST左江`、`左江科技`、旧简称之间可能指向同一上市公司，但不能简单全局剥离 `ST`。例如“ST板块”是 sector，而不是公司；“ST”前缀有强金融语义，应作为别名生成和风险分级的规则，而不是普通字符串清洗。

5. A+H、港股通、集团/子公司关系需要明确计数口径。

- `is_hs` 字段可标识沪股通/深股通，A+H 公司还可能有港股简称。若目标是“公司实体曝光”，新闻中“中国平安”通常应计到 601318；若目标是“具体证券/市场曝光”，则“港股中国平安涨”与 “A股中国平安涨”应区分。
- 推荐在本研究中把 canonical id 定义为目标表中的证券/指数代码，但在公司 alias 上采用“公司曝光”口径: mention 指向上市公司主体即可计数；只有当目标集中同时包含 A/H 或同集团多上市平台时，才需要 share-class 或 context disambiguation。

6. 多义族名在中文金融新闻中特别常见。

- “中信”可能指中信证券、中信银行、中信股份/中信集团、中信建投、中信特钢、中信海直等。
- “平安”可能指中国平安、平安银行、平安证券、平安集团。
- “招商”可能指招商银行、招商证券、招商蛇口、招商轮船、招商局集团。
- “国电/华能/华电/中金/国君/太保”等也类似。

这些 alias 不应靠 LLM yes/no 每次确认，而应进入高风险 alias 清单: 仅在有代码、完整简称、类型标签、上下文行业词或同文共现证据时计数；否则输出 unknown/no-count。

## 3. 别名生成:LLM vs 主数据派生

### 主数据 + 规则派生

推荐作为主路径。

优点:

- 准确率高: 交易所/Tushare/AKShare/中证/申万等来源提供的简称、全称、代码、历史名称，都是实体身份的硬证据。
- 可复现: 可以固定数据源、下载日期、字段、清洗规则、alias table 版本。学术研究中，这比“某天调用某个 LLM 生成了一批别名”更容易复核。
- 可审计: 每个 alias 可记录 `source=stock_basic.name/namechange/index_basic/manual_curated`、`effective_start/end`、`risk_level`、`normalization_rule`。
- 可维护: 证券主数据更新后，alias table 可批量再生成；规则变更可做 diff。
- 可控 precision/recall: 可按 alias tier 逐层启用，并在 gold set 上评估。

缺点:

- 覆盖不了所有新闻口语化/市场黑话。例如“宁王”指宁德时代，“茅台”可指贵州茅台也可指白酒产品/集团，“鹅厂”指腾讯但不在 A 股主数据。
- 对板块和主题概念覆盖依赖数据源。财联社常写“AI算力”“低空经济”“机器人概念”等，若目标板块来自同花顺/东方财富/申万/中证不同体系，需要明确 source-of-truth。

### LLM 生成别名

适合辅助发现，不适合作为 authority。

优点:

- 能补充非正式称呼、缩写、英文名、媒体常用称法。
- 对小目标集可快速生成候选，帮助人工审阅。
- 可用于解释某个 mention 为什么可能指某个候选。

主要问题:

- 幻觉: LLM 可能生成不存在或不常用的别名，尤其是把集团名、产品名、地名、行业名误当上市公司别名。
- 不稳定: 即使 temperature=0，模型版本、系统提示、上下文和服务端更新也会改变结果。对训练数据泄露研究这种 confirmatory 因子，复现风险很高。
- precision 风险集中在短 alias: “中信”“平安”“华能”“国电”“招商”“东方”“长江”“昆仑”等高频短词一旦误计，会系统性抬高曝光频率。
- 后处理复杂: 现有方案用 6 条规则把可疑 alias 强制 high，再逐条 LLM yes/no，本质上是在修补 LLM alias 生成带来的不确定性。

### LLM 逐条确认

不建议作为默认在线/批处理步骤。

原因:

- 对本任务不是必要能力: 已有目标代码和主数据时，大部分匹配可以通过 exact alias、代码、类型、日期、上下文词确定。
- 成本与延迟不必要: 120 万文章中高歧义 alias 的命中可能很大，逐条调用 LLM 会变成主要成本。
- 可复现性弱: 即使缓存，也只能复现已缓存样本；换模型或漏缓存会改变结果。
- 难以校准: LLM yes/no 常给出过度自信判断，尤其短快讯上下文不足时。

更合适的使用方式:

- 用 LLM 离线审计“高频未匹配 mention”和“高频高风险 alias 样本”，输出候选解释。
- 由人工或确定性准则把被接受的 alias/rule 写入 versioned alias table。
- 对极少数研究关键且无法规则化的残差，可使用 LLM，但必须固定 prompt、model、temperature、输入字段，保存完整 I/O，并在报告中单独标记为 LLM-adjudicated，不与 deterministic counts 混在一起。

## 4. 现有方案评判

现有方案: LLM 生成别名，每别名带 `ambiguity_risk: high/low`；6 条规则把可疑别名强制 high；high-ambiguity 命中逐条用 LLM yes/no 确认；缓存。

总体判断: 对本场景而言，LLM 使用偏 over-engineering；主数据、时间有效性、候选生成评估、确定性消歧和误差审计偏 under-engineering。

### 多余或成本过高的部分

1. LLM 作为主 alias generator 过重。

目标实体有证券/指数代码，A 股简称、全称、历史曾用名、指数简称均可从权威主数据得到。把 LLM 放在主路径会引入幻觉和版本不稳定，然后再需要 6 条规则和 LLM 确认去补救。更合理的是主数据派生为主，LLM 只对 unmatched/high-frequency residual 做建议。

2. high-ambiguity 命中逐条 LLM yes/no 大多不必要。

“中信”这类 alias 的正确处理不是每篇问 LLM，而是建立候选集和可判定证据:

- 文中同时出现 `600030`、`中信证券`、`券商/证券/投行`，才计中信证券。
- 文中出现 `601998`、`银行/存款/贷款`，才计中信银行。
- 只有“中信系”“中信集团”或无上下文，则不计具体上市公司，或计到集团但不计目标证券。

这类规则可审计、可复现，也便于统计 unresolved。LLM yes/no 可以用于抽样分析，而不是生产计数。

3. alias 自带 `high/low` 由 LLM 判断不可靠。

歧义风险应由 alias table 计算出来，而不是模型主观判断。可定义:

- normalized alias 在全证券/指数/板块 universe 中映射候选数。
- alias 长度、字符类型、是否常见姓氏/地名/行业词/集团词。
- 是否跨 type 冲突，例如“300”可能是数字、指数、股票代码片段。
- 是否只在目标集唯一但在 broader universe 不唯一。

这种 risk scoring 可重复运行，并能解释为什么一个 alias 被降级或禁用。

4. 缓存缓解成本，但不解决方法论问题。

缓存只能保证同一批输入不重复调用 LLM，不能保证新数据、新模型、新 alias 的一致性，也不能让学术读者复现实验。

### 不足或缺失的部分

1. 没有把权威证券主数据放在第一层。

应优先使用 Tushare/AKShare/交易所/中证/申万等主数据字段，包括 `ts_code/symbol/name/fullname/cnspell/list_status/list_date/delist_date/is_hs/namechange`。如果 alias 不是来自主数据或规则派生，应标为 `manual/llm_suggested`，不得默认启用。

2. 缺少 broader universe 碰撞检测。

只在目标 80-430 个实体内部查“一名多标的”不够。即使目标集里只有中信证券，“中信”仍然会在真实世界中指向中信银行、中信集团、中信建投等。风险应在全 A 股、主要港股/指数/行业板块及常见集团名上检测。

3. 缺少时间维度。

2020-2026 跨越大量更名、ST 戴帽/摘帽、退市。alias table 应记录生效区间。历史名是否全期可用要有政策:

- 当前/历史官方简称: 默认可用于指向同一公司，但跨出有效期时风险提高。
- 旧名在改名多年后出现: 若上下文是“曾用名/原名/重组前”，可计；若出现同名冲突，则需证据。

4. 缺少 type compatibility。

语料实体已有 type，应该强制利用。company alias 不应匹配 index/sector；sector mention 不应匹配公司；“ST板块”不应被拆成公司 alias；“沪深300”应为 index，不是普通数字。

5. 缺少精确的 count policy。

要明确计数是 article-level binary count: 同一篇文章多次命中同一目标只计 1。也要明确是否只统计 salient entities，不扫描全文；是否用 raw text 中证券代码补召回；公司主体 vs 证券 share-class 如何处理。

6. 缺少评估方案。

没有 gold set 和 tier-level metrics，就无法判断 LLM alias/confirmation 是否真的提升 recall，还是引入 false positives。业界 EL 通常会分别评估 candidate generation recall@k、linking precision/recall、NIL accuracy；AIDA 论文也以 precision/recall 和 P@1 等指标评估候选分配质量: https://www.hoffart.ai/wp-content/papercite-data/pdf/hoffart-2011a.pdf 。

7. 对“只需计数”的任务目标没有充分利用。

如果目标只是曝光频率，不需要每个 mention 都链接到完整 KB。对无法确定的高歧义短 alias，宁可不计或进入 unresolved，也不要用 LLM 猜测。曝光因子更怕系统性 false positive。

## 5. 推荐 pipeline

### 5.1 输入与 canonical schema

为每个目标实体建立 canonical record:

- `entity_id`: 证券/指数/板块唯一代码，例如 `600519.SH`、`000300.SH/399300.SZ`、`801010.SI`。
- `entity_type`: `company/index/sector`。
- `canonical_name`: 当前官方简称。
- `full_name`: 公司全称或指数全称。
- `source`: SSE/SZSE/BSE/CNINFO/Tushare/AKShare/CSIndex/SW/CITIC/other。
- `market/exchange/publisher/category`: 交易所、市场板块、指数发布方、行业层级。
- `effective_dates`: 上市日期、退市日期、名称生效区间。

同时构建 broader blocking universe，不只包含目标:

- 全 A 股当前与历史简称。
- 主要指数、申万/中信/中证行业指数、常见概念板块。
- 对 A+H 或集团强相关公司，加入港股简称/集团名作为 collision-only aliases。

目的不是链接所有实体，而是识别“某 alias 只在目标集唯一，但在真实市场中不唯一”的风险。

### 5.2 归一化规则

对 alias 和语料抽取实体同时保存 raw string 与 normalized string。建议规则:

- 全角/半角统一，大小写统一，繁简视语料需要统一。
- 去除包裹符号和常见噪声: `（600519.SH）`、`(600519)`、空格、顿号旁噪声。
- 统一证券代码格式: `600519`、`SH600519`、`600519.SH`、`sh.600519` 归到同一 code key。
- 统一 `*ST`、`ＳＴ`、`ST` 表示，但保留是否含 ST 前缀的特征。
- 不做无条件短化。例如不要把“中国平安”短成“平安”，不要把“中信证券”短成“中信”，不要把“招商银行”短成“招商”。

### 5.3 别名生成

按 tier 生成 alias，并记录来源、风险和启用条件。

Tier 0: 代码别名，最高置信。

- `600519`、`600519.SH`、`SH600519`、`贵州茅台(600519.SH)`。
- 指数同理，但必须区分股票代码与指数代码，例如 `000001.SH` 是上证指数，`000001.SZ` 是平安银行。

Tier 1: 官方主数据别名。

- 当前证券简称、公司全称、Tushare `stock_basic.name/fullname/cnspell`。
- Tushare `namechange.name` 的历史简称，带 `start_date/end_date/change_reason`。
- 指数/板块的官方简称、全称、发布方、指数代码。

Tier 2: 确定性派生别名。

- ST 变体: 从历史简称中生成带 `ST/*ST` 和去除风险警示前缀的候选，但去除后必须长度足够且全市场唯一，否则 high risk。
- 法定后缀剥离: 从公司全称剥离“股份有限公司”“有限责任公司”“集团股份有限公司”等，只在结果长度 >= 4 且 broader universe 唯一时启用。
- A/B/H 后缀变体: 如“万科A -> 万科”仅在 broader universe 和目标口径允许时启用；否则保留原简称。
- 指数常用名: 建议维护小型人工白名单，例如 `上证指数/沪指/上证综指`、`深证成指/深成指`、`创业板指`、`科创50`、`沪深300/HS300/CSI 300`、`中证500/中证1000`。不要把纯数字 `300/500/1000` 当低风险 alias。

Tier 3: 语料发现的候选别名。

- 从 unmatched extracted entities 中按频次、与目标代码/官方名同文共现、PMI 或上下文模式发现候选。
- LLM 可用于解释或补充建议，但输出必须进入人工/规则审核。
- 被接受后写入 alias table，记录 `source=manual_from_corpus` 或 `source=llm_suggested_human_accepted`，不得隐式批量启用。

### 5.4 风险分级

不要让 LLM 给 alias 主观标 `high/low`。用规则计算:

Low risk:

- exact code alias。
- normalized alias 在 broader universe 的同 type 中唯一。
- 官方简称/全称或历史名称，且不是常见短词、地名、姓氏、行业词。

Medium risk:

- 唯一但较短，或跨 type 有冲突。
- 历史名跨出生效区间使用。
- 派生别名来自后缀剥离、ST 剥离、A/B/H 剥离。

High risk:

- normalized alias 对应多个实体，或只在目标集唯一但 broader universe 不唯一。
- 1-2 个汉字且非白名单指数简称。
- 常见集团族名、地名、姓氏、泛行业词，如“中信”“平安”“招商”“东方”“长江”“国电”“华能”“中金”“消费”“军工”“地产”等。
- 纯数字指数缩写，如“300”“500”；纯英文缩写如 “AI”“ST”“ETF”。

High risk alias 默认不自动计数，除非后续消歧证据满足规则。

### 5.5 匹配流程

对每篇文章:

1. 取 LLM 已抽取的 salient entities: `surface/type`。
2. 对每个 surface 做 normalized lookup。
3. 按 type compatibility 过滤候选:
   - company mention -> company target。
   - index mention -> index target。
   - sector/concept/industry mention -> sector target。
   - unknown type 可进入更严格匹配，只允许代码/全称/低风险官方简称。
4. 按文章日期过滤或调权历史名称。
5. 对每个目标 article-level 去重: 同一篇命中多 alias 只计 1。
6. 可选补充: 在 raw title/body 中扫描证券代码和带代码括号的官方形式。代码命中是 deterministic，可弥补 LLM entity extractor 漏掉代码的情况。

### 5.6 消歧规则

推荐按证据强度分层:

1. Exact code wins。

出现 `600030.SH`、`600030` 且上下文/市场不冲突时，直接链接中信证券。代码比任何 alias 更强。

2. Full official name / long official name wins。

“中信证券股份有限公司”“中信银行股份有限公司”不需要 LLM。

3. Low-risk unique official alias wins。

“贵州茅台”“宁德时代”“隆基绿能”若全市场唯一，直接计数。

4. Type and context constraints。

高风险 alias 只有在上下文出现 disambiguating cues 时计数:

- “中信 + 券商/证券/投行/保荐/中信证券” -> 中信证券。
- “中信 + 银行/存款/贷款/净息差/中信银行” -> 中信银行。
- “平安 + 保险/寿险/财险/集团/中国平安” -> 中国平安。
- “平安 + 银行/零售银行/息差/平安银行” -> 平安银行。
- “沪深300/上证50/科创50/创业板指” -> index；“300”单独不计。

5. Target-only collision policy。

如果 alias 在目标集中只有一个候选，但在 broader universe 中有多个真实候选，不自动计数。例如目标集中只有中信证券，文章 entity 只有“中信”，不能因为 target-only unique 就计中信证券。

6. Unresolved policy。

证据不足时输出 unresolved/no-count。保留 `article_id, surface, type, candidate_ids, reason` 供后续误差分析。对 confirmatory 因子而言，宁可牺牲少量 recall，也不要让短歧义 alias 制造系统性 false positive。

### 5.7 LLM 在哪里仍有价值

不需要 LLM:

- 主 alias table 的官方简称、全称、代码、历史名称生成。
- exact/normalized lookup。
- 代码、类型、日期、collision-based risk scoring。
- 大多数 company/index/sector 匹配和消歧。

可以用 LLM:

- 审计高频 unmatched extracted entities，提出可能对应的目标和理由。
- 对 top N 高频 unresolved alias 样本做离线解释，帮助人工写规则。
- 对板块/主题概念的自然语言变体做候选扩展，例如“算力租赁/AI算力/算力概念”，但最终仍需映射到指定板块体系。
- 对少数必须判定且规则无法覆盖的样本做 adjudication；必须保存 prompt、model、temperature、输入输出、时间戳，并在结果中单独标记。

### 5.8 评估方案

评估单位应是 article-target pair，而不是 mention 字符串本身。因为最终使用的是“该实体被提及的文章数”。

Gold set 构建:

- 分层抽样:
  - exact code 命中样本。
  - low-risk 官方简称命中样本。
  - derived alias 命中样本。
  - high-risk alias 命中样本。
  - unresolved 高歧义样本。
  - no-match 但含目标相关词的潜在 false negative 样本。
- 按年份、entity_type、目标实体、alias tier、文章长度分层。
- 对每篇文章标注: 目标实体是否被 saliently mentioned；若有歧义，标注“不确定/不计”。

指标:

- Candidate generation recall@k: 正确目标是否在候选集中。
- Disambiguation accuracy: 候选集中有正确目标时是否选对。
- Article-level precision/recall/F1: 对最终计数最重要。
- Per-target count error: `abs(pred_count - gold_count) / gold_count`，并看是否影响 exposure factor 排序。
- Micro vs macro: micro 看总体样本，macro 防止高曝光龙头掩盖小实体错误。
- Tier-level metrics: 分别报告 code、official、derived、high-risk、LLM/manual alias 的 precision/recall。

必要 ablation:

1. 主数据 official aliases only。
2. + 历史曾用名。
3. + 确定性派生别名。
4. + 语料发现/manual aliases。
5. + LLM-assisted aliases 或 LLM adjudication。

只有当第 5 步在 gold set 上显著提升 recall，且 precision 损失可接受，才值得引入 LLM 到最终 pipeline。否则保留为审计工具。

推荐阈值思路:

- 用于 confirmatory 因子的主计数，应优先选择高 precision 版本，例如 precision >= 98% 的 deterministic count。
- 另可报告 sensitivity count: 加入 medium-risk/manual aliases 后的宽松版本，检验下游结论是否稳健。

### 最小推荐方案

- 用 Tushare/AKShare/交易所/中证/申万主数据生成 versioned alias table，字段含 `entity_id/type/alias/source/risk/effective_dates`。
- alias 来源只默认启用: 代码、当前简称、公司/指数全称、历史曾用名、少量人工白名单指数简称。
- 对所有 alias 在 broader universe 做 collision 检测，短词和族名默认 high risk。
- 匹配只基于已抽取 salient entities + 可选 raw text 代码扫描；同篇同目标只计 1。
- low-risk exact match 自动计数；high-risk alias 必须有代码、完整名、type 或上下文 cue，否则 unresolved/no-count。
- LLM 不参与主路径；只用于高频 unmatched/unresolved 的离线候选发现和审计，接受结果必须写回可版本化规则表。
- 建立 article-target gold set，按 alias tier 报告 precision/recall/F1 和 per-target count error。

一句话结论: 现有方案总体偏 over-engineering，因为把 LLM 放在 alias 生成和逐条确认两条主路径上；同时又偏 under-engineering，因为没有充分利用证券主数据、代码、历史名称、类型约束、时间有效性和系统评估。


# R-1w 标的历史价格行为(Entity Trailing Price Behavior)— 操作化 spec

**状态**: 准入级操作化已定(2026-06-05),余为 pilot 前细节。父决策 = R-1r(F_entval 模型内部
valence 先验 DROP;其"模型靠名字方向先验当捷径"的问题,因子层由本族**客观价格历史记录**承载,
扰动层由匿名化扰动承载)。
**构念**: 标的的**方向性历史价格记录**——模型可能顺它当泄露捷径。

---

## 0. 实施闸门(lead 要求,2026-06-05)

**本族每个因子实施前,lead 亲自过目 §8 的源论文。** spec / DECISIONS 维护一份**源论文清单**
(论文 → 做了啥 → 引用 → 撑哪个决定),供 lead 实施前复核。

---

## 1. 候选网格(6)+ 带符号合一形式

三维 × 两锚,同一条后复权历史价格读出:

| | **方向**(净涨跌符号) | **大小**(|净涨跌|) | **波动**(路径离散) |
|---|---|---|---|
| **published_at 锚**(截至新闻日) | ① | ② | ③ |
| **cutoff 锚**(截至模型 cutoff) | ④ | ⑤ | ⑥ |

- **两锚各自独立、不交互**:published_at 锚 = 案子当时客观状态;cutoff 锚 = 模型训练能见到的那段
  (更贴泄露——测模型会不会顺这段历史方向当捷径)。无两锚差值 / 交互项。
- **带符号合一形式**(方向 × 大小 = 带符号 r):量价方向族 pilot **必测**的第三种函数形式
  (见 memory `price_volume_signed_form`);适用 ①④ 方向格,不适用波动 / 市值。

---

## 2. 操作化决定

- **窗口长度 L**:✅ **36 个月(≈756 交易日)主**;12 个月(≈252)稳健扫。门槛随 L。走"长窗记录"非短动量。
- **留缝 G**:✅ **1 个月(≈21 交易日)skip**,两锚对称。不另设短缝稳健扫(缝在 756 天窗边上 minor)。
  论证:住 Jegadeesh-Titman 长窗历史收益文献,1 月跳是对口先例;它**包含**事件研究 5 天缝(清事前
  抢跑漂移)**并额外**削掉最近一月短期反转 + 微结构噪声。
- **回报口径**:✅ **raw 为主**(符合行情族 + Gulen-Petkova 绝对强度先例);超额(减大盘 / 行业指数)
  预登记稳健,**基准 pilot 选;行业基准与 F_industry 口径一致(中证),不用申万**。调整一律减法、不排序。
- **累计方式**:✅ **起止价比**(后复权 `P_止 / P_起 − 1`,非逐日复利);大小右偏则取 log 稳健。
- **方向**:✅ **纯符号**(涨 / 跌),**无中性带**(±0.5% 是短窗噪声地板,36 月累计里退化)。
- **波动估计量**:✅ **收盘到收盘已实现波动**(日收益样本标准差,报 per-day;出处 pilot 前核)。
  稳健:下行半离差、EWMA、特异波动。砍:区间法(A 股涨跌停压瘫)、GARCH(过重)。详 §3。
- **年限不够**:✅ 两态 + 缺失指示一种口径,详 §4。
- **涨跌停**:长线窗口**一律方向保留、不 censor 幅度**(与行情族 R-1l 单日 censor 口径不同,prereg 注明);
  `limit_days_in_window` 计数**可选记录**。
- **停牌**:有效交易日链式 / 起止价跨过;停牌日不补零;长停牌(≥5 日)复牌当天那一跳剔出 σ。
- **复权**:后复权。

---

## 3. 波动估计量 + 出处(lead 实施前复核)

- **默认 = 收盘到收盘历史波动**:`σ_日 = sqrt( Σ(r_t−r̄)²/(N−1) )`,`r_t=ln(C_t/C_{t-1})`。
  **无单一奠基论文**——教科书估计量,是 Parkinson/Garman-Klass measure 效率所用的基准对照物。
  (别混"realized volatility"专名 = Andersen-Bollerslev-Diebold-Labys 2001/03,用日内高频,非本处。)
- **稳健① EWMA / 近期加权**:`σ²_t=(1−λ)r²_t+λσ²_{t-1}`,λ=0.94。出处:**RiskMetrics —
  Technical Document(J.P. Morgan/Reuters, 4th ed., 1996)**。
- **稳健② 下行半离差**(只数下跌):`sqrt(Σ min(r_t,0)²/N)`。出处:**Markowitz 1959**(书,
  semivariance)+ **Sortino & van der Meer 1991**(JPM,下行偏差)。
- **稳健③ 特异波动**(剥大盘残差):`r_t=α+β·r_mkt,t+e_t` 取 std(e_t),基准同 §2 超额口径。出处:
  **Ang, Hodrick, Xing & Zhang 2006**(JF)+ **Fama & French 1993**(三因子模型)。
- **砍 区间法**:Parkinson 1980 / Garman-Klass 1980 / Rogers-Satchell 1991 / Yang-Zhang 2000
  ——理论效率高,但 **A 股涨跌停封板(H=L=C)把当日振幅塌成 0、恰在最极端日子里系统性低估**;
  长窗里效率红利又缩水。砍。
- **砍 GARCH**:逐票拟合脆、加自由度、预测味,对描述性标签过重。砍。

---

## 4. 年限不够(insufficient history)的处理

核心:**两态——有记录 / 无记录;无记录只用缺失指示一种口径,稳健靠窗口长度扫。**

1. **门槛** = 窗口内有效(在交易、非停牌)交易日 ≥ ⌊L/2⌋(36 月≈378 / 12 月≈126;均 ≥60,σ 稳定性自动满足)。
   - 够 → 照常算三维。
   - 不够(次新股 / 长停牌)→ 三维同时无定义,打**一个 (实体×锚) 级标记 `insufficient_history=1`**。
2. **怎么进模型(缺失指示,唯一口径)**:无记录票全留在回归里、单拎一个系数——
   - **方向维**(类别):**涨 / 跌 / 无记录**(无记录单列一类,不硬塞)。
   - **大小 / 波动维**(连续):占位 + `insufficient_history` 标记。
   真因子斜率只从"有记录"票估出,占位不污染斜率;`insufficient_history` 系数本身是个结果。
3. **不补 0 / 不年化短窗 / 不偷偷丢**。
4. **不采的两个口径**(记下理由):
   - **整层丢**——与缺失指示斜率相等(无记录票占位无变化),全模型下的微小差别由 F_age 共线检查覆盖。
   - **行业中位插补 / 多重插补**——年轻票记录结构上不存在、非"未观测",插补=凭空造声誉;
     多重插补"缺失随机下传播不确定性"前提也不成立。**明确排除**(prereg 写明)。
5. **稳健 = 窗口长度扫(36m/12m)**:改"无记录"桶大小(12m 让大批年轻票挪回有记录),比建模口径更要害。
6. **IPO 烧入**:窗口起点 = max(起点, 上市日 + 21 交易日);剔完压到门槛下 → `insufficient_history`。
7. **机制含义(feature)**:年轻票结构上无长记录 → 落无记录类 → 与 F_age 天然耦合;显式建成交互、不藏。
8. **`history_coverage`(=有效天/L)**:pilot 阶段算作诊断(查覆盖率是否有影响);**是否进正式 schema
   待 pilot 后定**。
9. **schema**:6 因子列 + flags `{insufficient_history, limit_days_in_window(可选)}`;无 short_history /
   anchor_pair_complete;`history_coverage` 为 pilot 诊断、正式 schema 待定。

---

## 5. 复用行情族 vs 本族新增

**复用(沿用 R-1k/l/m + R-1f 既定约定)**:raw 为主;一序两读(方向=sign / 大小=|·|);调整=减法不排序;
涨跌停方向保留;log 右偏稳健;VIF≥10 或 |r|≥0.90 区分度阈、无 metric 级 fallback;不补零 / 标记分层;
akshare/Tushare + 后复权;F_age 的 case×model、model_cutoff 由模型随机效应吸收。

**本族新增(无先例)**:① 长窗**事前**窗口;② 窗口长度 L;③ 留缝 G;④ **波动维**整个;⑤ 最短历史门槛
+ `insufficient_history` 两态分层;⑥ **两锚(published_at / cutoff)各自独立的因子列,不交互**;
⑦ 长窗不做单日幅度 censor;⑧ 方向不设中性带(长窗 ±0.5% 退化)。

---

## 6. 共线盯防(pilot)

VIF≥10 / |r|≥0.90,撞了 R-1e 降级:**F_age**(门槛在年轻端按构造诱导相关,机制预期)/ **F_mktdir**
(published_at 方向 vs 事后结果方向)/ **F_salience / F_mktcap**(蓝筹长期赢家三维都载荷)/ **族内两锚版本互查** /
波动 vs 大小(大 move 常伴大波动)。

---

## 7. lead 决定(已定 2026-06-05)

- 窗口 **36m 主、12m 稳健**;留缝 **1 月**;回报 **raw 主**(超额作稳健,基准 pilot 选、行业用中证);
  累计 **起止价比**;方向 **纯符号、无中性带**;波动 **收盘到收盘**(出处 pilot 前核);涨跌停 **长窗不 censor**
  (`limit_days_in_window` 可选);年限不够 **缺失指示一种口径**(整层丢 / 插补 / ≥60 obs / anchor_pair_complete 均不设);
  `history_coverage` **pilot 诊断、正式 schema 待定**;两锚 **不交互**。
- 余 pilot 前细节:门槛具体数、超额基准最终选择(中证口径)、波动稳健排序。

---

## 8. 源论文清单(lead 实施前过目;引用数为现查量级,标"待核"者未拉到精确)

**窗口长度**
- Jegadeesh & Titman 1993, JF,《Returns to Buying Winners and Selling Losers》(≈1.1–1.2 万)
  —— 动量奠基 + "跳最近一月避短期反转";12 月动量活信号(避开)+ 留缝出处。
- De Bondt & Thaler 1985, JF,《Does the Stock Market Overreact?》(≈7,900)—— 3–5 年长期反转;36 月依据。
- Gu, Kelly & Xiu 2020, RFS,《Empirical Asset Pricing via Machine Learning》(数千量级,**待核**)
  —— ML 资产定价标杆,mom36m 长窗特征。

**留缝**
- Jegadeesh-Titman 1993(1 月跳 = 主)· MacKinlay 1997, JEL,《Event Studies in Economics and Finance》
  (≈4,700)—— 估计 / 事件窗口隔开;被 1 月跳包含。

**raw vs 超额**
- Gulen & Petkova,《Absolute Strength: Exploring Momentum in Stock Returns》(SSRN,数百量级,**待核**)
  —— 原始绝对收益定义赢家 / 输家;raw 为主的引证。

**波动**(默认无单一论文)
- EWMA:RiskMetrics — Technical Document(J.P. Morgan/Reuters, 1996,**待核**)。
- 下行半离差:Markowitz 1959(书)+ Sortino & van der Meer 1991, JPM(均**待核**)。
- 特异波动:Ang, Hodrick, Xing & Zhang 2006, JF(**待核**)+ Fama & French 1993, JFE(≈28,889)。
- 砍 区间法:Parkinson 1980, JB(≈2,000)/ Garman-Klass 1980, JB(≈1,500)/ Rogers-Satchell 1991
  / Yang-Zhang 2000, JB(数百量级,**待核**)。

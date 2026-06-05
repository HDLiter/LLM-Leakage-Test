# R-1i 文本长度(Text Length,F_len)— 最终决策

**状态**: 锁定 2026-06-04(定义 + 操作化 + 候选池准入)
**结局**: **进入 R-1e 候选池(confirmatory 候选)**
**pilot 闸门**: pilot 若它在密度等因子之外**带不出独立信号**(纯当噪声 / 混杂),
**降级为纯控制变量**(报告里只作背景协变量扣掉、不当主因子),不重开 R-1i 定义。

**审计轨迹**: 本候选池快速轮无独立白板;三步快速判 + 操作化决定内嵌于本文件。

---

## 1. 定义

文本长度量的是:**一篇文章正文有多少字** —— 纯粹的"总量 / 体量",
与事实密度(R1g)是一对镜像:

- **事实密度(F_density,R1g)** 问"单位篇幅里塞了多少硬信息"(浓不浓);
- **文本长度(F_len)** 问"总共有多少字"(多不多)。

| 字段 | 值 |
|---|---|
| 因子类型 | **Type 1**(纯文本属性;把所有模型拿走,"这篇有多少字"还在) |
| 粒度 | **article 级**(同一 article_id → 同一长度,与 focal entity 无关),与 F_template / F_density 同级 |
| 泄露机制链环节 | **③ 可记忆性**(文本**总量**越大 = 可供模型记的东西总量越多;区别于密度的"浓度") |

---

## 2. 双重身份:候选因子 + 天然控制变量

长度是统计里最经典的"麻烦变量"(nuisance covariate)—— 很多别的因子可能都得
**扣掉长度**才干净。故 F_len 有双重身份:

1. **候选因子**:"总量"这个机制(可记忆内容总量)本身是个可测的案例属性 → 按
   confirmatory 候选进池。
2. **控制变量**:同一长度量也是下游因子做混杂控制时**该被扣掉的背景项**。

**pilot 闸门据此设**:若 pilot 显示长度在密度等因子之外**带不出独立的记忆信号**,
R-1e 把它从"主因子"降为"纯控制协变量"(继续算、继续在统计里扣,但不当 headline
因子报告)。near-zero 成本(长度本就作 R1g 分母在算),降级亦不浪费。

---

## 3. 因子值 + 变换

```text
length_chars[article] = 正文字符数(去空白)        # 口径跟随 R1g 分母
F_len[article]        = log1p(length_chars)
```

| 决定 | 值 | 理由 |
|---|---|---|
| **长度口径** | **正文字符数(去空白)** | 零依赖、可复现(不吃 jieba 版本 / 词典差异)、与 agent 标注解耦;**口径跟随 R1g 分母**,两因子共用同一份长度 |
| **变换** | **log1p** | 长度是跨数量级原始计数(短电报几十字 vs 长文上千字),右偏厚尾 → 取对数压一压,同 R-1b/c/f。**与 F_density 反向**:density 是已归一比值用原值,F_len 是原始计数须 log。预登记原值稳健性,pilot 现近正态再切 |
| **零值** | **无零值**(每篇必有正文,length ≥ 1)→ 无零值策略;log1p 选用是为压厚尾、非处理零 |

---

## 4. 稳健性:词数版

| 替代变量 | 测的是 | Slot |
|---|---|---|
| **词数版** | 分母 / 计量单位换"词数"(token 数)而非字符数 —— 长度效应是否依赖字符 vs 词的口径 | Appendix |

**为什么单列词数版(理由升格)**:不只是"换个长度单位看稳不稳"。**词 / token 更贴近
语言模型实际怎么"看"长度** —— 模型按 token 处理,不按字符。故词数版是一个**有认知依据
的替代长度量**,而非单纯的单位敏感性检查。

**分词器跟随 benchmark 路线选择**(与 F_template / R1g §6 **同一道路线耦合**):

- **benchmark 走路线 B**(agent 在选中的几千 case 上分词):词数 = **agent 切词数**。
- **benchmark 走路线 A**(无 agent 分词):词数 = **jieba 切词数**。

**F_len 词数版无"分子-分母对齐"麻烦**(区别于 R1g §6):R1g 须对齐是因为它有分子
(事实颗粒)、分母(长度)两个量,切词会切碎事实颗粒;**F_len 只数一个量**(token 总数),
route A / B 下都是直接数,**不继承 R1g §6 的对齐规则**,两路线下皆纯净。

---

## 5. 区分度检查

| 字段 | 值 |
|---|---|
| 阈值 | **VIF ≥ 10 OR \|r\| ≥ 0.90**(沿用 R-1b/c/d/f/g/h) |
| 比较对象 | vs F_density(R-1g)、vs F_template(R-1d)、vs F_salience / F_recur |
| 预期结果 | 与 density 概念正交(论证见下);正式检查在 pilot |
| 触发后行动 | **R-1e 决定**(无 metric 级 fallback;同 R-1c Option C) |

**概念区分度论证**:
- **vs F_density(R-1g)**:总量 vs 单位密度。R1g §4 专门以归一(除以长度)把 density 与
  F_len 拉开 —— "原始事实计数会与 F_len 高相关,归一是 density 区别于 F_len 的命根"。
  分歧案例:又长又稀的讲话稿(高 F_len + 低 density)vs 又短又密的数据简报(低 F_len +
  高 density)。实操残留相关(长文是否系统性更密 / 更稀)留 pilot 查。
- **vs F_template**:体量 vs 套路度,正交。
- **vs F_salience / F_recur**:那两个是实体级出现频率,F_len 是文本体量,正交。

---

## 6. verdict + 下游锚点

- **进 R-1e 候选池(confirmatory 候选)**;pilot 无独立信号 → 降为纯控制协变量(§2)。
- **R-1e**:不预承诺进 primary;据 pilot 是否带独立记忆信号 + 与 density 区分度决定;
  若降级,以控制协变量身份继续供下游统计使用。
- **F_template / R1g 路线**:词数版稳健性的分词器跟随 benchmark 的 agent-vs-jieba 路线
  选择(§4);F_template 那道 pilot 前操作化审计须知会它**同时牵动 F_len 词数版**。

---

## 7. B-2 schema requirements

`factor_provenance.run_inputs.per_task.text_length`(字段命名 / 风格留 B-2 整体 session):

- `factor_name = text_length`
- `framing_claim = total_text_volume`
- `source_layer = L1_deduplicated_articles`(article content 口径)
- `row_unit = article_id`
- `length_unit_primary = content_char_count`(去空白,跟随 R1g 分母)
- `transform = log1p`(robustness: `raw`)
- `robustness_word_length = follows_R1d_template_route`(B:agent token 数;A:jieba token 数;**单一计数,无分子-分母对齐**;见 §4)
- `zero_policy = none`(每篇必有正文,无零值)
- `discriminant_threshold = {vif: 10, abs_correlation: 0.90}`
- `fallback_policy = no_metric_fallback; defer_to_r1e`
- `pilot_gate = demote_to_control_covariate_if_no_independent_signal`

### Provenance hashes
- S0 source snapshot hash · word-length tokenizer / route manifest hash(when word-length robustness run)
  · layer / view definition hash · sampling manifest hash(when factor values tied to a sampled frame)

---

## 8. 不在 R-1i 范围内

- 词数版分词器的最终路线选择(跟随 F_template;R-4b / pilot 前定)
- R-1e 因子最终选择(R-1i 闭 + pilot 后)
- 长度作控制变量时进哪些下游统计模型(统计层的事,挪 R-4b)

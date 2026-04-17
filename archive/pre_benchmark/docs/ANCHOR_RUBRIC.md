# Anchor Level Rubric
rubric_version: 1.0

Use this rubric to score how strongly a news text could let a model link the text to one specific real-world A-share event, assuming the event was seen in training. Judge only the text shown to the annotator, not metadata, URLs, tags, or outside knowledge. Apply the tree top-down and stop at the first `YES`.

## Operational Definitions

- `Named specific entity`: full company, institution, person, or full document title. A stock code alone does not count.
- `Concrete event`: a filing/headline-level action or outcome such as `拟回购`, `签订合同`, `发布年报`, `被立案`, `收购某公司`. Generic statements such as `业绩下滑`, `景气回升`, or `市场看好` are not concrete.
- `Time anchor`: a time cue inside the text tied to the event, including full dates, relative dates, report periods, or phrases such as `昨日晚间公告`, `本周`, `年报发布日`. Publish-date metadata does not count.
- `Unique locator`: a cue that can nearly hard-match one record, such as a full exact date, a full `《...》` document title, an announcement ID, or a named institution + concrete event + exact amount/count so distinctive that full-text search would return one dominant event.

## Decision Tree

```text
Q1. Does the text contain both a named specific entity and a unique locator?
YES -> Level 3
NO  -> Q2

Q2. Does the text contain all three: one named specific entity, one concrete event, and one time anchor tied to that event?
YES -> Level 2
NO  -> Q3

Q3. Does the text contain some event-bearing clue, but only at class level rather than instance level:
    - generalized/masked entity, or named entity with only vague wording; and
    - vague event/result, with no usable time anchor?
YES -> Level 1
NO  -> Q4

Q4. After rejecting Q1-Q3, is the text still non-identifying: market roundup, ETF/fund marketing,
    recurring template content, broad trend summary, or named entity mention without a concrete event?
YES -> Level 0
NO  -> Level 0
```

## Examples

### Level 3

1. Typical: `2024年4月12日，国务院发布《关于加强监管防范风险推动资本市场高质量发展的若干意见》，资本市场新“国九条”落地。`
   Rationale: Full date plus full document title uniquely pins one policy release, so it is not merely a strong anchor.
2. Edge: `《关于进一步减轻义务教育阶段学生作业负担和校外培训负担的意见》印发，教育股集体下挫。`
   Rationale: Even without an explicit date, the full titled document is a unique searchable identifier, so it stays at Level 3.

### Level 2

1. Typical: `宁德时代昨日晚间公告，拟使用不超过50亿元回购股份。`
   Rationale: It names the company, the event, and a time anchor, but lacks a unique locator such as a full date or announcement ID.
2. Edge: `招商银行在年报发布日披露，拟发行二级资本债补充资本。`
   Rationale: `年报发布日` is a valid time anchor tied to a concrete event, but it is not unique enough for Level 3.

### Level 1

1. Typical: `某头部券商业绩下滑，投行业务承压。`
   Rationale: The entity and event are both generic classes, so the text suggests an event type but not one identifiable case.
2. Edge: `隆基绿能业绩承压，光伏价格战拖累盈利。`
   Rationale: A named company alone does not lift the case above Level 1 when the event wording is still vague and untimed.

### Level 0

1. Typical: `今日两市成交额放量，AI与半导体板块轮动走强。`
   Rationale: This is a daily market roundup with no case-level anchor to one real-world event.
2. Edge: `某ETF紧跟红利主线，低费率布局央国企高股息机会。`
   Rationale: Marketing copy names an investment theme, not a discrete historical event, so it remains Level 0.

## Prohibited Shortcuts

- Do not use `publish_time`; only time cues written inside the text count.
- Do not treat a stock code as Level 3; a code identifies an entity, not a unique event.
- Do not treat numbers alone as anchors; percentages, price moves, and generic amounts do not identify one event by themselves.
- Do not upgrade for an institution name alone; Level 2/3 requires institution + concrete event, and Level 2 also needs a time anchor.
- Do not apply a bias such as "prefer lower" or "prefer higher"; follow the tree mechanically.

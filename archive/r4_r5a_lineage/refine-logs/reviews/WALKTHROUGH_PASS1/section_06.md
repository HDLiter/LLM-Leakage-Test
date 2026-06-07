# Pass 1 Walk-through — 第 6 章 / 共 7 章:工作流 WS0 → WS5

> 供 Codex 连贯性审查器读取。审查任务严格限定:只指出自相矛盾、逻辑断点、
> 追溯不到研究问题的步骤;禁止提新机制、新严谨度、改进建议。

## 七条工作流

- WS0 搭骨架:代码骨架 + 配置(模型清单/运行参数)+ 冒烟工具。地基,
  不依赖任何人,最先开工。
- WS0.5 算因子:每条新闻的 4 因子值(事件分类/实体抽取/复现计数/标的
  显著度)。Thales prompt 对接 + 因子计算管线。
- WS1 P_logprob 管线("看模型反应",白盒逐 token 意外度)。
- WS2 P_predict 管线("让模型预测",14 模型方向+信心,解析)。
- WS3 造扰动 + 人工审计(C_FO 换假结果 / C_NoOp 塞杂讯)。
- WS4 跑 pilot(冻结 780 案例清单,跑算子,产出结果表)。
- WS5 pilot 统计 + 预注册。

## 依赖

WS0 → (WS0.5 / WS1 / WS2 / WS3 四条并行) → WS4 → WS5。
WS0 必须最先;中间四条并行(例外:WS3 造 C_FO 需先取 WS0.5 事件类型标签);
WS4 等四条全好;WS5 接 WS4。

## 两道可行性闸门

ML Engineer feasibility gate ×2:WS0 骨架建完后 / WS1-3 冒烟后正式 pilot 前。
与用户的 implementation-first / 可行性优先理念一致——计划管路结构有此意识。

## WS0.5 位置

WS0 之后、与 WS1/2/3 并排的"算因子"支线;必须先于 WS4 关闭(pilot 需因子
值分层 / 查 n_eff);也是 WS3 上游。是与"重开操作化层"纠缠最深的一条。

## 重开叠加到工作流图(依赖地图)

- WS0:不受影响,基本完成(接口 memo 2026-04-26 签字、runstate 等已落地)。
- WS1:不受影响,跑得最靠前(算子层,与因子/扰动/预测目标重开不沾边;
  AutoDL 云上推进中)。最安全支线。
- WS2:部分受影响——管线骨架稳;flag ⑥(R-6 预测目标)定了才能完全锁。
- WS0.5:在重开区正中央(R-1 因子实现+选择重审);design-agnostic 基建
  可并行,指标定义不提交、memo 不签。
- WS3:在重开区(R-2 扰动重审;且本就在 WS0.5 下游)。
- WS4/WS5:下游顺延;pilot 依赖 WS0.5+WS3(均在重开区)→ pilot 开跑随
  重开后推。

关键区分:工作流"管路"健全(切分合理/并行清楚/有可行性闸门/WS0.5 先于
WS4);被重开的是管路里流的内容(因子/扰动/预测目标定义),非管路本身。

## 本章 flag

flag ⑤ 扩展:phase7 plan 除 N=100/N=430 外,还有 "9-model / nine-model"
过时数字——§5.1 WS0 可行性闸门 "nine-model P_predict smoke / all 9 models"、
§5.3 标题 "WS2: P_predict nine-model pipeline";fleet 已扩到 14 P_predict-
eligible。同一批"扩 fleet/扩 pilot 前遗留数字",一起修。
其余无新硬 flag——工作流结构连贯。

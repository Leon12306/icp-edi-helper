# icp-edi-helper — ICP/EDI 经营许可办理 SOP 手册

> **Boss Claw 内置能力** · 企商链 OPC 平台 · 版本 v1.8

## 这是什么

一个给 **Boss Claw** 平台内置的 ICP/EDI 经营许可办理 SOP 手册。让加盟商即使不懂企服行业，也能像资深服务商一样指导客户办理 ICP 或 EDI 许可证。

> ⚠️ 客户不会直接使用这个技能。客户咨询加盟商，加盟商遇到问题才咨询 Boss Claw。

## 适用人群

| 角色 | 使用目的 |
|------|---------|
| **服务商**（懂业务） | 减少查找资料、回复咨询的时间，快速给方案 |
| **加盟商**（不懂或一知半解） | 提高成单转化率——专业地引导客户到他这里代办资质 |
| **平台管理人员** | 减少重复操作，统一服务标准 |

## 核心目标

**提升加盟商专业性，指导其如何与客户沟通，让客户到加盟商处代办资质。**

转化逻辑：加盟商用这个技能获取话术、模板、流程 → 专业地跟客户沟通 → 客户觉得"自己搞太麻烦"→ 主动找加盟商代办 → 加盟商获利。

## 触发词

ICP许可证、EDI许可证、ICP备案、增值电信业务、ICP证、EDI证、经营性网站、平台入驻

## 快速使用

```
1. 输入客户业务类型 → 获得推荐的资质类型（ICP/EDI/备案）
2. 输入省份 → 获得该省办理入口和特殊要求
3. 输入"要模板" → 获得可编辑的材料模板
4. 输入"变更/续期/注销" → 获得对应流程和表单
```

## 目录结构

```
icp-edi-helper/
├── SKILL.md                      # 主流程 SOP（6步法）
├── README.md                     # 使用说明（本文件）
└── references/
    ├── overview.md               # ICP/EDI 全国通用指南
    ├── edi-knowledge.md          # EDI 独立知识库
    ├── licensing-changes.md      # 变更/续期/注销
    ├── provincial-authorities.md # 31省官网+电话
    ├── province-comparison.md    # 各省差异对照
    ├── provinces/                # 31省详细办理指南（独立文件）
    │   ├── anhui.md
    │   ├── beijing.md
    │   ├── shanghai.md           # 上海内容最丰富（外资试点等）
    │   └── ...（共31个省份）
    └── templates/
        ├── icp-templates.md      # 可研报告、安全制度模板
        └── icp-form-checklist.md # 新业务表单 + 变更表单全部字段清单
```

**使用方式：**
- 查全国通用信息 → `references/overview.md`
- 查某省详情 → `references/provinces/{省份}.md`（如 `references/provinces/guangdong.md`）
- 查各省差异 → `references/province-comparison.md`
- 查官网电话 → `references/provincial-authorities.md`
- 查表单字段 → `references/templates/icp-form-checklist.md`（新业务 + 变更）
- 查材料模板 → `references/templates/icp-templates.md`

## 当前覆盖

| 资质 | 状态 |
|------|------|
| ICP/EDI 许可证（新业务） | ✅ 完成 |
| ICP/EDI 变更/续期/注销 | ✅ 完成 |
| 表单模板（新业务 + 变更） | ✅ 完成 |
| 31省办理指南 | ✅ 完成 |
| 各省差异对照 | ✅ 完成 |
| 各省官网+电话 | ✅ 完成 |
| 关键词映射 | ✅ 完成 |

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.8 | 2026-06-03 | 删除"各省代办费用参考"表，删除关键结论中的代办费用引用。技能名称改为 `icp-edi-helper`。 |
| v1.7 | 2026-06-03 | 聚焦 ICP/EDI：删除其他 9 类资质占位行，标题和描述统一为 ICP/EDI 经营许可办理。 |
| v1.6 | 2026-06-03 | 内部文件归拢：`pattern-acroform-pdf-extraction.md` 移入 `.internal/`。 |
| v1.5 | 2026-06-03 | 变更表单补充：新增 10 类变更专用表单 + 15 类业务开展情况表 + 7 类选填承诺书。 |
| v1.4 | 2026-06-03 | 新增 icp-form-checklist.md：27 页新业务表单完整字段提取。 |
| v1.3 | 2026-06-03 | 内容去重：删除 overview.md 中重复的代办费和官网表。 |
| v1.2 | 2026-06-03 | 新增 references/ 组织原则规范。 |
| v1.1 | 2026-06-03 | 目录结构重组：31 省拆为 provinces/ 子目录独立文件。 |
| v1.0 | 2026-06-03 | 初始版本。覆盖 ICP/EDI 全量知识库 + 31 省指南。 |

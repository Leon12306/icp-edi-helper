# references/ 索引 — AI 5秒决策树

> **AI 加载顺序**：先看本文件，按用户输入关键词定位到要读的 1-2 个文件即可。**不要全部加载**，避免浪费上下文。

---

## 决策树（按用户问题定位）

```
用户问什么？
│
├─ "做什么业务要办什么证" / "我网站要办吗"
│  └─ → references/license-keyword-map.md
│  └─ → references/overview.md（第二节 ICP vs EDI 快速判断）
│
├─ 给企业名称 / 统一社会信用代码
│  └─ → 运行 scripts/query_company.py "企业名称"
│  └─ → 看完结果直接进 references/overview.md 第三条对照硬性条件
│
├─ 通用问题：硬性条件 / 通用流程 / 罚款 / 入口
│  └─ → references/overview.md
│
├─ ICP 与 EDI 有什么区别
│  └─ → references/edi-knowledge.md
│
├─ 变更/续期/注销/年报
│  └─ → references/licensing-changes.md
│
├─ 某省电话 / 某省官网
│  └─ → references/provincial-authorities.md（一行一省表）
│
├─ 某省具体要求（材料、流程、特殊规定）
│  └─ → references/provinces/{省拼音}.md
│     （如：广东→guangdong.md，北京→beijing.md）
│
├─ 31 省差异 / 哪家最快 / 哪家严
│  └─ → references/province-comparison.md
│
├─ 写材料没思路 / 要模板
│  └─ → references/templates/icp-templates.md
│
├─ 在线表单怎么填 / 字段说明
│  └─ → references/templates/icp-form-checklist.md
│
└─ 不确定 / 兜底
   └─ → references/overview.md（默认起点）
```

---

## 文件清单（每个文件只负责一个主题）

| 文件 | 主题 | 何时读 |
|------|------|--------|
| `overview.md` | ICP/EDI **全国通用**指南（核心） | 默认起点，90% 问题先看这 |
| `edi-knowledge.md` | EDI 独立知识库（EDI 与 ICP 的差异） | 客户问 EDI 特有材料 |
| `licensing-changes.md` | 变更/续期/注销/年报 | 客户已办证，需变更 |
| `license-keyword-map.md` | 用户口语 → 资质映射 | 客户描述业务不确定办什么 |
| `provincial-authorities.md` | 31 省电话+官网表 | 查电话/官网 |
| `province-comparison.md` | 跨省差异 | 客户在多个省之间比较 |
| `provinces/{拼音}.md` | 单省详情 | 客户指定某个省 |
| `templates/icp-templates.md` | 材料模板（可研报告、安全制度等） | 客户不会写材料 |
| `templates/icp-form-checklist.md` | 在线表单字段清单 | 客户不会填表 |
| `index.md` | 本文件 — 决策树 | **每次先读这个** |

---

## 单省文件速查（拼音索引）

| 拼音 | 文件 | 拼音 | 文件 |
|------|------|------|------|
| 北京 | beijing.md | 河北 | hebei.md |
| 天津 | tianjin.md | 山西 | shanxi.md |
| 上海 | shanghai.md | 内蒙古 | neimenggu.md |
| 重庆 | chongqing.md | 辽宁 | liaoning.md |
| 黑龙江 | heilongjiang.md | 吉林 | jilin.md |
| 江苏 | jiangsu.md | 浙江 | zhejiang.md |
| 安徽 | anhui.md | 福建 | fujian.md |
| 江西 | jiangxi.md | 山东 | shandong.md |
| 河南 | henan.md | 湖北 | hubei.md |
| 湖南 | hunan.md | 广东 | guangdong.md |
| 广西 | guangxi.md | 海南 | hainan.md |
| 四川 | sichuan.md | 贵州 | guizhou.md |
| 云南 | yunnan.md | 西藏 | xizang.md |
| 陕西 | shaanxi.md | 甘肃 | gansu.md |
| 青海 | qinghai.md | 宁夏 | ningxia.md |
| 新疆 | xinjiang.md | | |

> 省文件中**不重复**列硬性条件/材料清单/办理流程，公共内容统一在 `overview.md`。

---

## 触发词（命中后调对应的）

| 客户说 | 命中文件 |
|--------|---------|
| ICP / ICP许可证 / 网站许可证 | overview.md + edi-knowledge.md |
| EDI / EDI许可证 / 平台许可证 | edi-knowledge.md |
| 增值电信业务 / 增值电信业务许可证 | overview.md |
| ICP备案 / 备案 | overview.md（看"自营不收费"分支） |
| 外资 / 100% / 港澳 | provincial-authorities.md（查 4 个试点省）+ overview.md |
| 续期 / 变更 / 注销 / 年报 | licensing-changes.md |
| 加盟商话术 / 客户问题 | overview.md + edi-knowledge.md |
| 模板 / 怎么写 / 怎么填 | templates/icp-templates.md + templates/icp-form-checklist.md |

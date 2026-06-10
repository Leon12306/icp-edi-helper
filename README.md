# icp-edi-helper — 项目说明（给人类维护者）

> 企商链 Boss Claw 平台内置技能 · ICP/EDI 经营许可办理 SOP
>
> 📌 **你是人不是 AI**？那你来对地方了——这是项目的"开发者文档"。AI 加载的是 `SKILL.md`（精简操作手册），那份不要塞版本历史/踩坑经验。

## 一句话定位

让加盟商即使不懂企服行业，也能像资深服务商一样指导客户办理资质。

## SKILL.md vs README.md（明确分工）

| 维度 | SKILL.md（AI 加载） | README.md（人类看） |
|------|---------------------|---------------------|
| 读者 | AI 加盟商辅助 | 项目维护者、新加入开发者 |
| 长度 | 精简（≤ 230 行） | 详细（按需） |
| 内容 | 6 步流程 + 决策树 + 索引 | 版本历史 + 踩坑 + 目录结构 + 维护指南 |
| 何时加载 | AI 每次执行任务 | 人类 PR 维护时阅读 |
| 不应包含 | 版本历史、踩坑、文件结构详细图 | 操作话术、SOP 步骤 |

**简单说**：SKILL.md 是给 AI 用的"操作手册"，README.md 是给人类维护者用的"项目说明"。两者不重复。

## 目录结构

```
icp-edi-helper/
├── SKILL.md                       # AI 加载的精简操作手册
├── README.md                      # 本文件 — 人类维护者参考
├── .env.example                   # 企查查密钥配置模板
├── .gitignore                     # 保护 .env + 采集器输出
├── scripts/
│   └── query_company.py           # 企查查企业信息查询 + ICP/EDI 条件评估
├── province-fetcher/              # 31省官方办事指南自动采集器（v2.1+）
│   ├── README.md
│   ├── data/provinces_meta.json   # 31省通管局元数据
│   ├── scripts/                   # 5 个 Python 脚本
│   └── output/                    # 采集结果（git ignore）
└── references/
    ├── index.md                   # AI 5秒决策树（v2.2 新增）
    ├── overview.md                # ICP/EDI 全国通用指南（核心）
    ├── edi-knowledge.md           # EDI 独立知识库
    ├── licensing-changes.md       # 变更/续期/注销
    ├── license-keyword-map.md     # 用户口语 → 资质映射
    ├── provincial-authorities.md  # 31省电话表（一行一省）
    ├── province-comparison.md     # 跨省差异（无重复电话）
    ├── provinces/                 # 31省文件（每个文件只含省特异）
    └── templates/                 # 材料模板 + 表单字段
```

## 维护指南

### references/ 组织原则（v2.2 重申）

整理自 v1.1 → v2.2 的踩坑经验，**新增资质/省份时必须遵守**：

1. **禁止把多个主题堆在一个大文件里**。例如 31 省指南拆成 31 个独立文件（`provinces/` 子目录）。AI 加载整个文件浪费上下文，改一个省要动全文件。

2. **同一类数据只存在于一个文件中**：
   - 各省电话 → `provincial-authorities.md`
   - 各省差异 → `province-comparison.md`
   - 各省特异条款 → `provinces/{拼音}.md`
   - 硬性条件、未办后果等通用信息 → `overview.md`
   - 31 个省文件中**不允许重复列**硬性条件/材料清单/办理流程——用 `见 xxx.md` 引用。

3. **内部文件用 `.internal/` 隔离**。工作流脚本、采集脚本、临时草稿不应让 AI 在 `skill_view` 时看到。

4. **模板放 `templates/` 目录**，不归在 `references/` 根目录。

5. **省份级文件用 `provinces/` 子目录**。文件名用拼音：`guangdong.md`、`shanghai.md`。

6. **不要收录市场参考价数据**。代办费、中介报价等市场数据变动频繁、来源不可靠、官方不公布。放入正式手册会带来维护负担。

### v2.2 重构变更（重要）

| 变更 | 原因 |
|------|------|
| 31 个省份文件从 65 行 → 25-30 行 | 公共内容已迁移到 overview.md，省文件中只保留省特异+电话 |
| 公共内容用 `见 xxx.md` 引用 | AI 减少重复读取，节省上下文 |
| 新增 `references/index.md` | AI 5 秒决策树，按用户输入关键词快速定位文件 |
| 合并 `provincial-authorities.md` + `province-comparison.md` | 之前两个文件都列电话表，重复 |
| SKILL.md 删除版本历史和踩坑经验 | 这些只给维护者看，AI 加载浪费上下文 |
| SKILL.md 顶部加"AI 5 秒决策树" | 让 AI 第一眼就找到要读哪个文件 |

### 31 省文件标准结构

```markdown
# {省名} — 增值电信业务经营许可证办理指南

> 数据来源：{省通信管理局} + 工信部政务服务平台

## 一、基本信息
| 项目 | 内容 |
| 实施主体 | {省通信管理局} |
| 咨询电话 | {电话} |
| 网上办理入口 | https://ythzxfw.miit.gov.cn |

## 二、省特异条款（如有）
- {该省独有要求}

## 三、受理条件 / 申请材料 / 办理流程 / 费用周期
→ 见 `references/overview.md`（第 X 条）
```

## 当前覆盖（2026-06-09）

| 模块 | 状态 | 文件 |
|------|------|------|
| ICP/EDI 许可证（新业务） | ✅ | `references/overview.md` |
| EDI 独立知识库 | ✅ | `references/edi-knowledge.md` |
| ICP/EDI 变更/续期/注销 | ✅ | `references/licensing-changes.md` |
| 表单模板（新业务 + 变更） | ✅ | `references/templates/icp-templates.md` + `icp-form-checklist.md` |
| 31省办理指南 | ✅ | `references/provinces/*.md`（31 个独立文件） |
| 各省差异对照 | ✅ | `references/province-comparison.md` |
| 各省官网+电话 | ✅ | `references/provincial-authorities.md` |
| 关键词映射 | ✅ | `references/license-keyword-map.md` |
| 企查查企业查询 | ✅ | `scripts/query_company.py` |
| **官方指南自动采集（v2.1）** | ✅ 19/29 绿 | `province-fetcher/` |

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.2 | 2026-06-09 | **去重 + AI 可读性重构**：① SKILL.md 删除版本历史和踩坑经验（移到 README），加 5 秒决策树；② 31 个省份文件从 65 行压缩到 25-30 行（公共内容用引用代替重复）；③ 新增 `references/index.md` AI 决策树；④ 合并 `provincial-authorities.md` + `province-comparison.md` 重复电话表；⑤ SKILL.md 与 README.md 明确分工。 |
| v2.1 | 2026-06-08 | 新增 `province-fetcher/` 31省官方办事指南自动采集器：白名单 `miit.gov.cn` 体系、HTML+PDF 双路径解析、表格化"事项清单"页面回退、总览页检测、跨省一致性校验、🟢🟡🟠🔴 4 档质量分级。覆盖 29/31 省（河南/四川无独立指南页已标注），🟢 绿色省份从 5 → 19。 |
| v2.0 | 2026-06-04 | 质量治理：内容去重 + 聚焦 ICP/EDI + 话术补全 + 外资试点 + 企查查增强。 |
| v1.9 | 2026-06-03 | 新增企查查 API 企业查询。 |
| v1.8 | 2026-06-03 | 删除"各省代办费用参考"表。技能改名 `icp-edi-helper`。 |
| v1.7 | 2026-06-03 | 聚焦 ICP/EDI，删除其他资质占位。 |
| v1.6 | 2026-06-03 | 内部文件移入 `.internal/`。 |
| v1.5 | 2026-06-03 | 变更表单补充。 |
| v1.4 | 2026-06-03 | 新增表单字段清单。 |
| v1.3 | 2026-06-03 | 内容去重，改为跨文件引用。 |
| v1.2 | 2026-06-03 | 新增组织原则规范（踩坑经验编码）。 |
| v1.1 | 2026-06-03 | 目录结构重组。 |
| v1.0 | 2026-06-03 | 初始版本。 |

## 踩坑经验（教训记录）

整理 v1.0 → v2.2 的踩坑，避免重蹈覆辙：

1. **SKILL.md 不要塞版本历史** — 每次 AI 加载都重复读，浪费上下文且容易让 AI 误以为版本号对当前任务有意义。
2. **省文件中不要重复列硬性条件/材料清单/办理流程** — 全国统一的内容统一在 `overview.md`，省文件中只保留省特异条款（如河北的扫描件要求、上海的外资试点）。
3. **电话表不要同时存在于 `provincial-authorities.md` 和 `province-comparison.md`** — 之前两个文件都列电话表，重复且维护困难。v2.2 已合并。
4. **不要收录市场参考价** — 代办费、中介报价等市场数据变动频繁、来源不可靠。v1.8 已删除。
5. **大文件拆成小文件** — 31 省指南不要塞一个 2400 行的 `province-guides.md`，AI 加载整个浪费上下文。
6. **省文件名用拼音** — `guangdong.md` 而不是 `province-guangdong.md` 或 `广东省.md`。AI 路径匹配更稳。
7. **.internal/ 隔离内部文件** — 工作流笔记、踩坑经验、PDF 提取技巧等不应让 AI 在 `skill_view` 时看到。
8. **电话正则要容忍 0-12 字符标点间隔** — 工信部页面 "联系电话\n021-xxxx" 这种格式用 `联系电话\s*` 是匹配不到后面电话的。v2.1 已修。
9. **办结时限正则要 17+ 模式** — 各省写法差异巨大（"X 日内作出是否准予" / "X 日内形成初审意见" / "X 日内一次性退回补正" 等）。
10. **PDF 路径不能漏** — 上海 PDF 只到"许可证申请条件"，范围太窄是数据问题不是解析问题。

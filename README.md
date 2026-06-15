# icp-edi-helper — 项目说明

> 企商链 Boss Claw 平台内置技能 · ICP/EDI 经营许可办理 SOP
>
> 📌 **你是人不是 AI**？那你来对地方了——这是项目的"开发者文档"。AI 加载的是 `SKILL.md`（精简操作手册），那份不要塞版本历史/踩坑经验。

## 一句话定位

让加盟商即使不懂企服行业，也能像资深服务商一样指导客户办理资质。

## 📦 独立分发说明

v2.3 起，本技能包是**自包含、可独立分发**的：

- ✅ 整个目录可直接 `cp -r` 到其他 AI 平台（Claude Code / Cursor / Trae / Cline / 任何支持 Skill 的工具）
- ✅ 无外部依赖（除可选的企查查 API 和 province-fetcher 的 PDF 解析）
- ✅ 业务内容、文档、脚本、校验全在目录内
- ❌ 不需要再创建 `output/` 或 `*.bak*` 副本目录

分发到其他 AI 平台后，参考 [快速启动](#快速启动) 一节即可。

---

## SKILL.md vs README.md（明确分工）

| 维度 | SKILL.md（AI 加载） | README.md（人类看） |
|------|---------------------|---------------------|
| 读者 | AI 加盟商辅助 | 项目维护者、新加入开发者 |
| 长度 | 精简（≤ 230 行） | 详细（按需） |
| 内容 | 6 步流程 + 决策树 + 索引 | 版本历史 + 踩坑 + 目录结构 + 维护指南 |
| 何时加载 | AI 每次执行任务 | 人类 PR 维护时阅读 |
| 不应包含 | 版本历史、踩坑、文件结构详细图 | 操作话术、SOP 步骤 |

**简单说**：SKILL.md 是给 AI 用的"操作手册"，README.md 是给人类维护者用的"项目说明"。两者不重复。

---

## 快速启动

### 给 AI 平台使用

```bash
# 1. 复制整个项目到目标位置
cp -r icp-edi-helper/ ~/my-ai-skills/icp-edi-helper/

# 2. （可选）配置企查查 API 密钥
cd ~/my-ai-skills/icp-edi-helper/
cp .env.example .env
# 填入 QCC_APP_KEY / QCC_SECRET_KEY

# 3. 验证技能包完整性
bash scripts/validate-skill.sh
# 期望输出：26 PASS / 0 WARN / 0 FAIL
```

### 给加盟商使用

```bash
# 直接由 Boss Claw 平台 AI 加载 SKILL.md
# AI 内部按 references/index.md 决策树自动路由
# 加盟商无需直接操作文件
```

---

## 目录结构

```
icp-edi-helper/
├── SKILL.md                       # AI 加载的精简操作手册
├── AGENTS.md                      # AI 协作执行规则（v2.3 新增）
├── README.md                      # 本文件 — 人类维护者参考
├── CHANGELOG.md                   # 完整变更日志
├── package.json                   # 技能元数据（v2.3 新增）
├── .env.example                   # 企查查密钥配置模板
├── .gitignore                     # 保护 .env + 采集器输出
├── examples/                      # 用例样例（v2.3 新增）
│   ├── usage.md                   # 标准用例 + 触发词矩阵
│   └── edge-cases.md              # 异常输入用例
├── scripts/
│   ├── query_company.py           # 企查查企业信息查询 + ICP/EDI 条件评估
│   ├── _refactor_provinces.py     # 一次性重构脚本（v2.1 期间）
│   └── validate-skill.sh          # 技能包质量门禁（v2.3 新增）
├── reports/                       # QA 报告（validate-skill.sh 产物）
│   ├── qa-report.md
│   └── qa-report.json
├── province-fetcher/              # 31省官方办事指南自动采集器（v2.1+）
│   ├── README.md
│   ├── data/provinces_meta.json
│   ├── scripts/                   # 5 个 Python 脚本
│   └── output/                    # 采集结果（git ignore）
└── references/
    ├── index.md                   # AI 5秒决策树
    ├── overview.md                # ICP/EDI 全国通用指南（核心）
    ├── edi-knowledge.md           # EDI 独立知识库
    ├── licensing-changes.md       # 变更/续期/注销
    ├── license-keyword-map.md     # 用户口语 → 资质映射
    ├── provincial-authorities.md  # 31省电话表（一行一省）
    ├── province-comparison.md     # 跨省差异（无重复电话）
    ├── workflow.md                # 6 步法详细（v2.3 新增，吸收 SKILL.md 下沉内容）
    ├── quality-checklist.md       # 质量验收清单（v2.3 新增）
    ├── error-handling.md          # 错误处理分级 E1-E5（v2.3 新增）
    ├── qcc-api-guide.md           # 企查查 API 详细（v2.3 新增）
    ├── provinces/                 # 31省文件（每个文件只含省特异）
    └── templates/                 # 材料模板 + 表单字段
```

---

## 维护指南

### references/ 组织原则（v2.2 起，新资质/省份时必须遵守）

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

6. **不要收录市场参考价数据**。代办费、中介报价等市场数据变动频繁、来源不可靠、官方不公布。

7. **不要写 `output/` 或 `*.bak*` 副本**。v2.3 起技能包自包含，所有交付物原地修改。进度跟踪写在交付汇报中，不写文件。

### v2.3 变更（结构性升级）

| 变更 | 原因 |
|------|------|
| 新增 `AGENTS.md` | AI 协作规则（任务识别/澄清/读写/汇报）独立成文 |
| 新增 `package.json` | 技能元数据规范化（name/version/keywords/entry/files） |
| 新增 `examples/usage.md` + `edge-cases.md` | 7 个典型用例（标准/异常/边界场景） |
| 新增 `references/{workflow,quality-checklist,error-handling,qcc-api-guide}.md` | 把 SKILL.md 长内容下沉 |
| 新增 `scripts/validate-skill.sh` | 26 项自动质量门禁（可接 CI） |
| 精简 `SKILL.md` | 从 223 行 → 116 行，AI 加载效率 +50% |
| 去掉 `references/recovery.md` | 进度跟踪统一在交付汇报中，不写文件 |
| **自包含可独立分发** | 整个目录可复制到任何 AI 平台直接使用 |

### v2.2 重构变更

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

---

## 当前覆盖（2026-06-15）

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
| 6 步法详细 | ✅ | `references/workflow.md`（v2.3 新增） |
| 企查查 API 详细 | ✅ | `references/qcc-api-guide.md`（v2.3 新增） |
| 质量验收 | ✅ | `references/quality-checklist.md`（v2.3 新增） |
| 错误处理分级 | ✅ | `references/error-handling.md`（v2.3 新增） |
| 企查查企业查询 | ✅ | `scripts/query_company.py` |
| 用例样例 | ✅ | `examples/{usage,edge-cases}.md`（v2.3 新增） |
| 质量门禁脚本 | ✅ | `scripts/validate-skill.sh`（v2.3 新增） |
| 官方指南自动采集（v2.1） | ✅ 19/29 绿 | `province-fetcher/` |

---

## 版本历史

完整变更记录见 [CHANGELOG.md](./CHANGELOG.md)。

## 踩坑经验（教训记录）

整理 v1.0 → v2.3 的踩坑，避免重蹈覆辙：

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
11. **不要写 `output/` 或 `*.bak*` 副本** — 技能包要自包含、可独立分发。v2.3 已改为原地修改。

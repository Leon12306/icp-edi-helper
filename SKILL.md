---
name: icp-edi-helper
<<<<<<< HEAD
description: Use when franchisees or service providers need to guide clients through ICP/EDI license applications, handle renewals/changes/cancellations, look up company registration info via Qichacha API, or find province-specific filing procedures. Triggered by mentions of ICP许可证, EDI许可证, 增值电信业务, 经营性网站, 平台入驻资质, or 企查查企业查询.
tags: [sales, government-service, multi-license, bossclaw, franchise-enablement, sop-manual, versioned, qcc-api]
version: 2.0
last_updated: 2026-06-04
=======
description: 企商链 Boss Claw 平台内置的 ICP/EDI 经营许可办理 SOP 手册。为服务商、加盟商、平台管理人员提供专业指导，提升加盟商对客户的沟通能力与成单转化率。覆盖 ICP/EDI 新业务申请、变更、续期全流程。支持企查查 API 自动查询企业工商信息。
tags: [sales, government-service, icp-edi, bossclaw, franchise-enablement, sop-manual, qcc-api]
version: 2.2
last_updated: 2026-06-09
>>>>>>> dev
---

# ICP/EDI 经营许可办理 SOP

> 适用平台：Boss Claw（企商链 OPC） · 服务商/加盟商/平台管理人员使用
> 客户**不直接使用**这个技能——客户咨询加盟商，加盟商遇到问题才咨询 Boss Claw

---

## 0. AI 5 秒决策树（先看这个）

| 客户说... | 跳过到 |
|----------|--------|
| "我想知道要办什么证" / "做什么业务要不要办" | [第1步](#第1步了解客户生意--推荐证) |
| 给企业名称 / 统一社会信用代码 | [企查查 API](#-企业信息自动查询企查查-api) |
| 询问某个省的具体要求 | `references/provinces/{省拼音}.md`（如 `references/provinces/guangdong.md`） |
| 询问 31 省差异 / 哪家最快 | `references/province-comparison.md` |
| 询问某省电话 / 官网 | `references/provincial-authorities.md` |
| 要模板 / 表单字段 | `references/templates/icp-templates.md` + `references/templates/icp-form-checklist.md` |
| 询问 EDI 与 ICP 区别 | `references/edi-knowledge.md` |
| 变更/续期/注销 | `references/licensing-changes.md` |
| 硬性条件 / 罚款金额 / 通用流程 | `references/overview.md` |
| 不知道在哪办 / 不确定省份 | `references/overview.md` 第一条 |

> **少读多引用**：每份文件只读一次。重复内容已经在 v2.2 集中到 `overview.md`，其余文件用 `见 xxx.md` 引用。

---

## 1. 整体流程（6 步法）

```
第1步  客户做什么生意 → 推荐证（获取弹药）
第2步  3 个问题 → 判断要不要办（确认需求）
第3步  硬性条件 → 客户能不能办（评估能力）
第4步  材料清单 → 给客户模板（提供弹药）
第5步  哪点哪 → 一步步教客户提交（指导操作）
第6步  拿到证 → 提醒续期/变更（售后维护）
```

**有企业名称时**：第 2 + 3 步直接用 `scripts/query_company.py` 一键评估，跳过逐项追问。

---

## 第1步：了解客户生意 → 推荐证

| 客户业务 | 推荐证 | 一句话话术 |
|----------|--------|-----------|
| 网站/小程序，用户付费 | ICP许可证 | "你这个属于经营性网站，需要办 ICP 许可证" |
| 平台让商家入驻卖货 | EDI许可证 | "你这个是平台模式，需要办 EDI 许可证" |
| 自己卖货的官网 | ICP备案 | "自营官网只需要做 ICP 备案，免费" |
| 不确定 | [判断逻辑](#判断逻辑--icp-edi-快速判断) | |

### 判断逻辑 — ICP/EDI 快速判断

| 你的业务 | 需要的证 |
|---------|---------|
| 自营电商（自己卖货） | ICP备案 |
| 内容付费/会员制 | ICP许可证 |
| 分类信息/招聘/广告平台 | ICP许可证 |
| 第三方商家入驻 | EDI许可证 |
| 在线数据处理/订单处理 | EDI许可证 |
| 企业官网（不收费） | ICP备案 |

更多口语映射 → `references/license-keyword-map.md`

---

## 🔍 企业信息自动查询（企查查 API）

**当加盟商给了客户公司名称或统一社会信用代码时，Boss Claw 必须调用 `scripts/query_company.py` 自动评估，无需逐项追问。**

<<<<<<< HEAD
### ⚙️ 前置配置（一次性）
=======
### 调用方式
>>>>>>> dev

```bash
# 1. 一次性配置密钥（推荐 .env）
cp .env.example .env
<<<<<<< HEAD
# 编辑 .env，填入企查查 AppKey 和 SecretKey
```

> ⚠️ `.env` 已加入 `.gitignore`，不会被提交。

### ▶️ 调用方式

```bash
# 基本查询
=======
# 填入 QCC_APP_KEY / QCC_SECRET_KEY

# 2. 查询
>>>>>>> dev
python3 scripts/query_company.py "杭州某某科技有限公司"
python3 scripts/query_company.py "企业名称" --json    # 程序化输出
```

### 自动评估项

| 检查项 | API 可查 | 不满足时话术 |
|--------|---------|------------|
| 💰 注册资本 ≥ 100万 | ✅ | "注册资本不够可做工商增资，3 天搞定" |
| 🏢 有限责任公司 | ✅ | "个体户不行，需注册有限公司" |
| 📋 经营范围含"增值电信业务" | ✅ | "经营范围没这个，需变更（5-7 天）" |
| ✅ 登记状态存续 | ✅ | "公司状态不对，需先恢复正常" |
| 🌐 外资情况 | ✅ | 试点省（北京/上海/浙江/海南）：外资可达100%<br>其他省：需走额外审批 |
| 3 名员工社保 | ❌ 需问 | — |
| 域名在公司名下 | ❌ 需问 | — |
| 已完成 ICP 备案 | ❌ 需问 | — |
| 网站可访问 | ❌ 需问 | — |

### 与 6 步法衔接

- **第2步**（判断要不要办）→ 脚本返回企业状态、类型
- **第3步**（硬性条件）→ 脚本自动评估 5 项
- API 查不到的 4 项，加盟商按话术追问客户

<<<<<<< HEAD
### 📄 输出示例

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  企业名称：杭州某某科技有限公司
  统一社会信用代码：91330100XXXXXXXXXX
  法定代表人：张三
  省份：浙江
  企业类型：有限责任公司
  成立日期：2020-03-15
  注册地址：浙江省杭州市...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【ICP/EDI 办理条件评估】

  💰 注册资本：注册资本 500万人民币，≥ 100万元 ✅
  🏢 企业类型：企业类型为'有限责任公司'，符合要求 ✅
  📋 经营范围：经营范围未包含'增值电信业务'，需先做经营范围变更 ⚠️
  ✅ 登记状态：登记状态：存续 ✅
  🌐 外资情况：内资企业 ✅

  结论：⚠️ 存在 1 个问题需要解决：经营范围无'增值电信业务'→需做经营范围变更（约5-7天）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### ⚠️ 查询失败处理

| 情况 | 加盟商话术 |
|------|-----------|
| 查不到（名称不全/记错） | "这个名字没查到，您方便发一下营业执照上的**公司全称**吗？或者统一社会信用代码也行，那是最准确的。" |
| 查到但非目标公司 | "查到一个叫'XXX'的公司，是您说的这家吗？不是的话麻烦发一下准确的全称。" |
| API 调用失败（网络/额度） | "系统暂时查不了，我先按常规流程帮您梳理——您公司注册资本大概多少？是什么类型？" 然后走第2步人工3问。 |

> **核心原则**：查不到时不卡住，自动退回第2步人工询问，不让加盟商在客户面前露怯。

### 🔗 与6步法的衔接

查询结果**直接替代第2步和第3步的逐项追问**：
- **第2步**（判断要不要办）→ 脚本返回企业状态、类型，自动判断
- **第3步**（硬性条件）→ 脚本自动评估注册资本、企业类型、经营范围、外资情况
- 加盟商拿到结果后，用话术告诉客户哪些条件满足、哪些需要补
- **省去的对话**：不用再问"你公司注册资本多少？""你公司类型是什么？""经营范围有增值电信业务吗？"——一键全知道

### 🔌 数据源

- 企查查开放平台 API 410：`https://api.qichacha.com/ECIV4/GetBasicDetailsByName`
- 请求参数：`?key={AppKey}&keyword={企业名称或信用代码}`
- 鉴权方式：Header 传 `Token`（MD5(AppKey + Timespan + SecretKey).upper()）+ `Timespan`（秒级Unix时间戳）。无 Authorization header。
- 费用：按次计费（详见 https://openapi.qcc.com 定价页）
- 返回字段：Name（企业名称）、RegistCapi（注册资本）、EconKind（企业类型）、Scope（经营范围）、Status（登记状态）、Province（省份）、OperName（法人）、CreditCode（统一社会信用代码）、Address（注册地址）、StartDate（成立日期）
=======
> 完整 API 文档（鉴权/参数/字段）：`scripts/query_company.py --help`
>>>>>>> dev

---

## 第2步：判断 — 客户到底要不要办

**有企业名称**：企查查 API 一键完成（见上）
**无企业名称**：用 3 个问题确认

1. "你的业务/平台上线了吗？"
2. "你收钱的方式？（用户付费/商家入驻/自己卖货）"
3. "公司注册资本大概多少？"

### 三种结论 + 话术

**✅ 需要办**：
> "您这个业务需要办 [ICP/EDI] 许可证，这是国家硬性要求，不办可能被罚款 10-100 万。我帮您梳理一下基本条件，满足不了也没关系，我帮您想办法。"

**❌ 不需要办**（留钩子）：
> "您目前不需要办这个证，自营官网只需要做 ICP 备案就行，免费。不过以后想开放商家入驻就需要办了，到时您再找我。"

**⚠️ 需要换证**：
> "您刚才说的业务，不是 ICP 证，是 [EDI] 许可证。这两个容易搞混——ICP 是内容/服务收费用，EDI 是平台让商家入驻用。我帮您重新看看材料。"

---

## 第3步：硬性条件

**API 查过的**：直接看结论，跳到第 4 步
**没查的**：逐项确认。完整 7 项硬性条件 → `references/overview.md` 第三条

**加盟商开场白**：
> "先看看您的公司能不能满足基本要求，满足不了也没关系，我帮您想办法。"

---

## 第4步：材料 — 给客户模板（转化关键）

不要只说"你需要准备 XX"，而是：
1. 列材料清单（标注：自有/需准备/可代办）
2. **直接给可编辑模板** → 客户复制粘贴改
3. 客户说"我不会写" → 加盟商帮他改

材料模板 → `references/templates/icp-templates.md`
表单字段 → `references/templates/icp-form-checklist.md`
EDI 特有材料 → `references/edi-knowledge.md`

**转化要点**：模板由加盟商提供，客户觉得"自己搞太麻烦" → 主动找加盟商代办。

---

## 第5步：提交 — 哪点哪

每个步骤要明确：去哪（URL） / 点哪（按钮） / 填什么（字段）

1. **全国通用入口** → `references/overview.md` 第一条
2. **省份差异**：
   - 电话/官网 → `references/provincial-authorities.md`
   - 跨省差异 → `references/province-comparison.md`
   - 单省详情 → `references/provinces/{拼音}.md`（如 `guangdong.md`）

---

## 第6步：售后 — 续期/变更/注销

| 事项 | 提醒内容 | 详情 |
|------|---------|------|
| 有效期 | 5 年 | 到期前 90 天申请续期 |
| 年报 | 每年 3-6 月 | 不交列入不良名单 |
| 变更 | 公司改名/换法人/搬家 | 30 天内去变更 |
| 注销 | 不做了要注销 | 不能甩手就跑 |

完整 → `references/licensing-changes.md`

---

## 加盟商话术规范

| ❌ 不要说 | ✅ 要说 |
|----------|--------|
| "你需要办理增值电信业务许可证" | "你需要办一个 ICP 许可证，就是经营性网站的上网许可证" |
| "注册资本不低于 100 万元" | "公司注册时写的注册资本要 ≥ 100 万" |
| "近三年无违法违规记录" | "公司这几年没被处罚过吧？" |

---

## ⚠️ 各省差异提醒

**硬说"各省都一样"会翻车。** 核心流程全国通用，材料细节各省不同：

- **广东**：要公司章程 + 网站截图 + 服务器接入协议
- **北京**：审核最严，承诺 40 工作日办结
- **上海**：多一个企业服务云预审环节（外资 100% 试点）
- **湖南**：申请材料要仿宋三号字、A4 单面打印
- **广西**：要交纸质材料原件到政务中心
- **海南**：外资 100% 试点（2024-10 起）
- **浙江**：外资 100% 试点
- **社保**：部分省 1 个月够了，部分要连续 3 个月

完整差异 → `references/province-comparison.md`

---

## 🛰️ 自动采集（v2.1+，可选）

`province-fetcher/` 子系统**只收录 `miit.gov.cn` 官方页**，自动维护省份指南源数据。
仅在以下情况使用：
- 工信部/省局改版后 → `cd province-fetcher && python3 scripts/fetch_province.py all`
- 复核某省 → `python3 fetch_province.py fetch {省份}`
- 查质量分级 → `python3 scripts/grade.py`

当前质量（2026-06-08）：🟢19 / 🟡5 / 🟠3 / 🔴2（29 省已采集，2 省官网无独立页）

<<<<<<< HEAD
⚠️ 目录规范：
- references/ 下的文件是 AI 加载的知识库
- references/.internal/ 是内部文件（工作流脚本、PDF提取指南等），不应暴露给 AI 使用时读取
- scripts/ 是可执行脚本，供 AI 调用获取外部数据（企查查 API 等）
- README.md 是给 AI 和人类的使用说明，不在 references/ 内
- 每个文件只负责一个主题，避免跨文件重复

## references/ 组织原则（新增资质时必须遵守）

整理自 v1.1 → v1.2 的踩坑经验：

1. **禁止把多个主题堆在一个大文件里**。例如 31 省指南应该拆成 31 个独立文件（`provinces/` 子目录），而不是塞一个 2400 行的 `province-guides.md`。AI 加载整个文件浪费上下文，改一个省要动全文件。

2. **同一类数据只存在于一个文件中**。例如各省特殊要求放在 `province-comparison.md`，overview.md 里出现同样的内容就删掉并改为引用。硬性条件、未办后果等通用信息统一在 overview.md，其他资质文件里引用它。

3. **内部文件用 .internal/ 隔离**。工作流脚本、采集脚本、临时草稿不应让 AI 在 skill_view 时看到。

4. **模板放 templates/ 目录**，不归在 references/ 根目录。

5. **省份级文件用 `provinces/` 子目录**，不用 `province-xxx/` 文件夹（AI 无法自动扫描子目录内容）。文件名用拼音缩写：`guangdong.md`。

6. **内部工作流笔记放 `.internal/` 子目录**（`references/.internal/`）。例如 `acroform-pdf-extraction.md` 记录了政务 acroform PDF 提取方法。这类文件不被 AI 加载，但可供开发者查阅。

7. **不要收录市场参考价数据**。代办费、中介报价等市场数据变动频繁、来源不可靠、官方不公布。放入正式手册会带来维护负担且可能被误用为官方信息。如需引用，标注"仅供参考，以当地代办商实际报价为准"。


=======
> AI 不必主动运行此子系统——仅当发现 `references/provinces/*.md` 与实际官网不一致时，由维护者触发。
>>>>>>> dev

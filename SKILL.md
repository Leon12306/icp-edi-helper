---
name: icp-edi-helper
description: 企商链 Boss Claw 平台内置的 ICP/EDI 经营许可办理 SOP 技能包。覆盖 ICP/EDI 新业务申请、变更、续期全流程，支持企查查 API 自动评估企业资质。
keywords: [sales, government-service, icp-edi, bossclaw, franchise-enablement, sop-manual, qcc-api]
version: 2.3.0
last_updated: 2026-06-15
---

# ICP/EDI 经营许可办理 SOP

> 适用平台：Boss Claw（企商链 OPC） · 服务商/加盟商/平台管理人员使用
> 客户**不直接使用**这个技能——客户咨询加盟商，加盟商遇到问题才咨询 Boss Claw
>
> **📦 独立分发**：本技能包是自包含的，可直接复制到其他 AI 平台使用，无需任何外部依赖。

---

## 0. AI 5 秒决策树（先看这个）

| 客户说... | 跳过到 |
|----------|--------|
| "我想知道要办什么证" / "做什么业务要不要办" | `references/workflow.md` 第 1 步 |
| 给企业名称 / 统一社会信用代码 | `references/qcc-api-guide.md`（一键评估） |
| 询问某个省的具体要求 | `references/provinces/{省拼音}.md`（如 `guangdong.md`） |
| 询问 31 省差异 / 哪家最快 | `references/province-comparison.md` |
| 询问某省电话 / 官网 | `references/provincial-authorities.md` |
| 要模板 / 表单字段 | `references/templates/icp-templates.md` |
| 询问 EDI 与 ICP 区别 | `references/edi-knowledge.md` |
| 变更/续期/注销 | `references/licensing-changes.md` |
| 硬性条件 / 罚款金额 / 通用流程 | `references/overview.md` |

> **少读多引用**：每份文件只读一次。重复内容已集中到 `overview.md`，其余文件用 `见 xxx.md` 引用。

---

## 1. 工作流摘要（6 步法）

```
第1步  客户做什么生意 → 推荐证（获取弹药）
第2步  3 个问题 → 判断要不要办（确认需求）
第3步  硬性条件 → 客户能不能办（评估能力）
第4步  材料清单 → 给客户模板（提供弹药）
第5步  哪点哪 → 一步步教客户提交（指导操作）
第6步  拿到证 → 提醒续期/变更（售后维护）
```

**有企业名称时**：第 2 + 3 步直接用 `scripts/query_company.py` 一键评估，跳过逐项追问。

**详情**（话术、模板、差异）→ `references/workflow.md`

---

## 2. 快速判断表

| 客户业务 | 推荐证 |
|----------|--------|
| 网站/小程序，用户付费 | ICP许可证 |
| 平台让商家入驻卖货 | EDI许可证 |
| 自己卖货的官网 | ICP备案（免费） |
| 不确定 | `references/workflow.md` 第 1 步判断逻辑 |

更多口语映射 → `references/license-keyword-map.md`

---

## 3. 各省差异提醒（一句话）

> 硬说"各省都一样"会翻车。典型差异：广东要公司章程+网站截图；北京审核最严；上海/海南/浙江外资 100% 试点；湖南要仿宋三号字单面打印；广西要纸质原件。
>
> 完整差异 → `references/province-comparison.md`

---

## 4. 企查查 API（推荐优先用）

**有企业名称时**，调用 `scripts/query_company.py` 自动评估 5 项硬性条件：

```bash
cp .env.example .env  # 填入 QCC_APP_KEY / QCC_SECRET_KEY
python3 scripts/query_company.py "杭州某某科技有限公司"
```

**API 不可查的 4 项**（员工社保/域名/ICP 备案/网站可访问）→ 加盟商追问客户。

详细字段映射、错误处理 → `references/qcc-api-guide.md`

---

## 5. 加盟商话术规范（速记）

| ❌ 不要说 | ✅ 要说 |
|----------|--------|
| "你需要办理增值电信业务许可证" | "你需要办一个 ICP 许可证" |
| "注册资本不低于 100 万元" | "公司注册时写的注册资本要 ≥ 100 万" |
| "近三年无违法违规记录" | "公司这几年没被处罚过吧？" |

---

## 6. 维护入口

| 角色 | 看什么 |
|------|--------|
| AI 加载 | 本文件 + `references/index.md`（按需 1-2 个文件） |
| 人类维护者 | `README.md`（项目说明 + 维护指南 + 踩坑经验） |
| 校验脚本 | `scripts/validate-skill.sh` |
| AI 协作规则 | `AGENTS.md`（任务识别/澄清/读写权限/汇报） |

---

## 7. 关联文档

- 工作流详情 → [references/workflow.md](references/workflow.md)
- 质量验收 → [references/quality-checklist.md](references/quality-checklist.md)
- 错误处理 → [references/error-handling.md](references/error-handling.md)
- 企查查 API → [references/qcc-api-guide.md](references/qcc-api-guide.md)
- AI 协作规则 → [AGENTS.md](AGENTS.md)

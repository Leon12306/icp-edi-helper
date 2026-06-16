# Quality Checklist — 技能包质量验收清单

> 本文件定义 icp-edi-helper 技能包交付前必须通过的验收项。
> 配套 `scripts/validate-skill.sh` 自动校验。

---

## 一、结构完整性（PASS/FAIL）

| # | 检查项 | 阈值 | 阻塞 |
|---|--------|------|------|
| Q1 | `SKILL.md` 存在 | 必须 | 是 |
| Q2 | `SKILL.md` 含 YAML front matter | 必须 | 是 |
| Q3 | `SKILL.md` 含 `name` 字段 | 必须 | 是 |
| Q4 | `SKILL.md` 含 `description` 字段 | 必须 | 是 |
| Q5 | `name` 为 lower-kebab-case | `^[a-z0-9]+(-[a-z0-9]+)*$` | 是 |
| Q6 | `description` 含触发关键词 | ≥ 10 字 | 是 |
| Q7 | `AGENTS.md` 存在 | 必须 | 是 |
| Q8 | `README.md` 存在 | 必须 | 是 |
| Q9 | `package.json` 存在 | 必须 | 是 |
| Q10 | `package.json` 含 `name/version/description` | 必须 | 是 |
| Q11 | `examples/usage.md` 存在 | 必须 | 是 |
| Q12 | `examples/` 含 ≥ 2 个用例 | 必须 | 是 |
| Q13 | `references/workflow.md` 存在 | 必须 | 是 |
| Q14 | `references/quality-checklist.md` 存在 | 必须 | 是 |
| Q15 | `references/error-handling.md` 存在 | 必须 | 是 |
| Q16 | `references/qcc-api-guide.md` 存在 | 必须 | 是 |
| Q17 | `references/index.md` 存在 | 必须 | 是 |
| Q18 | `scripts/validate-skill.sh` 存在 + 可执行 | 必须 | 是 |

---

## 二、内容质量（WARN/PASS）

| # | 检查项 | 阈值 | 阻塞 |
|---|--------|------|------|
| C1 | SKILL.md 行数 | ≤ 230 行 | 否 |
| C2 | SKILL.md 含 5 秒决策树 | 必须 | 是 |
| C3 | SKILL.md 不含版本历史/踩坑 | 0 命中 | 否 |
| C4 | SKILL.md 不含市场参考价 | 0 命中 | 否 |
| C5 | 31 省文件命名符合拼音规范 | ≥ 31 个 | 否 |
| C6 | `references/provinces/` 不重复 overview 内容 | 0 处 | 否 |
| C7 | `provincial-authorities.md` 与 `province-comparison.md` 不重复电话表 | 0 处 | 否 |
| C8 | 引用闭环：`见 xxx.md` 中 xxx.md 存在 | 100% | 是 |
| C9 | 内部文件隔离：`references/.internal/` 不被 SKILL.md 引用 | 0 引用 | 否 |
| C10 | `.env` 不在 git 跟踪 | 必须 | 是 |
| C11 | `references/templates/` 存在且含模板 | ≥ 1 | 否 |
| C12 | AGENTS.md 含错误分级 E1-E5 | 5 级 | 否 |
| C13 | AGENTS.md 含汇报格式 | 必须 | 否 |

---

## 三、运行时质量（人工抽检）

| # | 检查项 | 频率 | 责任 |
|---|--------|------|------|
| R1 | 5 秒决策树命中率 | 每周 | 平台管理 |
| R2 | 加盟商反馈"不准确" | 每周 | 平台管理 |
| R3 | API 调用失败率 | 每日 | DevOps |
| R4 | 各省文件与官网一致性 | 每月 | 内容维护 |
| R5 | 加盟商话术点击率 | 每周 | 销售运营 |

---

## 四、版本与变更

- v2.3 新增本文件
- v2.3 新增 AGENTS.md / package.json / examples / 3 个 references / validate-skill.sh
- v2.3 精简 SKILL.md：把 6 步法/话术/差异/质量数据等下沉到 references/workflow.md
- v2.3 去掉 recovery.md（进度跟踪统一在交付汇报中）
- v2.3 技能包改为自包含、可独立分发

---

## 五、关联文档

- 错误分级处理 → [error-handling.md](error-handling.md)
- 工作流详情 → [workflow.md](workflow.md)
- 企查查 API → [qcc-api-guide.md](qcc-api-guide.md)

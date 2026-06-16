# Changelog

本项目所有值得记录的变更都记录在此文件。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [未发布]

## [2.3] - 2026-06-15

### Added
- `AGENTS.md` AI 协作执行规则（任务识别 / 澄清策略 / 读写权限 / 汇报格式）
- `package.json` 技能元数据（name / version / description / keywords / files / scripts）
- `examples/usage.md` + `examples/edge-cases.md` 7 个用例样例（标准评估 / 跨省咨询 / 异常输入 / 客户误入 / 违规承诺 / API 降级 / 多省对比）
- `references/workflow.md` 6 步法详细 + 加盟商话术规范 + 各省差异速览
- `references/quality-checklist.md` Q1-Q18 结构完整性 + C1-C13 内容质量 + R1-R5 运行时质量
- `references/error-handling.md` E1-E5 错误分级 + 典型场景处理 + 5 项错误提示模板
- `references/qcc-api-guide.md` 企查查 API 鉴权 / 字段映射 / 错误降级
- `scripts/validate-skill.sh` 26 项自动质量门禁（可接 CI）

### Changed
- `SKILL.md` 精简：223 行 → 116 行（-48%），长内容下沉到 references
- `SKILL.md` 顶部加"📦 独立分发"说明
- `README.md` 重写：加 v2.3 升级章节 + 快速启动 + 自包含分发说明
- `references/index.md` 更新副本引用映射

### Removed
- `references/recovery.md` 删除（进度跟踪统一在交付汇报中，不写文件）
- `output/` 副本目录概念（项目改为自包含、原地修改）
- `*.bak*` 备份副本概念（修改前用 git/PR 流程管理）

### Quality Gate
- ✅ 26 PASS / 0 WARN / 0 FAIL

## [2.2] - 2026-06-09

### Changed
- **去重 + AI 可读性重构**：
  - SKILL.md 删除版本历史和踩坑经验（移到 README），加 5 秒决策树
  - 31 个省份文件从 65 行压缩到 25-30 行（公共内容用引用代替重复）
  - 新增 `references/index.md` AI 决策树
  - 合并 `provincial-authorities.md` + `province-comparison.md` 重复电话表
  - SKILL.md 与 README.md 明确分工

## [2.1] - 2026-06-08

### Added
- 新增 `province-fetcher/` 31省官方办事指南自动采集器：
  - 白名单 `miit.gov.cn` 体系
  - HTML+PDF 双路径解析
  - 表格化"事项清单"页面回退
  - 总览页检测
  - 跨省一致性校验
  - 🟢🟡🟠🔴 4 档质量分级
- 覆盖 29/31 省（河南/四川无独立指南页已标注），🟢 绿色省份从 5 → 19

## [2.0] - 2026-06-04

### Changed
- 质量治理：内容去重 + 聚焦 ICP/EDI + 话术补全 + 外资试点 + 企查查增强

## [1.9] - 2026-06-03

### Added
- 新增企查查 API 企业查询

## [1.8] - 2026-06-03

### Removed
- 删除"各省代办费用参考"表

### Changed
- 技能改名 `icp-edi-helper`

## [1.7] - 2026-06-03

### Changed
- 聚焦 ICP/EDI，删除其他资质占位

## [1.6] - 2026-06-03

### Changed
- 内部文件移入 `.internal/`

## [1.5] - 2026-06-03

### Added
- 变更表单补充

## [1.4] - 2026-06-03

### Added
- 新增表单字段清单

## [1.3] - 2026-06-03

### Changed
- 内容去重，改为跨文件引用

## [1.2] - 2026-06-03

### Added
- 新增组织原则规范（踩坑经验编码）

## [1.1] - 2026-06-03

### Changed
- 目录结构重组

## [1.0] - 2026-06-03

### Added
- 初始版本

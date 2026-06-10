# 政务网站批量采集与文档整理流程

> **状态（v2.1，2026-06-08 更新）**：本流程已升级为 `province-fetcher/` 自动化采集器。本文件保留作为**白名单规则 + 兜底策略**的速查表。

## 触发场景

需要对多个省份的政务服务机构（通信管理局、工信厅等）进行批量网页内容采集，并整理为结构化文档。

## 核心方法

### 1. 白名单（强制）

**只接受工信部体系**（`miit.gov.cn`）下页面作为权威源。搜狐/顺企网/网易/今日头条/中帆/007swz/qq.com 等第三方转载一律不收。

| 接受 | 拒绝 |
|------|------|
| `bjca.miit.gov.cn` | `sohu.com` `toutiao.com` `163.com` |
| `ythzxfw.miit.gov.cn` | `11467.com`（顺企网） `trustexporter.com` |
| `dxzhgl.miit.gov.cn` / `tsm.miit.gov.cn` | `51sole.com`（搜了网） `007swz.com` |
| `jyhwzhq.miit.gov.cn`（集约化平台，PDF 附件托管） | `qq.com` `weibo.com` `douban.com` |

详见 `province-fetcher/scripts/allowlist.py`。

### 2. 候选 URL 构造

各省份通管局页面路径通常符合以下模式（按命中率排序）：

```
https://{short_domain}/bsfw/bszn/art/{year}/art_{hash}.html          # 办事指南
https://{short_domain}/zwgk/dxgl/fwzlgl/art/{year}/art_{hash}.html  # 政务公开
https://{short_domain}/bsfw/xzxk/art/{year}/art_{hash}.html         # 行政许可
https://{short_domain}/xxgk/jgdj/art/{year}/art_{hash}.html         # 安徽表格清单
http://{short_domain}/cms_files/filemanager/oldfile/.../*.pdf        # 上海/宁夏 PDF
```

`{short_domain}` 见 `province-fetcher/data/provinces_meta.json`（如 `bjca` / `tjca` / `gdca` / `shxca` / `qhca`）。

### 3. 解析器兜底（7 层）

| 差异类型 | 兜底方案 | 实现位置 |
|---------|---------|---------|
| 章节标题同义词 | `SECTION_SYNONYMS` | `fetcher.py` |
| 章节标题含描述 | 冒号后内容作为首条 | `parse_section` |
| 多段办结时限 | `parse_review_deadline` 17 个正则 | `REVIEW_PATTERNS` |
| 材料列表混在标题段 | 跳过动作性标题，多章符合并 | `parse_numbered_list_items` |
| 表格化"事项清单"页 | `parse_table_license_row` 提取 `申办材料/办理时限/收费标准` 列 | `fetcher.py` |
| PDF 文本断行 | `fetch_pdf` 按"句末标点"合并续行 | `fetcher.py` |
| 总览页检测 | `OVERVIEW_KEYWORDS` 触发告警 | `fetcher.py` |
| 电话触发词多形态 | `PHONE_RE` 容忍 0-12 字符的标点/换行/&nbsp; 间隔 | `PHONE_RE` |

### 4. 质量分级（强制）

```bash
python3 province-fetcher/scripts/grade.py
```

🟢 green — 条件≥3 + 材料≥3 + 时限 + 电话
🟡 yellow — 条件≥3 + （材料≥1 或 时限）
🟠 orange — 条件≥3 但材料=0 + 时限=0
🔴 red — 条件=0 且 材料=0

**当前分布（2026-06-08）**：🟢19 🟡5 🟠3 🔴2

### 5. 5 黄 3 橙 2 红 = 真实数据缺口

不是解析器问题，是源页本身没写：

| 缺口 | 省 | 源页实际情况 |
|------|----|------------|
| 审查时限缺失 | 天津/西藏 | 源页只有 7 条件 + 10 材料 + 联系电话，无"X 日内作出" |
| 咨询电话缺失 | 广东 | 源页无任何"电话/咨询"关键词 |
| 材料清单缺失 | 海南/新疆 | 源页只引《42 号令》第八条，不展开列材料 |
| 表格无条列 | 安徽 | "为企业办实事清单"表格"申请条件"列为空 |
| 仅系统链接 | 山东 | 源页只列 7 条件+流程，材料全部指向 `tsm.miit.gov.cn` 系统 |
| PDF 范围窄 | 上海 | PDF 只到"许可证申请条件"两段，无材料/时限/电话 |
| 渝快办已 404 | 重庆 | 源页仅"渝快办"平台跳转，平台已 404 |
| 总览页 | 青海 | 源页是"经营许可/码号/互联网管理" 3 业务简介 |

### 6. 一致性校验（多省硬性条件对比）

`province-fetcher/scripts/consistency.py` 检查 7 项：

- 注册资本 100 万（省内）/ 1000 万（跨省）
- 3 名员工 / 3 名负责人 社保
- 域名证书要求
- 公司法人代表
- 外资股比（4 个试点：北京/上海/浙江/海南）
- 等等

出现矛盾 → 标 `conflict`，由人工确认。

## 历史（旧版采集方法，2026-06-02 之前）

> 此方法已被 `province-fetcher/` 取代。保留作为备查。

旧版按以下步骤：
1. `web_search` 关键词：`{省份} 通信管理局 增值电信业务经营许可 首次申请 办事指南`
2. 优先 `banshi.{省}.gov.cn/pubtask/task/...` 页面（已废弃，迁移到 `miit.gov.cn`）
3. `web_extract` 抓取具体办事指南页面
4. 各省政务网站首页经常超时（`tjj.*.gov.cn` 普遍无法直接抓取），用第三方转载文章辅助（**v2.1 已删除此策略，改用白名单**）
5. 输出到 `~/work/icp-province-docs/`

**新方法（v2.1）已废弃 2/4/5 步骤**，全部走 `miit.gov.cn` 体系 + 自动化解析。

## 7. 已采集完成的省份（2026-06-08）

- 29/31 省 `guide_url` 已填，剩河南/四川（官网动态加载/无独立页）
- 19/29 省达到 🟢 绿色（条件≥3 + 材料≥3 + 时限 + 电话）
- 元数据：`province-fetcher/data/provinces_meta.json`
- 结果：`province-fetcher/output/all_provinces.json`
- 详细说明：`province-fetcher/README.md`

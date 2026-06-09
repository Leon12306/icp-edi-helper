# province-fetcher

独立于 `references/` 体系的 31 省增值电信业务经营许可官方办事指南采集器。

## 目标

> 只收录**官方**信息，不收第三方营销稿。

## 设计原则

1. **白名单域名** — 只接受 `miit.gov.cn` 体系下的页面。搜狐/顺企网/网易/今日头条等一律拒绝。
2. **可追溯** — 每条输出都带 `source_url` 和 `fetched_at`，人工可一键验证。
3. **不做猜测填充** — 字段缺失就缺失，绝不补默认值。
4. **一致性校验** — 多省共有硬性条件（注册资本/办结时限/社保 3 人）做交叉对比，矛盾即标 `conflict`。
5. **PDF 兼容** — 部分省份官方页是 PDF（如上海）或 HTML 短+PDF 附件（宁夏）；fetch_pdf 自动接管。

## 目录结构

```
province-fetcher/
├── README.md                          # 本文件
├── data/
│   └── provinces_meta.json            # 31省通管局短域名+官方入口
├── scripts/
│   ├── allowlist.py                   # 白名单/候选URL构造（含 jyhwzhq 集约化平台）
│   ├── fetcher.py                     # 抓取+结构化解析（HTML/PDF 双路径）
│   ├── consistency.py                 # 多省一致性校验
│   ├── fetch_province.py              # CLI 主入口
│   └── grade.py                       # 采集质量分级（🟢🟡🟠🔴）
├── output/                            # 采集结果输出（运行后生成）
```

## 安装

```bash
pip3 install requests beautifulsoup4 pdfplumber
```

## 用法

### 列出所有省份元数据

```bash
python3 scripts/fetch_province.py list
```

### 采集单省（广东，已有 guide_url）

```bash
python3 scripts/fetch_province.py fetch 广东
python3 scripts/fetch_province.py fetch 广东 --format json
```

### 强制指定 URL（用于新发现但未写入元数据的官方页）

```bash
python3 scripts/fetch_province.py fetch 上海 --url https://shca.miit.gov.cn/.../xxx.html
```

### 批量采集 + 一致性校验

```bash
python3 scripts/fetch_province.py all --check-consistency
```

### 质量分级

```bash
python3 scripts/grade.py
```

## 当前元数据状态

`guide_url` 字段含义：
- ✅ 已填：从该 URL 抓取并解析
- ❌ 未填：需要人工/搜索引擎定位后填入

```
省份     拼音           短域名                   guide_url
北京     beijing        bjca.miit.gov.cn         ✅
天津     tianjin        tjca.miit.gov.cn         ❌
...
广东     guangdong      gdca.miit.gov.cn         ✅
广西     guangxi        gxca.miit.gov.cn         ✅
贵州     guizhou        gzca.miit.gov.cn         ✅
...
陕西     shaanxi        shxca.miit.gov.cn        ❌
...
```

**共 31 省，已配置 25 省。** 未配置省份：天津/陕西/青海/河南（部分搜不到"首次申请"独立指南页，只能用"外资/变更/常见问题"代替）。

## 解析器兼容性（关键改进）

各省份用词差异巨大，fetcher 做了 5 层兜底：

| 差异类型 | 举例 | 兜底方案 |
|---------|------|---------|
| 章节标题同义词 | "申请条件"/"办理条件"/"受理条件"/"申办条件"/"应当符合下列条件" | `SECTION_SYNONYMS` 关键词扩展 |
| 章节标题含描述 | "一、申请经营山西地区增值电信业务的，应当符合下列条件：" | 冒号后内容作为首条 |
| 多段办结时限 | "5 日内决定是否受理；60 日内审查完毕" | `parse_review_deadline` 返回多段拼接 |
| 材料列表混在标题段 | "二、申请材料提交" 是动作段，真正材料在"三、申请材料清单" | 跳过动作性标题，多章符合并 |
| 黑名单过滤过头 | "申请表" 是真材料名 | 区分"申请表"和"申请表（标题）" |
| PDF 文本断行 | "公\n司"、"最\n低" | `fetch_pdf` 按"句末标点"合并续行 |
| 章节无"一、"前缀 | 福建"受理条件"/"其它应提交的附件材料" | 关键字最早位置定位 + `INNER_BREAK` 防越界 |
| HTML 短正文 + PDF 附件 | 宁夏 HTML 只有 PDF 链接 | 自动 fallback 解析 PDF 附件 |

## 当前质量分布

```
🟢 green  (5)   河北/内蒙古/江苏/江西/宁夏
🟡 yellow (16)  北京/山西/黑龙江/浙江/福建/湖北/湖南/广东/广西/海南/贵州/云南/西藏/甘肃/新疆/辽宁
🟠 orange (3)   上海（PDF 仅有条件）/安徽（表格清单）/山东（无材料章）
🔴 red    (1)   重庆（页面只是已挂"渝快办"链接）
```

## 局限性 / 已知问题

1. **PDF 文本不一定完整** — 上海 PDF 仅有"申请条件"，不含材料/时限/电话；这是 PDF 本身的内容缺失。
2. **历史文章** — 通信管理局页面可能被替换/下架，采集时若返回 404 应更新 `guide_url`。
3. **陕西/河南/青海/TJ 短域名特殊**（元数据有 `_note`），首次采集需人工验证可达性。
4. **bot 拦截** — 工信部站点偶发 403，可加 `Retry-After` 退避重试（未实现）。
5. **不收录"代办费"** — 严格遵循 Skill 规范，不收录市场参考价数据。
6. **重庆页面空** — 重庆 通管局指南页只是"渝快办"平台跳转链接，平台已 404；执行标准按工信部 42 号令（与全国其他省一致）。
7. **安徽表格页** — 安徽 通管局没有独立"申请指南"HTML 页，现采的是"为企业办实事清单"，需后续从其他渠道补充条件详情。

## 后续可扩展

- [x] 给 `fetcher.py` 加 PDF 文本提取（pdfplumber）
- [x] 上海/宁夏 PDF 路径走通
- [x] 加入 `jyhwzhq.miit.gov.cn` 白名单（集约化平台 PDF 附件）
- [x] 多省一致数据交叉校验
- [ ] 给 `fetcher.py` 加 retry 退避
- [ ] 把 `output/*.md` 自动回写到 `../references/provinces/{pinyin}.md`（需要人审）
- [ ] 加 cron 定时任务，每 6 个月自动复核一次

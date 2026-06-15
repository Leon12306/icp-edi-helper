# QCC API Guide — 企查查 API 调用指南

> 本文件从 SKILL.md v2.2 下沉而来，详细说明企查查 API 的鉴权、调用、字段映射。
> SKILL.md 仅保留调用入口，详细文档见本文件。

---

## 一、配置

### 1.1 申请密钥

前往 [企查查开放平台](https://open.qcc.com/) 申请：

- `QCC_APP_KEY`
- `QCC_SECRET_KEY`

### 1.2 写入 .env

```bash
cp .env.example .env
# 填入：
# QCC_APP_KEY=your_app_key_here
# QCC_SECRET_KEY=your_secret_key_here
```

⚠️ **不要把 .env 提交到 git**（已在 .gitignore 中）。

---

## 二、调用方式

### 2.1 命令行

```bash
# 普通模式
python3 scripts/query_company.py "杭州某某科技有限公司"

# JSON 输出（程序化）
python3 scripts/query_company.py "企业名称" --json
```

### 2.2 完整参数

```bash
python3 scripts/query_company.py --help
```

---

## 三、自动评估项

### 3.1 API 可查（5 项）

| 检查项 | API 返回字段 | 评估逻辑 | 不满足时话术 |
|--------|------------|---------|------------|
| 💰 注册资本 ≥ 100万 | `RegisteredCapital` | 数值 ≥ 1000000 | "注册资本不够可做工商增资，3 天搞定" |
| 🏢 有限责任公司 | `CompanyType` / `EconKind` | 含"有限责任" | "个体户不行，需注册有限公司" |
| 📋 经营范围含"增值电信业务" | `BusinessScope` | 字符串匹配 | "经营范围没这个，需变更（5-7 天）" |
| ✅ 登记状态存续 | `Status` / `RegistStatus` | "存续" / "在业" | "公司状态不对，需先恢复正常" |
| 🌐 外资情况 | `ForeignInvest` / 股东信息 | 股东含境外 | 试点省（北京/上海/浙江/海南）：外资可达100%<br>其他省：需走额外审批 |

### 3.2 API 不可查（4 项）

加盟商按话术追问客户：

- **3 名员工社保** — 部分省 1 个月够了，部分要连续 3 个月
- **域名在公司名下** — WHOIS 查询可辅助
- **已完成 ICP 备案** — 工信部备案系统查询
- **网站可访问** — 浏览器测试

---

## 四、与 6 步法衔接

```
第2步（判断要不要办）
   ↓ 调用 query_company.py
   ↓ 拿到：公司状态、类型、外资
   ↓
第3步（硬性条件）
   ↓ 自动评估 5 项（API 可查）
   ↓
   加盟商追问 4 项（API 不可查）
   ↓
第4步（材料准备）
```

---

## 五、错误处理

| 错误 | 原因 | 降级方案 |
|------|------|---------|
| 401 Unauthorized | 密钥错误或过期 | 联系企查查客服更新 |
| 429 Too Many Requests | 触发限流 | 等待 60 秒后重试 |
| 500 Internal Server Error | 企查查服务异常 | 降级到"3 个问题"流程 |
| Connection timeout | 网络问题 | 降级到"3 个问题"流程 |

详细错误分级 → [error-handling.md](error-handling.md)

---

## 六、API 字段映射参考

> 不同企业类型字段可能略有差异，以实际 API 返回为准。

| 中文 | API 字段 | 类型 | 示例 |
|------|---------|------|------|
| 企业名称 | `Name` | string | 杭州某某科技有限公司 |
| 统一社会信用代码 | `CreditCode` | string | 91330100MA... |
| 法定代表人 | `LegalPerson` | string | 张三 |
| 注册资本 | `RegisteredCapital` | number | 1000000 |
| 成立日期 | `StartDate` | date | 2020-01-01 |
| 企业类型 | `CompanyType` | string | 有限责任公司(自然人投资或控股) |
| 经营状态 | `Status` | string | 存续 |
| 经营范围 | `BusinessScope` | string | ...增值电信业务... |
| 注册地址 | `Address` | string | 浙江省杭州市... |

---

## 七、关联文档

- 工作流 → [workflow.md](workflow.md)
- 错误处理 → [error-handling.md](error-handling.md)

#!/usr/bin/env python3
"""
企查查企业工商信息查询脚本
数据源：企查查开放平台 API 410（企业工商信息）
用途：根据企业名称或统一社会信用代码查询工商信息，自动评估 ICP/EDI 许可证办理条件

鉴权方式：
  Header Token: MD5(AppKey + Timespan + SecretKey).upper()
  Header Timespan: Unix时间戳（秒）

密钥配置（按优先级）：
  1. 命令行参数 --app-key / --secret-key
  2. 系统环境变量 QCC_APP_KEY / QCC_SECRET_KEY
  3. 项目根目录 .env 文件

海外部署（数据不能出境）：
  设置 QCC_RELAY_URL 环境变量或 --relay-url 参数指向国内 SCF 中继地址
  脚本会自动通过中继转发请求，无需直接访问企查查
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time

from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    import requests
except ImportError:
    print("需要 requests 库：pip3 install requests", file=sys.stderr)
    sys.exit(1)


def load_dotenv() -> Dict[str, str]:
    """从项目根目录 .env 文件加载环境变量（不覆盖已有的环境变量）"""
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if not env_file.exists():
        return {}
    loaded = {}
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    loaded[key] = value
    return loaded


API_URL = "https://api.qichacha.com/ECIV4/GetBasicDetailsByName"

# ── ICP/EDI 办理硬性条件 ──────────────────────────────────────

MIN_REGISTERED_CAPITAL = 100  # 万元

REQUIRED_COMPANY_TYPES = [
    "有限责任公司",
    "有限公司",
]

BLOCKED_COMPANY_TYPES = [
    "个体工商户",
    "个人独资",
    "合伙企业",
]

REQUIRED_SCOPE_KEYWORDS = [
    "增值电信业务",
    "经营电信业务",
    "电信业务",
]

# 增值电信业务扩大对外开放试点省份（2024年10月起，外资ICP可达100%）
FOREIGN_PILOT_PROVINCES = {
    "北京", "上海", "浙江", "海南",
}


def make_auth_headers(app_key: str, secret_key: str) -> Dict[str, str]:
    """生成企查查 API 鉴权 Header

    正确的鉴权方式（经实测验证）：
    - Token header = MD5(AppKey + Timespan + SecretKey).upper()
    - Timespan header = 秒级Unix时间戳
    - 不使用 Authorization header
    """
    timespan = str(int(time.time()))
    token_val = hashlib.md5((app_key + timespan + secret_key).encode("utf-8")).hexdigest().upper()
    return {
        "Token": token_val,
        "Timespan": timespan,
    }


def query_company(keyword: str, app_key: str, secret_key: str, relay_url: str = "") -> Dict[str, Any]:
    """调用企查查 API 查询企业工商信息。
    如果设置了 relay_url，则通过国内 SCF 中继转发（解决海外数据不能出境问题）。
    """
    if relay_url:
        return _query_via_relay(keyword, relay_url)

    headers = make_auth_headers(app_key, secret_key)
    headers["Content-Type"] = "application/json"
    params = {"key": app_key, "keyword": keyword}

    try:
        resp = requests.get(API_URL, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": True, "message": f"API 请求失败：{e}", "reason": "network"}

    return _parse_response(resp.json(), keyword)


def _query_via_relay(keyword: str, relay_url: str) -> Dict[str, Any]:
    """通过国内 SCF 中继转发请求"""
    try:
        resp = requests.get(
            relay_url.rstrip("/") + "/",
            params={"keyword": keyword},
            timeout=15,
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": True, "message": f"中继请求失败：{e}", "reason": "network"}

    return _parse_response(resp.json(), keyword)


def _parse_response(data: dict, keyword: str) -> Dict[str, Any]:
    """解析企查查响应（直连和 relay 返回格式一致）"""
    if data.get("Status") != "200":
        return {"error": True, "message": data.get("Message", "查询失败"), "reason": "api_error", "raw": data}

    result = data.get("Result")
    if not result or not result.get("Name"):
        return {"error": True, "message": f"未查到 '{keyword}' 的工商信息，请确认企业名称是否完整准确", "reason": "not_found"}

    return result


def parse_capital_yuan(capital_str: str) -> Optional[float]:
    """
    解析注册资本字符串，返回万元为单位的数值。
    示例输入：
      "1000万人民币"  → 1000.0
      "500.00万人民币" → 500.0
      "1亿元人民币"   → 10000.0
      "USD 100万元"   → 100.0 (外币暂按数值取)
    """
    if not capital_str:
        return None

    # 去掉空格
    s = capital_str.strip()

    # 匹配 "数字亿元" 或 "数字万元"
    m_yi = re.match(r"([\d.]+)\s*亿元", s)
    if m_yi:
        return float(m_yi.group(1)) * 10000  # 亿 → 万

    m_wan = re.match(r"([\d.]+)\s*万元", s)
    if m_wan:
        return float(m_wan.group(1))

    # 兜底：提取第一个数字
    m_num = re.search(r"([\d.]+)", s)
    if m_num:
        return float(m_num.group(1))

    return None


def check_scope(scope: str) -> Dict[str, Any]:
    """检查经营范围是否包含增值电信相关关键词"""
    if not scope:
        return {"has_telecom_scope": False, "matched_keywords": [], "suggestion": "经营范围为空，无法判断"}

    matched = [kw for kw in REQUIRED_SCOPE_KEYWORDS if kw in scope]

    return {
        "has_telecom_scope": len(matched) > 0,
        "matched_keywords": matched,
        "suggestion": (
            "经营范围包含增值电信业务相关内容 ✅"
            if matched
            else "经营范围未包含'增值电信业务'或'经营电信业务'，需先做经营范围变更 ⚠️"
        ),
    }


def check_company_type(econ_kind: str) -> Dict[str, Any]:
    """检查企业类型是否符合要求"""
    if not econ_kind:
        return {"is_qualified_type": None, "suggestion": "企业类型为空，无法判断"}

    # 检查是否被排除的类型
    for blocked in BLOCKED_COMPANY_TYPES:
        if blocked in econ_kind:
            return {"is_qualified_type": False, "suggestion": f"企业类型为'{econ_kind}'，不符合要求（需要有限责任公司） ❌"}

    # 检查是否符合的类型
    for required in REQUIRED_COMPANY_TYPES:
        if required in econ_kind:
            return {"is_qualified_type": True, "suggestion": f"企业类型为'{econ_kind}'，符合要求 ✅"}

    # 其他类型（股份公司等）一般也可以
    if "股份" in econ_kind:
        return {"is_qualified_type": True, "suggestion": f"企业类型为'{econ_kind}'，符合要求 ✅"}

    return {"is_qualified_type": False, "suggestion": f"企业类型为'{econ_kind}'，可能不符合要求，需确认是否为公司制法人 ⚠️"}


def check_registration_status(status: str) -> Dict[str, Any]:
    """检查企业登记状态"""
    if not status:
        return {"is_active": None, "suggestion": "登记状态为空，无法判断"}

    if "存续" in status or "在营" in status or "开业" in status:
        return {"is_active": True, "suggestion": f"登记状态：{status} ✅"}

    if "注销" in status:
        return {"is_active": False, "suggestion": f"登记状态：{status}，企业已注销，无法办理 ❌"}

    if "吊销" in status:
        return {"is_active": False, "suggestion": f"登记状态：{status}，企业被吊销，无法办理 ❌"}

    if "迁入" in status or "迁出" in status:
        return {"is_active": True, "suggestion": f"登记状态：{status}，正常但需注意地址问题 ⚠️"}

    return {"is_active": None, "suggestion": f"登记状态：{status}，需人工确认 ⚠️"}


def evaluate_icp_edi(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据企查查返回的工商信息，评估 ICP/EDI 许可证办理条件
    """
    # 提取关键字段
    name = result.get("Name", "")
    capital_str = result.get("RegistCapi", "") or result.get("RegisteredCapital", "")
    capital_unit = result.get("RegisteredCapitalUnit", "") or ""
    capital_ccy = result.get("RegisteredCapitalCCY", "") or ""
    capital_value = result.get("RegisteredCapital", "")  # 纯数值
    econ_kind = result.get("EconKind", "")
    scope = result.get("Scope", "")
    status = result.get("Status", "")
    province = result.get("Province", "")
    oper_name = result.get("OperName", "")
    credit_code = result.get("CreditCode", "")
    address = result.get("Address", "")
    start_date = result.get("StartDate", "")
    ent_type = result.get("EntType", "")

    # 解析注册资本
    capital_wan = parse_capital_yuan(capital_str)

    # 各项检查
    capital_check = {
        "raw_value": capital_str,
        "value_wan_yuan": capital_wan,
        "meets_requirement": capital_wan is not None and capital_wan >= MIN_REGISTERED_CAPITAL,
        "suggestion": (
            f"注册资本 {capital_str}，≥ 100万元 ✅"
            if capital_wan is not None and capital_wan >= MIN_REGISTERED_CAPITAL
            else (
                f"注册资本 {capital_str}，不足 100万元，需做工商增资 ⚠️"
                if capital_wan is not None
                else f"注册资本 '{capital_str}' 无法解析，需人工确认 ⚠️"
            )
        ),
    }

    type_check = check_company_type(econ_kind)
    scope_check = check_scope(scope)
    status_check = check_registration_status(status)

    # 外资判断：优先看 EconKind 字段，EntType 不可靠（台港澳独资也返回0）
    foreign_keywords = ["外资", "外商", "港澳台", "台港澳", "港澳", "外国", "境外"]
    is_foreign = any(kw in econ_kind for kw in foreign_keywords) if econ_kind else False
    is_pilot = province in FOREIGN_PILOT_PROVINCES

    if is_foreign:
        if is_pilot:
            foreign_suggestion = (
                f"涉及外资（{econ_kind}），但 {province} 是外资试点省份（2024.10起外资 ICP 可达 100%），正常流程办理 ✅"
            )
        else:
            foreign_suggestion = (
                f"涉及外资（{econ_kind}），需走外资审批流程（工信部外商投资审定 + 商务部备案） ⚠️"
            )
    else:
        foreign_suggestion = "内资企业 ✅"

    foreign_check = {
        "is_domestic": not is_foreign,
        "is_pilot_province": is_pilot,
        "suggestion": foreign_suggestion,
    }

    # 如果外资但在试点省份，视为通过（非阻塞）
    foreign_ok = (not is_foreign) or (is_foreign and is_pilot)

    # 汇总
    all_passed = all([
        capital_check["meets_requirement"],
        type_check["is_qualified_type"] is True,
        scope_check["has_telecom_scope"] is True,
        status_check["is_active"] is True,
        foreign_ok,
    ])

    issues = []
    if not capital_check["meets_requirement"]:
        issues.append("注册资本不足100万→需工商增资（约3天）")
    if type_check["is_qualified_type"] is not True:
        issues.append("企业类型不符→需注册有限责任公司")
    if not scope_check["has_telecom_scope"]:
        issues.append("经营范围无'增值电信业务'→需做经营范围变更（约5-7天）")
    if status_check["is_active"] is not True:
        issues.append("企业状态异常→需先恢复正常状态")
    if is_foreign and not is_pilot:
        issues.append("涉及外资且非试点省份→需走外资审批流程")

    return {
        "company_name": name,
        "credit_code": credit_code,
        "legal_person": oper_name,
        "province": province,
        "address": address,
        "start_date": start_date,
        "econ_kind": econ_kind,
        "capital_check": capital_check,
        "type_check": type_check,
        "scope_check": scope_check,
        "status_check": status_check,
        "foreign_check": foreign_check,
        "overall_passed": all_passed,
        "issues": issues,
        "conclusion": (
            "✅ 基本条件全部满足，可以继续准备材料办理 ICP/EDI 许可证"
            if all_passed
            else f"⚠️ 存在 {len(issues)} 个问题需要解决：{'；'.join(issues)}"
        ),
    }


def main():
    # 1) 从 .env 加载（不覆盖已有环境变量）
    dotenv_vars = load_dotenv()

    parser = argparse.ArgumentParser(description="查询企业工商信息，评估 ICP/EDI 许可证办理条件")
    parser.add_argument("keyword", help="企业名称或统一社会信用代码")
    parser.add_argument("--app-key", default=os.environ.get("QCC_APP_KEY") or dotenv_vars.get("QCC_APP_KEY", ""),
                        help="企查查 AppKey（优先级：命令行 > 环境变量 > .env）")
    parser.add_argument("--secret-key", default=os.environ.get("QCC_SECRET_KEY") or dotenv_vars.get("QCC_SECRET_KEY", ""),
                        help="企查查 SecretKey（优先级：命令行 > 环境变量 > .env）")
    parser.add_argument("--relay-url", default=os.environ.get("QCC_RELAY_URL") or dotenv_vars.get("QCC_RELAY_URL", ""),
                        help="国内 SCF 中继地址（海外部署必填，解决数据不能出境）")
    parser.add_argument("--raw", action="store_true", help="输出企查查原始返回（不评估）")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出评估结果")

    args = parser.parse_args()

    if not args.app_key or not args.secret_key:
        if not args.relay_url:
            print("错误：需要企查查 API 密钥，或设置 QCC_RELAY_URL 走国内中继。", file=sys.stderr)
            sys.exit(1)
        # 走 relay 模式，本地不需要密钥

    # 查询
    result = query_company(args.keyword, args.app_key, args.secret_key, relay_url=args.relay_url)

    if result.get("error"):
        reason = result.get("reason", "unknown")
        err_msg = result.get("message", "未知错误")

        if args.json:
            # JSON 模式：输出结构化错误，AI 可根据 reason 字段决策
            print(json.dumps({
                "error": True,
                "reason": reason,
                "message": err_msg,
                "fallback_action": (
                    "ask_full_name" if reason == "not_found"
                    else "manual_step2" if reason == "network"
                    else "manual_step2"
                ),
            }, ensure_ascii=False, indent=2))
        else:
            print(f"查询失败：{err_msg}", file=sys.stderr)

        if args.raw:
            print(json.dumps(result.get("raw", {}), ensure_ascii=False, indent=2))

        # 非 JSON 模式下给出加盟商话术提示
        if not args.json:
            if reason == "not_found":
                print("\n💡 加盟商话术：\"这个名字没查到，您方便发一下营业执照上的公司全称吗？或者统一社会信用代码也行。\"", file=sys.stderr)
            else:
                print("\n💡 加盟商话术：\"系统暂时查不了，我先按常规流程帮您梳理——您公司注册资本大概多少？是什么类型？\"", file=sys.stderr)

        sys.exit(1)

    # 原始输出
    if args.raw:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 评估
    evaluation = evaluate_icp_edi(result)

    if args.json:
        print(json.dumps(evaluation, ensure_ascii=False, indent=2))
        return

    # 人类可读输出
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  企业名称：{evaluation['company_name']}")
    print(f"  统一社会信用代码：{evaluation['credit_code']}")
    print(f"  法定代表人：{evaluation['legal_person']}")
    print(f"  省份：{evaluation['province']}")
    print(f"  企业类型：{evaluation['econ_kind']}")
    print(f"  成立日期：{evaluation['start_date']}")
    print(f"  注册地址：{evaluation['address']}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("【ICP/EDI 办理条件评估】")
    print()
    print(f"  💰 注册资本：{evaluation['capital_check']['suggestion']}")
    print(f"  🏢 企业类型：{evaluation['type_check']['suggestion']}")
    print(f"  📋 经营范围：{evaluation['scope_check']['suggestion']}")
    print(f"  ✅ 登记状态：{evaluation['status_check']['suggestion']}")
    print(f"  🌐 外资情况：{evaluation['foreign_check']['suggestion']}")
    print()
    print(f"  结论：{evaluation['conclusion']}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if __name__ == "__main__":
    main()

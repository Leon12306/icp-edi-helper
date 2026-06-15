"""
多省共有硬性条件一致性校验。

用途：把多个省解析出的"申请条件"和"办结时限"放到一起做交叉对比。
    出现矛盾时打 conflict 标签，由人工确认。
"""

import re
from typing import Iterable

from fetcher import GuideDoc


# 关键事实关键词（出现即视为有这条）
HARD_FACT_KEYWORDS = {
    "registered_capital_100w": [
        "注册资本最低", "最低限额", "100 万元人民币", "100万元人民币",
    ],
    "registered_capital_1000w": [
        "1000 万元人民币", "1000万元人民币", "1000万人民币",
    ],
    "three_employees_social": [
        # 工信部统一要求"3 名负责人社保"，各省说法不一
        "三个负责人", "3个负责人", "3 个负责人",
        "三名员工", "3名员工", "3 名员工", "三名工作人员",
        "社保证明", "社保缴纳证明", "社会保险证明",
        "为.+名.+缴纳社保", "为.+个负责人.+缴纳", "为.+名负责人.+社保",
    ],
    "domain_validity": [
        "域名证书", "有效期内域名",
    ],
    "no_foreign_for_non_pilot": [
        "外商投资", "外资", "境外直接上市",
    ],
}


# 办结时限数字提取
REVIEW_DAYS_RE = re.compile(r"(\d{1,3})\s*日")


def _keyword_hit_count(text: str, keywords: list[str]) -> int:
    """
    支持字符串包含 + 正则（以 '^' 开头视为正则）。
    返回命中数量。
    """
    hits = 0
    for kw in keywords:
        if kw.startswith("^") or "+" in kw or ".*" in kw or ".+" in kw or "[" in kw:
            if re.search(kw, text):
                hits += 1
        else:
            if kw in text:
                hits += 1
    return hits


def extract_facts(doc: GuideDoc) -> dict:
    """从单个指南文档里提取硬性事实标记"""
    text_parts = [doc.title or "", " ".join(doc.apply_conditions), " ".join(doc.required_materials)]
    text = "\n".join(text_parts)

    facts = {
        "source": doc.source_url,
        "publish_date": doc.publish_date,
        "review_deadline": doc.review_deadline,
    }
    for key, keywords in HARD_FACT_KEYWORDS.items():
        facts[key] = _keyword_hit_count(text, keywords) > 0

    # 提取办结日（最严格数字）
    if doc.review_deadline:
        m = REVIEW_DAYS_RE.search(doc.review_deadline)
        facts["review_days"] = int(m.group(1)) if m else None
    else:
        facts["review_days"] = None
    return facts


def check_consistency(docs: Iterable[GuideDoc]) -> dict:
    """
    对一组 GuideDoc 做一致性检查。
    返回：{
      "total": N,
      "with_conditions": M,
      "conflicts": [ {field, values, sources} ],
      "summary": {...}
    }
    """
    facts_list = [extract_facts(d) for d in docs if d.apply_conditions]
    if not facts_list:
        return {
            "total": 0,
            "with_conditions": 0,
            "conflicts": [],
            "summary": "无可比较的文档",
        }

    conflicts = []

    # 注册资本冲突：100w 和 1000w 不应同时存在（应明确"省内 100w，跨省 1000w"）
    cap_100 = sum(1 for f in facts_list if f["registered_capital_100w"])
    cap_1000 = sum(1 for f in facts_list if f["registered_capital_1000w"])
    cap_missing = sum(1 for f in facts_list if not f["registered_capital_100w"] and not f["registered_capital_1000w"])

    if cap_100 == 0 and cap_1000 == 0 and cap_missing < len(facts_list):
        conflicts.append({
            "field": "registered_capital",
            "issue": "所有文档都未提及注册资本最低限额，疑似采集遗漏",
            "affected_sources": [f["source"] for f in facts_list],
        })

    # 办结时限：各省法定相同（60日），如有差异需提示
    review_days_values = {(f["review_days"], f["review_deadline"]) for f in facts_list if f["review_days"]}
    if len(review_days_values) > 2:  # 允许 5/60 这种"受理 + 审查"两个数字
        conflicts.append({
            "field": "review_deadline",
            "issue": f"办结时限数字存在多种：{review_days_values}",
            "affected_sources": [f["source"] for f in facts_list if f["review_days"]],
        })

    # 社保 3 人：应当普遍出现，缺失过半说明数据有缺
    social_hits = sum(1 for f in facts_list if f["three_employees_social"])
    if social_hits < len(facts_list) * 0.5:
        conflicts.append({
            "field": "three_employees_social",
            "issue": f"仅 {social_hits}/{len(facts_list)} 篇提及 3 人社保，可能采集不完整",
            "affected_sources": [f["source"] for f in facts_list if not f["three_employees_social"]],
        })

    return {
        "total": len(facts_list),
        "with_conditions": sum(1 for d in docs if d.apply_conditions),
        "facts": facts_list,
        "conflicts": conflicts,
        "summary": f"{len(facts_list)} 省数据，{len(conflicts)} 处冲突" if conflicts else f"{len(facts_list)} 省数据，无冲突",
    }


if __name__ == "__main__":
    # 简单自测
    print("此模块需配合 fetcher.parse_guide 使用。请运行 fetch_province.py 触发一致性检查。")

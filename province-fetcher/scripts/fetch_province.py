#!/usr/bin/env python3
"""
31省增值电信业务经营许可官方办事指南采集器

用法：
  # 采集单省（广东），从元数据里读 guide_url，没有就报错
  python3 fetch_province.py 广东

  # 强制指定 URL（覆盖元数据）
  python3 fetch_province.py 广东 --url https://gdca.miit.gov.cn/.../xxx.html

  # 输出 markdown 而不是 JSON
  python3 fetch_province.py 广东 --format md

  # 采集多省后做一致性检查
  python3 fetch_province.py --all --check-consistency

  # 列出所有省份元数据
  python3 fetch_province.py --list
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 让脚本能被直接 import 同目录模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetcher import parse_guide, GuideDoc, to_json
from consistency import check_consistency


META_PATH = Path(__file__).resolve().parent.parent / "data" / "provinces_meta.json"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def load_meta() -> dict:
    if not META_PATH.exists():
        print(f"元数据文件不存在: {META_PATH}", file=sys.stderr)
        sys.exit(1)
    with META_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_province(meta: dict, name: str) -> Optional[dict]:
    name = name.strip()
    for p in meta["provinces"]:
        if p["name_zh"] == name or p["pinyin"] == name:
            return p
    return None


def doc_to_markdown(doc: GuideDoc, province: dict) -> str:
    """单条解析结果 → markdown 片段"""
    lines = []
    lines.append(f"# {province['name_zh']} — 增值电信业务经营许可办理指南（采集）")
    lines.append("")
    lines.append(f"> 数据源：{doc.source_url}")
    lines.append(f"> 采集时间：{doc.fetched_at}")
    if doc.publish_date:
        lines.append(f"> 官方页发布日期：{doc.publish_date}")
    lines.append("")
    lines.append("## 基本信息")
    lines.append("")
    lines.append(f"- 实施主体：{doc.authority or '未解析出'}")
    lines.append(f"- 咨询电话：{doc.hotline or province.get('license_hotline', '未解析出')}")
    lines.append(f"- 办结时限：{doc.review_deadline or '未解析出'}")
    lines.append(f"- 申请入口：{province.get('main_entry')}")
    lines.append(f"- 电子证照：{province.get('market_entry')}")
    lines.append("")

    if doc.apply_conditions:
        lines.append("## 申请条件")
        lines.append("")
        for i, c in enumerate(doc.apply_conditions, 1):
            lines.append(f"{i}. {c}")
        lines.append("")

    if doc.required_materials:
        lines.append("## 申请材料")
        lines.append("")
        for i, m in enumerate(doc.required_materials, 1):
            lines.append(f"{i}. {m}")
        lines.append("")

    if doc.apply_procedure:
        lines.append("## 办理流程")
        lines.append("")
        for i, p in enumerate(doc.apply_procedure, 1):
            lines.append(f"{i}. {p}")
        lines.append("")

    if doc.pdf_attachments:
        lines.append("## 附件")
        lines.append("")
        for pdf in doc.pdf_attachments:
            lines.append(f"- [{pdf['title']}]({pdf['url']})")
        lines.append("")

    if doc.parse_warnings:
        lines.append("## ⚠️ 解析警告")
        lines.append("")
        for w in doc.parse_warnings:
            lines.append(f"- {w}")
        lines.append("")

    if doc.error:
        lines.append(f"## ❌ 错误")
        lines.append("")
        lines.append(doc.error)
        lines.append("")

    if doc.full_text_excerpt:
        lines.append("---")
        lines.append("")
        lines.append("### 原文摘要（人工复核用）")
        lines.append("")
        lines.append("```")
        lines.append(doc.full_text_excerpt[:600])
        lines.append("```")

    return "\n".join(lines)


def cmd_fetch(args):
    meta = load_meta()
    province = find_province(meta, args.province)
    if not province:
        print(f"未找到省份: {args.province}", file=sys.stderr)
        print("可用省份:", ", ".join(p["name_zh"] for p in meta["provinces"]), file=sys.stderr)
        sys.exit(1)

    url = args.url or province.get("guide_url")
    if not url:
        print(f"省份 {province['name_zh']} 的元数据中未配置 guide_url，请用 --url 手动指定", file=sys.stderr)
        sys.exit(1)

    print(f"[{province['name_zh']}] 抓取: {url}", file=sys.stderr)
    doc = parse_guide(url)

    if args.format == "json":
        print(to_json(doc))
    else:
        print(doc_to_markdown(doc, province))

    # 同时保存到 output 目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = province["pinyin"]
    if args.format == "json":
        out_path = OUTPUT_DIR / f"{safe_name}.json"
    else:
        out_path = OUTPUT_DIR / f"{safe_name}.md"
    out_path.write_text(
        to_json(doc) if args.format == "json" else doc_to_markdown(doc, province),
        encoding="utf-8",
    )
    print(f"已保存到: {out_path}", file=sys.stderr)


def cmd_list(args):
    meta = load_meta()
    print(f"{'省份':<8} {'拼音':<14} {'短域名':<24} {'guide_url':<10}")
    print("-" * 70)
    for p in meta["provinces"]:
        guide = "✅" if p.get("guide_url") else "❌"
        print(f"{p['name_zh']:<8} {p['pinyin']:<14} {p['short_domain']:<24} {guide}")
    total = len(meta["provinces"])
    with_guide = sum(1 for p in meta["provinces"] if p.get("guide_url"))
    print(f"\n共 {total} 省，已配置官方指南: {with_guide}")


def cmd_all(args):
    meta = load_meta()
    docs = []
    for p in meta["provinces"]:
        if not p.get("guide_url"):
            print(f"[跳过] {p['name_zh']}: 无 guide_url", file=sys.stderr)
            continue
        print(f"[抓取] {p['name_zh']}: {p['guide_url']}", file=sys.stderr)
        doc = parse_guide(p["guide_url"])
        doc._province = p  # type: ignore[attr-defined]
        docs.append(doc)

    if args.check_consistency:
        result = check_consistency(docs)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 汇总输出
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        bundle = OUTPUT_DIR / "all_provinces.json"
        bundle.write_text(
            json.dumps(
                [
                    {
                        "province": getattr(d, "_province", {}).get("name_zh"),
                        **json.loads(to_json(d)),
                    }
                    for d in docs
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"汇总已保存到: {bundle}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="31省增值电信业务经营许可官方办事指南采集器")
    sub = parser.add_subparsers(dest="command")

    p_fetch = sub.add_parser("fetch", help="采集单个省份")
    p_fetch.add_argument("province", help="省份名（中文或拼音）")
    p_fetch.add_argument("--url", help="强制指定官方页 URL（覆盖元数据）")
    p_fetch.add_argument("--format", choices=["json", "md"], default="md")
    p_fetch.set_defaults(func=cmd_fetch)

    p_list = sub.add_parser("list", help="列出所有省份元数据")
    p_list.set_defaults(func=cmd_list)

    p_all = sub.add_parser("all", help="采集所有已配置 guide_url 的省份")
    p_all.add_argument("--check-consistency", action="store_true", help="采集后做一致性校验")
    p_all.set_defaults(func=cmd_all)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()

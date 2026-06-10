#!/usr/bin/env python3
"""
v2.2 重构脚本：把 31 个省份文件从 65 行模板压缩为 25-30 行
只保留"基本信息"（电话）+"省特异条款"（如有），其余引用 overview.md
"""
import os

# 31 省元数据（基础信息 + 省特异条款）
PROVINCE_DATA = {
    "beijing": {
        "name": "北京", "agency": "北京市通信管理局", "phone": "010-51938033",
        "note": "审核最严，承诺 40 工作日办结。外资 100% 试点。"
    },
    "tianjin": {
        "name": "天津", "agency": "天津市通信管理局", "phone": "022-60351158",
        "note": ""
    },
    "shanghai": {
        "name": "上海", "agency": "上海市通信管理局", "phone": "021-63905098",
        "note": "外资 100% 试点。特殊规定见 `references/provinces/_shanghai-special.md`（前置审批/年检/变更/处罚/外资）。"
    },
    "chongqing": {
        "name": "重庆", "agency": "重庆市通信管理局", "phone": "023-68583855",
        "note": "官网仅'渝快办'跳转链接，无独立指南页。实际办理参考 `references/overview.md`。"
    },
    "hebei": {
        "name": "河北", "agency": "河北省通信管理局", "phone": "0311-86693334",
        "note": "扫描件要求：单个文件 ≤ 5MB，> 10 张图片打包 word/pdf 上传。"
    },
    "shanxi": {
        "name": "山西", "agency": "山西省通信管理局", "phone": "0351-8788059",
        "note": "支持邮寄取证。"
    },
    "neimenggu": {
        "name": "内蒙古", "agency": "内蒙古自治区通信管理局", "phone": "0471-6684170",
        "note": ""
    },
    "liaoning": {
        "name": "辽宁", "agency": "辽宁省通信管理局", "phone": "024-86581138",
        "note": "隐瞒情况或提供虚假材料的，1 年内不得再次申请。"
    },
    "jilin": {
        "name": "吉林", "agency": "吉林省通信管理局", "phone": "0431-88956129",
        "note": ""
    },
    "heilongjiang": {
        "name": "黑龙江", "agency": "黑龙江省通信管理局", "phone": "0451-53006020",
        "note": ""
    },
    "jiangsu": {
        "name": "江苏", "agency": "江苏省通信管理局", "phone": "025-83666303",
        "note": ""
    },
    "zhejiang": {
        "name": "浙江", "agency": "浙江省通信管理局", "phone": "0571-87880010",
        "note": "外资 100% 试点（2024-10 起）。办理入口：浙江政务服务网 + 工信部政务服务平台。"
    },
    "anhui": {
        "name": "安徽", "agency": "安徽省通信管理局", "phone": "0551-65680803",
        "note": ""
    },
    "fujian": {
        "name": "福建", "agency": "福建省通信管理局", "phone": "0591-83175175",
        "note": ""
    },
    "jiangxi": {
        "name": "江西", "agency": "江西省通信管理局", "phone": "0791-86218176",
        "note": ""
    },
    "shandong": {
        "name": "山东", "agency": "山东省通信管理局", "phone": "0532-83891813",
        "note": "材料全部指向 tsm.miit.gov.cn 系统（电信业务市场综合管理信息系统）。"
    },
    "henan": {
        "name": "河南", "agency": "河南省通信管理局", "phone": "0371-65795120",
        "note": "官网动态加载，无独立指南页。执行标准按工信部 42 号令。"
    },
    "hubei": {
        "name": "湖北", "agency": "湖北省通信管理局", "phone": "027-87796369",
        "note": ""
    },
    "hunan": {
        "name": "湖南", "agency": "湖南省通信管理局", "phone": "0731-81111266",
        "note": "申请材料要仿宋三号字、A4 单面打印。"
    },
    "guangdong": {
        "name": "广东", "agency": "广东省通信管理局", "phone": "020-87690666",
        "note": "要公司章程 + 网站截图 + 服务器接入协议。"
    },
    "guangxi": {
        "name": "广西", "agency": "广西壮族自治区通信管理局", "phone": "0771-2622281",
        "note": "要交纸质材料原件到政务中心。"
    },
    "hainan": {
        "name": "海南", "agency": "海南省通信管理局", "phone": "0898-66533831",
        "note": "外资 100% 试点（2024-10 起）。"
    },
    "sichuan": {
        "name": "四川", "agency": "四川省通信管理局", "phone": "028-87015272",
        "note": "官网未挂独立'首次申请'指南页。执行标准按工信部 42 号令。"
    },
    "guizhou": {
        "name": "贵州", "agency": "贵州省通信管理局", "phone": "0851-85608887",
        "note": ""
    },
    "yunnan": {
        "name": "云南", "agency": "云南省通信管理局", "phone": "0871-3557966",
        "note": ""
    },
    "xizang": {
        "name": "西藏", "agency": "西藏自治区通信管理局", "phone": "0891-6334193",
        "note": ""
    },
    "shaanxi": {
        "name": "陕西", "agency": "陕西省通信管理局", "phone": "029-88416655",
        "note": "5 日内一次性告知补正；60 日内审查完毕。"
    },
    "gansu": {
        "name": "甘肃", "agency": "甘肃省通信管理局", "phone": "0931-8788991",
        "note": ""
    },
    "qinghai": {
        "name": "青海", "agency": "青海省通信管理局", "phone": "0971-6128996",
        "note": "官网为'经营许可/码号/互联网管理'3 业务总览页，无独立'首次申请'指南。"
    },
    "ningxia": {
        "name": "宁夏", "agency": "宁夏回族自治区通信管理局", "phone": "0951-6086810",
        "note": "指南页可能为 PDF 附件形式。"
    },
    "xinjiang": {
        "name": "新疆", "agency": "新疆维吾尔自治区通信管理局", "phone": "0991-2388863",
        "note": ""
    },
}


def build_province_file(pinyin: str, data: dict) -> str:
    """生成新的省份文件（v2.2 标准结构）"""
    content = f"""# {data['name']} — 增值电信业务经营许可证办理指南

> 数据来源：{data['agency']} + 工信部政务服务平台

## 一、基本信息

| 项目 | 内容 |
|------|------|
| 实施主体 | {data['agency']} |
| 咨询电话 | {data['phone']} |
| 网上办理入口 | https://ythzxfw.miit.gov.cn |

## 二、省特异条款
"""
    if data['note']:
        content += f"\n- {data['note']}\n"
    else:
        content += "\n（无，详见全国通用指南）\n"

    content += """
## 三、受理条件 / 申请材料 / 办理流程 / 费用周期

→ 全部通用，详见 `references/overview.md`（第三条硬性条件、第四条材料、第五条费用）
"""
    return content


def main():
    base_dir = "references/provinces"
    for pinyin, data in PROVINCE_DATA.items():
        path = os.path.join(base_dir, f"{pinyin}.md")
        content = build_province_file(pinyin, data)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ {pinyin}.md  ({len(content.splitlines())} lines)")
    print(f"\n共 {len(PROVINCE_DATA)} 个省文件已压缩为 v2.2 标准结构")


if __name__ == "__main__":
    main()

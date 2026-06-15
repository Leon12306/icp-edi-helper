"""
抓取与结构化解析。

设计原则（准确优先于完整）：
  1. 只接受白名单域名（miit.gov.cn 体系），非白名单一律丢弃
  2. 字段缺失就缺失，不做"猜测填充"
  3. 任何输出都带 source_url + fetched_at，可追溯
  4. 解析失败不抛异常给上层，而是返回 error 字段
"""

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("需要 requests 和 beautifulsoup4：pip3 install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)

try:
    import pdfplumber
    import io as _io
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

from allowlist import is_official_url


# ── 输出数据结构 ───────────────────────────────────────────

@dataclass
class GuideDoc:
    """单条官方办事指南的解析结果"""
    source_url: str
    fetched_at: str                      # ISO 8601
    title: Optional[str] = None
    publish_date: Optional[str] = None   # 例如 "2025-02-20"
    authority: Optional[str] = None      # 实施主体（XX省通信管理局）
    apply_fee: Optional[str] = None
    apply_method: Optional[str] = None
    apply_url: Optional[str] = None
    review_deadline: Optional[str] = None  # 办结时限
    hotline: Optional[str] = None
    apply_conditions: list[str] = field(default_factory=list)
    required_materials: list[str] = field(default_factory=list)
    apply_procedure: list[str] = field(default_factory=list)
    pdf_attachments: list[dict] = field(default_factory=list)  # {title, url}
    full_text_excerpt: Optional[str] = None  # 前 800 字用于人工复核
    error: Optional[str] = None
    parse_warnings: list[str] = field(default_factory=list)
    table_license_row: Optional[dict] = None  # 来自"事项清单"表格行的原始数据


# ── HTTP 抓取 ──────────────────────────────────────────────

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

TIMEOUT = 20


def is_pdf_url(url: str) -> bool:
    """URL 是否指向 PDF 文档（去掉 query/fragment 后判断扩展名）"""
    from urllib.parse import urlparse
    path = urlparse(url).path.lower()
    return path.endswith(".pdf")


def fetch_html(url: str) -> tuple[Optional[str], Optional[str]]:
    """
    抓取 URL 文本内容。
    返回 (html, error)。白名单校验失败时直接返回错误，不发请求。
    """
    if not is_official_url(url):
        return None, f"非白名单域名，拒绝抓取: {url}"

    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
        # 工信部站点多为 utf-8，少量 gb2312；让 requests 自动判别
        resp.encoding = resp.apparent_encoding or resp.encoding
        return resp.text, None
    except requests.exceptions.RequestException as e:
        return None, f"请求失败: {e}"


def fetch_pdf(url: str) -> tuple[Optional[str], Optional[str]]:
    """
    下载 PDF 并提取其中的纯文本。
    返回 (text, error)。白名单校验失败时直接返回错误。
    """
    if not HAS_PDFPLUMBER:
        return None, "缺少 pdfplumber 库：pip3 install pdfplumber"
    if not is_official_url(url):
        return None, f"非白名单域名，拒绝抓取: {url}"

    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
        # 验证 content-type，防止 HTML 错误页被当 PDF 处理
        ct = resp.headers.get("Content-Type", "").lower()
        if "pdf" not in ct and not is_pdf_url(url):
            return None, f"Content-Type 不是 PDF（{ct}），拒绝解析"

        text_parts = []
        with pdfplumber.open(_io.BytesIO(resp.content)) as pdf:
            for page in pdf.pages:
                # 保留表格抽取：合并表格为多行
                page_text = page.extract_text() or ""
                if page_text:
                    text_parts.append(page_text)
        # ── PDF 文本断行规范化 ──
        # pdfplumber 抽取后中文文本经常有"句中换行"，但不会把段落完全打散
        # 策略：
        #   1) 空行 → 段落分隔（保留）
        #   2) 上行不以句末标点（。；！?）结尾 → 视为本段续行，与下行合并
        #   3) 跳过这种"段中续行"合并的情况：下一行是结构化标记
        #      （一/二、/1、/① 等）→ 视为独立行保留
        SENT_END = "。；！？\n"  # 视为段落/句子结束
        STRUCTURE_START = re.compile(
            r"^\s*(?:[一二三四五六七八九十百]+[、．]|[（(][一二三四五六七八九十0-9]+[）)]|\d+[、．]|[①②③④⑤⑥⑦⑧⑨])"
        )
        pages_text = []
        for page_text in text_parts:
            lines = page_text.splitlines()
            merged = []
            buf = ""
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    # 空行：先把 buf flush，再加一个空行
                    if buf:
                        merged.append(buf.rstrip())
                        buf = ""
                    merged.append("")
                    continue
                if not buf:
                    buf = stripped
                else:
                    # buf 不以句末标点结尾 → 视为续行
                    last_char = buf.rstrip()[-1] if buf.rstrip() else ""
                    if last_char not in SENT_END:
                        # 下一行是结构化标记 → 不合并
                        if STRUCTURE_START.match(stripped):
                            merged.append(buf.rstrip())
                            buf = stripped
                        else:
                            buf = buf.rstrip() + stripped
                    else:
                        merged.append(buf.rstrip())
                        buf = stripped
            if buf:
                merged.append(buf.rstrip())
            # 折叠连续空行
            cleaned = re.sub(r"\n{3,}", "\n\n", "\n".join(merged))
            pages_text.append(cleaned)
        return "\n".join(pages_text), None
    except requests.exceptions.RequestException as e:
        return None, f"PDF 下载失败: {e}"
    except Exception as e:
        return None, f"PDF 解析失败: {e}"


# ── 字段解析 ──────────────────────────────────────────────

# 发布时间匹配：常见 "发布时间：2025-02-20 15:16" / "2025-07-02"
PUB_DATE_PATTERNS = [
    r"发布\s*时间\s*[：:]\s*(\d{4})[-年](\d{1,2})[-月](\d{1,2})",
    r"发布\s*时间\s*[：:]\s*(\d{4})[-年](\d{1,2})[-月](\d{1,2})日?\s*\d{0,2}[：:]?\d{0,2}",
    r"发布日期\s*[：:]\s*(\d{4})[-年.](\d{1,2})[-月.](\d{1,2})",
    r"(\d{4})[-年](\d{1,2})[-月](\d{1,2})日?\s+\d{1,2}[：:]\d{1,2}",
]


def parse_publish_date(text: str) -> Optional[str]:
    for pat in PUB_DATE_PATTERNS:
        m = re.search(pat, text)
        if m:
            y, mo, d = m.group(1), m.group(2), m.group(3)
            return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"
    return None


# 办结时限 / 办理时限
# 关键事实：广东通管局写法是 "5 日内决定是否受理；自收到全部申请材料之日起 60 日内审查完毕"
# 要把"受理"和"审查"两个时限都拿到
REVIEW_PATTERNS = [
    # 优先匹配含 "5 日内" / "60 日内" 等关键数字的整句
    r"(\d{1,3}\s*日\s*内\s*决定\s*是否\s*受理)",
    r"(\d{1,3}\s*日\s*内\s*审查\s*完毕)",
    r"(\d{1,3}\s*日\s*内\s*作出\s*批准)",
    r"(\d{1,3}\s*日\s*内\s*作出\s*是否\s*准予)",     # 山西写法
    r"(\d{1,3}\s*日\s*内\s*作出\s*是否\s*受理)",     # 通用
    r"(\d{1,3}\s*日\s*内\s*办结)",
    r"(\d{1,3}\s*个?\s*工作日\s*内\s*完?成?审查工作?)",
    r"(\d{1,3}\s*个?\s*工作日\s*内\s*作出)",
    r"(\d{1,3}\s*日\s*内\s*出具)",
    r"(\d{1,3}\s*日\s*内\s*完成)",
    r"(\d{1,3}\s*日\s*内\s*形成\s*初审\s*意见)",     # 北京写法
    r"(\d{1,3}\s*日\s*内\s*一次性\s*退回\s*补正)",   # 北京/通用
    r"(\d{1,3}\s*日\s*内\s*作出\s*批准\s*或者\s*不予批准\s*的\s*决定)",
    r"(\d{1,3}\s*日\s*内\s*颁发)",
    r"(\d{1,3}\s*个?\s*工作日)",
    r"(?:办理时限|审查时限)[\s\S]{0,100}?(\d{1,3}\s*日(?:内)?)",
    r"(?:自[^。]{0,30}之日[起至]?\s*)(\d{1,3}\s*日)",
]


def parse_review_deadline(text: str) -> Optional[str]:
    """返回多段时限的拼接（如 '5 日内决定是否受理；60 日内审查完毕'）
    若只有一段，返回该段。
    优先级：含'审查/出具/完成/决定/颁发'动词的 > 纯数字"X 日" / "X 工作日"
    """
    found = []
    found_keys = set()  # 去重键
    verb_count = 0
    for pat in REVIEW_PATTERNS:
        m = re.search(pat, text)
        if not m:
            continue
        phrase = re.sub(r"\s+", " ", m.group(1)).strip()
        if not phrase:
            continue
        # 去重键：去掉空格
        key = phrase.replace(" ", "")
        if key in found_keys:
            continue
        # 优先级：含动词的更优先
        is_verb_phrase = any(
            v in phrase for v in ["审查", "出具", "完成", "决定", "颁发", "作出"]
        )
        is_bare = bool(re.fullmatch(r"\d{1,3}\s*日|\d{1,3}\s*个?\s*工作日", phrase.replace(" ", "")))
        if is_bare and verb_count >= 2:
            # 已有 2 段含动词的，跳过纯数字
            continue
        if is_verb_phrase:
            verb_count += 1
        found.append(phrase)
        found_keys.add(key)
        if len(found) >= 3:
            break
    if not found:
        return None
    return "；".join(found)


# 申请条件/材料/流程 的编号列表
# 匹配以下行首模式：
#   "1、xxx"   "1. xxx"   "1）xxx"   "1) xxx"
#   "（一）xxx" "(一) xxx"
#   "(1) xxx"  "(1)、xxx"
#   "- xxx"   "• xxx"
# 注意：行尾不能是 ":" 或 "："（那是子标题）
CONDITION_ITEM_RE = re.compile(
    r"^\s*(?:[（(]?\s*[\d零一二三四五六七八九十]+\s*[）)、.\s]+|[-•]\s+)(.+)$",
    re.MULTILINE,
)


def parse_numbered_list_items(text: str, section_start: str, section_end: Optional[str] = None) -> list[str]:
    """
    从文本中按"申请条件"/"申请材料"等小节抽取编号列表。
    策略：
      1) 一级章节：一、/二、/三、... + 顿号/点号 + 标题（可能含冒号和后续描述）
      2) 章节内：所有编号项（1、/1./（一）/①/⑴）都收
      3) 章节标题里"含冒号的描述"也作为首条
      4) 标题里没显式"申请条件"但用同义词（应当符合、应当具备）的，也视作条件章节
    """
    # section_start 同义词：用于兼容各省用词差异
    SECTION_SYNONYMS = {
        "申请条件": [
            "申请条件", "申办条件", "应具备条件", "应当具备", "应当符合",
            "应当符合下列条件", "应当符合以下条件", "须具备条件",
            "办理条件", "申办条件", "许可条件", "准入条件", "受理条件",
        ],
        "申请材料": [
            "申请材料", "申报材料", "办理材料", "要件", "需提供要件",
            "申办材料", "应提交材料", "提交材料", "应提交的附件材料",
            "其它应提交的附件材料", "其他应提交材料", "申报要件",
        ],
        "办理流程": [
            "办理流程", "申请流程", "办理程序", "申办流程", "办事程序",
            "办理方式", "审批流程",
        ],
    }
    if section_start in SECTION_SYNONYMS:
        candidate_keywords = SECTION_SYNONYMS[section_start] + [section_start]
    else:
        candidate_keywords = [section_start]

    SECTION_RE = re.compile(
        r"^[一二三四五六七八九十]+[、．][^\n]{1,80}$",
        re.MULTILINE,
    )
    section_starts = [(m.start(), m.end(), m.group(0).strip()) for m in SECTION_RE.finditer(text)]

    target_start, target_end = None, len(text)
    best_kw = section_start  # 初始化，给章节路径用
    for pos, end, title in section_starts:
        if any(kw in title for kw in candidate_keywords):
            target_start = pos
            # 下一个章节候选边界词
            end_keywords = [section_end] if section_end else []
            if section_start == "申请条件":
                end_keywords += ["申请材料", "办理材料", "办理流程", "办理程序", "联系方式", "咨询电话", "申办材料", "申办流程", "申报材料"]
            elif section_start == "申请材料":
                end_keywords += ["办理流程", "申请流程", "办理程序", "受理审查", "材料审核", "审核", "联系方式", "联系地址", "受理", "审查", "决定", "办理条件", "申办流程", "法律依据", "受理条件"]
            for p2, e2, t2 in section_starts:
                if p2 > pos:
                    if any(kw in t2 for kw in end_keywords):
                        target_end = p2
                        break
                    # 兜底：下一个章节不包含 section_start 的同义词
                    if not any(kw in t2 for kw in candidate_keywords):
                        target_end = p2
                        break
            break

    if target_start is None:
        # 兜底：直接 find 所有同义词，取最早出现的位置
        # 注意：同义词列表可能很长，要在全文里找最小 pos
        best_pos = None
        best_kw = None
        for kw in candidate_keywords:
            pos = text.find(kw)
            if pos != -1 and (best_pos is None or pos < best_pos):
                best_pos = pos
                best_kw = kw
        if best_pos is None:
            return []
        target_start = best_pos

    if section_end:
        idx = text.find(section_end, target_start + len(section_start))
        if idx != -1:
            target_end = min(target_end, idx)

    # 兜底：若 section_end 没找到，用 end_keywords（适用 sections 没有"一、"等章节前缀的页面）
    if target_end == len(text):
        end_keywords_fallback = []
        if section_start == "申请条件":
            end_keywords_fallback = ["其它应提交的附件材料", "申请材料", "办理流程", "办理程序", "联系方式", "法律依据", "受理条件"]
        elif section_start == "申请材料":
            end_keywords_fallback = ["受理条件", "法律依据", "办理流程", "办理程序", "联系方式", "联系地址"]
        # 找所有 end_keyword 中最早出现的位置
        best_ek_pos = None
        for ek in end_keywords_fallback:
            ek_pos = text.find(ek, target_start + len(best_kw or section_start))
            if ek_pos != -1 and ek_pos > target_start:
                if best_ek_pos is None or ek_pos < best_ek_pos:
                    best_ek_pos = ek_pos
        if best_ek_pos is not None:
            target_end = min(target_end, best_ek_pos)

    # 更紧的结束点：检测子章节分界（如"受理条件"、"法律依据"），避免材料列表吞掉后面内容
    INNER_BREAK = {
        "申请材料": ["受理条件", "法律依据", "办理条件", "审批依据"],
    }.get(section_start, [])
    for ib in INNER_BREAK:
        ib_pos = text.find(ib, target_start + len(best_kw or section_start))
        if ib_pos != -1 and ib_pos > target_start and ib_pos < target_end:
            target_end = ib_pos

    sub = text[target_start:target_end]
    items = []
    for m in CONDITION_ITEM_RE.finditer(sub):
        line = m.group(1).strip()
        if 2 <= len(line) <= 500:
            items.append(line)

    # ── 关键修复：把章节标题里"含冒号的描述"也作为首条 ──
    title_match = SECTION_RE.match(sub)
    if title_match:
        title_text = title_match.group(0).strip()
        colon_pos = title_text.find("：")
        if colon_pos == -1:
            colon_pos = title_text.find(":")
        if colon_pos > 0 and colon_pos < len(title_text) - 1:
            tail = title_text[colon_pos + 1:].strip()
            if 4 <= len(tail) <= 200 and not re.search(r"[:：]$", tail):
                if not items or tail[:20] not in items[0]:
                    items.insert(0, tail)

    # 合并因换行被切碎的"数字+单位"片段
    merged = []
    for line in items:
        if merged:
            prev = merged[-1]
            if (
                prev.rstrip().endswith(("为", "为：", "：", "不低于", "限额为", "额度为"))
                and re.fullmatch(r"\s*[\d.,]+\s*", line)
            ):
                merged[-1] = prev + line
                continue
        if merged and re.fullmatch(r"\s*[\u4e00-\u9fa5,]+\s*", line) and len(line) <= 12:
            merged[-1] = merged[-1] + line
            continue
        merged.append(line)
    return merged


# 联系方式：电话
# 前缀关键词：联系电话 / 咨询电话 / 受理电话 / 联系方式 / 业务咨询
# 中间允许：中文标点、空白、&nbsp;(\xa0)、换行等任意 0-12 字符
PHONE_RE = re.compile(
    r"(?:联系电话|咨询电话|受理电话|联系方式|业务咨询|电话)"
    r"(?:[\s\u4e00-\u9fa5：:、，,。；;（()）【】\[\]／\/&]){0,12}?"
    r"([\d][\d\-/（）()／\/]{6,29}\d)"
)


def parse_hotline(text: str) -> Optional[str]:
    m = PHONE_RE.search(text)
    if m:
        # 清洗：去掉 NBSP/不间断空白和所有空白字符
        phone = re.sub(r"\s+", "", m.group(1))
        phone = phone.replace("\xa0", "").replace("\u3000", "")
        # 截断到第一个非数字/非短横/非括号字符
        clean = re.match(r"[\d\-/（）()]+", phone)
        if clean:
            return clean.group(0)
        return phone
    return None


# 实施主体
AUTHORITY_PATTERNS = [
    r"主办机构\s*[：:]\s*([^\n。]{2,30})",
    r"办理机构\s*[：:]\s*([^\n。]{2,30})",
    r"实施主体\s*[：:]\s*([^\n。]{2,30})",
    r"由\s*([\u4e00-\u9fa5]{2,15}通信管理局)\s*负责",
]


def parse_authority(text: str) -> Optional[str]:
    for pat in AUTHORITY_PATTERNS:
        m = re.search(pat, text)
        if m:
            return m.group(1).strip()
    return None


# PDF 附件
def parse_pdf_attachments(soup: BeautifulSoup, base_url: str) -> list[dict]:
    attachments = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if href.lower().endswith(".pdf") or ".pdf?" in href.lower():
            abs_url = urljoin(base_url, href)
            if is_official_url(abs_url):
                attachments.append({"title": text or "未命名PDF", "url": abs_url})
    return attachments


def parse_table_license_row(soup: BeautifulSoup) -> Optional[dict]:
    """从"事项清单"表格中抽取"电信业务经营许可"行的字段。

    适用于"为企业办实事清单"等表格化页（如安徽）。
    表头通常为：序号|事项名称|事项概述|服务对象|办理方式|申办材料|办理时限|收费标准及依据|其他
    """
    # 关键词：业务名
    business_keywords = [
        "电信业务经营许可", "增值电信业务经营许可",
        "电信业务经营许可证", "增值电信业务许可证",
    ]

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue
        # 找表头
        header_row = rows[0]
        headers = [c.get_text(strip=True) for c in header_row.find_all(["th", "td"])]
        if not headers:
            continue
        # 表头必须含"事项名称"和"申办材料"
        if "事项名称" not in headers or "申办材料" not in headers:
            continue

        col_name = headers.index("事项名称")
        col_overview = headers.index("事项概述") if "事项概述" in headers else -1
        col_materials = headers.index("申办材料")
        col_way = headers.index("办理方式") if "办理方式" in headers else -1
        col_deadline = headers.index("办理时限") if "办理时限" in headers else -1
        col_fee = headers.index("收费标准及依据") if "收费标准及依据" in headers else -1
        col_object = headers.index("服务对象") if "服务对象" in headers else -1

        # 找含 "电信业务经营许可" 的行
        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            if len(cells) <= col_materials:
                continue
            name = cells[col_name].get_text(strip=True)
            if not any(kw in name for kw in business_keywords):
                continue
            # 找到了！抽字段
            materials_text = cells[col_materials].get_text(strip=True) if col_materials >= 0 else ""
            overview = cells[col_overview].get_text(strip=True) if col_overview >= 0 else ""
            way = cells[col_way].get_text(strip=True) if col_way >= 0 else ""
            deadline = cells[col_deadline].get_text(strip=True) if col_deadline >= 0 else ""
            fee = cells[col_fee].get_text(strip=True) if col_fee >= 0 else ""
            obj = cells[col_object].get_text(strip=True) if col_object >= 0 else ""

            # 拆分材料："1、xxx；2、xxx；3、xxx" → ["xxx", "xxx", "xxx"]
            materials_list = []
            for part in re.split(r"[；;]", materials_text):
                part = part.strip()
                if not part:
                    continue
                # 去掉前导编号 "1、"
                m = re.match(r"^\s*[\d零一二三四五六七八九十]+[、．.）)\s]+(.+)$", part)
                if m:
                    materials_list.append(m.group(1).strip())
                else:
                    materials_list.append(part)

            return {
                "name": name,
                "overview": overview,
                "object": obj,
                "way": way,
                "materials": materials_list,
                "materials_raw": materials_text,
                "deadline": deadline,
                "fee": fee,
            }
    return None


# ── 主解析函数 ────────────────────────────────────────────

def _extract_structured_fields(doc: GuideDoc, full_text: str) -> None:
    """把 full_text 中的关键字段填到 doc（HTML 和 PDF 共用）"""
    full_text = re.sub(r"\n{2,}", "\n", full_text)
    # 关键：把"一、\n申请条件"合并成"一、申请条件"，让一级章节标题和文字回到一行
    # 这只对单换行做合并（双换行已被上面折叠），不会把段落粘在一起
    full_text = re.sub(r"(?<=[、．])\n(?=[\u4e00-\u9fa5])", "", full_text)

    # 发布日期
    doc.publish_date = parse_publish_date(full_text)

    # 实施主体
    doc.authority = parse_authority(full_text)

    # 办结时限
    doc.review_deadline = parse_review_deadline(full_text)

    # 咨询电话
    doc.hotline = parse_hotline(full_text)

    # 申请条件（识别 "三、申请条件" 段）
    doc.apply_conditions = parse_numbered_list_items(
        full_text,
        section_start="申请条件",
        section_end="申请材料",
    )

    # 申请材料（识别 "四、申请材料" / "五、办理材料" 段）
    # 关键：必须在材料列表出现 **之后** 找 section_end，否则会把申请条件段包进来
    raw_materials = parse_numbered_list_items(
        full_text,
        section_start="申请材料",
        section_end="办理流程",
    )
    if not raw_materials:
        raw_materials = parse_numbered_list_items(
            full_text,
            section_start="办理材料",
            section_end="办理流程",
        )

    # 过滤掉明显不是材料条目的内容（小节标题、章节编号、纯符号）
    MATERIAL_BLOCKLIST_PREFIXES = (
        "证书领取", "电子证照", "纸质证书", "法律依据", "设定依据",
        "申请条件", "申请材料提交", "申请材料审核", "申请材料清单",
        "办理流程", "办理地点", "联系方式",
        "收费标准", "办理时间", "数量限制", "禁止性要求", "注意事项",
        "业务种类", "申请流程", "相关下载", "常见问题",
        # 注意：不要过滤"申请表"——它是真实材料名
    )
    doc.required_materials = [
        m for m in raw_materials
        if not any(m.startswith(p) for p in MATERIAL_BLOCKLIST_PREFIXES)
        and len(m) >= 4
    ]

    # 申请流程
    doc.apply_procedure = parse_numbered_list_items(
        full_text,
        section_start="办理流程",
        section_end="费用",
    )

    # 留个摘要，方便人工复核
    doc.full_text_excerpt = full_text[:800]

    # 警告
    if not doc.apply_conditions:
        doc.parse_warnings.append("未解析出申请条件")
    if not doc.required_materials:
        doc.parse_warnings.append("未解析出申请材料")
    if not doc.review_deadline:
        doc.parse_warnings.append("未解析出办结时限")


def parse_guide(url: str) -> GuideDoc:
    """抓取并解析单个办事指南页（自动识别 HTML / PDF）"""
    doc = GuideDoc(
        source_url=url,
        fetched_at=datetime.now().isoformat(timespec="seconds"),
    )

    # ── PDF 路径 ──
    if is_pdf_url(url):
        full_text, err = fetch_pdf(url)
        if err:
            doc.error = err
            return doc
        # PDF 标题通常在文档首行；粗略取第一行去掉空白作 title
        first_lines = [l.strip() for l in full_text.splitlines() if l.strip()]
        if first_lines:
            doc.title = first_lines[0][:200]
        _extract_structured_fields(doc, full_text)
        return doc

    # ── HTML 路径 ──
    html, err = fetch_html(url)
    if err:
        doc.error = err
        return doc

    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        doc.error = f"HTML 解析失败: {e}"
        return doc

    # 标题：通常在 h1 / .article-title / title 中
    title_candidates = [
        soup.select_one("h1"),
        soup.select_one(".article-title"),
        soup.select_one(".title"),
        soup.select_one("title"),
    ]
    for tag in title_candidates:
        if tag and tag.get_text(strip=True):
            doc.title = tag.get_text(strip=True)
            break

    # 提取正文文本（去 script/style/header/nav/footer）
    for tag in soup(["script", "style", "header", "nav", "footer", "aside"]):
        tag.decompose()
    body = soup.find("body") or soup
    full_text = body.get_text(separator="\n", strip=True)

    # PDF 附件
    doc.pdf_attachments = parse_pdf_attachments(soup, url)

    # ── 回退：HTML 正文很短 + 有 PDF 附件 → 解析 PDF（宁夏这种） ──
    if len(full_text.strip()) < 400 and doc.pdf_attachments:
        # 找带"指南"/"许可"/"审批"/"申请"等关键词的 PDF
        target_pdf = None
        for pdf in doc.pdf_attachments:
            t = pdf.get("title", "")
            u = pdf.get("url", "").lower()
            if any(kw in t for kw in ["指南", "许可", "审批", "申请"]) or "guide" in u:
                target_pdf = pdf
                break
        if target_pdf is None and doc.pdf_attachments:
            target_pdf = doc.pdf_attachments[0]

        if target_pdf:
            pdf_text, pdf_err = fetch_pdf(target_pdf["url"])
            if not pdf_err and pdf_text and len(pdf_text.strip()) > 200:
                # 把 PDF 文本作为主内容
                if not doc.title or len(doc.title) < 5:
                    first_lines = [l.strip() for l in pdf_text.splitlines() if l.strip()]
                    if first_lines:
                        doc.title = first_lines[0][:200]
                _extract_structured_fields(doc, pdf_text)
                doc.parse_warnings.append(f"内容来自 PDF 附件: {target_pdf['title']}")
                return doc

    # 共用结构化字段抽取
    _extract_structured_fields(doc, full_text)

    # 表格化页面（"为企业办实事清单"）回退：用 table parser 覆盖
    license_row = parse_table_license_row(soup)
    if license_row:
        # 用表格行的精确数据覆盖
        doc.required_materials = license_row["materials"]
        doc.parse_warnings.append(
            f"材料来自表格行 '{license_row['name']}' (事项清单页)"
        )
        if license_row["overview"] and (not doc.apply_conditions or len(doc.apply_conditions) < 2):
            doc.apply_conditions = [license_row["overview"]]
        if license_row["deadline"]:
            doc.review_deadline = license_row["deadline"]
        if license_row["way"]:
            # 用"办理方式"作为唯一流程，覆盖之前的噪声
            doc.apply_procedure = [license_row["way"]]
        if license_row["fee"]:
            doc.apply_fee = license_row["fee"]
        doc.table_license_row = license_row

    # 总览页（青海型）：3 大业务名并列，识别为"无独立指南页"
    OVERVIEW_KEYWORDS = ["经营许可", "码号资源", "互联网管理"]
    if (
        not doc.required_materials
        and not doc.review_deadline
        and all(kw in full_text for kw in OVERVIEW_KEYWORDS)
    ):
        doc.parse_warnings.append("总览页：仅含 3 大业务简介，无具体条件/材料/时限")

    return doc


# ── 调试输出 ──────────────────────────────────────────────

def to_json(doc: GuideDoc) -> str:
    return json.dumps(asdict(doc), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 简单自测：解析广东通管局官方页
    test_url = "https://gdca.miit.gov.cn/bsfw/bszn/jyxk/tzgg/art/2025/art_9802f0eeae4647b5bc22a6af33ae0bf7.html"
    print(f"测试 URL: {test_url}\n")
    doc = parse_guide(test_url)
    print(to_json(doc))

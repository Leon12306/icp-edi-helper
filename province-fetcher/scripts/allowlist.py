"""
白名单域名与候选 URL 构造。

准确采集的第一性原理：只接受工信部体系（miit.gov.cn）下的页面作为权威源。
搜狐/顺企网/网易/今日头条/中帆等第三方转载一律不收。
"""

# ── 域名白名单 ─────────────────────────────────────────────
# 全部是工信部 ICP 备案下的官方域名
OFFICIAL_DOMAIN_SUFFIXES = (
    "miit.gov.cn",          # 工信部及各省通管局
    "beian.miit.gov.cn",    # 备案管理系统
    "ythzxfw.miit.gov.cn",  # 工信部政务服务平台（在线办理入口）
    "dxzhgl.miit.gov.cn",   # 电信业务市场综合管理信息系统
    "tsm.miit.gov.cn",      # 综合管理系统（年报/咨询）
    "jyhwzhq.miit.gov.cn",  # 集约化综合管理平台（各省 PDF 附件托管）
)

# 必须拒绝的第三方域名后缀（出现即丢弃，避免误用营销稿）
BLOCKED_DOMAIN_SUFFIXES = (
    "sohu.com",
    "toutiao.com",
    "163.com",
    "11467.com",        # 顺企网
    "trustexporter.com",
    "51sole.com",       # 搜了网
    "007swz.com",
    "qq.com",
    "weibo.com",
    "douban.com",
    "zhihu.com",
)

# 工信部首页常被引用的站内组织结构入口（用于发现新省份的官方页）
SEED_URLS = [
    "https://www.miit.gov.cn/zzjg/index.html",   # 工信部组织机构页
    "https://tsm.miit.gov.cn/dxxzsp/contact.jsp",  # 31省咨询电话表
]


def is_official_url(url: str) -> bool:
    """判断 URL 是否在白名单域名内"""
    from urllib.parse import urlparse
    host = urlparse(url).netloc.lower()
    if not host:
        return False
    if any(host.endswith(suf) for suf in BLOCKED_DOMAIN_SUFFIXES):
        return False
    return any(host.endswith(suf) for suf in OFFICIAL_DOMAIN_SUFFIXES)


# ── 候选 URL 构造 ─────────────────────────────────────────
# 各省通管局办事指南页通常落在以下路径规律中
CANDIDATE_PATH_TEMPLATES = [
    "/bsfw/bszn/index.html",                                # 办事指南列表
    "/bsfw/bszn/jyxk/index.html",                           # 经营许可子目录
    "/bsfw/bszn/jyxk/tzgg/index.html",                      # 通知公告子目录
    "/zwgk/dxhhlwgl/index.html",                            # 电信和互联网管理目录
    "/zwgk/dxhhlwgl/jsxm/index.html",                       # 电信业务经营许可
    # 具体文章路径无法预测，留给搜索引擎定位
]


def build_candidate_urls(short_domain: str) -> list[str]:
    """根据省通管局短域名，构造可能存在办事指南的候选 URL 列表"""
    base = f"https://{short_domain}".rstrip("/")
    return [base + path for path in CANDIDATE_PATH_TEMPLATES]


def build_subsection_urls(short_domain: str) -> list[str]:
    """构造省通管局常见子站入口，用于人工补充候选"""
    return [
        f"https://{short_domain}/bsfw/",
        f"https://{short_domain}/bsfw/bszn/",
        f"https://{short_domain}/zwgk/",
        f"https://{short_domain}/zwgk/dxhhlwgl/",
        f"https://{short_domain}/tzgg/",   # 通知公告
    ]


# ── 标题关键词（用于从搜索结果/列表页中识别真正的"办事指南"页） ──
GUIDE_TITLE_KEYWORDS = [
    "增值电信业务经营许可",
    "增值电信业务经营许可证",
    "ICP",
    "EDI",
    "电信业务经营许可",
    "电信业务市场",
    "信息服务业务",
    "在线数据处理与交易处理",
]

# 强信号：标题里同时含 "指南" / "办事指南" / "申请" 才认为有内容价值
GUIDE_TITLE_MUST_CONTAIN_ANY = [
    "指南",
    "申请",
    "办事",
    "材料",
    "条件",
]

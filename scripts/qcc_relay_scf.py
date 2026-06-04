"""
企查查 API 中继 — 腾讯云 SCF 云函数
用途：解决海外服务器「数据不能出境」问题
部署：腾讯云 SCF → 国内区域 → 函数 URL 触发器
"""

import hashlib
import json
import os
import time
from urllib import parse, request as urlreq

# ── 密钥通过 SCF 环境变量注入 ──
APP_KEY = os.environ["QCC_APP_KEY"]
SECRET_KEY = os.environ["QCC_SECRET_KEY"]
API_URL = "https://api.qichacha.com/ECIV4/GetBasicDetailsByName"


def _auth_headers():
    """企查查鉴权：Token = MD5(AppKey+Timespan+SecretKey).upper()"""
    ts = str(int(time.time()))
    token = hashlib.md5((APP_KEY + ts + SECRET_KEY).encode()).hexdigest().upper()
    return {"Token": token, "Timespan": ts}


def _json_resp(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(body, ensure_ascii=False),
    }


def main_handler(event, context):
    # 1. 取 keyword（兼容函数 URL 和 API 网关两种事件格式）
    qs = event.get("queryStringParameters") or event.get("queryString") or {}
    keyword = qs.get("keyword", "").strip()
    if not keyword:
        return _json_resp(400, {"error": True, "message": "缺少 keyword 参数"})

    # 2. 转发请求到企查查
    url = f"{API_URL}?key={APP_KEY}&keyword={parse.quote(keyword)}"
    req = urlreq.Request(url, headers=_auth_headers())

    try:
        with urlreq.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return _json_resp(200, data)
    except Exception as e:
        return _json_resp(502, {"error": True, "message": f"企查查请求失败: {e}"})

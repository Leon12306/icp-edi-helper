import json
import re
import sys
sys.path.insert(0, 'province-fetcher/scripts')
from fetcher import fetch_html
from bs4 import BeautifulSoup

with open('province-fetcher/data/provinces_meta.json', 'r') as f:
    meta = json.load(f)

targets = ['北京', '天津', '山西', '广东', '海南', '西藏', '新疆']

url_map = {}
for p in meta['provinces']:
    if p['name_zh'] in targets:
        url_map[p['name_zh']] = p.get('guide_url')

for name in targets:
    url = url_map.get(name)
    if not url:
        print(f'=== {name} === NO URL')
        continue
    try:
        html, _ = fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        print(f'=== {name} (text_len={len(text)}) ===')
        for m in list(re.finditer(r'.{15}(?:\d+\s*个?\s*工作日|\d+\s*日).{15}', text))[:8]:
            ctx = m.group(0).replace('\n', '|')
            print('  RD ctx:', repr(ctx))
        print()
    except Exception as e:
        print(f'=== {name} === ERROR: {e}')

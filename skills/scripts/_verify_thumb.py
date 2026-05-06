import json, sys, re, requests
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

records = [json.loads(l) for l in open(r'.cursor/skills/level-common/resource_index.jsonl', encoding='utf-8')]

targets = ['宝箱', '食人花', '马车', '桥板数字7']
found = []
for name in targets:
    for r in records:
        if r.get('type') == 'MeshPart' and r.get('name') == name:
            found.append((r['id'], r['name'], r.get('subcategory','')))
            break

for aid, name, sub in found:
    print(f"id={aid}  name={name}  subcategory={sub}")

# 下载第一个的缩略图
with open(r'.cursor/skills/level-common/资源预览图/preview_urls.md', encoding='utf-8') as f:
    text = f.read()
obj_section = text[text.find('## 物件'):]
url_map = dict(re.findall(r'AssetId=(\d+)\):\s*(https?://\S+)', obj_section))

for aid, name, sub in found[:2]:
    url = url_map.get(str(aid))
    if url:
        ext = url.split('.')[-1].lower()
        p = Path(f'.tmp_thumbnails/verify_{aid}.{ext}')
        if not p.exists():
            r = requests.get(url, timeout=10)
            p.write_bytes(r.content)
        print(f"下载: {p}  (name={name})")

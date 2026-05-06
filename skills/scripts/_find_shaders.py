import sys, re
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

MEISHU = Path(r'D:\meishu\Assets')

# 在整个 Assets 目录搜索 shader GUID
target_guids = {
    '35c766587d43e0b438a2016b86f6e45f': 'GUID_A(1340次)',
    '9e0b78a84584ffb4b9d963b4c6f26436': 'GUID_B(1024次)',
    '490ca57f88ccf7640937aeabbdb5251f': 'GUID_C(913次)',
    'f6cfad5ad170a024d90ca61d63882e74': 'GUID_D(764次)',
    'ea0864178139ac84da5cd6df7ba2f82c': 'GUID_E(376次)',
    '8fa84e1c8f3a97b4bb416e8eb087630e': 'GUID_F(304次)',
}

GUID_RE = re.compile(r'guid:\s*([a-f0-9]{32})')
found = {}
print('搜索 shader meta 文件...')
for meta_p in MEISHU.rglob('*.meta'):
    try:
        txt = meta_p.read_text(encoding='utf-8', errors='ignore')
        m = GUID_RE.search(txt)
        if m and m.group(1) in target_guids:
            g = m.group(1)
            src_p = meta_p.with_suffix('')
            found[g] = src_p
    except:
        pass

print(f'命中 {len(found)} / {len(target_guids)}:')
for g, label in target_guids.items():
    if g in found:
        sp = found[g]
        print(f'  {label} → {sp}')
        if sp.exists():
            txt = sp.read_text(encoding='utf-8', errors='ignore')
            first = txt.splitlines()[0]
            print(f'    首行: {first}')
    else:
        print(f'  {label} → 未找到')

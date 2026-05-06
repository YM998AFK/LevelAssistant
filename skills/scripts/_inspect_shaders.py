import sys, re
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

MEISHU = Path(r'D:\meishu\Assets\BundleResources')
GUID_RE = re.compile(r'guid:\s*([a-f0-9]{32})')

# 统计所有 mat 里的 shader guid
shader_guids = {}
for mat in MEISHU.rglob('*.mat'):
    try:
        txt = mat.read_text(encoding='utf-8', errors='ignore')
        m = re.search(r'm_Shader:\s*\{fileID:\s*(\d+),\s*guid:\s*([a-f0-9]+)', txt)
        if m:
            fid, guid = m.group(1), m.group(2)
            if guid not in shader_guids:
                shader_guids[guid] = {'fileID': fid, 'count': 0}
            shader_guids[guid]['count'] += 1
    except:
        pass

print(f'发现 {len(shader_guids)} 种不同 shader GUID：')
for g, info in sorted(shader_guids.items(), key=lambda x: -x[1]['count'])[:20]:
    print(f'  {g} (fileID={info["fileID"]}) 使用次数={info["count"]}')

# 查找这些 guid 对应的 .shader 文件
print('\n反查 .shader 文件...')
shader_meta_map = {}
for meta_p in MEISHU.rglob('*.shader.meta'):
    try:
        txt = meta_p.read_text(encoding='utf-8', errors='ignore')
        m = GUID_RE.search(txt)
        if m:
            shader_meta_map[m.group(1)] = meta_p.with_suffix('')
    except:
        pass
# 也搜 .hlsl .cginc
for meta_p in MEISHU.rglob('*.meta'):
    if 'shader' in meta_p.stem.lower() or 'Shader' in meta_p.stem:
        try:
            txt = meta_p.read_text(encoding='utf-8', errors='ignore')
            m = GUID_RE.search(txt)
            if m:
                shader_meta_map[m.group(1)] = meta_p

        except:
            pass

print(f'找到 shader meta: {len(shader_meta_map)} 个')
for g in list(shader_guids.keys())[:10]:
    if g in shader_meta_map:
        sp = shader_meta_map[g]
        print(f'  {g} → {sp.name}')
        if sp.exists():
            first_line = sp.read_text(encoding='utf-8', errors='ignore').splitlines()[0]
            print(f'    内容首行: {first_line}')
    else:
        print(f'  {g} → 未找到对应文件')

# 常见 Unity 内置 shader guid
BUILTIN = {
    '0000000000000000f000000000000000': 'Unity/Standard',
    '0000000000000000e000000000000000': 'Unity/Diffuse',
    'fe21ea43d7cb4c94f83bc6e97755e3dc': 'Unity/Standard(Specular)',
}
print('\n内置 shader 命中:')
for g, name in BUILTIN.items():
    if g in shader_guids:
        print(f'  {g} ({name}) 使用次数={shader_guids[g]["count"]}')

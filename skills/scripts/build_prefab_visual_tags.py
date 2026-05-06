"""
从 D:\meishu 的贴图/材质文件提取 3D 物件的准确颜色和渲染风格标签。

提取字段：
- dominant_color: 从真实贴图像素提取主色（替代场景截图色）
- is_transparent: 材质 RenderQueue > 2450
- render_style: Unlit / Lit / Toon
- has_emission: 是否有自发光
- color_source: "texture"（来源标注）
"""
import re, json, sys, colorsys
from pathlib import Path
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("警告: Pillow 未安装，跳过颜色提取。运行: pip install Pillow")

MEISHU    = Path(r'D:\meishu\Assets\BundleResources')
REPO_ROOT = Path(r'c:\Users\Hetao\Desktop\公司')
PREFAB_MD = REPO_ROOT / '.cursor/skills/level-common/object_prefab_meta.md'
JSONL     = REPO_ROOT / '.cursor/skills/level-common/resource_index.jsonl'

GUID_RE = re.compile(r'guid:\s*([a-f0-9]{32})')

# ─── 色名映射 ─────────────────────────────────────────────────────────────────
def rgb_to_colorname(r, g, b) -> str:
    if max(r, g, b) < 30:
        return "黑"
    if min(r, g, b) > 220:
        return "白"
    if max(r, g, b) - min(r, g, b) < 25:
        if max(r, g, b) > 180:
            return "白"
        return "灰"
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if s < 0.12:
        return "灰"
    deg = h * 360
    if deg < 15 or deg >= 345: return "红"
    if deg < 45:  return "橙"
    if deg < 75:  return "黄"
    if deg < 165: return "绿"
    if deg < 195: return "青"
    if deg < 255: return "蓝"
    if deg < 285: return "紫"
    if deg < 345: return "粉"
    return "红"


def dominant_color_from_file(path: Path) -> str | None:
    if not HAS_PIL or not path.exists():
        return None
    try:
        img = Image.open(path)
        if img.mode == 'RGBA':
            bg = Image.new('RGB', img.size, (128, 128, 128))
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.resize((32, 32))
        pixels = list(img.getdata())
        # 过滤近黑/近白（背景色）再求平均
        valid = [p for p in pixels if not (max(p) < 20 or min(p) > 235)]
        if not valid:
            valid = pixels
        r = sum(p[0] for p in valid) // len(valid)
        g = sum(p[1] for p in valid) // len(valid)
        b = sum(p[2] for p in valid) // len(valid)
        return rgb_to_colorname(r, g, b)
    except Exception as e:
        return None


# ─── 从 object_prefab_meta.md 资源追溯表解析贴图路径 ─────────────────────────
def parse_texture_map(md_text: str) -> dict[str, list[str]]:
    """返回 {str_id: [tex_filename, ...]}"""
    result: dict[str, list[str]] = defaultdict(list)
    in_trace = False
    for line in md_text.splitlines():
        if '## 资源追溯' in line:
            in_trace = True
            continue
        if in_trace and line.startswith('## '):
            break
        if not in_trace or not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 5 or not cells[0].isdigit():
            continue
        aid = cells[0]
        tex_cell = cells[4]  # 贴图列
        if tex_cell and tex_cell != '-':
            names = [t.strip() for t in tex_cell.split(',') if t.strip()]
            result[aid].extend(names)
    return dict(result)


# ─── 在 meishu 里查找贴图文件 ─────────────────────────────────────────────────
# 建立文件名 → 路径索引（只扫 model/ 下）
print("建立贴图文件名索引...")
tex_name_index: dict[str, Path] = {}
for p in (MEISHU / 'model').rglob('*'):
    if p.suffix.lower() in {'.png', '.tga', '.jpg', '.psd', '.exr'}:
        tex_name_index[p.name] = p
print(f"  贴图索引: {len(tex_name_index)} 个文件")


# ─── Shader GUID 硬编码表（已通过 _find_shaders.py 确认）────────────────────
SHADER_GUID_STYLE: dict[str, str] = {
    # Toon（卡通/赛璐珞渲染）
    '35c766587d43e0b438a2016b86f6e45f': 'Toon',   # CelOutline SampleColor
    '9e0b78a84584ffb4b9d963b4c6f26436': 'Toon',   # CelNoOutline
    '8fa84e1c8f3a97b4bb416e8eb087630e': 'Toon',   # CelOutline
    # Standard（Unity 标准光照）
    '0000000000000000f000000000000000': 'Lit',    # Unity/Standard
    # VFX（粒子/特效透明混合）
    '490ca57f88ccf7640937aeabbdb5251f': 'VFX',   # XC_P_ADD_Mask_CD（加法）
    'f6cfad5ad170a024d90ca61d63882e74': 'VFX',   # XC_P_Blender_Mask_CD
    'ea0864178139ac84da5cd6df7ba2f82c': 'VFX',   # XC_P_Blender
    # 其余自定义（较少）
    '595c4ff2e28a47c47a5ef03ec4b17506': 'Toon',  # 待确认，量219
    'a85f4d0994a21764890b809ec5315778': 'Toon',  # 待确认，量215
}

# ─── 从 .mat 文件提取渲染信息 ─────────────────────────────────────────────────
# 先建 guid → mat_path 索引
print("建立 material guid 索引...")
mat_guid_index: dict[str, Path] = {}
for meta_p in MEISHU.rglob('*.mat.meta'):
    mat_p = meta_p.with_suffix('')  # remove .meta
    if not mat_p.exists():
        continue
    try:
        txt = meta_p.read_text(encoding='utf-8', errors='ignore')
        m = GUID_RE.search(txt)
        if m:
            mat_guid_index[m.group(1)] = mat_p
    except Exception:
        pass
print(f"  material 索引: {len(mat_guid_index)} 个")

# shader 使用硬编码 GUID 表（SHADER_GUID_STYLE），无需动态扫描


def parse_mat(mat_path: Path) -> dict:
    """从 .mat 提取 render_queue / render_style / has_emission"""
    info = {}
    try:
        txt = mat_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return info
    # render queue
    m = re.search(r'm_CustomRenderQueue:\s*(-?\d+)', txt)
    if m:
        rq = int(m.group(1))
        if rq > 0:
            info['render_queue'] = rq
            info['is_transparent'] = rq > 2450
    # shader guid → 用硬编码表
    m = re.search(r'm_Shader:\s*\{fileID:\s*\d+,\s*guid:\s*([a-f0-9]+)', txt)
    if m:
        sg = m.group(1)
        style = SHADER_GUID_STYLE.get(sg)
        if style:
            info['render_style'] = style
    # emission：只有 keywords 里有独立的 _EMISSION 列表项才算真正开启
    has_em = bool(re.search(r'^[ \t]*-[ \t]+_EMISSION\b', txt, re.MULTILINE))
    info['has_emission'] = has_em
    return info


# ─── 从 prefab 文件提取所引用的 material guids ────────────────────────────────
def get_mat_guids_from_prefab(prefab_path: Path) -> list[str]:
    guids = []
    try:
        txt = prefab_path.read_text(encoding='utf-8', errors='ignore')
        # m_Materials: 段
        in_mats = False
        for line in txt.splitlines():
            s = line.strip()
            if s.startswith('m_Materials:'):
                in_mats = True
                continue
            if in_mats:
                if s.startswith('-') and 'guid:' in line:
                    m = GUID_RE.search(line)
                    if m:
                        guids.append(m.group(1))
                elif s.startswith('m_') and not s.startswith('m_Materials'):
                    in_mats = False
    except Exception:
        pass
    return list(set(guids))


# ─── 主处理 ───────────────────────────────────────────────────────────────────
print("\n解析 object_prefab_meta.md 贴图追溯表...")
md_text = PREFAB_MD.read_text(encoding='utf-8')
tex_map = parse_texture_map(md_text)
print(f"  有贴图追溯的物件: {len(tex_map)} 个")

# prefab 路径索引
SPRITE3D_DIR = MEISHU / 'ide' / 'sprite3d'
prefab_index: dict[str, Path] = {}
for p in SPRITE3D_DIR.glob('*.prefab'):
    prefab_index[p.name] = p

print("\n读取 resource_index.jsonl...")
records = [json.loads(l) for l in JSONL.open(encoding='utf-8')]
meshparts = {str(r['id']): r for r in records if r.get('type') == 'MeshPart'}

# 从 object_prefab_meta.md 主表解析 prefab 文件名
print("解析主表 prefab 文件名...")
prefab_name_map: dict[str, str] = {}  # aid → prefab_filename
in_main = False
for line in md_text.splitlines():
    if '## 主表' in line:
        in_main = True
        continue
    if in_main and line.startswith('## '):
        break
    if not in_main or not line.startswith('|'):
        continue
    cells = [c.strip() for c in line.strip('|').split('|')]
    if len(cells) >= 3 and cells[0].isdigit():
        prefab_name_map[cells[0]] = cells[2]  # aid → prefab filename

print(f"  prefab 文件名映射: {len(prefab_name_map)} 个")

# ─── 逐物件提取 ───────────────────────────────────────────────────────────────
print("\n开始提取颜色/渲染属性...")
color_hits = 0
mat_hits = 0
color_dist: Counter = Counter()
style_dist: Counter = Counter()

# 先清空可能有误的旧值
for r in meshparts.values():
    r.pop('has_emission', None)

for aid, r in meshparts.items():
    # 1. dominant_color from texture
    color_set = False
    tex_names = tex_map.get(aid, [])
    for tname in tex_names:
        tp = tex_name_index.get(tname)
        if tp:
            c = dominant_color_from_file(tp)
            if c:
                r['dominant_color'] = c
                r['color_source'] = 'texture'
                color_dist[c] += 1
                color_hits += 1
                color_set = True
                break

    # 2. render info from material
    pfab_name = prefab_name_map.get(aid)
    pfab_path = prefab_index.get(pfab_name) if pfab_name else None
    if pfab_path:
        mat_guids = get_mat_guids_from_prefab(pfab_path)
        mat_infos = []
        for g in mat_guids:
            mp = mat_guid_index.get(g)
            if mp:
                mat_infos.append(parse_mat(mp))

        if mat_infos:
            mat_hits += 1
            # 合并多个 material 的信息（取第一个非空，render_style 每次覆盖）
            for info in mat_infos:
                if 'is_transparent' in info:
                    r['is_transparent'] = info['is_transparent']
                if 'render_style' in info:
                    style_dist[info['render_style']] += 1
                    r['render_style'] = info['render_style']
                if info.get('has_emission') and not r.get('has_emission'):
                    r['has_emission'] = True
                break  # 只取第一个有效 material

print(f"  dominant_color 提取成功: {color_hits} / {len(meshparts)}")
print(f"  material 信息提取成功: {mat_hits} / {len(meshparts)}")
print(f"  颜色分布: {dict(color_dist.most_common())}")
print(f"  渲染风格分布: {dict(style_dist.most_common())}")

# ─── 写回 jsonl ───────────────────────────────────────────────────────────────
print("\n写回 resource_index.jsonl...")
with JSONL.open('w', encoding='utf-8') as f:
    for rec in records:
        clean = {k: v for k, v in rec.items() if v is not None and v != '' and v != []}
        f.write(json.dumps(clean, ensure_ascii=False, separators=(',', ':')) + '\n')
print("完成！")

"""扫 D:\\meishu 的物件 prefab，提取美术目录里真正有用的元数据。

补齐「prefab 源头层」的信息（相比 .ws 实例层）：

- **碰撞体**（Box/Sphere/Capsule/Mesh）类型、尺寸、中心偏移、是否 Trigger
- **Animator** 控制器 guid → 追到 .controller 文件 → 权威 AnimatorState clip 名
- **动画 loop / duration**（来自 .fbx.meta 的 clipAnimations）
- **Mesh 源 FBX 追溯**：MeshFilter/SkinnedMeshRenderer 引用哪些 FBX
- **Material / 贴图追溯**：prefab → .mat → _MainTex/_BaseMap 贴图文件
- **渲染方式 / 粒子 / 光源 / 音源**
- **MonoBehaviour 脚本 guid 列表**（识别 pangu 引擎组件）
- **默认 Scale / 子节点数**

产出：.cursor/skills/level-common/object_prefab_meta.md
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# ─── 路径配置 ───────────────────────────────────────────────────────
REPO_ROOT = Path(r"c:\Users\Hetao\Desktop\公司")
MEISHU_ROOT = Path(r"D:\meishu\Assets\BundleResources")
SPRITE3D_DIR = MEISHU_ROOT / "ide" / "sprite3d"
CHARACTER_DIR = MEISHU_ROOT / "ide" / "character"
MODEL_DIR = MEISHU_ROOT / "model"

CATALOG = REPO_ROOT / ".cursor" / "skills" / "level-common" / "asset_catalog.md"
OUT = REPO_ROOT / ".cursor" / "skills" / "level-common" / "object_prefab_meta.md"

# 采样率：Unity 默认 30 fps（clipAnimations 里不写 sampleRate，只有帧号）
DEFAULT_FPS = 30.0

# 已知 pangu 引擎脚本 guid
PANGU_SCRIPTS = {
    "43f3bb7d12b804831b796f70b04ca723": "MeshPartSettings",
}

# 图片/贴图后缀
TEX_SUFFIX = {".png", ".jpg", ".jpeg", ".tga", ".psd", ".exr", ".tif", ".tiff", ".bmp"}

# ─── 小工具 ──────────────────────────────────────────────────────
VEC3_RE = re.compile(r"\{x:\s*([-0-9.eE]+),\s*y:\s*([-0-9.eE]+),\s*z:\s*([-0-9.eE]+)")
GUID_RE = re.compile(r"guid:\s*([a-f0-9]{32})")
DOC_HEADER_RE = re.compile(r"^---\s+!u!(\d+)\s+&(-?\d+)")


def parse_vec3(line: str) -> tuple[float, float, float] | None:
    m = VEC3_RE.search(line)
    if not m:
        return None
    try:
        return (float(m.group(1)), float(m.group(2)), float(m.group(3)))
    except ValueError:
        return None


def fmt(x: float) -> str:
    if abs(x) < 1e-5:
        return "0"
    if abs(x - round(x)) < 1e-4:
        return str(int(round(x)))
    return f"{x:.2f}".rstrip("0").rstrip(".") or "0"


def fmt_vec(v: tuple[float, float, float] | None) -> str:
    if v is None:
        return "-"
    return f"[{fmt(v[0])}, {fmt(v[1])}, {fmt(v[2])}]"


def split_docs(text: str):
    """按 `--- !u!<cls> &<fid>` 切成文档段。返回 [(cls, fid, body_lines)]."""
    docs = []
    cur_cls: str | None = None
    cur_fid: str | None = None
    cur: list[str] = []
    for line in text.splitlines():
        m = DOC_HEADER_RE.match(line)
        if m:
            if cur_cls is not None:
                docs.append((cur_cls, cur_fid, cur))
            cur_cls, cur_fid = m.group(1), m.group(2)
            cur = []
        else:
            if cur_cls is not None:
                cur.append(line)
    if cur_cls is not None:
        docs.append((cur_cls, cur_fid, cur))
    return docs


# Unity class IDs
CLS_GAMEOBJECT = "1"
CLS_TRANSFORM = "4"
CLS_MESHRENDERER = "23"
CLS_MESHFILTER = "33"
CLS_SKINNED_MESH_RENDERER = "137"
CLS_BOX_COLLIDER = "65"
CLS_SPHERE_COLLIDER = "135"
CLS_CAPSULE_COLLIDER = "136"
CLS_MESH_COLLIDER = "64"
CLS_ANIMATOR = "95"
CLS_PARTICLE_SYSTEM = "198"
CLS_LIGHT = "108"
CLS_AUDIO_SOURCE = "82"
CLS_MONO_BEHAVIOUR = "114"
CLS_PREFAB_INSTANCE = "1001"
CLS_ANIMATOR_STATE = "1102"


# ─── Prefab 解析 ──────────────────────────────────────────────
@dataclass
class Collider:
    kind: str
    size: tuple[float, float, float] | None = None
    center: tuple[float, float, float] | None = None
    radius: float | None = None
    height: float | None = None
    is_trigger: bool = False


@dataclass
class PrefabMeta:
    path: Path
    root_name: str = ""
    root_scale: tuple[float, float, float] | None = None
    child_gameobject_count: int = 0
    mesh_renderer_count: int = 0
    skinned_renderer_count: int = 0
    particle_count: int = 0
    light_count: int = 0
    audio_count: int = 0
    has_animator: bool = False
    animator_controller_guid: str | None = None
    colliders: list[Collider] = field(default_factory=list)
    mono_script_guids: list[str] = field(default_factory=list)
    prefab_instance_count: int = 0
    # 新增：资源追溯
    mesh_guids: set[str] = field(default_factory=set)
    material_guids: set[str] = field(default_factory=set)


def parse_prefab(path: Path) -> PrefabMeta:
    meta = PrefabMeta(path=path)
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return meta

    docs = split_docs(text)

    # Transform → GameObject 映射，找 root
    transforms: dict[str, dict] = {}
    gameobjects: dict[str, str] = {}
    for cls, fid, body in docs:
        if cls == CLS_TRANSFORM:
            entry = {"father": None, "gameobject": None, "scale": None}
            for ln in body:
                s = ln.strip()
                if s.startswith("m_Father:"):
                    gm = re.search(r"fileID:\s*(-?\d+)", ln)
                    if gm:
                        entry["father"] = gm.group(1)
                elif s.startswith("m_GameObject:"):
                    gm = re.search(r"fileID:\s*(-?\d+)", ln)
                    if gm:
                        entry["gameobject"] = gm.group(1)
                elif s.startswith("m_LocalScale:"):
                    entry["scale"] = parse_vec3(ln)
            transforms[fid] = entry
        elif cls == CLS_GAMEOBJECT:
            name = ""
            for ln in body:
                s = ln.strip()
                if s.startswith("m_Name:"):
                    name = s.split(":", 1)[1].strip()
                    break
            gameobjects[fid] = name

    root_tf_fid: str | None = None
    for fid, t in transforms.items():
        if t["father"] == "0":
            root_tf_fid = fid
            break
    if root_tf_fid:
        tf = transforms[root_tf_fid]
        meta.root_scale = tf["scale"]
        if tf["gameobject"] and tf["gameobject"] in gameobjects:
            meta.root_name = gameobjects[tf["gameobject"]]

    meta.child_gameobject_count = max(0, len(gameobjects) - 1)

    for cls, fid, body in docs:
        if cls == CLS_MESHRENDERER:
            meta.mesh_renderer_count += 1
            # 抓 m_Materials
            in_mats = False
            for ln in body:
                s = ln.strip()
                if s.startswith("m_Materials:"):
                    in_mats = True
                    continue
                if in_mats:
                    if s.startswith("-") and "guid:" in ln:
                        gm = GUID_RE.search(ln)
                        if gm:
                            meta.material_guids.add(gm.group(1))
                    elif s.startswith("m_") and not s.startswith("m_Materials"):
                        in_mats = False
        elif cls == CLS_MESHFILTER:
            for ln in body:
                s = ln.strip()
                if s.startswith("m_Mesh:"):
                    gm = GUID_RE.search(ln)
                    if gm:
                        meta.mesh_guids.add(gm.group(1))
                    break
        elif cls == CLS_SKINNED_MESH_RENDERER:
            meta.skinned_renderer_count += 1
            in_mats = False
            for ln in body:
                s = ln.strip()
                if s.startswith("m_Materials:"):
                    in_mats = True
                    continue
                if in_mats:
                    if s.startswith("-") and "guid:" in ln:
                        gm = GUID_RE.search(ln)
                        if gm:
                            meta.material_guids.add(gm.group(1))
                    elif s.startswith("m_") and not s.startswith("m_Materials"):
                        in_mats = False
                if s.startswith("m_Mesh:"):
                    gm = GUID_RE.search(ln)
                    if gm:
                        meta.mesh_guids.add(gm.group(1))
        elif cls == CLS_PARTICLE_SYSTEM:
            meta.particle_count += 1
        elif cls == CLS_LIGHT:
            meta.light_count += 1
        elif cls == CLS_AUDIO_SOURCE:
            meta.audio_count += 1
        elif cls == CLS_PREFAB_INSTANCE:
            meta.prefab_instance_count += 1
        elif cls == CLS_ANIMATOR:
            meta.has_animator = True
            for ln in body:
                s = ln.strip()
                if s.startswith("m_Controller:"):
                    gm = GUID_RE.search(ln)
                    if gm:
                        meta.animator_controller_guid = gm.group(1)
                    break
        elif cls == CLS_MONO_BEHAVIOUR:
            for ln in body:
                s = ln.strip()
                if s.startswith("m_Script:"):
                    gm = GUID_RE.search(ln)
                    if gm:
                        meta.mono_script_guids.append(gm.group(1))
                    break
        elif cls == CLS_BOX_COLLIDER:
            col = Collider(kind="Box")
            for ln in body:
                s = ln.strip()
                if s.startswith("m_IsTrigger:"):
                    col.is_trigger = s.endswith("1")
                elif s.startswith("m_Size:"):
                    col.size = parse_vec3(ln)
                elif s.startswith("m_Center:"):
                    col.center = parse_vec3(ln)
            meta.colliders.append(col)
        elif cls == CLS_SPHERE_COLLIDER:
            col = Collider(kind="Sphere")
            for ln in body:
                s = ln.strip()
                if s.startswith("m_IsTrigger:"):
                    col.is_trigger = s.endswith("1")
                elif s.startswith("m_Radius:"):
                    try:
                        col.radius = float(s.split(":", 1)[1].strip())
                    except ValueError:
                        pass
                elif s.startswith("m_Center:"):
                    col.center = parse_vec3(ln)
            meta.colliders.append(col)
        elif cls == CLS_CAPSULE_COLLIDER:
            col = Collider(kind="Capsule")
            for ln in body:
                s = ln.strip()
                if s.startswith("m_IsTrigger:"):
                    col.is_trigger = s.endswith("1")
                elif s.startswith("m_Radius:"):
                    try:
                        col.radius = float(s.split(":", 1)[1].strip())
                    except ValueError:
                        pass
                elif s.startswith("m_Height:"):
                    try:
                        col.height = float(s.split(":", 1)[1].strip())
                    except ValueError:
                        pass
                elif s.startswith("m_Center:"):
                    col.center = parse_vec3(ln)
            meta.colliders.append(col)
        elif cls == CLS_MESH_COLLIDER:
            col = Collider(kind="Mesh")
            for ln in body:
                s = ln.strip()
                if s.startswith("m_IsTrigger:"):
                    col.is_trigger = s.endswith("1")
            meta.colliders.append(col)

    return meta


# ─── 反向索引（guid → 源文件 / clip 元数据）────────────────────
@dataclass
class FbxClipInfo:
    name: str
    take_name: str = ""
    first_frame: float = 0.0
    last_frame: float = 0.0
    loop_time: bool = False   # loopTime: 1/0（是否循环播放）
    loop: bool = False        # loop: 1/0（Additional "Loop Pose" flag）
    cycle_offset: float = 0.0

    @property
    def duration(self) -> float:
        if self.last_frame > self.first_frame:
            return (self.last_frame - self.first_frame) / DEFAULT_FPS
        return 0.0


@dataclass
class FbxMeta:
    guid: str
    path: Path
    clips: list[FbxClipInfo] = field(default_factory=list)


def parse_fbx_meta(path: Path) -> FbxMeta | None:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    gm = GUID_RE.search(text)
    if not gm:
        return None
    fbx_path = path.with_suffix("")  # .fbx.meta → .fbx
    fm = FbxMeta(guid=gm.group(1), path=fbx_path)

    # 定位 clipAnimations: 段，逐条解析
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip() == "clipAnimations:" or lines[i].rstrip().endswith("clipAnimations:"):
            # 下面若干以 "- serializedVersion" 开头的条目
            j = i + 1
            while j < len(lines):
                ln = lines[j]
                s = ln.strip()
                if s.startswith("- serializedVersion"):
                    clip = FbxClipInfo(name="")
                    j += 1
                    # 该 clip 的字段行都以至少 6 个空格缩进（比 "    - " 深 2 空格）
                    while j < len(lines):
                        kl = lines[j]
                        ks = kl.strip()
                        # 下一个 clip 或退出 clipAnimations 段
                        if ks.startswith("- serializedVersion"):
                            break
                        if not kl.startswith("      "):
                            break
                        if ks.startswith("name:"):
                            clip.name = ks.split(":", 1)[1].strip()
                        elif ks.startswith("takeName:"):
                            clip.take_name = ks.split(":", 1)[1].strip()
                        elif ks.startswith("firstFrame:"):
                            try:
                                clip.first_frame = float(ks.split(":", 1)[1].strip())
                            except ValueError:
                                pass
                        elif ks.startswith("lastFrame:"):
                            try:
                                clip.last_frame = float(ks.split(":", 1)[1].strip())
                            except ValueError:
                                pass
                        elif ks.startswith("loopTime:"):
                            clip.loop_time = ks.endswith("1")
                        elif ks == "loop: 1" or ks == "loop: 0":
                            clip.loop = ks.endswith("1")
                        elif ks.startswith("cycleOffset:"):
                            try:
                                clip.cycle_offset = float(ks.split(":", 1)[1].strip())
                            except ValueError:
                                pass
                        j += 1
                    if clip.name:
                        fm.clips.append(clip)
                elif s.startswith("- ") or s == "" or (ln.startswith("    ") and not ln.startswith("      ")):
                    # 下一级字段开始（如 `isReadable:`）→ 退出
                    break
                else:
                    j += 1
            break
        i += 1

    return fm


def build_fbx_index() -> dict[str, FbxMeta]:
    idx: dict[str, FbxMeta] = {}
    for p in MEISHU_ROOT.rglob("*.fbx.meta"):
        fm = parse_fbx_meta(p)
        if fm:
            idx[fm.guid] = fm
    # 补一下 .FBX.meta（大写）
    return idx


def build_controller_index() -> dict[str, Path]:
    idx: dict[str, Path] = {}
    for p in MODEL_DIR.rglob("*.controller.meta"):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        gm = GUID_RE.search(txt)
        if gm:
            ctrl = p.with_suffix("")
            if ctrl.exists():
                idx[gm.group(1)] = ctrl
    return idx


def build_meta_guid_index(root: Path, suffixes: set[str]) -> dict[str, Path]:
    """扫 <root> 下 *.<ext>.meta，返回 guid → 源文件路径。"""
    idx: dict[str, Path] = {}
    for meta_path in root.rglob("*.meta"):
        src = meta_path.with_suffix("")
        if src.suffix.lower() not in suffixes:
            continue
        if not src.exists():
            continue
        try:
            txt = meta_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        gm = GUID_RE.search(txt)
        if gm:
            idx[gm.group(1)] = src
    return idx


# ─── Controller 解析：state → (name, motion_guid) ────────────
ANIMATOR_STATE_NAME_RE = re.compile(r"^\s*m_Name:\s*(.+)$")


@dataclass
class ControllerState:
    name: str
    motion_guid: str = ""


def parse_controller_states(path: Path) -> list[ControllerState]:
    out: list[ControllerState] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return out
    # 同时抓 m_Motion 的 guid
    for cls, fid, body in split_docs(text):
        if cls != CLS_ANIMATOR_STATE:
            continue
        state = ControllerState(name="")
        for ln in body:
            s = ln.strip()
            if s.startswith("m_Name:") and not state.name:
                state.name = s.split(":", 1)[1].strip()
        # m_Motion 可能跨多行
        in_motion = False
        motion_text = ""
        for ln in body:
            if ln.strip().startswith("m_Motion:"):
                in_motion = True
                motion_text = ln
                continue
            if in_motion:
                if ln.startswith("    ") or ln.startswith("   -"):
                    motion_text += " " + ln.strip()
                else:
                    break
        gm = GUID_RE.search(motion_text)
        if gm:
            state.motion_guid = gm.group(1)
        if state.name:
            out.append(state)
    return out


# ─── Material 解析：.mat → 贴图 guid 列表 ─────────────────────
MAT_PROP_NAMES = ("_MainTex", "_BaseMap", "_BaseColorMap", "_AlbedoMap")


def parse_material_textures(mat_path: Path) -> list[str]:
    """从 .mat 里抽主贴图 guid（优先 _MainTex，其次 _BaseMap 等）。"""
    try:
        text = mat_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    lines = text.splitlines()
    found: list[tuple[str, str]] = []  # (prop_name, guid)
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        for prop in MAT_PROP_NAMES:
            if s.startswith(f"- {prop}:") or s == f"{prop}:":
                # 下一行是 m_Texture: {fileID: .., guid: .., ..}
                if i + 1 < len(lines):
                    nxt = lines[i + 1]
                    if "m_Texture:" in nxt and "guid:" in nxt:
                        gm = GUID_RE.search(nxt)
                        if gm:
                            found.append((prop, gm.group(1)))
                break
        i += 1
    # 去重，保留优先顺序
    seen = set()
    out = []
    for _, g in found:
        if g and g not in seen:
            seen.add(g)
            out.append(g)
    return out


# ─── asset_catalog 解析 ────────────────────────────────────────
def load_catalog_objects() -> list[dict]:
    text = CATALOG.read_text(encoding="utf-8")
    out: list[dict] = []
    in_sec = False
    col_idx: dict[str, int] = {}
    header_found = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_sec = line.strip() == "## 物件 (MeshPart)"
            header_found = False
            col_idx = {}
            continue
        if not in_sec or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not header_found:
            if "AssetId" in cells:
                col_idx = {c: i for i, c in enumerate(cells)}
                header_found = True
            continue
        if cells[0].startswith("-"):
            continue
        aid = cells[col_idx["AssetId"]]
        if not aid.isdigit():
            continue
        out.append({
            "aid": aid,
            "name": cells[col_idx.get("名称", 1)] if "名称" in col_idx else "",
            "prefab": cells[col_idx.get("prefab文件", 2)] if "prefab文件" in col_idx else "",
            "course": cells[col_idx.get("课程分类", 3)] if "课程分类" in col_idx else "",
            "known_anims": cells[col_idx.get("已知动画", 4)] if "已知动画" in col_idx else "",
            "scale_hint": cells[col_idx.get("常用Scale", 5)] if "常用Scale" in col_idx else "",
        })
    return out


def find_prefab(prefab_name: str, roots: list[Path]) -> Path | None:
    if not prefab_name:
        return None
    for root in roots:
        p = root / prefab_name
        if p.exists():
            return p
    for root in roots:
        hits = list(root.rglob(prefab_name))
        if hits:
            return hits[0]
    return None


# ─── 格式化输出 ───────────────────────────────────────────────
def describe_collider(c: Collider) -> str:
    parts = [c.kind]
    if c.kind == "Box" and c.size:
        parts.append(fmt_vec(c.size))
    elif c.kind == "Sphere" and c.radius is not None:
        parts.append(f"r={fmt(c.radius)}")
    elif c.kind == "Capsule":
        seg = []
        if c.radius is not None:
            seg.append(f"r={fmt(c.radius)}")
        if c.height is not None:
            seg.append(f"h={fmt(c.height)}")
        if seg:
            parts.append(",".join(seg))
    if c.is_trigger:
        parts.append("Trigger")
    return " ".join(parts)


def describe_pivot(c: Collider) -> str:
    if not c.center or not c.size:
        if c.center:
            return fmt_vec(c.center)
        return "-"
    cy = c.center[1]
    sy = c.size[1]
    if sy < 1e-5:
        return fmt_vec(c.center)
    ratio = cy / sy
    if abs(ratio - 0.5) < 0.15:
        tag = "轴心在底部"
    elif abs(ratio) < 0.15:
        tag = "轴心居中"
    elif ratio > 0.7:
        tag = "轴心偏下"
    else:
        tag = "轴心偏移"
    return f"{fmt_vec(c.center)} ({tag})"


def render_capabilities(m: PrefabMeta) -> str:
    caps = []
    if m.skinned_renderer_count > 0:
        caps.append(f"蒙皮×{m.skinned_renderer_count}")
    if m.mesh_renderer_count > 0:
        caps.append(f"静态×{m.mesh_renderer_count}")
    if m.particle_count > 0:
        caps.append(f"粒子×{m.particle_count}")
    if m.light_count > 0:
        caps.append(f"光源×{m.light_count}")
    if m.audio_count > 0:
        caps.append(f"音源×{m.audio_count}")
    return " / ".join(caps) if caps else "-"


def render_scripts(m: PrefabMeta) -> str:
    tags = []
    for g in m.mono_script_guids:
        if g in PANGU_SCRIPTS:
            tags.append(PANGU_SCRIPTS[g])
    if not tags and m.mono_script_guids:
        tags.append(f"其它脚本×{len(m.mono_script_guids)}")
    return " / ".join(tags) if tags else "-"


def render_clip_entry(state_name: str, clip: FbxClipInfo | None) -> str:
    if clip is None or clip.duration <= 0:
        return state_name
    tag = f"{clip.duration:.2f}s,{'循环' if clip.loop_time else '一次'}"
    return f"{state_name}({tag})"


# ─── main ─────────────────────────────────────────────────────
def main():
    if not SPRITE3D_DIR.exists():
        raise SystemExit(f"美术目录不存在: {SPRITE3D_DIR}")

    print(">> 扫 asset_catalog 物件表 ...")
    objs = load_catalog_objects()
    print(f"   物件行数: {len(objs)}")

    print(">> 建 FBX (guid→path+clipAnimations) 索引 ...")
    fbx_idx = build_fbx_index()
    clip_rich = sum(1 for fm in fbx_idx.values() if fm.clips)
    print(f"   FBX 数: {len(fbx_idx)}（有 clip 元数据: {clip_rich}）")

    print(">> 建 controller 索引 ...")
    ctrl_idx = build_controller_index()
    print(f"   .controller 数: {len(ctrl_idx)}")

    print(">> 建 material / texture 索引 ...")
    mat_idx = build_meta_guid_index(MEISHU_ROOT, {".mat"})
    tex_idx = build_meta_guid_index(MEISHU_ROOT, TEX_SUFFIX)
    print(f"   .mat: {len(mat_idx)} / texture: {len(tex_idx)}")

    print(">> 解析物件 prefab ...")
    rows = []
    not_found = 0
    prefab_roots = [SPRITE3D_DIR, CHARACTER_DIR, MEISHU_ROOT / "ide"]

    for obj in objs:
        row = dict(obj)
        row["meta"] = None
        row["clip_entries"] = []      # [(state_name, FbxClipInfo|None, motion_fbx_path|None)]
        row["mesh_fbx_paths"] = []    # [Path]
        row["mat_paths"] = []         # [Path]
        row["tex_paths"] = []         # [Path] (unique)
        pfab = find_prefab(obj["prefab"], prefab_roots) if obj["prefab"] else None
        if not pfab:
            not_found += 1
            rows.append(row)
            continue
        try:
            meta = parse_prefab(pfab)
        except Exception as e:
            print(f"   解析失败 {pfab.name}: {e}")
            rows.append(row)
            continue
        row["meta"] = meta

        # Mesh → FBX
        for g in meta.mesh_guids:
            if g in fbx_idx:
                p = fbx_idx[g].path
                if p not in row["mesh_fbx_paths"]:
                    row["mesh_fbx_paths"].append(p)

        # Material → .mat 路径 → 贴图
        seen_tex = set()
        for g in meta.material_guids:
            if g in mat_idx:
                mat_path = mat_idx[g]
                if mat_path not in row["mat_paths"]:
                    row["mat_paths"].append(mat_path)
                for tg in parse_material_textures(mat_path):
                    if tg in tex_idx and tg not in seen_tex:
                        seen_tex.add(tg)
                        row["tex_paths"].append(tex_idx[tg])

        # Controller → clip 列表（带 loop/duration）
        if meta.animator_controller_guid and meta.animator_controller_guid in ctrl_idx:
            states = parse_controller_states(ctrl_idx[meta.animator_controller_guid])
            for st in states:
                motion_fbx: Path | None = None
                clip_info: FbxClipInfo | None = None
                if st.motion_guid in fbx_idx:
                    fm = fbx_idx[st.motion_guid]
                    motion_fbx = fm.path
                    # 只认 clip.name 精确匹配 state.name 的（避免 fallback 到同 FBX 其它 clip 的参数）
                    for c in fm.clips:
                        if c.name == st.name and c.last_frame > c.first_frame:
                            clip_info = c
                            break
                row["clip_entries"].append((st.name, clip_info, motion_fbx))

        rows.append(row)

    matched = sum(1 for r in rows if r["meta"] is not None)
    clip_resolved = sum(sum(1 for _, c, _ in r["clip_entries"] if c) for r in rows)
    clip_total = sum(len(r["clip_entries"]) for r in rows)
    mat_any = sum(1 for r in rows if r["mat_paths"])
    tex_any = sum(1 for r in rows if r["tex_paths"])
    print(f"   prefab 命中 {matched} / {len(rows)}（缺 {not_found}）")
    print(f"   clip loop/duration 命中 {clip_resolved} / {clip_total}")
    print(f"   有 material 的物件: {mat_any}, 有 texture 的: {tex_any}")

    # ─── 输出 markdown ───
    lines: list[str] = []
    lines.append("# 物件 Prefab 元数据 (object_prefab_meta)")
    lines.append("")
    lines.append("> 自动由 [scripts/build_object_prefab_meta.py](../../../scripts/build_object_prefab_meta.py) 生成。")
    lines.append("> 数据源：")
    lines.append("> - prefab: `D:/meishu/Assets/BundleResources/ide/sprite3d/*.prefab`")
    lines.append("> - controller: `D:/meishu/Assets/BundleResources/model/**/*.controller`")
    lines.append("> - animation clip: `*.fbx.meta` 里 `clipAnimations` 段（firstFrame/lastFrame/loopTime）")
    lines.append("> - material/texture: `*.mat` → `_MainTex/_BaseMap` guid → 贴图文件")
    lines.append("")
    lines.append("## 命中率")
    lines.append("")
    lines.append(f"- asset_catalog 物件行：**{len(rows)}**")
    lines.append(f"- 在美术目录找到 prefab：**{matched}**（缺 {not_found}）")
    lines.append(f"- AnimatorState 总数 {clip_total}，其中 loop/duration 命中 **{clip_resolved}**（其余 FBX.meta 为 legacy 模式不含 clip 元数据）")
    lines.append(f"- 成功追溯 material 的物件：**{mat_any}** / 成功追溯 texture 的：**{tex_any}**")
    lines.append("")
    lines.append("## 字段说明")
    lines.append("")
    lines.append("- **Collider**：真实物理碰撞体（Box/Sphere/Capsule/Mesh），尺寸来自 prefab 源头，不受 .ws 里 Size/Scale 覆盖。")
    lines.append("  - Box → `m_Size`；Sphere → `r=`；Capsule → `r=/h=`；`Trigger` 代表可穿过")
    lines.append("- **轴心偏移**：")
    lines.append("  - `轴心在底部`：center.y ≈ size.y/2 → 摆放时直接 `Position.y = 地面` 即可")
    lines.append("  - `轴心居中`：center ≈ 0 → 摆地上要抬 size.y/2")
    lines.append("  - 其它 → 需手动核对")
    lines.append("- **渲染/能力**：静态×N / 蒙皮×N / 粒子×N / 光源×N / 音源×N")
    lines.append("- **动画**：`state名(时长s,循环|一次)`；时长按 30fps 推算。缺 loop/duration 的是 FBX.meta 未配置 clipAnimations（legacy 模式）。")
    lines.append("- **默认 Scale**：prefab 根 Transform m_LocalScale（多数 1，个别放大）。")
    lines.append("- **子GO**：prefab 内 GameObject 总数 - 1。")
    lines.append("- **特殊脚本**：pangu 引擎 MonoBehaviour（目前识别 MeshPartSettings）。")
    lines.append("")

    # ─── 主表 ───
    lines.append("## 主表：物件元数据")
    lines.append("")
    lines.append("| AssetId | 名称 | prefab | Collider | 轴心偏移 | 渲染/能力 | Animator clip (时长/循环) | 默认Scale | 子GO | 特殊脚本 |")
    lines.append("|---------|------|--------|----------|----------|-----------|---------------------------|-----------|------|----------|")

    def aid_key(r):
        try:
            return int(r["aid"])
        except Exception:
            return 10**9

    for r in sorted(rows, key=aid_key):
        m: PrefabMeta | None = r["meta"]
        if m is None:
            lines.append(
                f"| {r['aid']} | {r['name']} | {r['prefab'] or '-'} | 未找到prefab | - | - | - | - | - | - |"
            )
            continue

        if m.colliders:
            primary = next((c for c in m.colliders if c.kind != "Mesh"), m.colliders[0])
            col_str = describe_collider(primary)
            pivot_str = describe_pivot(primary)
            if len(m.colliders) > 1:
                col_str += f" (+{len(m.colliders) - 1}个)"
        else:
            col_str = "无"
            pivot_str = "-"

        if r["clip_entries"]:
            clip_str = ", ".join(render_clip_entry(n, c) for n, c, _ in r["clip_entries"])
        elif m.has_animator:
            clip_str = "(有Animator无控制器)"
        else:
            clip_str = "-"
        scale_str = fmt_vec(m.root_scale) if m.root_scale else "-"
        cap_str = render_capabilities(m)
        script_str = render_scripts(m)
        safe_clip = clip_str.replace("|", "/")
        lines.append(
            f"| {r['aid']} | {r['name']} | {r['prefab']} | {col_str} | {pivot_str} | "
            f"{cap_str} | {safe_clip} | {scale_str} | {m.child_gameobject_count} | {script_str} |"
        )

    # ─── 资源追溯表 ───
    lines.append("")
    lines.append("## 资源追溯：物件 → Mesh / Material / Texture")
    lines.append("")
    lines.append("> `源FBX` 是 MeshFilter / SkinnedMeshRenderer 引用的几何体文件；`材质` 是 prefab 引用的 .mat 数；`贴图` 是逐个 .mat 追到的主贴图文件名（去重）。")
    lines.append("")
    lines.append("| AssetId | 名称 | 源FBX (相对 meishu) | 材质数 | 贴图 |")
    lines.append("|---------|------|---------------------|--------|------|")
    for r in sorted(rows, key=aid_key):
        m: PrefabMeta | None = r["meta"]
        if m is None:
            continue
        mesh_rel = [str(p.relative_to(MEISHU_ROOT)).replace("\\", "/") for p in r["mesh_fbx_paths"]]
        tex_names = [p.name for p in r["tex_paths"]]
        if not mesh_rel and not tex_names:
            continue
        mesh_cell = "<br>".join(mesh_rel) if mesh_rel else "-"
        tex_cell = ", ".join(tex_names) if tex_names else "-"
        lines.append(
            f"| {r['aid']} | {r['name']} | {mesh_cell} | {len(r['mat_paths'])} | {tex_cell} |"
        )

    # ─── 动画详情表 ───
    lines.append("")
    lines.append("## 动画详情：可精确拿到 duration 的 clip")
    lines.append("")
    lines.append("> 只列出 FBX.meta 里有 clipAnimations 配置的动画；duration = (lastFrame - firstFrame) / 30fps。")
    lines.append("")
    lines.append("| AssetId | 物件 | state 名 | 循环 | 时长(s) | Motion FBX |")
    lines.append("|---------|------|---------|------|---------|-----------|")
    for r in sorted(rows, key=aid_key):
        for state_name, clip, motion_fbx in r["clip_entries"]:
            if clip is None or clip.duration <= 0:
                continue
            loop_flag = "循环" if clip.loop_time else "一次"
            dur = f"{clip.duration:.2f}"
            fbx_rel = str(motion_fbx.relative_to(MEISHU_ROOT)).replace("\\", "/") if motion_fbx else "-"
            lines.append(
                f"| {r['aid']} | {r['name']} | {state_name} | {loop_flag} | {dur} | {fbx_rel} |"
            )

    # ─── 分组速查 ───
    lines.append("")
    lines.append("## 速查：按能力分组")
    lines.append("")
    groups: dict[str, list] = defaultdict(list)
    for r in rows:
        m: PrefabMeta | None = r["meta"]
        if m is None:
            continue
        if m.has_animator and r["clip_entries"]:
            groups["能播放动画（Animator + 控制器有效）"].append(r)
        if m.skinned_renderer_count > 0:
            groups["带骨骼/蒙皮（SkinnedMeshRenderer）"].append(r)
        if m.particle_count > 0:
            groups["自带粒子特效"].append(r)
        if m.light_count > 0:
            groups["自带光源"].append(r)
        if m.audio_count > 0:
            groups["自带音源"].append(r)
        if any(c.is_trigger for c in m.colliders):
            groups["可穿过（Trigger）"].append(r)
        if not m.colliders:
            groups["无碰撞体（视觉装饰）"].append(r)

    for gname in ["能播放动画（Animator + 控制器有效）",
                  "带骨骼/蒙皮（SkinnedMeshRenderer）",
                  "自带粒子特效",
                  "自带光源",
                  "自带音源",
                  "可穿过（Trigger）",
                  "无碰撞体（视觉装饰）"]:
        if gname not in groups:
            continue
        lines.append(f"### {gname}（{len(groups[gname])} 个）")
        lines.append("")
        lines.append("| AssetId | 名称 | prefab |")
        lines.append("|---------|------|--------|")
        for r in sorted(groups[gname], key=aid_key):
            lines.append(f"| {r['aid']} | {r['name']} | {r['prefab']} |")
        lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f">> 已写出: {OUT}  ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

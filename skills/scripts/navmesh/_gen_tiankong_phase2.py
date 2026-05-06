# -*- coding: utf-8 -*-
"""Phase 2: 打包，加 export_info.json + icon，输出最终 zip。"""
import io, json, sys, shutil, time, uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import pkg_utils

LEVEL_NAME = "tiankong_quartet"
WORKDIR    = REPO / "output" / "new" / f"_{LEVEL_NAME}_workdir"
OUT_ZIP    = REPO / "output" / "new" / f"{LEVEL_NAME}.zip"

meta = json.loads((WORKDIR / "_phase1_meta.json").read_text(encoding="utf-8"))
ws_path = Path(meta["ws_path"])
ws_name = ws_path.name

def new_uuid4():  return str(uuid.uuid4())
def new_uuid32(): return uuid.uuid4().hex

# icon: 复用已有图片
ICON_SRC = REPO / "output" / "new" / "_xiaohetao_duizhang_workdir" / "2873199d-1e16-4b7f-84d8-509e37482fcf.png"
icon_uuid = new_uuid4()
icon_dest = WORKDIR / f"{icon_uuid}.png"
if ICON_SRC.exists():
    shutil.copy2(ICON_SRC, icon_dest)
else:
    import base64
    TINY_PNG = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8"
        "z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=="
    )
    icon_dest.write_bytes(TINY_PNG)

icon_path = f"pangu3d/universe/develop/612921974867361800/{icon_uuid}.png"

project_uuid = new_uuid4()
solution_uid = new_uuid4()

solution = {
    "init": solution_uid,
    "name": "天空王国四角色",
    "author": "",
    "modified": int(time.time()),
    "version": 1,
    "projects": [{
        "file": f"pangu3d/universe/develop/612921974867361800/{ws_name}",
        "icon": icon_path,
        "name": "Project_0",
        "uuid": project_uuid,
    }],
    "globals": [{
        "refs": [project_uuid],
        "obj": {
            "type": "CameraService",
            "id": new_uuid32(),
            "props": {"Name": "Camera", "EditMode": 0, "Current": "Camera45"},
            "children": [
                {
                    "type": "BlockScript",
                    "id": new_uuid32(),
                    "props": {"Name": "BlockScript", "EditMode": 0},
                    "uiState": {"pos": ["510","848"], "scroll": ["722","746"], "scale": "1"},
                },
                {
                    "type": "BlockScript",
                    "id": new_uuid32(),
                    "props": {"Name": "BlockScript", "EditMode": 0},
                    "uiState": {"pos": ["0","0"], "scroll": ["0","0"], "scale": "1"},
                },
            ],
        },
    }],
}
(WORKDIR / "solution.json").write_text(
    json.dumps(solution, ensure_ascii=False, separators=(",",":")),
    encoding="utf-8",
)

(WORKDIR / "export_info.json").write_text(
    json.dumps({"solutionUid": solution_uid}, ensure_ascii=False, separators=(",",":")),
    encoding="utf-8",
)

meta_f = WORKDIR / "_phase1_meta.json"
if meta_f.exists():
    meta_f.unlink()

if OUT_ZIP.exists():
    OUT_ZIP.unlink()
pkg_utils.pack_zip_clean(str(WORKDIR), str(OUT_ZIP))

size = OUT_ZIP.stat().st_size
print(f"[OK] {OUT_ZIP.name}  ({size:,} bytes)")

import zipfile
with zipfile.ZipFile(OUT_ZIP) as zf:
    for n in zf.namelist():
        print(f"  {n}")

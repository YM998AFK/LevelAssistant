# -*- coding: utf-8 -*-
"""制造两个坏包测试 gate4 是否能拦截。"""
import io, sys, json, zipfile
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "scripts")

MINIMAL_WS = json.dumps({
    "name": "t", "desc": "", "icon": "", "author": "",
    "created": 0, "modified": 0, "type": 3, "version": 3,
    "stageType": 0,
    "scene": {
        "type": "Scene", "id": "x",
        "props": {"AssetId": 1, "Name": "S", "EditMode": 0,
                  "BoundsCenter": ["0","0","0"], "BoundsSize": ["1","1","1"]},
        "children": [],
    },
    "agents": {"type": "Folder", "id": "a", "props": {"Name": "agents"}},
    "assets": {"type": "Folder", "id": "b", "props": {"Name": "assets"}, "children": []},
    "res": [], "showmyblock": True,
    "dialogues": {"DialogueGroups": []},
    "editorScene": {"cameras": []},
    "projectMode": 2,
})

tests = [
    {
        "name": "缺 export_info.json",
        "files": {"x.ws": MINIMAL_WS, "solution.json": '{"init":"aaa","name":"t","projects":[]}'},
    },
    {
        "name": "UUID 不匹配",
        "files": {
            "x.ws": MINIMAL_WS,
            "icon.png": b"\x89PNG",
            "solution.json": '{"init":"aaa","name":"t","projects":[]}',
            "export_info.json": '{"solutionUid":"bbb"}',
        },
    },
    {
        "name": "缺 icon png",
        "files": {
            "x.ws": MINIMAL_WS,
            "solution.json": '{"init":"aaa","name":"t","projects":[]}',
            "export_info.json": '{"solutionUid":"aaa"}',
        },
    },
]

import verify_gates

print("=== gate4 拦截测试 ===")
for tc in tests:
    p = Path(f"output/new/_gate4_test.zip")
    with zipfile.ZipFile(p, "w") as z:
        for fname, content in tc["files"].items():
            if isinstance(content, bytes):
                z.writestr(fname, content)
            else:
                z.writestr(fname, content.encode("utf-8"))
    g4 = verify_gates.run_gate4_zip_completeness(p)
    status = "FAIL ✅(正确拦截)" if not g4["pass"] else "PASS ❌(漏检!)"
    print(f"  [{tc['name']}] => {status}")
    for e in g4["errors"]:
        print(f"    error: {e}")
    p.unlink()
print()
print("gate4 实装到 verify_gates.py 完成")

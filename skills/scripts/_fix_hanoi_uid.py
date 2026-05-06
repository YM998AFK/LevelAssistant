"""
修复汉诺塔挑战包：
1. 扫描 ws 中所有 block params 找缺 "value" 的条目（诊断）
2. 修复 export_info.solutionUid 为数字微秒时间戳
3. 三值对齐：export_info.solutionUid / solution.init / solution.modified / projects[*].file path
4. 重新打包
"""
import sys, json, time, pathlib, zipfile
sys.stdout.reconfigure(encoding='utf-8')

# 路径
WORKDIR = pathlib.Path('output/new/汉诺塔挑战_workdir')
WS_PATH = WORKDIR / 'b8212e928dc647cfb659bc74e0cff402.ws'
EI_PATH = WORKDIR / 'export_info.json'
SOL_PATH = WORKDIR / 'solution.json'
OUT_ZIP = pathlib.Path('output/new/汉诺塔挑战.zip')

sys.path.insert(0, 'scripts')
from pkg_utils import clean_backups, pack_zip_clean

# ── 加载 ws ──
ws = json.loads(WS_PATH.read_bytes().decode('utf-8'))

# ── 诊断：找所有含 "type" 但缺 "value"/"val" 的 block param dict ──
issues = []

def scan(obj, path=''):
    if isinstance(obj, dict):
        if 'type' in obj:
            t = obj.get('type')
            # 正常 param: 字符串/数字/bool 类型必须有 "value"
            if t in ('string', 'number', 'bool', 'color') and 'value' not in obj:
                issues.append((path, obj))
            # block operator 必须有 "val"
            if t == 'block' and 'val' not in obj:
                issues.append((path, obj))
        for k, v in obj.items():
            scan(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            scan(v, f'{path}[{i}]')

scan(ws)

print(f"=== 结构诊断：找到 {len(issues)} 个疑似缺字段条目 ===")
for path, obj in issues[:20]:
    print(f"  {path}: {obj}")

# ── 修复 solutionUid ──
ei = json.loads(EI_PATH.read_bytes().decode('utf-8'))
sol = json.loads(SOL_PATH.read_bytes().decode('utf-8'))

old_uid = ei.get('solutionUid', '')
print(f"\n当前 export_info.solutionUid: {old_uid!r}")

# 生成新数字微秒时间戳 solutionUid
new_uid = str(int(time.time() * 1_000_000))
print(f"新 solutionUid (数字微秒): {new_uid!r}")

# 取 ws 文件名中的 uuid（ws 路径 = pangu3d/universe/develop/{old_numeric_uid}/xxx.ws）
# 从 solution.json 的 projects[0].file 拿到旧路径
old_file_path = sol['projects'][0]['file']
old_icon_path = sol['projects'][0]['icon']
ws_filename = old_file_path.split('/')[-1]
icon_filename = old_icon_path.split('/')[-1]

new_file_path = f"pangu3d/universe/develop/{new_uid}/{ws_filename}"
new_icon_path = f"pangu3d/universe/develop/{new_uid}/{icon_filename}"

print(f"旧 file path: {old_file_path}")
print(f"新 file path: {new_file_path}")

# 更新 export_info.json
ei['solutionUid'] = new_uid
EI_PATH.write_bytes(json.dumps(ei, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
print(f"[fix] export_info.solutionUid -> {new_uid}")

# 更新 solution.json
sol['init'] = new_uid
sol['modified'] = int(new_uid) // 1_000_000
sol['projects'][0]['file'] = new_file_path
sol['projects'][0]['icon'] = new_icon_path
SOL_PATH.write_bytes(json.dumps(sol, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
print(f"[fix] solution.init -> {new_uid}")
print(f"[fix] solution.modified -> {int(new_uid) // 1_000_000}")
print(f"[fix] projects[0].file -> {new_file_path}")
print(f"[fix] projects[0].icon -> {new_icon_path}")

# ── 重新打包 ──
clean_backups(WORKDIR)
pack_zip_clean(WORKDIR, OUT_ZIP)
print(f"\n[done] 已重新打包 -> {OUT_ZIP}")
print(f"  大小: {OUT_ZIP.stat().st_size // 1024} KB")

# -*- coding: utf-8 -*-
"""Apply v6 corrections: proper interior square with wall clearance."""
import sys, io, json, math, shutil
sys.path.insert(0, 'scripts')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pkg_utils

# 从 v4 重新提取（干净基线）
SRC = 'output/modify/抗寒跑操-小核桃队长展喵-v4.zip'
WORKDIR = 'output/modify/kanghan_v6_workdir'

if __import__('pathlib').Path(WORKDIR).exists():
    shutil.rmtree(WORKDIR)
pkg_utils.extract_zip_into(SRC, WORKDIR, force=True)

import os
WS = [f for f in os.listdir(WORKDIR) if f.endswith('.ws')][0]
WS_PATH = f'{WORKDIR}/{WS}'

data = json.loads(open(WS_PATH, encoding='utf-8').read())
scene = data['scene']

Y = '0.853'
NEW_POS = {
    # 正方形角点：边长7.98，中心(6.0,-1.5)，4角距墙均>=1单位
    'P1': ['2.01',  Y, '-5.49'],
    'P2': ['9.99',  Y, '-5.49'],
    'P3': ['9.99',  Y,  '2.49'],
    'P4': ['2.01',  Y,  '2.49'],
    # L1-L3：角色起跑原位（跑完回这里表演）
    'L1': ['4.0',   Y, '-4.49'],
    'L2': ['6.0',   Y, '-4.49'],
    'L3': ['8.0',   Y, '-4.49'],
    # 角色初始站位 = L1/L2/L3
    '小核桃': ['4.0',  Y, '-4.49'],
    '队长':   ['6.0',  Y, '-4.49'],
    '展喵':   ['8.0',  Y, '-4.49'],
    # control 放在正方形中心
    'control': ['6.0', Y, '-1.5'],
}

changed = []
for ch in scene['children']:
    nm = ch['props'].get('Name')
    if nm in NEW_POS:
        old = ch['props'].get('Position')
        ch['props']['Position'] = NEW_POS[nm]
        changed.append((nm, old, NEW_POS[nm]))

print('=== Position 更新 ===')
for nm, old, new in changed:
    print(f'  {nm}: {old} -> {new}')

# WaitSeconds 12 -> 20 (边长缩小，2圈时间也缩短)
def patch_wait(blocks, from_val, to_val):
    for b in blocks:
        if b.get('define') == 'WaitSeconds':
            params = b.get('sections', [{}])[0].get('params', [])
            if params and params[0].get('val') == from_val:
                params[0] = {'type': 'var', 'val': to_val}
                return True
        for sec in b.get('sections', []):
            if patch_wait(sec.get('children', []), from_val, to_val): return True
    return False

wait_patched = False
for ch in scene['children']:
    if ch['props'].get('Name') == 'control':
        for sub in ch.get('children', []):
            if sub['type'] == 'BlockScript':
                for frag in sub.get('fragments', []):
                    # v4 原值是12，v5 已改成32，这里用一个函数尝试两个值
                    if patch_wait([frag['head']], '32', '20') or \
                       patch_wait([frag['head']], '12', '20'):
                        wait_patched = True

print()
if wait_patched:
    print('WaitSeconds -> 20s OK')
else:
    print('WaitSeconds NOT FOUND - check manually')

# N6 验证
chars = [('小核桃', 4.0, -4.49), ('队长', 6.0, -4.49), ('展喵', 8.0, -4.49)]
ctrl = (6.0, -1.5)
print()
print('=== N6 间距验证 ===')
ok = True
for i in range(len(chars)):
    for j in range(i+1, len(chars)):
        d = math.sqrt((chars[i][1]-chars[j][1])**2+(chars[i][2]-chars[j][2])**2)
        flag = 'OK' if d >= 1.0 else 'FAIL'
        if d < 1.0: ok = False
        print(f'  {chars[i][0]}-{chars[j][0]}: {d:.2f}m {flag}')
for nm, x, z in chars:
    d = math.sqrt((x-ctrl[0])**2+(z-ctrl[1])**2)
    flag = 'OK' if d >= 0.5 else 'FAIL'
    if d < 0.5: ok = False
    print(f'  {nm}-control: {d:.2f}m {flag}')
print(f'N6 总体: {"PASS" if ok else "FAIL"}')

open(WS_PATH, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
print()
print('ws 已保存')

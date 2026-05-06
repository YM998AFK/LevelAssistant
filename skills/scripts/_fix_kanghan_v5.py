# -*- coding: utf-8 -*-
"""Fix kanghan v5: update P1-P4 (navmesh square), L1-L3, char positions, WaitSeconds."""
import sys, io, json, math
sys.path.insert(0, 'scripts')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WS = 'output/modify/kanghan_v5_workdir/b0f15ca2-193c-4512-a4f7-31e03114caaf.ws'
data = json.loads(open(WS, encoding='utf-8').read())
scene = data['scene']

Y = '0.853'
NEW_POS = {
    'P1': ['-0.043', Y, '-6.543'],
    'P2': ['13.043', Y, '-6.543'],
    'P3': ['13.043', Y,  '6.543'],
    'P4': ['-0.043', Y,  '6.543'],
    'L1': ['5.0',  Y, '-6.043'],
    'L2': ['6.5',  Y, '-6.043'],
    'L3': ['8.0',  Y, '-6.043'],
    '小核桃': ['5.0',  Y, '-6.043'],
    '队长':   ['6.5',  Y, '-6.043'],
    '展喵':   ['8.0',  Y, '-6.043'],
    'control': ['6.5', Y, '0.0'],
}

# 1. 更新 Position
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

# 2. 更新 control WaitSeconds 12 -> 32
def patch_wait12(blocks):
    for b in blocks:
        if b.get('define') == 'WaitSeconds':
            params = b.get('sections', [{}])[0].get('params', [])
            if params and params[0].get('val') == '12':
                params[0] = {'type': 'var', 'val': '32'}
                return True
        for sec in b.get('sections', []):
            if patch_wait12(sec.get('children', [])):
                return True
    return False

wait_patched = False
for ch in scene['children']:
    if ch['props'].get('Name') == 'control':
        for sub in ch.get('children', []):
            if sub['type'] == 'BlockScript':
                for frag in sub.get('fragments', []):
                    if patch_wait12([frag['head']]):
                        wait_patched = True

print()
if wait_patched:
    print('=== WaitSeconds 12 -> 32 OK ===')
else:
    print('=== WaitSeconds(12) NOT FOUND - check manually ===')

# 3. N6 验证
chars = [('小核桃', 5.0, -6.043), ('队长', 6.5, -6.043), ('展喵', 8.0, -6.043)]
ctrl = (6.5, 0.0)
print()
print('=== N6 间距验证 ===')
all_ok = True
for i in range(len(chars)):
    for j in range(i+1, len(chars)):
        d = math.sqrt((chars[i][1]-chars[j][1])**2+(chars[i][2]-chars[j][2])**2)
        ok = d >= 1.0
        if not ok:
            all_ok = False
        print(f'  {chars[i][0]}-{chars[j][0]}: {d:.2f}m  {"OK" if ok else "FAIL"}')
for nm, x, z in chars:
    d = math.sqrt((x-ctrl[0])**2+(z-ctrl[1])**2)
    ok = d >= 0.5
    if not ok:
        all_ok = False
    print(f'  {nm}-control: {d:.2f}m  {"OK" if ok else "FAIL"}')
print(f'  N6 总体: {"PASS" if all_ok else "FAIL"}')

# 4. 保存
open(WS, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
print()
print('ws 已保存:', WS)

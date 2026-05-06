import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

MEISHU = Path(r'D:\meishu\Assets\BundleResources')

# 验证已知贴图路径
test_cases = [
    'model/player/baoxiang/zhuo_D(2).tga',
    'model/player/baoxiang/shadows.png',
    'model/sprite3d/sm_l6_baoxiang.FBX',
    'model/sprite3d/t_l6_baoxiang.png',
    'model/sprite3d/t_l7_mofabaoxiang.png',
    'model/sprite3d/t_kejianbuji_xiaowujian.png',
    'model/sprite3d/t_l1_jyhn.png',
]

print('=== 贴图文件存在性 ===')
for rel in test_cases:
    p = MEISHU / rel.replace('/', '\\')
    print(f'  {"OK" if p.exists() else "NO"} {rel}')

# 统计 model/sprite3d 下有多少贴图
spr = MEISHU / 'model' / 'sprite3d'
print(f'\nmodel/sprite3d 存在: {spr.exists()}')
if spr.exists():
    for ext in ['.png', '.tga', '.jpg']:
        cnt = sum(1 for _ in spr.rglob(f'*{ext}'))
        print(f'  {ext}: {cnt} 个')

# 看下 model/player 下有多少
mp = MEISHU / 'model' / 'player'
print(f'\nmodel/player 存在: {mp.exists()}')
if mp.exists():
    for ext in ['.png', '.tga']:
        cnt = sum(1 for _ in mp.rglob(f'*{ext}'))
        print(f'  {ext}: {cnt} 个')

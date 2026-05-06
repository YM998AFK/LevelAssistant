import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

sp3d = Path(r'D:\meishu\Assets\BundleResources\ide\sprite3d')
items = list(sp3d.iterdir())
print(f'sprite3d 内容（共 {len(items)} 项）:')
for f in items[:30]:
    t = 'DIR' if f.is_dir() else 'FILE'
    print(f'  [{t}] {f.name}')

# 找贴图文件
print('\n查找贴图 (.png/.tga/.psd):')
for ext in ['.png', '.tga', '.psd', '.jpg']:
    found = list(sp3d.glob(f'*{ext}'))
    print(f'  {ext}: {len(found)} 个（直接）')

# 看prefab文件
prefabs = list(sp3d.glob('*.prefab'))
print(f'\nprefab 文件（直接）: {len(prefabs)} 个，样本: {[p.name for p in prefabs[:5]]}')

# 递归找宝箱相关
print('\n查找 baoxiang*:')
for p in sp3d.rglob('baoxiang*'):
    print(' ', p)

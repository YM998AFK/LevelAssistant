import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\Hetao\Desktop\公司\.cursor\skills\level-common\resource_index.jsonl', encoding='utf-8') as f:
    lines = [json.loads(l) for l in f]

meshparts = [r for r in lines if r.get('type') == 'MeshPart']

# 已有分类的 subcategory -> 名字样本
from collections import defaultdict, Counter
print('=== 已有子类 -> 名字样本（每类前5个）===')
by_sub = defaultdict(list)
for r in meshparts:
    sub = r.get('subcategory', '')
    if sub:
        by_sub[sub].append(r['name'])
for sub, names in sorted(by_sub.items(), key=lambda x: -len(x[1])):
    print(f'\n【{sub}】({len(names)}条)')
    print('  ' + ' / '.join(names[:8]))

# 没有分类的物件名字（按名字排序）
print('\n\n=== 无分类物件名字（486条）===')
no_cat = [r for r in meshparts if not r.get('subcategory')]
names_no_cat = sorted(r['name'] for r in no_cat)
for i, name in enumerate(names_no_cat):
    print(f'  {name}', end='\n' if (i+1)%5==0 else '  ')

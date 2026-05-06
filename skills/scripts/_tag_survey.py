import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\Hetao\Desktop\公司\.cursor\skills\level-common\resource_index.jsonl', encoding='utf-8') as f:
    lines = [json.loads(l) for l in f]

from collections import Counter, defaultdict

def show(title, items, key, top=20):
    print(f'\n=== {title} ===')
    c = Counter(str(r.get(key,'')) for r in items)
    for k,v in c.most_common(top):
        print(f'  {repr(k)}: {v}')

# --- Effect ---
effects = [r for r in lines if r.get('type') == 'Effect']
print(f'\n[Effect] 总数: {len(effects)}')
print('Effect 名称样本（前80）:')
for e in effects[:80]:
    print(f'  {e["id"]}: {e["name"]}')

# --- Sprite2D ---
sprites = [r for r in lines if r.get('type') == 'Sprite2D']
print(f'\n[Sprite2D] 总数: {len(sprites)}')
show('sprite_set top20', sprites, 'sprite_set')
print('Sprite2D 名称样本（前20）:')
for s in sprites[:20]:
    print(f'  {s["id"]}: {s["name"]} | set={s.get("sprite_set","")}')

# --- MeshPart category/subcategory/tags 有值 vs 空 ---
meshparts = [r for r in lines if r.get('type') == 'MeshPart']
print(f'\n[MeshPart] 总数: {len(meshparts)}')
has_cat = sum(1 for r in meshparts if r.get('category'))
has_sub = sum(1 for r in meshparts if r.get('subcategory'))
has_tag = sum(1 for r in meshparts if r.get('tags'))
has_size = sum(1 for r in meshparts if r.get('size_tier'))
print(f'  有 category: {has_cat}  有 subcategory: {has_sub}  有 tags: {has_tag}  有 size_tier: {has_size}')

from collections import Counter
cats = Counter(r.get('category','') for r in meshparts)
print('category 分布:')
for k,v in cats.most_common():
    print(f'  {repr(k)}: {v}')

subcats = Counter(r.get('subcategory','') for r in meshparts)
print('subcategory top15:')
for k,v in subcats.most_common(15):
    print(f'  {repr(k)}: {v}')

all_tags = Counter()
for r in meshparts:
    for t in r.get('tags', []):
        all_tags[t] += 1
print('tags top20:')
for k,v in all_tags.most_common(20):
    print(f'  {repr(k)}: {v}')

# --- Scene ---
scenes = [r for r in lines if r.get('type') == 'Scene']
print(f'\n[Scene] 总数: {len(scenes)}')
for field in ['scene_style','scene_env','scene_space','scene_func']:
    show(f'scene {field}', scenes, field, 15)

# --- UI ---
uis = [r for r in lines if r.get('type') == 'UI']
print(f'\n[UI] 总数: {len(uis)}')
for u in uis:
    print(f'  {u}')

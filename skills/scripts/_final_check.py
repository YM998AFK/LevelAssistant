import sys, json
sys.stdout.reconfigure(encoding='utf-8')
records = [json.loads(l) for l in open('.cursor/skills/level-common/resource_index.jsonl', encoding='utf-8')]
meshparts = [r for r in records if r.get('type') == 'MeshPart']
print(f'MeshPart 总量: {len(meshparts)}')

for field in ['dominant_color','render_style','is_transparent','has_emission','subcategory','style','level_role']:
    cnt = sum(1 for r in meshparts if r.get(field) not in (None, '', []))
    print(f'  {field}: {cnt}/{len(meshparts)} ({100*cnt//len(meshparts)}%)')

samples = [r for r in meshparts if r.get('dominant_color') and r.get('render_style')][:3]
for s in samples:
    print(f"\n  [{s['id']}] {s['name']}: color={s.get('dominant_color')} style={s.get('render_style')} subcategory={s.get('subcategory')} level_role={s.get('level_role')}")

import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\Hetao\Desktop\公司\.cursor\skills\level-common\resource_index.jsonl', encoding='utf-8') as f:
    lines = [json.loads(l) for l in f]

meshparts = [r for r in lines if r.get('type') == 'MeshPart']
chars = [r for r in lines if r.get('type') == 'Character']

# 角色 species 分布
from collections import Counter
print('=== 角色 species ===')
sp = Counter(r.get('species','') for r in chars)
for k,v in sp.most_common():
    print(f'  {k}: {v}')

# 看角色 abilities (移动类型)
print('\n=== 角色移动能力（fly/swim有）===')
fly = [r for r in chars if '飞' in r.get('abilities', [])]
swim = [r for r in chars if '游泳' in r.get('abilities', [])]
print(f'  能飞: {len(fly)} — {[r["name"] for r in fly[:8]]}')
print(f'  能游: {len(swim)} — {[r["name"] for r in swim[:8]]}')

# 看 MeshPart tags 里的风格词
from collections import Counter
style_words = ['魔法','科幻','古风','欧风','现代','机械','神话','卡通','赛博','蒸汽']
print('\n=== MeshPart tags 风格词 ===')
for w in style_words:
    cnt = sum(1 for r in meshparts if w in r.get('tags', []))
    print(f'  {w}: {cnt}')

# 无分类物件按关键词粗分
no_cat = [r for r in meshparts if not r.get('subcategory')]
print(f'\n=== 无分类 {len(no_cat)} 条，按关键词粗估 ===')
groups = {
    '3D精灵角色': ['_3D', '精灵版', '精灵'],
    '神话神兽': ['朱雀','白虎','青龙','梼杌','貔貅','饕餮','九婴','神兽','龙','凤'],
    '科技装置': ['脑电波','能源探头','EMP','芯片','进化芯片','脑机','探测器','传感'],
    '材料零件': ['合金','材料','碎片','矿','碳粉','硅','铜','硼砂','妖精金属'],
    '药品丹药': ['丹','药','解毒','镇定','毒液','蒙汗'],
    '文件书籍': ['账本','记录','日记','手册','圣旨','卷','文书','通关文牒','腰牌'],
    '平台路径': ['桥板','路线','履带','立体路径','线框','挂点'],
    '地砖地面': ['地砖','地板','地毯','土块'],
    '武器弹药': ['炮','弹','箭','枪','刀','锤','毒刺','激光'],
    '容器箱子': ['盲盒','盒子','存储器','胶囊'],
    '食物饮品': ['茶','咖啡','冰沙','榴莲','芒果','香蕉','菠萝','蜜雪','饼干'],
    '钥匙锁': ['锁','钥','令牌','笛','令'],
    '装饰标识': ['旗','横幅','条幅','标识','箭头','路线图'],
}
for gname, kws in groups.items():
    matched = [r['name'] for r in no_cat if any(kw in r['name'] for kw in kws)]
    if matched:
        print(f'  [{gname}] {len(matched)}条: {matched[:6]}')

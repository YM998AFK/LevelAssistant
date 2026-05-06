import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\Hetao\Desktop\公司\.cursor\skills\level-common\resource_index.jsonl', encoding='utf-8') as f:
    lines = [json.loads(l) for l in f]

meshparts = [r for r in lines if r.get('type') == 'MeshPart']
no_cat = [r for r in meshparts if not r.get('subcategory')]

# 测试：纯名字规则能覆盖多少空白条目
STYLE_RULES = [
    (['魔法','法袍','法阵','魔镜','魔杖','坩埚','咒','符','神笔','锦囊','魔药','丹炉','乾坤','法宝'], '魔法奇幻'),
    (['芯片','EMP','脑机','脑电波','能源探头','进化','电磁','雷达','传感','等离子','虚拟屏幕','科技','蒸汽'], '科幻蒸汽'),
    (['马车','牛车','古风','铜','玉','毛笔','算盘','圣旨','腰牌','竹','壁画','鼎','瓮','营地'], '中国古风'),
    (['朱雀','白虎','青龙','梼杌','九婴','饕餮','貔貅','神兽','毕方','鲲','凤','麒麟'], '神话'),
    (['无人机','飞机','机甲','机器','齿轮','管道','电路'], '科幻蒸汽'),
]
SUBCAT_RULES = [
    (['_3D精灵','3D精灵版','精灵版'], 'CHR3D', '角色/配角NPC_3D'),
    (['朱雀','白虎','青龙','梼杌','九婴','大鹏'], 'DECO', '装饰/神话神兽'),
    (['芯片','脑机','脑电波','能源探头','EMP','电磁','传感'], 'PROP', '道具/科技装置'),
    (['合金','碎片','矿石','碳粉','硅','硼砂','妖精金属','建材','材料条','材料板'], 'PROP', '道具/材料零件'),
    (['还魂丹','解毒','蒙汗药','镇定剂','药水','魔药','毒液'], 'PROP', '道具/药品丹药'),
    (['圣旨','腰牌','手册','日记本','借阅记录','通关文牒','账本','借阅'], 'PROP', '道具/书籍文件'),
    (['密码锁','鲁班锁','密码备忘','朋友一生','令牌'], 'PROP', '道具/钥匙锁具'),
    (['炮弹','飞箭','箭雨','毒刺','大炮','祈雨大炮','榴莲大炮','蘑菇炮'], 'PROP', '道具/武器弹药'),
    (['地砖','地板','地毯','土块','红土块','黑土块'], 'NAT', '地面/地表'),
    (['立体路径','空挂点','运输路线','路线','履带','传送履带'], 'BLD', '基础设施/路径标记'),
    (['桥板','搭桥'], 'BLD', '基础设施/平台桥板'),
    (['箭头','标识','旗子','横幅','条幅'], 'DECO', '装饰/横幅标识'),
    (['茶','咖啡','冰沙','奶','芒果派','饼干'], 'FOOD', '食物/饮品加工'),
    (['香蕉','榴莲','西瓜','菠萝','蜜雪','草莓'], 'FOOD', '食物/水果'),
    (['盲盒','胶囊存储器','空盒子'], 'PROP', '器皿/箱柜'),
]

matched_subcat = 0
matched_style = 0
ambiguous = []
for r in no_cat:
    name = r['name']
    sub_hit = False
    for kws, cat, sub in SUBCAT_RULES:
        if any(kw in name for kw in kws):
            matched_subcat += 1
            sub_hit = True
            break
    sty_hit = False
    for kws, sty in STYLE_RULES:
        if any(kw in name for kw in kws):
            matched_style += 1
            sty_hit = True
            break
    if not sub_hit and not sty_hit:
        ambiguous.append(name)

print(f'无分类共 {len(no_cat)} 条')
print(f'  名字规则可推断 subcategory: {matched_subcat} 条 ({matched_subcat/len(no_cat)*100:.0f}%)')
print(f'  名字规则可推断 style: {matched_style} 条 ({matched_style/len(no_cat)*100:.0f}%)')
print(f'  两者都推不出（需看图）: {len(ambiguous)} 条')
print('\n推不出的名字（前50）:')
for n in ambiguous[:50]:
    print(f'  {n}')

# 预览图覆盖统计
with open(r'c:\Users\Hetao\Desktop\公司\.cursor\skills\level-common\资源预览图\preview_urls.md', encoding='utf-8') as f:
    preview_text = f.read()
import re
# 从 preview_urls 里提取物件 section
obj_section = preview_text[preview_text.find('## 物件'):]
obj_ids = set(re.findall(r'AssetId=(\d+)', obj_section))
no_cat_ids = {str(r['id']) for r in no_cat}
covered = no_cat_ids & obj_ids
print(f'\n无分类物件有缩略图的: {len(covered)}/{len(no_cat_ids)} 条')
print(f'无分类物件无缩略图的: {len(no_cat_ids)-len(covered)} 条')

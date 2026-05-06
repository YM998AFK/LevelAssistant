import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'scripts/navmesh')
import navmesh_validate as V

SCENE_ID = 19454

# 纯剧情关卡——角色只需站在有效地面上，无需跨岛可达
# 使用第一次扫描验证通过的 x=-14.12 区域，加 x=-12.62 做前排
named = [
    ("禾木",      (-12.62, 0.27, 21.84)),  # 前排左  (有台词，靠近相机)
    ("桃子",      (-12.62, 0.27, 24.84)),  # 前排右  (有台词，靠近相机)
    ("小核桃",    (-14.12, 0.27, 20.34)),  # 中排左
    ("队长",      (-14.12, 0.27, 23.34)),  # 中排中
    ("雪球",      (-14.12, 0.27, 24.84)),  # 中排右
    ("乌拉呼",    (-14.12, 0.27, 21.84)),  # 中排左2
    ("宇航老师",  (-14.12, 0.27, 27.84)),  # 后排（传送出现）
    ("control",   (-12.62, 0.27, 23.34)),  # 摄像机锚点，Visible=false
]

# 只检查落地合法+间距，不检跨岛可达（纯剧情无需pathfind）
rep = V.validate_positions(
    SCENE_ID, named,
    require_reachable_pairs=[],
    min_spacing=1.0,
)
print(rep.pretty())
if rep.ok:
    print("\n✅ NavMesh 全PASS（纯剧情模式，无需跨岛可达）")
    print("\n最终坐标:")
    for name, (x,y,z) in named:
        print(f"  {name}: [{x:.3f}, 0.27, {z:.3f}]")

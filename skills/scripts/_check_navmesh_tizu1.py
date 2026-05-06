import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'scripts/navmesh')
import navmesh_validate as V

SCENE_ID = 19454

# 场景概况
try:
    summary = V.scene_summary(SCENE_ID)
    print(f"场景 {SCENE_ID} island_count = {summary['island_count']}")
    print(f"  最大岛质心 = {summary['largest_island_centroid']}")
except Exception as e:
    print(f"scene_summary 失败: {e}")

# 7个角色坐标（ws米 → Unity世界坐标，ws[0]=X, ws[1]=Z(高), ws[2]=Y(横)）
# ws Position → Unity: (ws[0], ws[1], ws[2]) = (x, y, z)
positions = [
    ("队长",      (1.0,  0.27,  0.0)),
    ("小核桃",    (1.0,  0.27, -1.5)),
    ("雪球",      (1.0,  0.27,  1.5)),
    ("禾木",      (2.5,  0.27, -1.0)),
    ("桃子",      (2.5,  0.27,  1.0)),
    ("乌拉呼",    (0.0,  0.27, -2.0)),
    ("宇航老师",  (-1.0, 0.27,  0.0)),
    ("control",   (1.5,  0.27,  0.0)),
]

reachable_pairs = [
    ("队长", "小核桃"),
    ("队长", "禾木"),
    ("队长", "桃子"),
    ("队长", "宇航老师"),
]

try:
    rep = V.validate_positions(
        SCENE_ID,
        positions,
        require_reachable_pairs=reachable_pairs,
        min_spacing=1.0,
    )
    print(rep.pretty())
    if rep.ok:
        print("✅ NavMesh 验证通过，所有坐标可用")
    else:
        print("❌ NavMesh 验证失败，需调整坐标")
        for issue in rep.issues:
            print(f"  - {issue}")
except Exception as e:
    print(f"validate_positions 失败: {e}")

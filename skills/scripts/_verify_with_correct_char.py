"""用正确的角色坐标(444,366,600)重新验证所有测试。"""
import sys, math
sys.stdout.reconfigure(encoding="utf-8")

# 角色真实坐标（来自截图编辑器显示）
char = (444, 366, 600)

print("=== 用正确角色坐标(444,366,600)重新验证 ===\n")

# 所有实测数据
tests = [
    ("正视-中 v2（已确认正确）",  (887, 636, 350), None),        # 用户确认正确
    ("Pitch=135 原始错误包",       (835, 1026, 346), (1279, 1392, 946)),
    ("Pitch=135 校准 by=0",        (835, 0, 346),   (1279, 366, 946)),
    ("Pitch=135 bz=967",           (514, 0, 967),   (958, 366, 1567)),
]

print(f"公式假设：cam = char + (bx, by, bz)")
print(f"  cam_X = {char[0]} + bx")
print(f"  cam_Y = {char[1]} + by")
print(f"  cam_Z = {char[2]} + bz\n")

for name, (bx,by,bz), actual_cam in tests:
    pred = (char[0]+bx, char[1]+by, char[2]+bz)
    if actual_cam:
        match = "✅" if pred == actual_cam else f"❌ 预测{pred} vs 实测{actual_cam}"
        print(f"{name}")
        print(f"  block({bx},{by},{bz}) → 预测 cam={pred}, 实测 cam={actual_cam}  {match}")
    else:
        print(f"{name}")
        print(f"  block({bx},{by},{bz}) → 预测 cam={pred}")
    print()

print("=== 俯45° 居中条件 ===")
print("cam_Y - char_Y = sqrt((cam_X-char_X)² + (cam_Z-char_Z)²) → 几何 45°")
print("即：by = sqrt(bx² + bz²)\n")

print("=== 推荐预设（角色坐标无关，只用相对偏移）===")
for label, dist in [("近",600),("中",1300),("远",2100),("超远",2800)]:
    by_v = round(dist / math.sqrt(2))    # vertical = horizontal = dist/√2
    bx_v = by_v                           # 纯正前方，bz=0
    pred = (char[0]+bx_v, char[1]+by_v, char[2]+0)
    print(f"  俯45-{label}  block({bx_v}, {by_v}, 0)  →  cam≈{pred}  3D={dist}cm")

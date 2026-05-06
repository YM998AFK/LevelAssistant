"""汇总所有视角参考图的摄像机数据，并基于基础角色包的角色位置计算相对偏移。"""
import sys, json, os
sys.stdout.reconfigure(encoding="utf-8")

# ── 从图片读取的原始数据（Camera x, y, z, dir, pitch, fov）────────────────
# 格式：(视角名, x, y, z, dir, pitch, fov)
RAW = [
    # 正视 (Pitch=90，水平)
    ("正视-近",    750,  370, 648,  -90,  90, 25.0),
    ("正视-中",    902,  370, 648,  -90,  90, 25.0),
    ("正视-远",   1400,  370, 648,  -90,  90, 25.0),
    ("正视-超远",  1600,  370, 648,  -90,  90, 25.0),
    # 俯45 (Pitch=135，俯45°)
    ("俯45-近",    723,  366, 911,  -90, 135, 25.0),
    ("俯45-中",    850,  366,1038,  -90, 135, 25.0),
    ("俯45-远",   1297,  366,1483,  -90, 135, 25.0),
    ("俯45-超远",  1509,  366,1695,  -90, 135, 25.0),
    # 俯30 (Pitch=120，俯30°)
    ("俯30-近",    751,  356, 820,  -90, 120, 25.0),
    ("俯30-中",   1016,  356, 973,  -90, 120, 25.0),
    ("俯30-远",   1230,  360,1075,  -90, 120, 25.0),
    ("俯30-超远",  1495,  360,1228,  -90, 120, 25.0),
    # 俯60 (Pitch=150，俯60°)
    ("俯60-近",    670,  364, 990,  -90, 150, 25.0),
    ("俯60-中",    850,  366,1302,  -90, 150, 25.0),
    ("俯60-远",   1452,  371,2343,  -90, 150, 25.0),
    ("俯60-超远",  1835,  374,3005,  -90, 150, 25.0),
    # 俯90 (Pitch=180，正俯视)
    ("俯90-近",    444,  366,1095,  -90, 180, 25.0),
    ("俯90-中",    444,  366,1335,  -90, 180, 25.0),
    ("俯90-远",    444,  366,1740,  -90, 180, 25.0),
    ("俯90-超远",  444,  366,2040,  -90, 180, 25.0),
]

# ── 基础角色包角色数据 ────────────────────────────────────────────────────
# 从 _read_base_char.py 输出：pos=[14.80266, 19.98423, 12.20055] m, scale=1, size=[1, 2.277619, 1]
char_pos_m = [14.80266, 19.98423, 12.20055]  # 米
char_scale = 1.0
char_size  = [1.0, 2.277619, 1.0]
char_height_m  = char_size[1] * char_scale   # 实际身高（米）
char_eye_y_m   = char_pos_m[1] + char_height_m * 0.85  # 眼睛 Y（米）

# 换算成 cm（与 Camera 显示单位一致）
char_x_cm  = char_pos_m[0] * 100   # 1480.3 cm
char_y_cm  = char_pos_m[1] * 100   # 1998.4 cm
char_z_cm  = char_pos_m[2] * 100   # 1220.1 cm
char_h_cm  = char_height_m * 100   # 227.8 cm
char_eye_cm = char_eye_y_m  * 100   # ~1805  cm

print(f"=== 基础角色（队长）===")
print(f"  世界坐标(cm): x={char_x_cm:.1f}  y={char_y_cm:.1f}  z={char_z_cm:.1f}")
print(f"  身高: {char_h_cm:.1f}cm  眼睛Y: {char_eye_cm:.1f}cm")
print()

# ── 计算相对偏移 ──────────────────────────────────────────────────────────
print("=== 视角数据汇总（Camera x/y/z = 摄像机世界坐标 cm）===")
print(f"{'视角名':<12} {'CamX':>6} {'CamY':>6} {'CamZ':>6}  {'Pitch':>5}  "
      f"{'dx(CamX-CharX)':>16} {'dy(CamY-CharY)':>16} {'dz(CamZ-CharZ)':>16}")
print("-"*100)

for name, cx, cy, cz, d, p, fov in RAW:
    dx = cx - char_x_cm   # 相对角色 X 偏移
    dy = cy - char_y_cm   # 相对角色 Y 偏移（高度差）
    dz = cz - char_z_cm   # 相对角色 Z 偏移
    print(f"{name:<12} {cx:>6} {cy:>6} {cz:>6}  {p:>5}  "
          f"  {dx:>+12.0f}cm   {dy:>+12.0f}cm   {dz:>+12.0f}cm")

print()

# ── 按视角类型统计 y 的稳定性 ────────────────────────────────────────────
print("=== y 值（摄像机世界 Y）稳定性验证 ===")
import statistics
for pitch, label in [(90, "正视"), (120, "俯30"), (135, "俯45"), (150, "俯60"), (180, "俯90")]:
    ys = [cy for (n, cx, cy, cz, d, p, fov) in RAW if p == pitch]
    print(f"  {label}(Pitch={pitch}): y = {ys}  均值={statistics.mean(ys):.1f}  std={statistics.stdev(ys) if len(ys)>1 else 0:.1f}")

print()
print("=== 结论 ===")
print("  FOV=25, Direction=-90 对所有视角恒定")
print("  y（摄像机世界 Y）在每个俯仰角内基本恒定（表明 CamY = 角色Y + 固定偏移）")
print(f"  角色 Y = {char_y_cm:.0f}cm")
for pitch, label in [(90, "正视"), (120, "俯30"), (135, "俯45"), (150, "俯60"), (180, "俯90")]:
    ys = [cy for (n, cx, cy, cz, d, p, fov) in RAW if p == pitch]
    avg = statistics.mean(ys)
    dy_rel = avg - char_y_cm
    dy_rel_h = dy_rel / char_h_cm
    print(f"  {label}(Pitch={pitch}): CamY均值={avg:.0f}  相对角色Y差={dy_rel:+.0f}cm = {dy_rel_h:+.2f}×身高")

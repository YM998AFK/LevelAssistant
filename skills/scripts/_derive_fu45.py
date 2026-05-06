"""推导 Pitch=135, Direction=-90 下 CameraFollow 的参数映射。"""
import sys, math
sys.stdout.reconfigure(encoding="utf-8")

# 校准包实测：block(835, 0, 346) → cam(1279, 366, 946)
# 角色位置：(14.80, 19.98, 12.20)
char = (14.80, 19.98, 12.20)
bx, by, bz = 835, 0, 346
cam = (1279, 366, 946)

# 实测映射
delta_X = cam[0] - char[0]   # bx → cam_X
delta_Y = cam[1] - char[1]   # bz → cam_Y  (由 bz=346 确认)
delta_Z = cam[2] - char[2]   # bx → cam_Z

print("=== Pitch=135 参数映射（由校准包推导）===")
print(f"  bx={bx} → ΔX={delta_X:.1f}  系数 k_X = {delta_X/bx:.4f}")
print(f"  bz={bz} → ΔY={delta_Y:.1f}  (cam_Y = char_Y + bz ✓)")
print(f"  bx={bx} → ΔZ={delta_Z:.1f}  系数 k_Z = {delta_Z/bx:.4f}")
print()

k_X = delta_X / bx   # 1.5142
k_Z = delta_Z / bx   # 1.1178

# 验证：k_X² + k_Z² 是否等于某个"球面半径"的平方
k_total = math.sqrt(k_X**2 + k_Z**2)
print(f"  水平半径系数 k_total = √(k_X²+k_Z²) = {k_total:.4f}")
print(f"  tan(45°) = height / horizontal_radius = 1.0")
print(f"  → 若要相机精准在 45° 俯角看到角色中心：bz = bx × {k_total:.4f}")
print()

# 结论：对 Pitch=135 的正确公式
# cam_X = char_X + bx * 1.5142
# cam_Y = char_Y + bz          (与 Pitch=90 一样)
# cam_Z = char_Z + bx * 1.1178
# cam_Y += by （offsetY 叠加到 Y，实际应置 0）

# 推导"俯45-中"（与参考截图相同视觉距离）
# 参考截图 cam=(850,366,1038) char=(14.8,20,12.2) → 3D 距离
ref_cam = (850, 366, 1038)
ref_dist = math.sqrt(sum((ref_cam[i]-char[i])**2 for i in range(3)))
print(f"参考截图 3D 距离 = {ref_dist:.1f} cm")

# 目标：同样视觉距离，角色精准在 45° 中央
dist_target = ref_dist  # 约 1367 cm
height_for_45 = dist_target * math.sin(math.radians(45))
horiz_for_45  = dist_target * math.cos(math.radians(45))
bx_new = horiz_for_45 / k_total  # horizontal_radius = bx * k_total
bz_new = height_for_45

print(f"目标 3D 距离 = {dist_target:.1f} cm，45° 俯角")
print(f"  需要 height = {height_for_45:.1f} → bz = {round(bz_new)}")
print(f"  需要 horizontal = {horiz_for_45:.1f} → bx = {round(bx_new)}")
print()

# 验证：这些 bx/bz 能产生 45° 角度吗？
bx_r, bz_r = round(bx_new), round(bz_new)
cam_r_X = char[0] + bx_r * k_X
cam_r_Y = char[1] + bz_r
cam_r_Z = char[2] + bx_r * k_Z
actual_dist = math.sqrt((cam_r_X-char[0])**2 + (cam_r_Y-char[1])**2 + (cam_r_Z-char[2])**2)
actual_angle = math.degrees(math.atan2(cam_r_Y-char[1], math.sqrt((cam_r_X-char[0])**2 + (cam_r_Z-char[2])**2)))
print(f"验证 block({bx_r}, 0, {bz_r}):")
print(f"  预测 cam 位置 = ({cam_r_X:.1f}, {cam_r_Y:.1f}, {cam_r_Z:.1f})")
print(f"  3D 距离 = {actual_dist:.1f} cm")
print(f"  俯仰角（从水平面看） = {actual_angle:.1f}°  ← 目标 45°")
print()
print(f"✅ 推荐'俯45-中'预设: CameraFollow(target, {bx_r}, 0, {bz_r})")
print(f"   Pitch=135, Direction=-90, FOV=25")

# 整个 20 组预设中，俯45 的 4 组
print()
print("=== 俯45 全部 4 组推荐参数（等比缩放）===")
refs = [
    ("俯45-近",   700),
    ("俯45-中",  ref_dist),  # 1367
    ("俯45-远",  2100),
    ("俯45-超远",2800),
]
for name, d in refs:
    h = d * math.sin(math.radians(45))
    bx_ = round(d * math.cos(math.radians(45)) / k_total)
    bz_ = round(h)
    print(f"  {name:<10} 3D dist={d:.0f}  block({bx_:>4}, 0, {bz_:>4})  Pitch=135")

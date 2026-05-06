"""
根据两次实测推导正确的 Pitch=135 参数映射，计算居中所需绝对坐标和 block 参数。

实测数据：
  Test1: block(835, 0, 346) → cam(1279, 366, 946)
  Test2: block(514, 0, 967) → cam(958, 366, 1567)
  (两次 cam_Y 均 = 366 = char_Y + 346，与 bz 无关)

关键发现：cam_Y = char_Y + 346 + by（对 Pitch=135, Direction=-90 固定，346 是轨道基础高度）
"""
import sys, math
sys.stdout.reconfigure(encoding="utf-8")

char = (14.80, 19.98, 12.20)

# 两次实测
# Test1: block(bx1=835, by=0, bz1=346) → cam1=(1279, 366, 946)
# Test2: block(bx2=514, by=0, bz2=967) → cam2=(958, 366, 1567)
bx1, bz1, cam1_X, cam1_Z = 835, 346, 1279, 946
bx2, bz2, cam2_X, cam2_Z = 514, 967, 958, 1567

BASE_HEIGHT_135 = 346  # cam_Y = char_Y + BASE_HEIGHT_135 + by

# 解线性方程组：cam_X - char_X = bx*k_Xb + bz*k_Xz
# cam_Z - char_Z = bx*k_Zb + bz*k_Zz
dX1 = cam1_X - char[0]; dZ1 = cam1_Z - char[2]
dX2 = cam2_X - char[0]; dZ2 = cam2_Z - char[2]

# For X: bx1*k_Xb + bz1*k_Xz = dX1; bx2*k_Xb + bz2*k_Xz = dX2
det = bx1*bz2 - bx2*bz1
k_Xb = (dX1*bz2 - dX2*bz1) / det
k_Xz = (bx1*dX2 - bx2*dX1) / det
k_Zb = (dZ1*bz2 - dZ2*bz1) / det
k_Zz = (bx1*dZ2 - bx2*dZ1) / det

print(f"=== Pitch=135 完整映射 ===")
print(f"  cam_X = char_X + bx×{k_Xb:.4f} + bz×{k_Xz:.4f}")
print(f"  cam_Y = char_Y + {BASE_HEIGHT_135} + by")
print(f"  cam_Z = char_Z + bx×{k_Zb:.4f} + bz×{k_Zz:.4f}")

# 验证
print(f"\n验证 Test1 block({bx1},0,{bz1}):")
print(f"  cam_X={char[0]+bx1*k_Xb+bz1*k_Xz:.1f} (实测{cam1_X})")
print(f"  cam_Z={char[2]+bx1*k_Zb+bz1*k_Zz:.1f} (实测{cam1_Z})")
print(f"验证 Test2 block({bx2},0,{bz2}):")
print(f"  cam_X={char[0]+bx2*k_Xb+bz2*k_Xz:.1f} (实测{cam2_X})")
print(f"  cam_Z={char[2]+bx2*k_Zb+bz2*k_Zz:.1f} (实测{cam2_Z})")

# 当前相机位置分析
cur_cam = (958, 366, 1567)
vert = cur_cam[1] - char[1]
horiz = math.sqrt((cur_cam[0]-char[0])**2 + (cur_cam[2]-char[2])**2)
actual_angle = math.degrees(math.atan2(vert, horiz))
print(f"\n=== 当前相机分析 ===")
print(f"  cam=({cur_cam[0]}, {cur_cam[1]}, {cur_cam[2]}), char=({char[0]:.1f}, {char[1]:.1f}, {char[2]:.1f})")
print(f"  垂直差 = {vert:.1f}cm, 水平距 = {horiz:.1f}cm")
print(f"  实际几何俯角 = {actual_angle:.1f}°  (Pitch=135 强制 45°，差太多 → 角色偏上)")

print(f"\n=== 正确绝对坐标（角色居中于 45°）===")
for label, dist_3d in [("近", 600), ("中", 1300), ("远", 2100), ("超远", 2800)]:
    # 保持当前水平方向（azimuth=36.4°），仅调整距离和高度
    az = math.atan2(cur_cam[2]-char[2], cur_cam[0]-char[0])
    h = dist_3d * math.sin(math.radians(45))  # 垂直 = 水平 = 斜边/√2
    horiz_target = h
    target_X = char[0] + horiz_target * math.cos(az)
    target_Y = char[1] + h
    target_Z = char[2] + horiz_target * math.sin(az)

    # 推算 block 参数
    # by = target_Y - char_Y - BASE_HEIGHT_135
    by = round(target_Y - char[1] - BASE_HEIGHT_135)
    delta_X_needed = target_X - char[0]
    delta_Z_needed = target_Z - char[2]
    det2 = k_Xb*k_Zz - k_Zb*k_Xz
    bx_need = (delta_X_needed*k_Zz - delta_Z_needed*k_Xz) / det2
    bz_need = (k_Xb*delta_Z_needed - k_Zb*delta_X_needed) / det2

    bx_r, by_r, bz_r = round(bx_need), max(0, by), round(bz_need)
    print(f"\n  俯45-{label}（3D距离={dist_3d}cm）：")
    print(f"    目标 cam 绝对坐标 ≈ ({target_X:.0f}, {target_Y:.0f}, {target_Z:.0f})")
    print(f"    block({bx_r}, {by_r}, {bz_r})")

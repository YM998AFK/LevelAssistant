"""
计算正视-中的正确 CameraFollow 相对偏移量。

关键认知：
- Camera display (x, y, z) = 摄像机世界绝对坐标（单位与 .ws position 一致）
- CameraFollow(target, distance, offsetY, height) 中的 distance/offsetY/height
  = 摄像机相对目标角色的偏移量
- 正确做法：offset = cam_abs - char_abs

坐标轴映射（验证规则）：
  cam_world = char_pos + (distance, height, offsetY) 分别对应 (X, Y, Z)
  即：
    camera_X = char_X + distance
    camera_Y = char_Y + height
    camera_Z = char_Z + offsetY
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

# 角色绝对坐标（来自 .ws，与 Camera display 同单位）
char_x = 14.80266
char_y = 19.98423
char_z = 12.20055

# Camera display 读取的摄像机绝对坐标（单位同上）
presets = [
    # (名称, cam_x, cam_y, cam_z, Pitch)
    ("正视-近",     750,  370, 648,  90),
    ("正视-中",     902,  370, 648,  90),
    ("正视-远",    1400,  370, 648,  90),
    ("正视-超远",   1600,  370, 648,  90),
    ("俯30-近",     751,  356, 820, 120),
    ("俯30-中",    1016,  356, 973, 120),
    ("俯30-远",    1230,  360,1075, 120),
    ("俯30-超远",  1495,  360,1228, 120),
    ("俯45-近",     723,  366, 911, 135),
    ("俯45-中",     850,  366,1038, 135),
    ("俯45-远",    1297,  366,1483, 135),
    ("俯45-超远",  1509,  366,1695, 135),
    ("俯60-近",     670,  364, 990, 150),
    ("俯60-中",     850,  366,1302, 150),
    ("俯60-远",    1452,  371,2343, 150),
    ("俯60-超远",  1835,  374,3005, 150),
    ("俯90-近",     444,  366,1095, 180),
    ("俯90-中",     444,  366,1335, 180),
    ("俯90-远",     444,  366,1740, 180),
    ("俯90-超远",   444,  366,2040, 180),
]

print(f"角色坐标: ({char_x}, {char_y}, {char_z})")
print()
print(f"{'视角名':<12} {'distance':>10} {'offsetY':>10} {'height':>10}  {'Pitch':>5}  验证(camera_X=char_X+dist)")
print("-" * 75)

for name, cx, cy, cz, pitch in presets:
    # offset = cam - char，对应 CameraFollow(target, distance, offsetY, height)
    # camera_X = char_X + distance → distance = cam_x - char_x
    # camera_Y = char_Y + height   → height   = cam_y - char_y
    # camera_Z = char_Z + offsetY  → offsetY  = cam_z - char_z
    distance = round(cx - char_x)
    height   = round(cy - char_y)
    offsetY  = round(cz - char_z)
    
    # 验证反推
    check_x = char_x + distance
    ok = "✅" if abs(check_x - cx) < 1 else "❌"
    
    print(f"{name:<12} {distance:>10} {offsetY:>10} {height:>10}  {pitch:>5}  {ok} cam_X={check_x:.1f}≈{cx}")

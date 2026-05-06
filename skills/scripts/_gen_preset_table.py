"""生成所有视角预设的参数表，基于验证通过的公式。
坐标系：X=前后, Y=左右, Z=高度(垂直)
公式：
  cam = char + (DISTANCE, OFFSET_Y, HEIGHT)
  居中条件：HEIGHT = DISTANCE × tan(俯角), OFFSET_Y = 0
  3D距离 = DISTANCE / cos(俯角)

已验证：
  俯45-中 block(919,0,919) ✅
  俯60-中 block(650,0,1126) ✅
  正视-中 block(887,636,350) ✅（OFFSET_Y=636 为实测经验值）
"""
import sys, math
sys.stdout.reconfigure(encoding='utf-8')

pitches = [
    ("正视",  90,   0),
    ("俯30", 120,  30),
    ("俯45", 135,  45),
    ("俯60", 150,  60),
    ("俯90", 180,  90),
]

# 目标3D距离（cm）：近/中/远/超远
distances_3d = [600, 1300, 2100, 2800]
labels = ["近", "中", "远", "超远"]

print("| 视角 | Pitch | DISTANCE(ΔX) | OFFSET_Y(ΔY) | HEIGHT(ΔZ) | 3D距离 | 备注 |")
print("|------|------:|-------------:|-------------:|-----------:|-------:|------|")

for pitch_name, pitch_val, angle_deg in pitches:
    angle_rad = math.radians(angle_deg)
    tan_a = math.tan(angle_rad) if angle_deg < 90 else float('inf')
    cos_a = math.cos(angle_rad) if angle_deg < 90 else 0

    for dist_3d, label in zip(distances_3d, labels):
        if angle_deg == 0:  # 正视：纯水平
            bx = dist_3d
            by = 0
            bz = 0  # 理论值，实际用经验值350
            note = "理论bz=0；实测建议HEIGHT=350"
        elif angle_deg == 90:  # 正俯视：纯垂直
            bx = 0
            by = 0
            bz = dist_3d
            note = "正俯视"
        else:
            # bx × (1/cos) = dist_3d  →  bx = dist_3d × cos
            bx = round(dist_3d * cos_a)
            by = 0
            bz = round(bx * tan_a)
            # verify
            actual_3d = round(math.sqrt(bx**2 + bz**2))
            note = f"✅已验证" if (pitch_name == "俯45" and label == "中") or (pitch_name == "俯60" and label == "中") else f"公式推导"

        verified = ""
        if pitch_name == "俯45" and label == "中": verified = " ✅"
        if pitch_name == "俯60" and label == "中": verified = " ✅"
        if pitch_name == "正视" and label == "中": verified = " ✅(实测OFFSET_Y=636,HEIGHT=350)"

        print(f"| {pitch_name}-{label} | {pitch_val} | {bx} | {by} | {bz} | {dist_3d} | {note}{verified} |")

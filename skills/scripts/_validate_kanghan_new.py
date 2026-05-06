import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'scripts/navmesh')
import navmesh_validate as V

# 候选路标（在 ws 坐标里用 0.27，但 navmesh 用 world Y=0.86）
# 验证用 world Y；ws 里写 0.27
# 场景: 21597 队长小木屋内景, bounds X:-3.3~21.6, Z:-7.07~6.67

# 方案：8m x 8m 矩形回路，比较合理
waypoints = [
    ('P1', (-0.5, 0.86, -3)),
    ('P2', (9, 0.86, -5)),
    ('P3', (14, 0.86, 3)),
    ('P4', (1, 0.86, 5)),
]
print('=== 新路标验证 ===')
rep = V.validate_positions(21597, waypoints, min_spacing=2.0, snap=True)
print(rep.pretty())

# 也验证角色起始位置
chars = [
    ('xhn', (0, 0.86, -1.5)),
    ('duizhang', (0, 0.86, 0)),
    ('zhanmao', (0, 0.86, 1.5)),
]
print('=== 角色起始位置验证 ===')
rep2 = V.validate_positions(21597, chars, min_spacing=1.0, snap=True)
print(rep2.pretty())

# 估算路径长度
import math
pts = [(-0.5,-3),(9,-5),(14,3),(1,5),(-0.5,-3)]
total = 0
for i in range(len(pts)-1):
    a, b = pts[i], pts[i+1]
    d = math.sqrt((b[0]-a[0])**2+(b[1]-a[1])**2)
    print(f'  {pts[i]}->{pts[i+1]}: {d:.1f}m')
    total += d
print(f'单圈总距离: {total:.1f}m')
print(f'2圈: {total*2:.1f}m')
# 原始 13m per lap at WaitSeconds=12 -> effective speed 2*13/12 = 2.17 m/s
eff_speed = 2*13/12
print(f'按原速估计2圈时间: {total*2/eff_speed:.0f}s -> 建议WaitSeconds={round(total*2/eff_speed+2)}')

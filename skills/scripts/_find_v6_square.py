# -*- coding: utf-8 -*-
"""Find largest square where each ACTUAL corner is walkable AND >= min_wall_dist from boundary."""
import sys, io, json, math
sys.path.insert(0, 'scripts')
sys.path.insert(0, 'scripts/navmesh')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from navmesh_loader import load_navmesh

m = load_navmesh(21597)
boundary_verts = [m.cverts[j] for j in m.boundary_loops[0]]

def point_in_tri_xz(px, pz, a, b, c):
    ax,az=a[0],a[2]; bx,bz=b[0],b[2]; cx2,cz2=c[0],c[2]
    d1=(px-bx)*(az-bz)-(ax-bx)*(pz-bz)
    d2=(px-cx2)*(bz-cz2)-(bx-cx2)*(pz-cz2)
    d3=(px-ax)*(cz2-az)-(cx2-ax)*(pz-az)
    return not ((d1<0 or d2<0 or d3<0) and (d1>0 or d2>0 or d3>0))

def walkable(x, z):
    for tri in m.tris:
        a,b,c=m.cverts[tri[0]],m.cverts[tri[1]],m.cverts[tri[2]]
        if point_in_tri_xz(x,z,a,b,c): return True
    return False

def dist_to_boundary(px, pz):
    min_d = float('inf')
    n = len(boundary_verts)
    for i in range(n):
        ax,az = boundary_verts[i][0], boundary_verts[i][2]
        bx,bz = boundary_verts[(i+1)%n][0], boundary_verts[(i+1)%n][2]
        dx,dz = bx-ax, bz-az
        dlen2 = dx*dx+dz*dz+1e-9
        t = max(0.0, min(1.0, ((px-ax)*dx+(pz-az)*dz)/dlen2))
        nx2,nz2 = ax+t*dx, az+t*dz
        d = math.sqrt((px-nx2)**2+(pz-nz2)**2)
        min_d = min(min_d, d)
    return min_d

MIN_WALL_DIST = 1.0  # 角点距墙至少 1 单位，确保在室内可见

def corners_ok(cx, cz, half):
    for x, z in [(cx-half, cz-half),(cx+half, cz-half),(cx+half, cz+half),(cx-half, cz+half)]:
        if not walkable(x, z): return False
        if dist_to_boundary(x, z) < MIN_WALL_DIST: return False
    return True

# 搜索最大满足条件的正方形（半格 0.25 精度）
best = None; best_area = 0
for cxi in range(4, 32):
    cx = cxi * 0.5
    for czi in range(-10, 12):
        cz = czi * 0.5
        if not walkable(cx, cz): continue
        lo, hi = 0.5, 8.0
        for _ in range(28):
            mid = (lo+hi)/2
            if corners_ok(cx, cz, mid/2): lo=mid
            else: hi=mid
        half = lo/2 - 0.01
        if not corners_ok(cx, cz, half): continue
        side = half*2
        if side**2 > best_area:
            best_area = side**2
            best = (cx, cz, half, side)

cx, cz, half, side = best
Y = '0.853'
print(f'最优正方形（角点离墙>={MIN_WALL_DIST}单位）: 边长={round(side,2)}, 中心=({cx},{cz})')
print(f'  面积={round(side**2,1)}  ({round(side**2/m.total_walkable_xz_area*100,1)}% of walkable)')
print()
corners = [('P1',cx-half,cz-half),('P2',cx+half,cz-half),
           ('P3',cx+half,cz+half),('P4',cx-half,cz+half)]
for nm,x,z in corners:
    d = dist_to_boundary(x, z)
    print(f'  {nm}: [{round(x,3)}, {Y}, {round(z,3)}]  dist_wall={round(d,2)}  walk={walkable(x,z)}')

# 角色起跑位：正方形前边内侧2单位，横排3人间距2
sz = cz - half + 1.0
print()
print('角色起跑位（前边内侧1.0，间距2.0）:')
char_pos = []
for i, nm in enumerate(['小核桃','队长','展喵']):
    ox = (i-1)*2.0
    px, pz = round(cx+ox, 3), round(sz, 3)
    char_pos.append((nm, px, pz))
    print(f'  {nm}: [{px}, {Y}, {pz}]')

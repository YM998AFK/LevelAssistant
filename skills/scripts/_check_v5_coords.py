# -*- coding: utf-8 -*-
import sys, io, json, math
sys.path.insert(0, 'scripts')
sys.path.insert(0, 'scripts/navmesh')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from navmesh_loader import load_navmesh

WS = 'output/modify/kanghan_v5_workdir/b0f15ca2-193c-4512-a4f7-31e03114caaf.ws'
data = json.loads(open(WS, encoding='utf-8').read())
scene = data['scene']

print('=== 当前 v5 坐标 ===')
for ch in scene['children']:
    nm = ch['props'].get('Name', '?')
    if nm in ['P1','P2','P3','P4','L1','L2','L3']:
        pos = ch['props'].get('Position', '?')
        print(f'  {nm}: {pos}')

m = load_navmesh(21597)

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
    verts = [m.cverts[j] for j in m.boundary_loops[0]]
    min_d = float('inf')
    n = len(verts)
    for i in range(n):
        ax,az = verts[i][0],verts[i][2]
        bx,bz = verts[(i+1)%n][0],verts[(i+1)%n][2]
        dx,dz = bx-ax, bz-az
        dlen2 = dx*dx+dz*dz+1e-9
        t = max(0.0, min(1.0, ((px-ax)*dx+(pz-az)*dz)/dlen2))
        nx2,nz2 = ax+t*dx, az+t*dz
        d = math.sqrt((px-nx2)**2+(pz-nz2)**2)
        min_d = min(min_d, d)
    return min_d

print()
print('=== v5 P1-P4 距边界距离 ===')
pts = [('P1',-0.043,-6.543),('P2',13.043,-6.543),('P3',13.043,6.543),('P4',-0.043,6.543)]
for nm,x,z in pts:
    d = dist_to_boundary(x, z)
    tag = 'ok' if d > 1.0 else 'WALL!'
    print(f'  {nm} ({x:.3f},{z:.3f}): dist={d:.3f}  [{tag}]')

print()
print('=== 搜索更好的正方形（内缩 1.5 单位安全边距）===')

def ok_with_margin(cx, cz, half, margin=1.5):
    h = half - margin
    if h <= 0: return False
    for x,z in [(cx-h,cz-h),(cx+h,cz-h),(cx+h,cz+h),(cx-h,cz+h)]:
        if not walkable(x,z): return False
        if dist_to_boundary(x,z) < margin: return False
    return True

best = None; best_area = 0
for cxi in range(6, 28):
    cx = cxi * 0.5
    for czi in range(-10, 10):
        cz = czi * 0.5
        if not walkable(cx, cz): continue
        lo, hi = 1.0, 8.0
        for _ in range(25):
            mid = (lo+hi)/2
            if ok_with_margin(cx, cz, mid/2, margin=1.5): lo=mid
            else: hi=mid
        half = lo/2 - 0.05
        if half < 1.0: continue
        if not ok_with_margin(cx, cz, half, 1.5): continue
        side = half*2
        if side**2 > best_area:
            best_area = side**2
            best = (cx, cz, half, side)

cx, cz, half, side = best
Y = '0.853'
print(f'最优正方形: 边长={round(side,2)}, 中心=({cx},{cz})')
print(f'  面积={round(side**2,1)}  ({round(side**2/m.total_walkable_xz_area*100,1)}%)')
print()
corners = [('P1',cx-half,cz-half),('P2',cx+half,cz-half),
           ('P3',cx+half,cz+half),('P4',cx-half,cz+half)]
for nm,x,z in corners:
    d = dist_to_boundary(x, z)
    print(f'  {nm}: [{round(x,2)}, {Y}, {round(z,2)}]  dist_wall={d:.2f}  walk={walkable(x,z)}')

print()
sx = cx; sz = cz - half + 1.5
print('角色起跑位（前边内侧1.5，横排间距1.5）:')
for i, nm in enumerate(['小核桃','队长','展喵']):
    print(f'  {nm}: [{round(sx+(i-1)*1.5, 2)}, {Y}, {round(sz, 2)}]')

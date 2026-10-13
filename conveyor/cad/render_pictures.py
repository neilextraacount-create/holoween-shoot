#!/usr/bin/env python3
"""Render the assembly pictures in docs/img/ (same placements as check_parts.py). Run after check_parts.py:
   python3 render_pictures.py"""
import os, sys, math, subprocess, importlib.util, numpy as np, trimesh
CAD = os.path.dirname(os.path.abspath(__file__))
import tempfile, shutil, os
OUTD = tempfile.mkdtemp()
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'img')
spec = importlib.util.spec_from_file_location('cp', CAD + '/check_parts.py'); cp = importlib.util.module_from_spec(spec); spec.loader.exec_module(cp)
V = cp.scad_values()
class R: 
    def __call__(self, *a): pass
    def head(self, *a): pass
A = cp.Asm(R(), V)
def save(name, mf):
    me = mf.to_mesh(); t = trimesh.Trimesh(np.asarray(me.vert_properties)[:, :3], np.asarray(me.tri_verts))
    t.export(f'{OUTD}/{name}.stl'); return name
def render(scene, items, eye, center, size=(1200, 900), auto=None):
    if auto is not None:                                   # auto = (azimuth, elevation, distance factor)
        bb = np.array([trimesh.load(f'{OUTD}/{n}.stl').bounds for n, _ in items])
        lo, hi = bb[:, 0].min(0), bb[:, 1].max(0); center = (lo + hi) / 2; r = np.linalg.norm(hi - lo)
        az, el, k = [math.radians(auto[0]), math.radians(auto[1]), auto[2]]
        eye = center + k * r * np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    lines = [f'color("{c}") import("{OUTD}/{n}.stl");' for n, c in items]
    open(f'{OUTD}/{scene}.scad', 'w').write("\n".join(lines))
    cam = ",".join(str(v) for v in list(eye) + list(center))
    subprocess.run(['xvfb-run', '-a', 'openscad', '--preview', f'--camera={cam}', '--projection=p', f'--imgsize={size[0]},{size[1]}',
                    '--colorscheme=Tomorrow', '-o', os.path.join(IMG, f'{scene}-assembly.png'), f'{OUTD}/{scene}.scad'], capture_output=True)
    print('wrote', os.path.join(IMG, f'{scene}-assembly.png'))
P = cp.head_assembly(A, V)
items = []
col = {'A': 'orange', 'B': 'orange', 'roller': 'silver', 'pin': 'silver', 'rotor': 'gold', 'gbody': 'darkorange', 'trap': 'mediumpurple',
       'seg1': 'mediumpurple', 'seg1_shaft': 'gold', 'seg2': 'mediumpurple', 'foot0': 'saddlebrown', 'foot1': 'saddlebrown', 'belt': '#222222', 'sleeve0': 'gold', 'gbolts': 'dimgray'}
for k, c in col.items():
    items.append((save('head_' + k, P[k]), c))
render('head', items, (420, -380, 320), (20, 40, 0))
T = cp.tail_assembly(A, V, 0)
col = {'L': 'orange', 'R': 'orange', 'roller': 'silver', 'axle': 'gold', 'blockL': 'darkorange', 'blockR': 'darkorange', 'nutL': 'dimgray', 'nutR': 'dimgray',
       'screwL': 'gold', 'screwR': 'gold', 'skidL': 'saddlebrown', 'skidR': 'saddlebrown', 'foot': 'saddlebrown', 'belt': '#222222'}
items = [(save('tail_' + k, T[k]), c) for k, c in col.items()]
render('tail', items, (-420, -420, 200), (80, 0, -90))
# station
hw = V["half_w"]
Mw = lambda z: cp.Mx([[1, 0, 0], [0, 0, 1], [0, -1, 0]], (0, -hw, z))
wu = A.bodies("wheel_unit")
br = cp.xf(A.mf("station_bracket"), cp.Mx([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], (0, V["st_y0"], 0)))
c0 = V["sk_c"]
st = cp.xf(A.mf("stake_1"), cp.Mx([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], (c0, -c0 + V["st_y0"] + V["spig"] / 2, -V["sk_hd"] + V["st_bot"])))
belt = cp.box(-250, 250, -V["belt_w"] / 2, V["belt_w"] / 2, -V["belt_t"], 0) + cp.box(-250, 250, -V["belt_w"] / 2, V["belt_w"] / 2, V["st_ret_top"], V["st_ret_top"] + V["belt_t"])
items = [(save('st_wheel_c', cp.xf(wu[0], Mw(V["st_carry_z"]))), 'silver'), (save('st_axle_c', cp.xf(wu[1], Mw(V["st_carry_z"]))), 'gold'),
         (save('st_wheel_r', cp.xf(wu[0], Mw(V["st_ret_z"]))), 'silver'), (save('st_axle_r', cp.xf(wu[1], Mw(V["st_ret_z"]))), 'gold'),
         (save('st_br', br), 'orange'), (save('st_stake', st), 'saddlebrown'), (save('st_belt', belt), '#222222')]
render('station', items, (260, -330, 60), (0, 20, -90))
# porch end: last segment, crank head, arm, posts, tray
N = int(V["seg_count"]); u_ch = V["gb_top_s"] + N * V["seg_len"]
seg = A.bodies("chute_segment"); ch = A.bodies("crank_head"); arm = A.bodies("crank_arm")
Mu, Mls, best, _ = cp.stand_place(A, V, u_ch)                 # same placement the checker verifies
z_hub = V["crank_head_len"] + V["sq_z"][0]
items = [(save('p_seg', cp.xf(seg[0], cp.line_M(V, u_ch - V["seg_len"]))), 'mediumpurple'), (save('p_segs', cp.xf(seg[1], cp.line_M(V, u_ch - V["seg_len"]))), 'gold'),
         (save('p_ch', cp.xf(ch[0], cp.line_M(V, u_ch))), 'mediumpurple'), (save('p_chs', cp.xf(ch[1], cp.line_M(V, u_ch))), 'gold'),
         (save('p_arm', cp.xf(arm[0] + arm[1], cp.line_M(V, u_ch) @ cp.T(V["Y_c"], 0, z_hub) @ cp.Rz(200))), 'orange'),
         (save('p_pu', cp.xf(A.mf("post_upper"), Mu)), 'saddlebrown'), (save('p_tray', best), 'saddlebrown')]
items += [(save(f'p_pl{i}', cp.xf(A.mf("post_lower"), M)), 'saddlebrown') for i, M in enumerate(Mls)]
cx, cy, cz = [float(v) for v in cp.xf(ch[0], cp.line_M(V, u_ch)).bounding_box()[:3]]
render('porch', items, None, None, auto=(-50, 20, 2.0))

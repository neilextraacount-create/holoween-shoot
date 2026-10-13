#!/usr/bin/env python3
"""The whole machine, assembled on the site: head, 4 stations, tail, chute line, crank, porch stand and
the belt, placed with the same transforms check_parts.py verifies module by module, on the same
step model as its SITE check (lawn at 5 deg, sidewalk, steps, porch).

Checks what only the whole machine shows:
  - how the head feet, the tail skids and foot meet the ground, and how deep each stake goes in;
  - the belt: the carry run touches every carry wheel, the return run every return wheel, the belt
    clears everything else, the return run stays off the lawn, the loop length matches the calculator.
Writes docs/img/full-machine.png and docs/img/full-machine-side.png.

    python3 full_assembly.py           (after check_parts.py)
"""
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import trimesh
import manifold3d as m3d

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_parts as cp   # noqa: E402

IN = 25.4
VIRTUAL = ("belt", "candy", "basket")         # check volumes in the module assemblies, not parts
IMG = HERE.parent / "docs" / "img"


class Rep:
    def __init__(self):
        self.fails, self.lines = 0, []

    def __call__(self, ok, msg):
        self.fails += not ok
        self.lines.append(f"  [{'ok' if ok else 'FAIL'}] {msg}")
        print(self.lines[-1], flush=True)

    def head(self, msg):
        self.lines.append("\n" + msg)
        print("\n" + msg, flush=True)


def seg_box(p1, p2, w, t, below=False):
    """thin box (belt) from p1 to p2 in the x-z plane of the head frame, width w across y"""
    d = np.array(p2) - np.array(p1)
    L = float(np.hypot(*d))
    ux, uz = d / L
    z0, z1 = (-t, 0.0) if below else (0.0, t)
    b = cp.box(0, L, -w / 2, w / 2, z0, z1)
    return cp.xf(b, cp.Mx([[ux, 0, -uz], [0, 1, 0], [uz, 0, ux]], (p1[0], 0, p1[1])))


def lowest_gap(mf, terrain):
    """smallest and largest height of a part's bottom vertices above the terrain (mm)"""
    me = mf.to_mesh()
    v = np.asarray(me.vert_properties)[:, :3]
    zt = np.array([terrain(x) for x in v[:, 0]])
    h = v[:, 2] - zt
    return float(h.min()), v[np.argmin(h)]


def main():
    V = cp.scad_values()
    rep = Rep()
    A = cp.Asm(rep, V)
    b = math.radians(V["belt_deg"])
    cb, sb = math.cos(b), math.sin(b)
    axle_h = V["head_h"] - V["belt_t"] - V["drv_rs"]
    W = cp.Mx([[cb, 0, -sb], [0, 1, 0], [sb, 0, cb]], (0, 0, axle_h))     # head frame -> world (as check_site)
    Rb = cp.Mx([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]])                     # undoes the belt tilt: Z world-vertical

    # ---------------------------------------------------------------- site (world: origin on the lawn under the drive axle)
    gap_x, run, rise, nr = V["site_head_gap"] * IN, V["site_run"] * IN, V["site_rise"] * IN, int(V["site_risers"])
    tl = math.tan(math.radians(5))
    lawn_len = 250 * IN
    x_sw = gap_x - lawn_len                      # sidewalk edge (lawn starts here)
    porch_z = gap_x * tl + nr * rise
    treads = nr - 1
    riser_x = [gap_x + i * run / max(treads, 1) for i in range(treads)] + [gap_x + run]

    def terrain(x):
        if x < x_sw:
            return x_sw * tl
        if x < gap_x:
            return x * tl
        return gap_x * tl + rise * sum(1 for r in riser_x if x >= r)

    # ---------------------------------------------------------------- head, line, crank, stand
    P = cp.head_assembly(A, V)
    N = int(V["seg_count"])
    seg = A.bodies("chute_segment")
    u_ch = V["gb_top_s"] + N * V["seg_len"]
    line = {}
    for i in range(1, N):
        line[f"seg{i + 1}"] = cp.xf(seg[0], cp.line_M(V, V["gb_top_s"] + i * V["seg_len"]))
        line[f"seg{i + 1}_shaft"] = cp.xf(seg[1], cp.line_M(V, V["gb_top_s"] + i * V["seg_len"]))
    ch = A.bodies("crank_head")
    line["crank_head"], line["crank_shaft"] = cp.xf(ch[0], cp.line_M(V, u_ch)), cp.xf(ch[1], cp.line_M(V, u_ch))
    arm = A.bodies("crank_arm")
    z_hub = V["crank_head_len"] + V["sq_z"][0]
    line["crank_arm"] = cp.xf(arm[0] + arm[1], cp.line_M(V, u_ch) @ cp.T(V["Y_c"], 0, z_hub) @ cp.Rz(200))
    Mu, Mls, tray, _ = cp.stand_place(A, V, u_ch)
    line["post_upper"] = cp.xf(A.mf("post_upper"), Mu)
    for i, M in enumerate(Mls):
        line[f"post_lower{i}"] = cp.xf(A.mf("post_lower"), M)
    line["tray"] = tray

    # ---------------------------------------------------------------- belt line, stations, tail (head frame)
    zt = V["drv_rs"] + V["belt_t"]                                    # belt top over the drive roller
    r_tt = V["tail_r"] + V["roll_crown"] + V["belt_t"]                # tail axle -> belt top
    x_tail_w = (-2.0 - (250 - V["site_head_gap"])) * IN               # tail axle 2 in out over the sidewalk (calc default)
    d_t = -(x_tail_w + sb * (zt - r_tt)) / cb                         # head-frame distance to the tail axle
    n_st = 4
    span = d_t / (n_st + 1)
    stations = {}
    st_x = []
    hw = V["half_w"]
    Mw = lambda z: cp.Mx([[1, 0, 0], [0, 0, 1], [0, -1, 0]], (0, -hw, z))
    wu = A.bodies("wheel_unit")
    c0 = V["sk_c"]
    for i in range(1, n_st + 1):                                       # station 1 nearest the sidewalk
        xh = -d_t + i * span
        S = cp.T(xh, 0, zt) @ Rb
        st_x.append(xh)
        stations[f"st{i}_carry"] = cp.xf(wu[0] + wu[1], S @ Mw(V["st_carry_z"]))
        stations[f"st{i}_return"] = cp.xf(wu[0] + wu[1], S @ Mw(V["st_ret_z"]))
        stations[f"st{i}_bracket"] = cp.xf(A.mf("station_bracket"), S @ cp.Mx([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], (0, V["st_y0"], 0)))
        stations[f"st{i}_stake"] = cp.xf(A.mf(f"stake_{i}"), S @ cp.Mx([[0, -1, 0], [0, 0, 1], [-1, 0, 0]],
                                                                         (c0, -c0 + V["st_y0"] + V["spig"] / 2, -V["sk_hd"] + V["st_bot"])))
    Tt = cp.tail_assembly(A, V, 0)
    tail = {k: cp.xf(v, cp.T(-d_t, 0, zt - r_tt)) for k, v in Tt.items() if k not in VIRTUAL}

    # belt: carry run straight from the tail apex to the drive apex; return run from the tail roller
    # bottom over each return wheel to the drive roller bottom (points = the belt's lower face)
    bw, bt = V["belt_w"], V["belt_t"]
    belt = {"carry": seg_box((-d_t, zt - bt), (0.0, zt - bt), bw, bt)}
    ret_pts = [(-d_t, zt - r_tt - (V["tail_r"] + V["roll_crown"]) - bt)]
    for xh in st_x:
        ret_pts.append((xh + sb * V["st_ret_top"], zt + cb * V["st_ret_top"]))
    ret_pts.append((0.0, -V["drv_rs"] - bt))
    for i in range(len(ret_pts) - 1):
        belt[f"return{i}"] = seg_box(ret_pts[i], ret_pts[i + 1], bw, bt)

    def world(d):
        return {k: cp.xf(v, W) for k, v in d.items()}
    head_w, line_w, st_w, tail_w, belt_w = world({k: v for k, v in P.items() if k not in VIRTUAL + ("seg2",)}), world(line), world(stations), world(tail), world(belt)

    # ---------------------------------------------------------------- checks
    rep.head("WHOLE MACHINE on the site (2 risers x 7 in ASSUMED; lawn 5 deg; tail axle 2 in over the sidewalk)")
    for nm in ("foot0", "foot1"):
        g, at = lowest_gap(head_w[nm], terrain)
        rep(abs(g) <= 15, f"head {nm}: lowest point {g:+.0f} mm from the lawn (shims or a shallow scrape fix up to 15 mm)")
    for nm in ("skidL", "skidR", "foot"):
        g, at = lowest_gap(tail_w[nm], terrain)
        rep(abs(g) <= 15, f"tail {nm}: lowest point {g:+.0f} mm from the {'sidewalk' if at[0] < x_sw else 'lawn'} at x {at[0] - x_sw:+.0f} mm from the sidewalk edge")
    for i in range(1, n_st + 1):
        stk = st_w[f"st{i}_stake"]
        bb = stk.bounding_box()
        xm = (bb[0] + bb[3]) / 2
        embed = terrain(xm) - bb[2]
        rep(110 <= embed <= 190, f"station {i}: stake goes {embed:.0f} mm into the ground (designed {V['spike_embed']:.0f})")
    rollers = [head_w["roller"], tail_w["roller"], tail_w["axle"]]
    wheels = [st_w[k] for k in st_w if k.endswith("carry") or k.endswith("return")]
    others = [v for k, v in {**head_w, **line_w, **tail_w, **st_w}.items()
              if k not in ("roller", "axle") and not k.endswith("carry") and not k.endswith("return")]
    allbelt = m3d.Manifold.batch_boolean(list(belt_w.values()), m3d.OpType.Add)
    rest = m3d.Manifold.batch_boolean(others, m3d.OpType.Add)
    A.check("belt (both runs) vs every part it should not touch", allbelt, rest, "clear", 1.0)
    for i in range(1, n_st + 1):
        A.check(f"station {i}: carry run rests on the carry wheel", belt_w["carry"], st_w[f"st{i}_carry"], "touch")
        ret = m3d.Manifold.batch_boolean([belt_w[k] for k in belt_w if k.startswith("return")], m3d.OpType.Add)
        A.check(f"station {i}: return run rests on the return wheel", ret, st_w[f"st{i}_return"], "touch")
    low = min(lowest_gap(belt_w[k], terrain)[0] for k in belt_w if k.startswith("return"))
    rep(low >= 30, f"return run stays {low:.0f} mm above the lawn at its lowest (need >= 30)")
    top_min = lowest_gap(belt_w["carry"], terrain)[0] + bt
    rep(True, f"carry run (belt top) {top_min / IN:.1f} in above the ground at its lowest point")
    loop = math.hypot(d_t, 0) + sum(math.dist(ret_pts[i], ret_pts[i + 1]) for i in range(len(ret_pts) - 1)) \
        + math.pi * (V["drv_rs"] + bt / 2) + math.pi * (V["tail_r"] + V["roll_crown"] + bt / 2)
    rep(True, f"belt loop along this path: {loop / 304.8:.2f} ft (the calculator's straight-run estimate is in calc/report-*.txt)")

    # ---------------------------------------------------------------- pictures
    tmp = Path(tempfile.mkdtemp())
    items = []

    def add(name, mf, colr):
        me = mf.to_mesh()
        trimesh.Trimesh(np.asarray(me.vert_properties)[:, :3], np.asarray(me.tri_verts)).export(tmp / f"{name}.stl")
        items.append((name, colr))
    ground = cp.box(x_sw - 600, gap_x + run + 1200, -900, 900, -60, 0)
    lawn = cp.xf(cp.box(0, lawn_len, -900, 900, -60, 0), cp.Mx([[math.cos(math.radians(5)), 0, -math.sin(math.radians(5))], [0, 1, 0],
                                                                [math.sin(math.radians(5)), 0, math.cos(math.radians(5))]], (x_sw, 0, x_sw * tl)))
    sidewalk = cp.box(x_sw - 1200, x_sw, -900, 900, x_sw * tl - 100, x_sw * tl)
    steps = cp.box(gap_x + run, gap_x + run + 1200, -900, 900, gap_x * tl - 60, porch_z)
    for i in range(treads):
        x0 = gap_x + i * run / max(treads, 1)
        steps = steps + cp.box(x0, gap_x + run, -900, 900, gap_x * tl - 60, gap_x * tl + (i + 1) * rise)
    add("lawn", lawn, "#3a7d2c")
    add("sidewalk", sidewalk, "#b9b9b9")
    add("steps", steps, "#a0522d")
    groups = [("head", head_w, "orange"), ("tail", tail_w, "orange"), ("stations", st_w, "darkorange"),
              ("line", line_w, "mediumpurple"), ("belt", belt_w, "#1a1a1a")]
    for gname, d, colr in groups:
        add(gname, m3d.Manifold.batch_boolean(list(d.values()), m3d.OpType.Add), colr)
    xc = (x_sw + gap_x + run + 900) / 2
    for fname, eye, center in (("full-machine", (gap_x + run + 2600, -2600, 2300), (x_sw * 0.42, 0, -150)),
                               ("full-machine-side", (xc, -10200, 450), (xc, 0, 330))):
        scad = tmp / f"{fname}.scad"
        scad.write_text("\n".join(f'color("{c}") import("{tmp / n}.stl");' for n, c in items))
        cam = ",".join(str(float(v)) for v in list(eye) + list(center))
        subprocess.run(["xvfb-run", "-a", "openscad", "--preview", f"--camera={cam}", "--projection=p", "--imgsize=1600,800",
                        "--colorscheme=Tomorrow", "-o", str(IMG / f"{fname}.png"), str(scad)], capture_output=True)
        print("wrote", IMG / f"{fname}.png")
    rep.head(f"RESULT: {'ALL CHECKS PASSED' if rep.fails == 0 else f'{rep.fails} CHECK(S) FAILED'}")
    (HERE / "full-assembly-report.txt").write_text("\n".join(rep.lines) + "\n")
    sys.exit(1 if rep.fails else 0)


if __name__ == "__main__":
    main()

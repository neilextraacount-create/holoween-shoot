#!/usr/bin/env python3
"""SIMPLE candy conveyor: render every part, check it, check the assemblies, the gear mesh and the
site layout, and export the STLs.

    python3 build.py          # writes stl/*.stl, check-report.txt, img/*.png
    python3 build.py --force  # re-render everything

Checks: watertight, body count, fits the P2S bed, no wide unsupported overhangs, nothing starts in
mid-air, print-in-place gaps; gear mesh over a full tooth; every part placed in its module (head,
tail at both ends of the take-up, station) against every other part and the belt; the belt line
over the lawn (station heights, stake depths, ground clearance, sag, loop length); loads.
"""
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import manifold3d as m3d
import numpy as np
import trimesh
from shapely import affinity
from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "cad"))
from check_parts import Mx, Report, Rx, Rz, T, clean_export, islands, overhangs, to_mf, xf   # noqa: E402
from gcode_gaps import cs_polys   # noqa: E402

SCAD = HERE / "simple.scad"
LIB = HERE.parent / "cad" / "lib.scad"
STL = HERE / "stl"
RAW = STL / ".raw"
IMG = HERE / "img"
BED, BED_Z = 246.0, 250.0
IN = 25.4

# name, qty, bodies, turn 45 deg on the bed, what it is
PARTS = [
    ("head_frame",      1, 1, False, "head frame (foot of the steps): drive roller slots, crank pin boss"),
    ("drive_roller",    1, 1, False, "drive roller with its 16-tooth pinion"),
    ("journal_pin",     2, 1, False, "journal pin, pressed into the plain end of each roller"),
    ("crank_gear",      1, 1, False, "40-tooth crank gear with a hex hub"),
    ("crank_arm",       1, 2, False, "crank arm with a print-in-place spinning grip"),
    ("crank_pin",       1, 1, False, "snap pin: holds the gear and the arm on the head frame"),
    ("tail_frame",      1, 1, False, "tail frame (sidewalk): roller slots and wedge windows"),
    ("tail_roller",     1, 1, False, "tail roller"),
    ("wedge",           2, 1, False, "belt-tightening wedge (one each side of the tail)"),
    ("cassette",        3, 3, False, "station wheels: top and bottom wheel, print-in-place"),
    ("station_stake_1", 1, 1, True,  "station 1 stake (nearest the sidewalk)"),
    ("station_stake_2", 1, 1, True,  "station 2 stake"),
    ("station_stake_3", 1, 1, True,  "station 3 stake (nearest the steps)"),
    ("anchor_stake",    4, 1, False, "anchor stake: 2 hold the head frame down, 2 the tail frame"),
]


# ----------------------------------------------------------------------------- rendering
def src_hash():
    h = hashlib.sha256()
    for f in (SCAD, LIB):
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def render(part, out):
    r = subprocess.run(["openscad", "-q", "-D", f'part="{part}"', "-o", str(out), str(SCAD)], capture_output=True, text=True)
    if r.returncode != 0 or not out.exists():
        raise SystemExit(f"render {part} failed:\n{r.stderr[-2000:]}")


def values():
    out = RAW / "vals.echo"
    subprocess.run(["openscad", "-D", 'part="dump"', "-o", str(out), str(SCAD)], capture_output=True, text=True)
    V = {}
    for line in out.read_text().splitlines():
        if line.startswith('ECHO: "VAL '):
            k, v = line[len('ECHO: "VAL '):].rstrip('"').split(" = ", 1)
            V[k] = json.loads(v)
    return V


def load(name):
    t = trimesh.load(str(RAW / f"{name}.stl"), force="mesh")
    t.merge_vertices()
    return t


def mf_of(name, cache={}):
    if name not in cache:
        cache[name] = to_mf(load(name))
    return cache[name]


def bodies_of(name, cache={}):
    if name not in cache:
        cache[name] = [to_mf(b) for b in load(name).split(only_watertight=False)]
    return cache[name]


# ----------------------------------------------------------------------------- part checks
def check_parts(rep):
    rep.head("PARTS (watertight, bodies, bed fit, overhangs, nothing starting in mid-air, print-in-place gaps)")
    for name, qty, nb, rot45, _what in PARTS:
        t = load(name)
        if rot45:
            t.apply_transform(trimesh.transformations.rotation_matrix(math.radians(45), [0, 0, 1]))
        t.apply_translation([-(t.bounds[0][0] + t.bounds[1][0]) / 2, -(t.bounds[0][1] + t.bounds[1][1]) / 2, -t.bounds[0][2]])
        bodies = t.split(only_watertight=False)
        ext = t.extents
        rep(t.is_watertight, f"{name}: watertight")
        rep(len(bodies) == nb, f"{name}: {len(bodies)} bodies (expected {nb})")
        rep(ext[0] <= BED and ext[1] <= BED and ext[2] <= BED_Z,
            f"{name}: {ext[0]:.0f} x {ext[1]:.0f} x {ext[2]:.0f} mm fits the bed ({BED:.0f} x {BED:.0f} x {BED_Z:.0f})")
        oh = [o for o in overhangs(t) if o[1] > 6.0]
        bad = [o for o in oh if o[1] > 12.0 and (o[4] is None or o[4] > 13.0)]
        rep(not bad, f"{name}: no unsupported overhang wider than 12 mm"
            + (f" (widest {max(o[1] for o in oh):.1f} mm, bridged half-span {max((o[4] or 0) for o in oh):.1f} mm)" if oh else "")
            + (f"; BAD {[(round(o[1], 1), round(o[3], 1), o[4]) for o in bad[:3]]}" if bad else ""))
        mf = to_mf(t)
        isl = islands(mf)
        rep(not isl, f"{name}: nothing starts in mid-air" + (f"; at {isl[:4]}" if isl else ""))
        if nb > 1:
            mfs = [to_mf(b) for b in bodies]
            g = min(a.min_gap(b, 5.0) for i, a in enumerate(mfs) for b in mfs[i + 1:])
            rep(g >= 0.40, f"{name}: print-in-place gap {g:.2f} mm (>= 0.40)")
        clean_export(t, STL / f"{name}.stl")


# ----------------------------------------------------------------------------- helpers
def place(name, M):
    return xf(mf_of(name), M)


def band2d(c, r_in, thick, x_from, x_to):
    """belt wrapped round a roller (XZ plane): half wrap on the side away from the runs, runs to x_to"""
    cx, cz = c
    R = r_in + thick
    outer = m3d.CrossSection.circle(R, 128).translate([cx, cz]) + \
        m3d.CrossSection.square([abs(x_to - cx), 2 * R]).translate([min(cx, x_to), cz - R])
    inner = m3d.CrossSection.circle(r_in, 128).translate([cx, cz]) + \
        m3d.CrossSection.square([abs(x_to - cx) + 1, 2 * r_in]).translate([min(cx, x_to) - (1 if x_to < cx else 0), cz - r_in])
    return outer - inner


def extrude_y(cs, width):
    """2D (x, z) -> solid along Y, centred"""
    return xf(m3d.Manifold.extrude(cs, width).translate([0, 0, -width / 2]), Rx(90))


def chk(rep, label, a, b, mode, lim=0.0):
    """mode 'clear': no overlap and gap >= lim; 'touch': overlap <= lim mm3 (contact allowed)"""
    ov = (a ^ b).volume()
    gap = a.min_gap(b, 20.0) if ov < 1e-6 else 0.0
    if mode == "clear":
        rep(ov < 1e-3 and gap >= lim - 1e-6, f"{label}: clear by {gap:.2f} mm (need {lim})" + (f"; OVERLAP {ov:.2f} mm3" if ov >= 1e-3 else ""))
    else:
        rep(ov <= lim, f"{label}: in contact, overlap {ov:.2f} mm3 (limit {lim})")
    return ov, gap


# ----------------------------------------------------------------------------- gear mesh
def gear_mesh(rep, V):
    rep.head("GEAR MESH (16T pinion on the drive roller, 40T crank gear; 2D sweep over a full tooth)")
    pz = V["L_w"] / 2 + V["p_y0"] + V["p_face"] / 2
    P = cs_polys(mf_of("drive_roller").slice(pz))[0]
    G0 = cs_polys(mf_of("crank_gear").slice(V["g_face"] / 2))[0]
    hz, gc = V["hz"], V["g_c"]
    gx, gy = gc[0], hz - gc[1]                       # gear centre in the pinion's print xy (y = hz - Z)
    ratio = V["z_pin"] / V["z_gear"]

    def state(a, psi):
        p = affinity.rotate(P, a, origin=(0, 0))
        g = affinity.translate(affinity.rotate(G0, -a * ratio + psi, origin=(0, 0)), gx, gy)
        return p.intersection(g).area, p.distance(g)
    best = max(((state(0, psi)[1] if state(0, psi)[0] < 1e-6 else -1, psi) for psi in np.arange(0, 9.0, 0.05)))
    psi = best[1]
    worst_ov, min_gap, max_gap = 0.0, 9.0, 0.0
    for a in np.linspace(0, 360 / V["z_pin"], 49):
        ov, d = state(a, psi)
        worst_ov, min_gap, max_gap = max(worst_ov, ov), min(min_gap, d), max(max_gap, d)
    rep(worst_ov < 0.01, f"teeth never overlap over a full tooth (worst {worst_ov:.3f} mm2)")
    rep(0.05 <= min_gap <= 0.6, f"running clearance {min_gap:.2f}-{max_gap:.2f} mm between the tooth flanks")
    rep(abs(math.hypot(gx, gy) - V["C"]) < 0.01, f"centre distance {V['C']:.1f} mm = module x (16 + 40) / 2")
    return psi


# ----------------------------------------------------------------------------- assemblies
def head(rep, V, psi):
    rep.head("HEAD (frame, drive roller + pin, crank gear + arm + pin, belt)")
    hz, gc, L2 = V["hz"], V["g_c"], V["L_w"] / 2
    g0, g1 = gc
    P = {"frame": place("head_frame", np.eye(4)),
         "roller": place("drive_roller", T(0, -L2, hz) @ Rx(-90)),
         "pinA": place("journal_pin", T(0, -L2 - V["j_len"] - 2, hz) @ Rx(-90)),
         "gear": place("crank_gear", T(g0, V["g_y0"], g1) @ Rx(-90) @ Rz(psi)),
         "cpin": place("crank_pin", Mx([[0, 1, 0], [-1, 0, 0], [0, 0, 1]], (g0, V["g_y0"] + V["g_face"] + V["arm_t"], g1 - (V["cp_r"] - 0.5))))}
    belt = extrude_y(band2d((0, hz), V["drv_rs"], V["belt_t"], 0, 400), V["belt_w"])
    chk(rep, "drive roller vs frame (journals in the slots, flanges by the walls)", P["roller"], P["frame"], "clear", 0.25)
    chk(rep, "journal pin vs frame", P["pinA"], P["frame"], "clear", 0.25)
    chk(rep, "crank gear vs frame (pin boss face)", P["gear"], P["frame"], "clear", 0.3)
    chk(rep, "crank gear vs drive roller (meshing)", P["gear"], P["roller"], "clear", 0.03)
    chk(rep, "crank pin vs frame (through the hole, catch face inside wall B)", P["cpin"], P["frame"], "clear", 0.15)
    chk(rep, "crank pin vs gear (the gear turns on it)", P["cpin"], P["gear"], "clear", 0.2)
    chk(rep, "belt vs drive roller", belt, P["roller"], "touch", 60.0)
    for k in ("frame", "gear", "cpin", "pinA"):
        chk(rep, f"belt vs {k}", belt, P[k], "clear", 3.0)
    low = 1e9
    for ang in range(0, 360, 30):
        arm = place("crank_arm", T(g0, V["g_y0"] + V["g_face"], g1) @ Rx(-90) @ Rz(ang))
        ov_r, gap_r = (arm ^ P["roller"]).volume(), arm.min_gap(P["roller"], 20)
        ov_f, gap_f = (arm ^ P["frame"]).volume(), arm.min_gap(P["frame"], 20)
        ov_b = (arm ^ belt).volume()
        ok = ov_r < 1e-3 and gap_r >= 0.3 and ov_f < 1e-3 and gap_f >= 1.0 and ov_b < 1e-3
        low = min(low, arm.bounding_box()[2])
        if not ok or ang == 0:
            rep(ok, f"crank arm at {ang} deg: clear of the pinion by {gap_r:.2f} mm, of the frame by {gap_f:.1f} mm, of the belt")
        if ang == 0:
            chk(rep, "crank arm vs gear (on the hex hub)", arm, P["gear"], "touch", 1.0)
            chk(rep, "crank arm vs crank pin (head on the arm)", arm, P["cpin"], "touch", 1.0)
    rep(low >= 40, f"crank handle's lowest point {low:.0f} mm above the lawn (>= 40)")
    rep(True, f"crank axis {g1:.0f} mm above the lawn, {g0:.0f} mm toward the tail from the roller")
    return P


def tail(rep, V):
    rep.head("TAIL (frame, roller + pin, 2 wedges, belt) at the take-up's two ends")
    tz, L2, x_f, jr = V["tz"], V["L_w"] / 2, V["x_f"], V["j_r"]
    tan = math.tan(math.radians(V["wd_ang"]))
    frame = place("tail_frame", np.eye(4))
    for label, z_tip in (("tightest", V["win_z0"]), ("loosest", V["tz"] - 25)):
        w = V["wd_t0"] + (tz - z_tip) * tan
        xj = x_f + w + jr + 0.05
        roller = place("tail_roller", T(xj, -L2, tz) @ Rx(-90))
        pin = place("journal_pin", T(xj, -L2 - V["j_len"] - 2, tz) @ Rx(-90))
        wedges = [place("wedge", Mx([[1, 0, 0], [0, 0, -1], [0, 1, 0]], (x_f, y0 + 5.6, z_tip))) for y0 in (V["w_in"] + 0.2, -V["w_out"] + 0.2)]
        belt = extrude_y(band2d((xj, tz), V["tail_r"] + 0.3, V["belt_t"], xj, -500), V["belt_w"])
        rep(xj + jr + V["j_gap"] <= V["slot_end"] + 1e-6, f"{label}: journal at x {xj:.1f} inside the slot (rear end {V['slot_end']})")
        chk(rep, f"{label}: tail roller vs frame", roller, frame, "clear", 0.25)
        chk(rep, f"{label}: journal pin vs frame", pin, frame, "clear", 0.25)
        for i, wd in enumerate(wedges):
            chk(rep, f"{label}: wedge {'BA'[i]} vs frame (front face on the window's face)", wd, frame, "touch", 1.0)
            chk(rep, f"{label}: wedge {'BA'[i]} vs roller journal (pushes it back)", wd, roller if i == 0 else pin, "touch", 3.0)
        chk(rep, f"{label}: belt vs frame", belt, frame, "clear", 3.0)
        chk(rep, f"{label}: belt vs wedges", belt, wedges[0] + wedges[1], "clear", 3.0)
        rep(True, f"{label}: wedge tip {z_tip:.0f} mm up, {w:.1f} mm thick at the journal")
    w_lo = V["wd_t0"] + 25 * tan
    w_hi = V["wd_t0"] + (tz - V["win_z0"]) * tan
    rep(True, f"take-up travel {w_hi - w_lo:.1f} mm (belt loop {2 * (w_hi - w_lo):.0f} mm); taper {V['wd_ang']} deg"
              f" self-locks (PLA friction angle about 17 deg)")


def station(rep, V):
    rep.head("STATION (stake, wheel cassette, belt runs)")
    sc, L2 = V["st_carry"], V["L_w"] / 2
    Mc = Mx([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], (0, -L2, -sc))
    cas = bodies_of("cassette")
    order = sorted(cas, key=lambda m: m.volume(), reverse=True)
    static, spools = order[0], order[1:]
    S = xf(static, Mc)
    W = [xf(s, Mc) for s in spools]
    Zm = -sc - V["st_sock_x"]                     # socket mouth (block bottom)
    off = (V["stake_leg"]) / 2
    Ms = Mx([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], (off, -V["spig"] / 2, Zm - 6))
    stake = place("station_stake_1", Ms)
    carry = xf(m3d.Manifold.cube([400, V["belt_w"], V["belt_t"]]), T(-200, -V["belt_w"] / 2, -V["belt_t"]))
    ret = xf(m3d.Manifold.cube([400, V["belt_w"], V["belt_t"]]), T(-200, -V["belt_w"] / 2, -48))
    top = [w for w in W if w.bounding_box()[5] > -10][0]
    bot = [w for w in W if w.bounding_box()[5] <= -10][0]
    chk(rep, "stake spigot in the cassette socket (shoulder under the block)", stake, S, "touch", 1.0)
    chk(rep, "stake vs wheels", stake, W[0] + W[1], "clear", 1.0)
    chk(rep, "top run rests on the top wheel", carry, top, "touch", 40.0)
    chk(rep, "return run rests on the bottom wheel", ret, bot, "touch", 40.0)
    chk(rep, "top run vs cassette frame", carry, S, "clear", 3.0)
    chk(rep, "return run vs cassette frame", ret, S, "clear", 3.0)
    chk(rep, "top run vs bottom wheel", carry, bot, "clear", 3.0)
    chk(rep, "return run vs top wheel (the runs pass between the wheels)", ret, top, "clear", 3.0)
    return S.bounding_box()[2]


# ----------------------------------------------------------------------------- site and loads
def site(rep, V, cas_bottom):
    rep.head("SITE (250 in of lawn at 5 deg, head at the foot of the steps, tail at the sidewalk)")
    a = math.radians(5.0)
    Hx = 250 * IN * math.cos(a)
    G = lambda s: s * math.tan(a)

    def world(s0, x, z):                        # module point (x toward the sidewalk, z up) -> site (s, Z), module tilted with the lawn
        ux, uz = -math.cos(a), -math.sin(a)
        nx_, nz = -math.sin(a), math.cos(a)
        return s0 + x * ux + z * nx_, G(s0) + x * uz + z * nz
    s_h0 = Hx - 6 * IN                          # head roller 6 in in front of the first riser (the crank clears the riser)
    hs, hzw = world(s_h0, 0, V["hz"])
    tanw = math.tan(math.radians(V["wd_ang"]))
    xj_mid = V["x_f"] + V["wd_t0"] + (25 + V["tz"] - V["win_z0"]) / 2 * tanw + V["j_r"]
    ts, tzw = world(0.0, xj_mid, V["tz"])
    r_d, r_t = V["drv_rs"] + V["belt_t"], V["tail_r"] + 0.3 + V["belt_t"]
    # upper tangent of the two belt circles
    d = math.hypot(hs - ts, hzw - tzw)
    ang = math.atan2(hzw - tzw, hs - ts)
    phi = math.asin((r_d - r_t) / d)
    nrm = (-math.sin(ang - phi), math.cos(ang - phi))
    p_t = (ts + r_t * nrm[0], tzw + r_t * nrm[1])
    p_h = (hs + r_d * nrm[0], hzw + r_d * nrm[1])
    top = lambda s: p_t[1] + (s - p_t[0]) * (p_h[1] - p_t[1]) / (p_h[0] - p_t[0])
    slope = math.degrees(math.atan2(p_h[1] - p_t[1], p_h[0] - p_t[0]))
    n = 3
    span = (hs - ts) / (n + 1)
    rep(True, f"belt top: {top(ts) - G(ts):.0f} mm over the sidewalk end, {top(hs) - G(hs):.0f} mm over the lawn at the head;"
              f" {slope:.2f} deg (lawn 5.00 deg); stations every {span / IN:.1f} in ({span / 1000:.2f} m)")
    sc, sx = V["st_carry"], V["st_sock_x"]
    lens = V["station_len"]
    rows = []
    for i in range(1, n + 1):
        s = ts + i * span
        H = top(s) - G(s)
        shoulder = H - sc - sx
        embed = lens[i - 1] - shoulder
        rows.append((i, s, H, shoulder, embed))
        rep(120 <= embed <= 175 and shoulder >= 40,
            f"station {i} at {s / IN:5.1f} in from the sidewalk: belt top {H:.0f} mm, block {shoulder:.0f} mm above the lawn,"
            f" stake {lens[i - 1]} mm -> {embed:.0f} mm in the ground (120-175)")
    # return run: tail roller bottom -> return wheel tops -> head roller bottom; ground clearance
    pts = [(ts, tzw - r_t)] + [(s, top(s) - 48) for _, s, *_ in rows] + [(hs, hzw - r_d)]
    clear = min(min(pz - G(px) for px, pz in pts), min(top(s) - sc - sx - G(s) for _, s, *_ in rows))
    rep(clear >= 40, f"lowest point of the return run / station block: {clear:.0f} mm above the lawn (>= 40)")
    # loop length
    L = math.hypot(p_h[0] - p_t[0], p_h[1] - p_t[1])
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        L += math.hypot(x1 - x0, z1 - z0)
    L += math.pi * (r_d + r_t - V["belt_t"])
    rep(True, f"belt loop about {L / 1000:.2f} m ({L / 304.8:.1f} ft) at mid take-up, plus 75 mm to sew the joint")
    # loads
    g = 9.81
    w_belt, w_dense = 0.061 * g, 0.15 * g
    T0 = 20.0
    span_m = span / 1000
    sag = (w_belt + w_dense) * span_m ** 2 / (8 * 15.0) * 1000
    sag_r = w_belt * span_m ** 2 / (8 * T0) * 1000
    gap = 48 - 2 * V["belt_t"]                    # free space between the runs at a station
    rep(sag - sag_r < gap, f"sag between stations: {sag:.0f} mm with dense candy, return run {sag_r:.0f} mm -> runs stay"
                           f" {gap - (sag - sag_r):.0f} mm apart at mid-span")
    mu = 0.3
    tail_f = 2 * T0 * mu * V["j_r"] / (V["tail_r"] + 2)
    wheels = 2 * n * 0.3
    R = tail_f + wheels + 2.0
    j_d = (2 * T0 + 15) * mu * V["j_r"] / 1000
    tq_roller = R * r_d / 1000 + j_d
    ratio = V["z_gear"] / V["z_pin"]
    tq = tq_roller * ratio / 0.85
    F = tq / (V["crank_r"] / 1000)
    v = ratio * 2 * math.pi * r_d / 1000
    need = math.log((T0 + R / 2) / (T0 - R / 2)) / math.pi
    rep(F < 20, f"cranking: belt drag {R:.1f} N -> {tq:.2f} N.m at the crank = {F:.0f} N on the handle; one turn a second moves"
                f" the belt {v:.2f} m/s ({(hs - ts) / 1000 / v:.0f} s porch to sidewalk)")
    rep(need < 0.2, f"drive grip: needs friction >= {need:.2f} on the ribbed roller (PLA on polypropylene about 0.25-0.3)")
    # tail roller: the belt runs leave it slightly uphill (toward the head) and lift it; the wedges' 8 deg faces push it down
    lift = (T0 + R / 2) * math.sin(math.radians(abs(slope))) + (T0 - R / 2) * math.sin(math.radians(abs(slope)))
    hold = 2 * T0 * math.sin(math.radians(V["wd_ang"])) + 0.42
    rep(hold > 1.5 * lift, f"tail roller stays in its slots: belt lift {lift:.1f} N, held down by the wedge faces and its weight {hold:.1f} N")
    Ft = 2 * tq / (V["gm"] * V["z_gear"] / 2000)
    rep(True, f"gear teeth at twice that torque: {Ft:.0f} N -> {Ft / (8 * 2 * 0.3):.0f} MPa (40T), {Ft / (7.5 * 2 * 0.27):.0f} MPa (16T)"
              " along the layers (PLA ~50)")
    w_arm = 32.0
    rep(True, f"crank arm {w_arm:.0f} x {V['arm_t']} mm at the hub, 30 N on the grip: {6 * 30 * (V['crank_r'] - 17) / (V['arm_t'] * w_arm ** 2):.1f} MPa;"
              f" crank pin Ø12 with {Ft / 2 + 30:.0f} N: {32 * (Ft / 2 + 30) * 15 / (math.pi * 12 ** 3):.1f} MPa")
    for nm, hgt, arm in (("head", V["hz"], 100.0), ("tail", V["tz"], 165.0)):
        M = 2 * T0 * hgt / 1000
        rep(True, f"{nm}: {2 * T0:.0f} N belt pull {hgt:.0f} mm up tips the frame with {M:.1f} N.m -> {M / arm * 1000:.0f} N pull"
                  f" on the anchor stake farthest from the pull (or {M / arm * 1000 / g:.1f} kg on that end of the base)")
    return {"stations": rows, "loop_m": L / 1000, "span": span}


def main():
    force = "--force" in sys.argv
    STL.mkdir(exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    key = src_hash()
    cache_f = RAW / "hash.json"
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    for name, *_ in PARTS:
        if force or cache.get(name) != key or not (RAW / f"{name}.stl").exists():
            print(f"render {name}", flush=True)
            render(name, RAW / f"{name}.stl")
            cache[name] = key
            cache_f.write_text(json.dumps(cache))
    V = values()
    rep = Report()
    check_parts(rep)
    psi = gear_mesh(rep, V)
    head(rep, V, psi)
    tail(rep, V)
    cb = station(rep, V)
    S = site(rep, V, cb)
    total = sum(q for _, q, *_ in PARTS)
    rep(total <= 21, f"{total} printed parts ({len(PARTS)} different), plus the belt")
    rep.lines.append(f"\nRESULT: {'ALL CHECKS PASSED' if not rep.fails else f'{rep.fails} CHECK(S) FAILED'}")
    print(rep.lines[-1])
    (HERE / "check-report.txt").write_text("\n".join(rep.lines).lstrip() + "\n")
    (HERE / "site.json").write_text(json.dumps({"psi": psi, **{k: v for k, v in S.items()}}, indent=1))
    sys.exit(1 if rep.fails else 0)


if __name__ == "__main__":
    main()

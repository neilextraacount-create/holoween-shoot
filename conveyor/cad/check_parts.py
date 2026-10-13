#!/usr/bin/env python3
"""
Candy conveyor v4: render every printed part, check it, then check the parts against
each other in their assembled positions.

  python3 check_parts.py              # render (cached) + all checks, writes stl/ and check-report.txt
  python3 check_parts.py --force      # re-render everything
  python3 check_parts.py --only parts # or: head, tail, station, line, site

Per part: OpenSCAD renders it without warnings, the mesh is watertight, it has the expected
number of separate bodies (print-in-place parts: 2) with at least the running gap between
them, it fits the Bambu Lab P2S bed (256 x 256 x 256 mm, 10 mm margin; long parts are
exported turned 45 degrees so they lie across the diagonal), no downward face flatter than
45 degrees wider than 12 mm (would need support; hole bridges and short ledges are fine),
and a filament estimate.

Assembly: each part is placed with the same transform the build uses and every pair that
sits close together is checked with exact mesh booleans (manifold3d): the overlap volume
and the smallest gap. "touch" pairs (faces that bear on each other) may touch but must not
overlap; "clear" pairs need the stated gap.

The gearbox STL comes from make_crown.py (crown teeth generated from the pinion motion).
"""
import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import manifold3d as m3d
import networkx as nx
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
SCAD = HERE / "conveyor.scad"
OUT = HERE / "stl"
CACHE = OUT / ".hashes.json"
PLA = 1.24                     # g/cm3
BED = 256.0 - 10.0
IN = 25.4

# name, qty, walls, infill %, expected bodies, turn 45 deg for the bed, what it is
PARTS = [
    ("test_coupon",     1, 3, 15, 7, False, "PRINT FIRST: fit ladder (spinners 0.35/0.45/0.55, sockets, M8 nut)"),
    ("wheel_unit",      8, 2, 15, 2, False, "station wheel, print-in-place (2 per station)"),
    ("station_bracket", 4, 4, 30, 1, False, "station bracket (holds 2 wheels on the stake)"),
    ("stake_1",         1, 4, 30, 1, True,  "station 1 stake (nearest the sidewalk)"),
    ("stake_2",         1, 4, 30, 1, True,  "station 2 stake"),
    ("stake_3",         1, 4, 30, 1, True,  "station 3 stake"),
    ("stake_4",         1, 4, 30, 1, True,  "station 4 stake (nearest the steps)"),
    ("drive_roller",    1, 3, 10, 1, False, "drive roller with 17T pinion"),
    ("drive_pin",       1, 4, 100, 1, False, "drive roller A-side journal pin (press in)"),
    ("head_side_a",     1, 4, 30, 1, False, "head side frame A (round journal hole)"),
    ("head_side_b",     1, 4, 30, 1, False, "head side frame B (open journal slot, gearbox mount)"),
    ("gearbox",         1, 3, 10, 2, False, "gearbox: 34T crown gear rotor in its housing, print-in-place"),
    ("trap",            1, 3, 15, 1, False, "drop trap (bottom of the chute, rests on the head frames)"),
    ("foot",            3, 4, 30, 1, False, "foot crossbar (2 head, 1 tail rear)"),
    ("tail_side_l",     1, 4, 30, 1, False, "tail side frame, left (-Y)"),
    ("tail_side_r",     1, 4, 30, 1, False, "tail side frame, right (+Y)"),
    ("tail_roller",     1, 3, 10, 2, False, "tail roller, print-in-place"),
    ("takeup_block",    2, 4, 40, 1, False, "take-up block (one per side)"),
    ("takeup_nut",      2, 4, 100, 1, False, "take-up square nut"),
    ("takeup_screw",    2, 4, 100, 1, False, "take-up screw with knob"),
    ("skid_l",          1, 4, 30, 1, False, "tail skid, left"),
    ("skid_r",          1, 4, 30, 1, False, "tail skid, right"),
    ("chute_segment",   5, 2, 15, 2, False, "chute segment with print-in-place drive shaft"),
    ("crank_head",      1, 3, 15, 2, False, "crank head: funnel + crank shaft, print-in-place"),
    ("crank_arm",       1, 3, 25, 2, False, "crank arm with spinning grip, print-in-place"),
    ("pin3",           14, 3, 100, 1, False, "3 mm pin: wheel pegs (8), crank arm, crank-head socket, stand height, tray, joint between 2 lower posts if any, spares (2)"),
    ("splice_template", 1, 3, 20, 1, False, "belt sewing template (box-and-X hole pattern)"),
    ("stand_shim",      4, 3, 100, 1, False, "shims to level the porch stand foot"),
    ("hex_coupler",     6, 3, 100, 1, False, "hex coupler between shafts"),
    ("ring_sleeve",     6, 3, 100, 1, False, "sleeve between bearing rings"),
    ("post_lower",      1, 4, 30, 1, True,  "porch stand post, lower"),
    ("post_upper",      1, 4, 30, 1, True,  "porch stand post, upper"),
    ("stand_tray",      1, 4, 20, 1, False, "porch stand foot (put the candy bowl on it)"),
    ("ground_screw",    4, 3, 30, 1, False, "ground screw (head front foot, tail skid rear anchors)"),
    ("spike",           4, 3, 30, 1, False, "L spike with nail head: 2 for the tail skid far pads, 2 optional for the head rear foot"),
    ("stake_cap",       1, 3, 30, 1, False, "push the stakes in through this cap"),
    ("gs_wrench",       1, 3, 30, 1, False, "T-wrench for the ground screws"),
    ("bolt8_28",       17, 4, 100, 1, False, "printed M8 bolt (13 frame joints + 4 ground screws)"),
    ("nut8",           13, 4, 100, 1, False, "printed M8 nut"),
    ("washer50",        4, 3, 100, 1, False, "50 mm washer over a ground screw"),
]


# ----------------------------------------------------------------------------- rendering
def src_hash():
    h = hashlib.sha256()
    for f in ("conveyor.scad", "lib.scad", "params.scad", "make_crown.py"):
        h.update((HERE / f).read_bytes())
    return h.hexdigest()[:16]


RAW = OUT / ".raw"


def render_one(part, force, cache, key):
    out = RAW / f"{part}.stl"
    if not force and out.exists() and cache.get(part) == key:
        return part, True, []
    if part == "gearbox":
        r = subprocess.run([sys.executable, str(HERE / "make_crown.py"), "--out", str(out)], capture_output=True, text=True)
        log = r.stdout + r.stderr
        ok = r.returncode == 0 and "GEARBOX OK" in log
        return part, ok, ([] if ok else [l for l in log.splitlines()[-12:]])
    r = subprocess.run(["openscad", "-o", str(out), "-D", f'part="{part}"', str(SCAD)], capture_output=True, text=True)
    warn = [l for l in (r.stdout + r.stderr).splitlines() if "WARNING" in l or "ERROR" in l]
    return part, r.returncode == 0 and out.exists() and not warn, warn


def scad_values():
    out = OUT / ".vals.echo"
    subprocess.run(["openscad", "-o", str(out), str(HERE / "dump_vals.scad")], capture_output=True, text=True)
    vals = {}
    for line in out.read_text().splitlines():
        m = re.match(r'ECHO: "VAL (\w+) = (.*)"', line)
        if m:
            vals[m.group(1)] = json.loads(m.group(2))
    return vals


# ----------------------------------------------------------------------------- mesh helpers
def load_tm(path):
    t = trimesh.load(str(path), force="mesh")
    t.merge_vertices()
    return t


def to_mf(t):
    mf = m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(t.vertices, dtype=np.float32),
                               tri_verts=np.asarray(t.faces, dtype=np.uint32)))
    if mf.status() != m3d.Error.NoError:
        raise RuntimeError(f"not a manifold: {mf.status()}")
    return mf


def xf(mf, M):
    return mf.transform(np.asarray(M, dtype=float)[:3, :4])


def Mx(R, t=(0, 0, 0)):
    M = np.eye(4)
    M[:3, :3] = np.asarray(R, dtype=float)
    M[:3, 3] = t
    return M


def T(x, y, z):
    return Mx(np.eye(3), (x, y, z))


def Rz(deg):
    a = math.radians(deg)
    return Mx([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])


def Rx(deg):
    a = math.radians(deg)
    return Mx([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])


def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def pair(a, b, search=30.0):
    """(overlap mm3, min gap mm). Gap is 0 when they overlap or touch; gaps above `search` read as `search`."""
    ov = (a ^ b).volume()
    gap = a.min_gap(b, search)
    return ov, gap


BIG = 1e4


def clip(mf, x0=-BIG, x1=BIG, y0=-BIG, y1=BIG, z0=-BIG, z1=BIG):
    return mf ^ box(x0, x1, y0, y1, z0, z1)


# ----------------------------------------------------------------------------- report
class Report:
    def __init__(self):
        self.lines, self.fails = [], 0

    def __call__(self, ok, text):
        self.lines.append(f"  [{'ok' if ok else 'FAIL'}] {text}")
        if not ok:
            self.fails += 1
        print(self.lines[-1], flush=True)

    def head(self, text):
        self.lines.append(f"\n{text}")
        print(self.lines[-1], flush=True)


# ----------------------------------------------------------------------------- printability
def overhangs(t):
    """Downward faces flatter than 45 deg that are not on the bed, as connected patches:
    returns [(area mm2, width mm, long span mm, z)] where width = 2 x area / boundary length
    (a strip's width, a ring's radial width). Narrow patches are short ledges or bridges over
    holes and print fine; a patch wider than about 12 mm would need support."""
    lim = math.cos(math.radians(45.0)) + 0.02
    n, c = t.face_normals, t.triangles_center
    bad = set(np.where((n[:, 2] < -lim) & (c[:, 2] > 0.3))[0].tolist())
    if not bad:
        return []
    g = nx.Graph()
    g.add_nodes_from(bad)
    for a, b in t.face_adjacency:
        if a in bad and b in bad:
            g.add_edge(a, b)
    out = []
    for comp in nx.connected_components(g):
        idx = np.array(list(comp))
        pts = t.triangles[idx].reshape(-1, 3)
        span = np.ptp(pts[:, :2], axis=0)
        edges = np.sort(t.faces[idx][:, [[0, 1], [1, 2], [2, 0]]].reshape(-1, 2), axis=1)
        uniq, cnt = np.unique(edges, axis=0, return_counts=True)
        rim = uniq[cnt == 1]
        perim = float(np.linalg.norm(t.vertices[rim[:, 0]] - t.vertices[rim[:, 1]], axis=1).sum()) or 1.0
        area = float(t.area_faces[idx].sum())
        out.append((area, 2 * area / perim, float(max(span)), float(pts[:, 2].min()), bridge_halfspan(t, idx, comp)))
    return sorted(out, key=lambda o: o[0], reverse=True)


def bridge_halfspan(t, idx, comp):
    """For a flat downward patch: the largest distance (in plan) from any point of it to an edge
    that has a wall going DOWN from it (an anchor the slicer can bridge from). A flat patch held
    by walls on both sides of a 16 mm gap gives 8. None if the patch is not flat or has no anchor."""
    if (t.face_normals[idx][:, 2] > -0.99).any():
        return None
    fa, fe = t.face_adjacency, t.face_adjacency_edges
    inside = np.isin(fa, idx)
    rim = inside[:, 0] ^ inside[:, 1]
    anchors = []
    for (a, b), e in zip(fa[rim], fe[rim]):
        other = b if a in comp else a
        p0, p1 = t.vertices[e[0]], t.vertices[e[1]]
        if t.triangles_center[other][2] < min(p0[2], p1[2]) - 0.05:      # the neighbour face hangs below the edge: a wall
            anchors.append((p0[:2], p1[:2]))
    if not anchors:
        return None
    A0 = np.array([a for a, _ in anchors]); A1 = np.array([b for _, b in anchors])
    d = A1 - A0
    dd = np.maximum((d * d).sum(1), 1e-12)
    k = 8
    w = np.array([(i / k, j / k) for i in range(k + 1) for j in range(k + 1 - i)])
    tri = t.triangles[idx][:, :, :2]
    pts = (tri[:, 0, None] * (1 - w[:, 0] - w[:, 1])[None, :, None] + tri[:, 1, None] * w[None, :, 0, None]
           + tri[:, 2, None] * w[None, :, 1, None]).reshape(-1, 2)
    worst = 0.0
    for i in range(0, len(pts), 2000):
        q = pts[i:i + 2000]
        u = np.clip(((q[:, None, :] - A0[None]) * d[None]).sum(2) / dd[None], 0, 1)
        dist = np.linalg.norm(A0[None] + u[..., None] * d[None] - q[:, None, :], axis=2).min(1)
        worst = max(worst, float(dist.max()))
    return worst


def islands(mf, step=0.2, reach=0.6):
    """Slice components that rest on nothing (any body) in the slices up to `reach` mm below: material
    that would start printing in mid-air. A print-in-place z gap of up to ~0.6 mm above another body
    (2-3 layers of air, like a support interface) counts as resting on it."""
    bb = mf.bounding_box()
    hist = [mf.slice(bb[2] + 0.05)]
    z, found = bb[2] + 0.15, []
    nback = int(round(reach / step))
    while z < bb[5] - 0.05:
        cs = mf.slice(z)
        below = hist[0]
        for h in hist[1:]:
            below = below + h
        for comp in cs.decompose():
            if comp.area() > 0.05 and (comp ^ below).area() < 1e-3:
                found.append((round(z, 2), round(comp.area(), 1)))
        hist = (hist + [cs])[-nback:]
        z += step
    return found


def clean_export(t, path):
    """export, then re-read the file as the slicer will; only if float32 rounding broke it,
    drop the faces that collapsed (zero-area slivers that close a seam must stay)"""
    t.export(path)
    e = trimesh.load(str(path), force="mesh")
    e.merge_vertices()
    if e.is_watertight:
        return e
    e.update_faces(e.nondegenerate_faces(height=1e-6))
    e.remove_unreferenced_vertices()
    e.merge_vertices()
    e.export(path)
    e = trimesh.load(str(path), force="mesh")
    e.merge_vertices()
    return e


# ----------------------------------------------------------------------------- per-part checks
def part_qty(V):
    """quantities that follow the parameters"""
    n = int(V["seg_count"])
    return {"chute_segment": n, "hex_coupler": n + 2, "ring_sleeve": n + 1, "post_lower": int(V["post_n"]),
            "pin3": 13 + int(V["post_n"])}


BRIDGE_OK = {"trap": 70.0}      # documented exception (docs/03): the 66 mm bridge over the top of the drop slot


def check_parts(rep, rendered, V):
    rep.head("PARTS (render, watertight, bodies, print-in-place gap, islands, overhangs, bed fit, filament)")
    total = 0.0
    rows = []
    qmap = part_qty(V)
    for name, qty, walls, infill, nbodies, turn, desc in PARTS:
        qty = qmap.get(name, qty)
        path = RAW / f"{name}.stl"
        ok_r, warn = rendered.get(name, (path.exists(), []))
        if not path.exists():
            rep(False, f"{name}: no STL ({'; '.join(warn)[:200]})")
            continue
        t = load_tm(path)
        bodies = t.split(only_watertight=False)
        problems = []
        if not ok_r:
            problems.append("render warnings: " + "; ".join(warn)[:200])
        if not t.is_watertight:
            problems.append("not watertight")
        if len(bodies) != nbodies:
            problems.append(f"{len(bodies)} bodies, expected {nbodies}")
        gap_txt = ""
        if nbodies > 1 and len(bodies) == nbodies:
            mfs = [to_mf(b) for b in bodies]
            gaps = [mfs[i].min_gap(mfs[j], 5.0) for i in range(len(mfs)) for j in range(i + 1, len(mfs))]
            g = min(gaps)
            gap_txt = f", body gap {g:.2f}"
            if g < 0.30:
                problems.append(f"print-in-place gap {g:.2f} < 0.30")
        isl = islands(to_mf(t))
        if isl:
            problems.append(f"{len(isl)} slice(s) start in mid-air, first at z {isl[0][0]} ({isl[0][1]} mm2)")
        if turn:
            t.apply_transform(Rz(45))
        t.apply_translation([-(t.bounds[0][0] + t.bounds[1][0]) / 2, -(t.bounds[0][1] + t.bounds[1][1]) / 2, -t.bounds[0][2]])
        e = clean_export(t, OUT / f"{name}.stl")
        if not e.is_watertight or len(e.split(only_watertight=False)) != nbodies:
            problems.append(f"exported file: watertight {e.is_watertight}, {len(e.split(only_watertight=False))} bodies")
        ext = t.bounds[1] - t.bounds[0]
        if max(ext[0], ext[1]) > BED or ext[2] > BED:
            problems.append(f"bbox {ext.round(1).tolist()} exceeds {BED}")
        if t.bounds[0][2] < -0.01:
            problems.append("below the bed")
        oh = [o for o in overhangs(load_tm(RAW / f"{name}.stl")) if o[0] > 4.0]
        bridges = [o for o in oh if o[1] > 12.0 and o[4] is not None and o[4] <= 10.0]   # flat, walls on both sides, span <= 20 mm
        wide = [o for o in oh if o[1] > 12.0 and o not in bridges]
        longest = max((2 * o[4] for o in oh if o[4] is not None), default=0.0)
        if longest > BRIDGE_OK.get(name, 25.0):
            problems.append(f"flat bridge {longest:.0f} mm long (allowed {BRIDGE_OK.get(name, 25.0):.0f})")
        if wide:
            problems.append("needs support: " + "; ".join(f"{a:.0f} mm2 {s0:.0f}x{s1:.0f} mm at z {z:.0f}" for a, s0, s1, z, _ in wide[:3]))
        oh_txt = f", overhangs ok (widest {max((o[1] for o in oh if o not in bridges), default=0):.1f} mm)" if not wide else ""
        if bridges and not wide:
            oh_txt += f", flat bridges up to {2 * max(o[4] for o in bridges):.0f} mm span"
        shell = min(t.area * walls * 0.42, t.volume)            # every surface gets `walls` perimeters / skins
        grams = (shell + max(0.0, t.volume - shell) * infill / 100) / 1000 * PLA
        if name != "test_coupon":
            total += grams * qty
        rows.append((name, qty, grams, ext, walls, infill, desc, turn))
        rep(not problems, f"{name} x{qty}: {ext[0]:.0f}x{ext[1]:.0f}x{ext[2]:.0f} mm{', turned 45' if turn else ''}{gap_txt}{oh_txt},"
                          f" ~{grams:.0f} g each{'; ' + '; '.join(problems) if problems else ''}")
    rep.head(f"FILAMENT ESTIMATE: about {total/1000:.2f} kg for one machine with the listed walls/infill"
             f" (an estimate; the slicer gives the real figure; add 10-15 % for test prints and waste)")
    md = ["| Part (STL) | Qty | Size on the bed, mm | Walls | Infill | ~g each | What it is |", "|---|---|---|---|---|---|---|"]
    for name, qty, grams, ext, walls, infill, desc, turn in rows:
        md.append(f"| `{name}` | {qty} | {ext[0]:.0f} x {ext[1]:.0f} x {ext[2]:.0f}{' (diagonal)' if turn else ''} | {walls} |"
                  f" {infill} % | {grams:.0f} | {desc} |")
    md.append(f"\nFilament for one machine (test coupon excluded): **about {total/1000:.2f} kg** (estimate from the meshes;"
              f" your slicer gives the real number).")
    (HERE / "parts-table.md").write_text("\n".join(md) + "\n")
    return rows


# ----------------------------------------------------------------------------- assembly
class Asm:
    def __init__(self, rep, V):
        self.rep, self.V, self.cache = rep, V, {}

    def mf(self, name):
        if name not in self.cache:
            self.cache[name] = to_mf(load_tm(RAW / f"{name}.stl"))
        return self.cache[name]

    def bodies(self, name):
        """split a print-in-place STL into its bodies, largest first"""
        key = name + "#bodies"
        if key not in self.cache:
            t = load_tm(RAW / f"{name}.stl")
            bs = sorted(t.split(only_watertight=False), key=lambda b: -abs(b.volume))
            self.cache[key] = [to_mf(b) for b in bs]
        return self.cache[key]

    def check(self, label, a, b, mode, need=0.0):
        ov, gap = pair(a, b, max(30.0, need + 20.0))
        if mode == "touch":
            ok = ov < 1.0
            self.rep(ok, f"{label}: touching faces, overlap {ov:.2f} mm3 (must be ~0), gap {gap:.2f}")
        elif mode == "fit":
            ok = ov < 0.5 and abs(gap - need) <= 0.1
            self.rep(ok, f"{label}: slip fit gap {gap:.2f} mm (designed {need:.2f}), overlap {ov:.2f} mm3")
        else:
            ok = ov < 0.01 and gap >= need
            self.rep(ok, f"{label}: clearance {gap:.2f} mm (need >= {need:g}){'' if ov < 0.01 else f', OVERLAP {ov:.1f} mm3'}")
        return ok


def line_M(V, u0):
    """line part print frame (x = Y, y = n, z = u - u0) -> head frame"""
    c, s = math.cos(math.radians(V["ua"])), math.sin(math.radians(V["ua"]))
    return Mx([[0, -s, c], [1, 0, 0], [0, c, s]], (u0 * c, 0, u0 * s))


def head_assembly(A, V):
    c, s = math.cos(math.radians(V["ua"])), math.sin(math.radians(V["ua"]))
    P = {}
    P["A"] = xf(A.mf("head_side_a"), Mx([[1, 0, 0], [0, 0, -1], [0, 1, 0]], (0, -V["side_in"], 0)))
    P["B"] = xf(A.mf("head_side_b"), Mx([[1, 0, 0], [0, 0, 1], [0, -1, 0]], (0, V["side_in"], 0)))
    P["roller"] = xf(A.mf("drive_roller"), Mx([[-s, c, 0], [0, 0, 1], [c, s, 0]], (0, -V["half_w"], 0)))
    P["pin"] = xf(A.mf("drive_pin"), Mx([[1, 0, 0], [0, 0, 1], [0, -1, 0]], (0, -V["half_w"] - V["drv_jlen"] - 2, 0)))
    gb = A.bodies("gearbox")                       # [rotor, body]
    Mg = Mx([[-s, 0, -c], [0, 1, 0], [c, 0, -s]], (V["gb_top_s"] * c, V["Y_c"], V["gb_top_s"] * s))
    P["rotor"], P["gbody"] = xf(gb[0], Mg), xf(gb[1], Mg)
    P["trap"] = xf(A.mf("trap"), line_M(V, V["tp_u0"]))
    bolts = m3d.Manifold()
    for hx, hz in V["gb_holes"]:
        bolts = bolts + xf(A.mf("bolt8_28"), Mx([[1, 0, 0], [0, 0, -1], [0, 1, 0]], (hx, V["side_out"] + 8 + 5, hz)))
        bolts = bolts + xf(A.mf("nut8"), Mx([[1, 0, 0], [0, 0, -1], [0, 1, 0]], (hx, V["side_in"], hz)))
    P["gbolts"] = bolts
    seg = A.bodies("chute_segment")                # [static, shaft]
    P["seg1"] = xf(seg[0], line_M(V, V["gb_top_s"]))
    P["seg1_shaft"] = xf(seg[1], line_M(V, V["gb_top_s"]))
    P["seg2"] = xf(seg[0], line_M(V, V["gb_top_s"] + V["seg_len"]))
    P["sleeve0"] = xf(A.mf("ring_sleeve"), line_M(V, V["gb_top_s"] - V["slv_len"] / 2) @ T(V["Y_c"], 0, 0))
    for i, xfoot in enumerate(V["h_feet"]):
        P[f"foot{i}"] = xf(A.mf("foot"), T(xfoot, 0, V["hz_g"]))
    # belt around the drive roller and the space the candy needs above it
    r0, bt, hw = V["drv_rs"], V["belt_t"], V["belt_w"] / 2
    wrap = (m3d.Manifold.cylinder(2 * hw, r0 + bt, r0 + bt, 128) - m3d.Manifold.cylinder(2 * hw + 2, r0, r0, 128).translate([0, 0, -1]))
    wrap = wrap.translate([0, 0, -hw]).rotate([90, 0, 0]) ^ box(0, 100, -hw, hw, -100, 100)
    P["belt"] = box(-400, 0, -hw, hw, r0, r0 + bt) + box(-400, 0, -hw, hw, -r0 - bt, -r0) + wrap
    P["candy"] = box(-400, -1, -hw + 3, hw - 3, r0 + bt + 0.5, r0 + bt + 28)
    return P


def socket_lock(A, V, lo_name, lo, lo_u0, up_name, up, up_u0):
    """the plain end of the lower piece must sit deep in the upper piece's socket and stop it turning"""
    if not isinstance(lo, m3d.Manifold) or lo_u0 is None:
        return
    lo_h = lo if lo_name == "trap" else xf(lo, line_M(V, lo_u0))
    zone = xf(box(-V["tr_in"] - 3, V["tr_in"] + 3, V["fl_bot"] - 3, V["wl_top"] + 1, 0, V["sock_len"]), line_M(V, up_u0))
    vol = (lo_h ^ zone).volume()
    A.rep(vol >= 1000, f"{lo_name} plain end inside the {up_name} socket: {vol:.0f} mm3 (need >= 1000)")
    turned = []
    for deg in (-0.5, 0.5):
        Rt = T(V["Y_c"], 0, 0) @ Rz(deg) @ T(-V["Y_c"], 0, 0)
        turned.append((xf(up, line_M(V, up_u0) @ Rt) ^ lo_h).volume())
    A.rep(min(turned) > 0.2, f"{up_name} cannot turn on the shaft: turning it 0.5 deg either way collides ({min(turned):.1f} mm3)")


def coupler_bite(A, V):
    """a hex coupler must grip: turned 15 deg inside a shaft socket it has to collide hard"""
    cp = A.mf("hex_coupler")
    shaft = A.bodies("chute_segment")[1]
    rotor = A.bodies("gearbox")[0]
    for nm, body, axis in (("segment shaft", shaft, (V["Y_c"], 0)), ("crown rotor", rotor, (0, 0))):
        base = (xf(cp, T(axis[0], axis[1], 0.5)) ^ body).volume()
        bite = (xf(cp, T(axis[0], axis[1], 0.5) @ Rz(15)) ^ body).volume() - base
        A.rep(bite >= 20, f"hex coupler bites in the {nm} socket: turned 15 deg it overlaps {bite:.0f} mm3 (need >= 20)")


def check_head(rep, A, V):
    rep.head("HEAD MODULE (drive roller, frames, gearbox, trap, first chute segment), assembled")
    P = head_assembly(A, V)
    k = A.check
    k("drive roller journal in frame B slot", P["roller"], P["B"], "fit", 0.30)
    k("drive roller vs frame A", P["roller"], P["A"], "clear", 0.9)
    k("drive pin journal in frame A", P["pin"], P["A"], "fit", 0.30)
    k("gearbox slab on frame B", P["gbody"], P["B"], "touch")
    k("crown gear vs drive roller (pinion mesh, cone, flanges)", P["rotor"], P["roller"], "clear", 0.15)
    k("gearbox housing vs drive roller", P["gbody"], P["roller"], "clear", 1.0)
    k("crown gear vs frame B", P["rotor"], P["B"], "clear", 1.0)
    for f in ("A", "B"):
        k(f"trap vs frame {f} (ledge over the guard bar)", P["trap"], P[f], "clear", 0.2)
    k("trap vs drive roller", P["trap"], P["roller"], "clear", 5.0)
    k("gearbox bolts + nuts vs drive roller, belt, crown gear, trap", P["gbolts"], P["roller"] + P["belt"] + P["rotor"] + P["trap"], "clear", 1.0)
    k("gearbox bolt nuts seat on frame B", P["gbolts"], P["B"], "touch")
    k("gearbox bolts pass through the gearbox slab (heads seat on it)", P["gbolts"], P["gbody"], "touch")
    socket_lock(A, V, "trap", P["trap"], V["tp_u0"], "segment 1", A.bodies("chute_segment")[0], V["gb_top_s"])
    socket_lock(A, V, "segment 1", A.bodies("chute_segment")[0], V["gb_top_s"], "segment 2", A.bodies("chute_segment")[0], V["gb_top_s"] + V["seg_len"])
    # candy path through the trap: a 30 mm tall, 60 mm wide piece sliding along the floor must not hit anything
    lane = xf(box(-V["tr_in"] + 3, V["tr_in"] - 3, V["fl_top"] + 0.3, V["fl_top"] + 30, 2.5, 160), line_M(V, V["tp_u0"]))
    k("30 mm candy passes under the trap lid and into the slot", lane, P["trap"], "clear", 0.2)
    coupler_bite(A, V)
    k("trap vs gearbox", P["trap"], P["gbody"] + P["rotor"], "clear", 3.0)
    k("trap plain end in segment 1 socket", P["trap"], P["seg1"], "fit", 0.30)
    k("segment 1 ring on the gearbox housing", P["seg1"], P["gbody"], "touch")
    k("segment 1 shaft end on the crown rotor end", P["seg1_shaft"], P["rotor"], "touch")
    k("ring sleeve in gearbox + segment 1 counterbores", P["sleeve0"], P["gbody"] + P["seg1"], "fit", 0.20)
    k("ring sleeve vs shafts", P["sleeve0"], P["rotor"] + P["seg1_shaft"], "clear", 0.5)
    for f in ("A", "B"):
        k(f"segment 1 vs frame {f}", P["seg1"], P[f], "clear", 2.0)
    k("segment 1 vs segment 2 (stacked)", P["seg1"], P["seg2"], "touch")
    for i in (0, 1):
        for f in ("A", "B"):
            k(f"foot {i} cheeks around frame {f} tab", P[f"foot{i}"], P[f], "fit", 0.20)
    belt_others = ["A", "B", "trap", "gbody", "rotor", "foot0", "foot1", "seg1", "pin"]
    k("belt vs frames, trap, gearbox, feet", P["belt"], sum((P[n] for n in belt_others[1:]), P[belt_others[0]]), "clear", 1.0)
    k("candy space above the belt vs everything", P["candy"],
      sum((P[n] for n in ["B", "trap", "gbody", "rotor", "foot0", "foot1", "seg1", "roller"]), P["A"]), "clear", 1.0)
    zmin = min(P[n].bounding_box()[2] for n in ("A", "B", "roller", "gbody", "rotor", "trap", "seg1"))
    rep(zmin >= V["hz_g"] + 2, f"nothing but the feet reaches the ground: lowest part {zmin - V['hz_g']:.0f} mm above the lawn")
    return P


def tail_assembly(A, V, Xa):
    P = {}
    so, tp, sy, hw = V["side_out"], V["tb_pad"], V["scr_y"], V["half_w"]
    P["L"] = xf(A.mf("tail_side_l"), Mx([[1, 0, 0], [0, 0, -1], [0, 1, 0]], (0, -V["side_in"], 0)))
    P["R"] = xf(A.mf("tail_side_r"), Mx([[1, 0, 0], [0, 0, 1], [0, -1, 0]], (0, V["side_in"], 0)))
    tr = A.bodies("tail_roller")                         # [roller, axle]
    Mr = Mx([[1, 0, 0], [0, 0, 1], [0, -1, 0]], (Xa, -hw, 0))
    P["roller"], P["axle"] = xf(tr[0], Mr), xf(tr[1], Mr)
    P["blockL"] = xf(A.mf("takeup_block"), Mx([[1, 0, 0], [0, 0, 1], [0, -1, 0]], (Xa, -(so + tp), 0)))
    P["blockR"] = xf(A.mf("takeup_block"), Mx([[1, 0, 0], [0, 0, -1], [0, 1, 0]], (Xa, so + tp, 0)))
    for side, sg in (("L", -1), ("R", 1)):
        P["nut" + side] = xf(A.mf("takeup_nut"), Mx([[0, 0, 1], [1, 0, 0], [0, 1, 0]], (Xa - V["tn_t"] / 2, sg * (so + sy), 0)))
        P["screw" + side] = xf(A.mf("takeup_screw"), Mx([[0, 0, 1], [1, 0, 0], [0, 1, 0]], (V["t_rear"] - 10, sg * (so + sy), 0)))
    P["skidR"] = xf(A.mf("skid_r"), T(0, 0, V["tz_g"]))
    P["skidL"] = xf(A.mf("skid_l"), T(0, 0, V["tz_g"]))
    P["foot"] = xf(A.mf("foot"), T(V["t_tabs"][0], 0, V["tz_g"]))
    r0, bt = V["tail_r"] + V["roll_crown"], V["belt_t"]
    wrap = (m3d.Manifold.cylinder(2 * hw, r0 + bt, r0 + bt, 128) - m3d.Manifold.cylinder(2 * hw + 2, r0, r0, 128).translate([0, 0, -1]))
    wrap = wrap.translate([0, 0, -hw]).rotate([90, 0, 0]).translate([Xa, 0, 0]) ^ box(Xa - 100, Xa, -hw, hw, -100, 100)
    P["belt"] = box(Xa, 600, -hw, hw, r0, r0 + bt) + box(Xa, 600, -hw, hw, -r0 - bt, -r0) + wrap
    P["basket"] = box(-350, -8, -150, 150, V["tz_g"], V["tz_g"] + 6 * IN)
    return P


def check_tail(rep, A, V):
    for Xa, tag in ((V["tu_in"], "take-up fully in"), (0, "take-up middle"), (V["tu_out"], "take-up fully out")):
        rep.head(f"TAIL MODULE, assembled, {tag} (axle X = {Xa})")
        P = tail_assembly(A, V, Xa)
        k = A.check
        for s in ("L", "R"):
            k(f"take-up block {s} in its frame window", P["block" + s], P[s], "fit", 0.20)
            k(f"take-up block {s} boss grips the axle square end", P["block" + s], P["axle"], "fit", 0.20)
            k(f"take-up block {s} boss vs roller counterbore", P["block" + s], P["roller"], "clear", 0.4)
            k(f"square nut {s} in the block pocket", P["nut" + s], P["block" + s], "fit", 0.20)
            k(f"take-up screw {s} knob bears on the frame lug", clip(P["screw" + s], x1=V["t_rear"] + 0.5), P[s], "touch")
            k(f"take-up screw {s} thread vs frame lug hole and block holes", clip(P["screw" + s], x0=V["t_rear"] + 0.5), P[s] + P["block" + s], "clear", 0.3)
            k(f"skid {s} cheeks around frame {s} tabs", P["skid" + s], P[s], "fit", 0.20)
            k(f"rear foot cheeks around frame {s} tab", P["foot"], P[s], "fit", 0.20)
        k("tail roller vs frames", P["roller"], P["L"] + P["R"], "clear", 0.9)
        others = P["L"] + P["R"] + P["blockL"] + P["blockR"] + P["screwL"] + P["screwR"] + P["nutL"] + P["nutR"]
        k("belt vs frames, blocks, screws", P["belt"], others + P["foot"] + P["skidL"] + P["skidR"], "clear", 1.0)
        k("basket space under the roller vs tail parts", P["basket"], others + P["foot"] + P["skidL"] + P["skidR"], "clear", 2.0)


def check_station(rep, A, V):
    rep.head("STATION (stake + bracket + 2 wheels), assembled")
    hw = V["half_w"]
    Mw = lambda z: Mx([[1, 0, 0], [0, 0, 1], [0, -1, 0]], (0, -hw, z))
    wu = A.bodies("wheel_unit")                    # [wheel, axle]
    br = xf(A.mf("station_bracket"), Mx([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], (0, V["st_y0"], 0)))
    c0 = V["sk_c"]
    st = xf(A.mf("stake_1"), Mx([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], (c0, -c0 + V["st_y0"] + V["spig"] / 2, -V["sk_hd"] + V["st_bot"])))
    k = A.check
    belt = box(-300, 300, -V["belt_w"] / 2, V["belt_w"] / 2, -V["belt_t"], 0) + \
        box(-300, 300, -V["belt_w"] / 2, V["belt_w"] / 2, V["st_ret_top"], V["st_ret_top"] + V["belt_t"])
    for z, nm in ((V["st_carry_z"], "carry"), (V["st_ret_z"], "return")):
        wheel, axle = xf(wu[0], Mw(z)), xf(wu[1], Mw(z))
        k(f"{nm} wheel peg in the bracket (0.1 per side; collar 0.15 from the face)", axle, br, "fit", 0.10)
        k(f"{nm} wheel (spinning part) vs bracket", wheel, br, "clear", 0.4)
        k(f"{nm} wheel vs stake", wheel, st, "clear", 2.0)
    k("bracket sits on the stake head", br, st, "touch")
    k("bracket spigot in the stake socket", clip(br, z1=V["st_bot"] - 0.5), st, "fit", 0.20)
    k("belt (both runs) vs bracket and stake", belt, br + st, "clear", 1.0)
    rep(True, f"carry run rides on the wheel top at belt-top Z=0; return run at Z={V['st_ret_top']:.0f} mm")


def stand_place(A, V, u_ch):
    """porch stand transforms: upper post (Mu), lower posts top to bottom (Mls), the tray placed the way
    round that keeps it on the porch, and the upper post's top spigot end (x)"""
    S = line_M(V, u_ch) @ T(*V["st_q"]) @ Rx(90 + V["aw"])         # socket frame: +z straight down
    hd, c0, sp = V["sk_hd"], V["sk_c"], V["spig"] / 2
    L_top = V["post_ub"] + V["spig_len"]
    # post frame: x along the post (up), spigots on the axis (spig/2, spig/2), head sockets on (sk_c, sk_c)
    up_to_sock = Mx([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], (0, 0, V["st_len"] - V["spig_len"] + L_top)) @ T(0, -sp, -sp)
    Mu = S @ Rz(45) @ up_to_sock
    Mls = [Mu @ T(-(V["post_b"] + V["ph_len"] + V["pu_gap"]), sp - c0, sp - c0)]   # nominal height
    for _ in range(int(V["post_n"]) - 1):
        Mls.append(Mls[-1] @ T(-(V["post_b"] + V["ph_len"]), sp - c0, sp - c0))
    socket_from_lo = Mx([[0, 1, 0], [0, 0, 1], [1, 0, 0]], (0, 0, hd)) @ T(0, -sp, -sp)   # lower post -> tray socket axes
    best = None
    for kq in range(4):                                         # the tray can sit 4 ways round; use the one that keeps it on the porch
        tr = xf(A.mf("stand_tray"), Mls[-1] @ np.linalg.inv(Rz(45 + 90 * kq) @ socket_from_lo))
        if best is None or tr.bounding_box()[0] > best.bounding_box()[0]:
            best = tr
    return Mu, Mls, best, L_top


def check_line(rep, A, V):
    rep.head("LINE (chute segments, crank head, crank arm, porch stand), assembled")
    N = int(V["seg_count"])
    k = A.check
    seg = A.bodies("chute_segment")
    u_ch = V["gb_top_s"] + N * V["seg_len"]
    sN = xf(seg[0], line_M(V, u_ch - V["seg_len"]))
    sN_shaft = xf(seg[1], line_M(V, u_ch - V["seg_len"]))
    ch = A.bodies("crank_head")                   # [static, shaft]
    chs, chf = xf(ch[0], line_M(V, u_ch)), xf(ch[1], line_M(V, u_ch))
    k("segment N plain end in the crank head socket", clip(sN, y0=-50, y1=50), clip(chs, y0=-50, y1=50), "fit", 0.30)
    socket_lock(A, V, f"segment {N}", seg[0], u_ch - V["seg_len"], "crank head", ch[0], u_ch)
    lane = xf(box(-V["tr_in"] + 3, V["tr_in"] - 3, V["fl_top"] + 0.3, V["fl_top"] + 18, 2.5, V["crank_head_len"] - 60), line_M(V, u_ch))
    k("candy channel through the crank head is clear (stand socket, web plate)", lane, chs, "clear", 0.2)
    lane2 = xf(box(-V["tr_in"] + 3, V["tr_in"] - 3, V["fl_top"] + 0.3, V["fl_top"] + 18, 2.5, V["seg_len"] + V["plain_ext"] - 3), line_M(V, u_ch - V["seg_len"]))
    k("candy channel through a chute segment and its joint is clear", lane2, sN + chs, "clear", 0.2)
    k("segment N ring on the crank head ring", sN, chs, "touch")
    k("segment N shaft end on the crank shaft end", sN_shaft, chf, "touch")
    # hex coupler in a shaft socket (same frame as the shaft)
    cp = xf(A.mf("hex_coupler"), line_M(V, u_ch - 11.5) @ T(V["Y_c"], 0, 0))
    k("hex coupler in the shaft sockets", cp, sN_shaft + chf, "fit", 0.20)
    # crank arm on the square drive, then swept around the shaft against the static crank head
    arm = A.bodies("crank_arm")                    # [arm+axle, grip] (order by volume)
    arm_all = arm[0] + arm[1]
    z_hub = V["crank_head_len"] + V["sq_z"][0]
    k("crank arm hub on the square drive (rests on the shaft shoulder)", xf(arm_all, line_M(V, u_ch) @ T(V["Y_c"], 0, z_hub)), chf, "touch")
    worst = 1e9
    for deg in range(0, 360, 15):
        g = xf(arm_all, line_M(V, u_ch) @ T(V["Y_c"], 0, z_hub) @ Rz(deg)).min_gap(chs, 50)
        worst = min(worst, g)
    rep(worst >= 3.0, f"crank arm swept a full turn (15 deg steps) vs crank head and funnel: closest {worst:.1f} mm (need >= 3)")
    # porch stand: tray -> lower post(s) -> adjustable upper post -> crank head socket
    Mu, Mls, tray, L_top = stand_place(A, V, u_ch)
    hd, c0, sp = V["sk_hd"], V["sk_c"], V["spig"] / 2
    pu, pl = A.mf("post_upper"), A.mf("post_lower")
    k("upper post top spigot in the crank head socket", xf(clip(pu, x0=L_top - V["spig_len"] + 0.5), Mu), chs, "fit", 0.20)
    k("upper post shoulder bears on the crank head socket", xf(pu, Mu), chs, "touch")
    post_u = xf(pu, Mu)
    lows = [xf(pl, M) for M in Mls]
    k("upper post long spigot in the lower post's deep socket", xf(clip(pu, x1=-0.5), Mu), lows[0], "fit", 0.20)
    for i in range(1, len(Mls)):
        k(f"lower post {i} spigot in lower post {i + 1}'s head socket", xf(clip(pl, x1=-0.5), Mls[i - 1]), lows[i], "fit", 0.20)
        k(f"lower post {i} rests on lower post {i + 1}'s head", lows[i - 1], lows[i], "touch")
    k("lowest post spigot in the tray socket", xf(clip(pl, x1=-0.5), Mls[-1]), tray, "fit", 0.20)
    k("lowest post rests on the tray socket", lows[-1], tray, "touch")
    post_l = lows[0]
    for lw in lows[1:]:
        post_l = post_l + lw
    # the locking pins go straight through their holes (pin modelled as a 3 mm rod along the post's z)
    rod = m3d.Manifold.cylinder(40, V["pin_d"] / 2, V["pin_d"] / 2, 24).translate([0, 0, -20])
    pins = [("crank head pin", Mu, L_top - 13, sp, post_u + chs),
            ("height pin (nominal hole)", Mls[0], V["post_b"] + V["ph_len"] - 15, c0, post_u + lows[0])]
    for i in range(1, len(Mls)):
        pins.append((f"pin between lower posts {i} and {i + 1}", Mls[i], V["post_b"] + V["ph_len"] - 15, c0, lows[i - 1] + lows[i]))
    pins.append(("tray pin", Mls[-1], -15, sp, lows[-1] + tray))
    for nm, M, x, y, others in pins:
        pin = xf(rod, M @ T(x, y, 0))
        k(f"{nm} passes through its holes", pin, others, "clear", 0.1)
    # with the height pin out the joint collapses pu_gap: the top spigot must drop clear of the crank head
    # socket, so the stand goes in under (and comes out from under) a crank head already on the line
    # worst case: the lowest height hole (porch highest), where the least spigot is left to slide in
    drop = V["pu_spig"] - V["pu_dmax"] - 0.5
    Mu_c = Mu @ T(-drop, 0, 0)
    low_hi = xf(pl, Mls[0] @ T(V["pu_dmax"] - (V["pu_spig"] - V["pu_gap"]), 0, 0))     # lower post up by 18 mm
    k(f"stand collapsed {drop:.1f} mm from the lowest height hole: upper post clears the crank head socket", xf(pu, Mu_c), chs, "clear", 3.0)
    k("stand collapsed: upper post's long spigot still runs free in the lower post", xf(pu, Mu_c), low_hi, "clear", 0.15)
    # static neighbours: the posts hang off the crank head socket (0.2 mm slip fit), so they move < 1 mm
    k("stand posts vs segment N and the crank shaft (static; socket play < 1 mm)", post_u + post_l, sN + chf, "clear", 2.0)
    worst = 1e9
    for deg in range(0, 360, 15):
        g = xf(arm_all, line_M(V, u_ch) @ T(V["Y_c"], 0, z_hub) @ Rz(deg)).min_gap(post_u + post_l, 50)
        worst = min(worst, g)
    rep(worst >= 3.0, f"crank arm swept a full turn (15 deg steps) vs the stand posts: closest {'over 50' if worst >= 50 else f'{worst:.1f}'} mm (need >= 3)")
    return tray


def check_site(rep, A, V, P_head, tray):
    """Line, head and porch stand against the steps (riser height ASSUMED 7 in until measured)."""
    rep.head(f"SITE: {V['site_risers']} risers x {V['site_rise']} in (ASSUMED), {V['site_run']} in run to the porch; drive axle {V['site_head_gap']} in before riser 1")
    b = math.radians(V["belt_deg"])
    axle_h = V["head_h"] - V["belt_t"] - V["drv_rs"]
    # world: origin on the lawn under the drive axle, x toward the porch, z up
    W = Mx([[math.cos(b), 0, -math.sin(b)], [0, 1, 0], [math.sin(b), 0, math.cos(b)]], (0, 0, axle_h))
    gap_x, run, rise, nr = V["site_head_gap"] * IN, V["site_run"] * IN, V["site_rise"] * IN, int(V["site_risers"])
    lawn_at = gap_x * math.tan(math.radians(5))
    porch_z = lawn_at + nr * rise
    treads = nr - 1                                         # same step model as the calculator
    steps = box(gap_x + run, gap_x + run + 900, -600, 600, -50, porch_z)
    for i in range(treads):
        x0 = gap_x + i * run / max(treads, 1)
        steps = steps + box(x0, gap_x + run, -600, 600, -50, lawn_at + (i + 1) * rise)
    N = int(V["seg_count"])
    seg = A.bodies("chute_segment")
    line = P_head["trap"] + P_head["seg1"]
    for i in range(1, N):
        line = line + xf(seg[0], line_M(V, V["gb_top_s"] + i * V["seg_len"]))
    line = line + xf(A.bodies("crank_head")[0], line_M(V, V["gb_top_s"] + N * V["seg_len"]))
    A.check("chute line vs the steps", xf(line, W), steps, "clear", 50.0)
    A.check("head module vs the first riser", xf(P_head["A"] + P_head["B"] + P_head["foot0"] + P_head["foot1"], W), steps, "clear", 20.0)
    tb = xf(tray, W).bounding_box()
    dz = tb[2] - porch_z
    rep(abs(dz) <= 5.0, f"porch stand tray bottom {dz:+.0f} mm from the porch floor (set stand_h = {V['stand_h'] + dz:.0f} to correct)")
    rep(tb[0] >= gap_x + run + 20, f"porch stand tray starts {(tb[0] - gap_x - run) / IN:.1f} in behind the porch edge (need >= 0.8 in)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", choices=["parts", "head", "tail", "station", "line", "site"])
    ap.add_argument("-j", type=int, default=3)
    a = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    rep = Report()
    key = src_hash()
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    names = [p[0] for p in PARTS]
    rendered = {}
    todo = [n for n in dict.fromkeys(names)]
    with ThreadPoolExecutor(a.j) as ex:
        for name, ok, warn in ex.map(lambda n: render_one(n, a.force, cache, key), todo):
            rendered[name] = (ok, warn)
            if ok:
                cache[name] = key
            print(f"  render {name}: {'ok' if ok else 'FAILED ' + '; '.join(warn)[:300]}", flush=True)
    CACHE.write_text(json.dumps(cache, indent=1))
    V = scad_values()
    if a.only in (None, "parts"):
        check_parts(rep, rendered, V)
    A = Asm(rep, V)
    P_head = None
    if a.only in (None, "head", "site"):
        P_head = head_assembly(A, V) if a.only == "site" else check_head(rep, A, V)
    if a.only in (None, "tail"):
        check_tail(rep, A, V)
    if a.only in (None, "station"):
        check_station(rep, A, V)
    tray = None
    if a.only in (None, "line", "site"):
        tray = check_line(rep, A, V)
    if a.only in (None, "site"):
        check_site(rep, A, V, P_head, tray)
    rep.head(f"RESULT: {'ALL CHECKS PASSED' if rep.fails == 0 else f'{rep.fails} CHECK(S) FAILED'}")
    (HERE / "check-report.txt").write_text("\n".join(rep.lines) + "\n")
    sys.exit(1 if rep.fails else 0)


if __name__ == "__main__":
    main()

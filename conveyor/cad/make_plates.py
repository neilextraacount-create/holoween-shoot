#!/usr/bin/env python3
"""Lay every printed part out on P2S build plates, by print settings, and write one 3MF per plate
(plates/NN_name.3mf) plus plates/plates.md (contents, settings, grams and time per plate).

Each plate holds parts that print with the same settings, so a plate needs one setting change in
the slicer at most. Parts keep the print orientation of their STL; they are only turned in 90 deg
steps about the vertical and shifted. Footprints are the parts' real silhouettes (not boxes), kept
6 mm apart, or 16 mm where the plate needs a 5 mm brim.

    python3 make_plates.py            # needs the STLs from check_parts.py; slices each plate to check it
    python3 make_plates.py --no-slice # layout only
"""
import argparse
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import trimesh
from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely.prepared import prep

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check_parts import PARTS, fill_doc, part_qty, scad_values   # noqa: E402

STL = HERE / "stl"
OUT = HERE.parent / "plates"
PROFILE = HERE / "p2s-check.ini"
BED = 256.0
MARGIN = 5.0                       # keep parts 5 mm in from the bed edge
GAP = 6.0                          # between parts
BRIM = 5.0

# print-settings groups: (title, walls, infill %, layer mm, brim)
GROUPS = {
    "coupon": ("Test coupon and test pieces", 3, 15, 0.20, False),
    "solid": ("Small parts, solid", 3, 100, 0.20, False),
    "solid_brim": ("Bolts, pins, couplers, take-up screws, solid", 3, 100, 0.20, True),
    "fine": ("Rollers and gearbox", 4, 15, 0.16, False),
    "frames": ("Frames, stakes, posts", 4, 30, 0.20, False),
    "frames_brim": ("Ground screws and wrench", 4, 30, 0.20, True),
    "line": ("Chute, crank head, trap", 4, 15, 0.20, True),
    "wheels": ("Station wheels", 4, 15, 0.20, True),
}
GROUP_OF = {"test_coupon": "coupon", "bolt8_28": "solid_brim", "takeup_screw": "solid_brim",
            "pin3": "solid_brim", "hex_coupler": "solid_brim",
            "drive_roller": "fine", "gearbox": "fine", "tail_roller": "fine",
            "ground_screw": "frames_brim", "gs_wrench": "frames_brim",
            "chute_segment": "line", "crank_head": "line", "trap": "line", "wheel_unit": "wheels"}
# the build order (docs/03): plates are printed in the order of the earliest module they serve
MODULE = {"test_coupon": 0,
          "drive_roller": 1, "drive_pin": 1, "head_side_a": 1, "head_side_b": 1, "gearbox": 1, "foot": 1,
          "bolt8_28": 1, "nut8": 1, "pin3": 1, "hex_coupler": 1, "ring_sleeve": 1,
          "stake_1": 2, "station_bracket": 2, "wheel_unit": 2, "stake_cap": 2,
          "tail_side_l": 3, "tail_side_r": 3, "tail_roller": 3, "takeup_block": 3, "takeup_nut": 3,
          "takeup_screw": 3, "skid_l": 3, "skid_r": 3, "spike": 3,
          "ground_screw": 4, "gs_wrench": 4, "washer50": 4,
          "stake_2": 5, "stake_3": 5, "stake_4": 5,
          "trap": 6, "chute_segment": 6, "crank_head": 6, "crank_arm": 6,
          "post_lower": 7, "post_upper": 7, "stand_tray": 7, "stand_shim": 7, "splice_template": 8}
TEST_PIECES = ["hex_coupler", "ring_sleeve", "bolt8_28", "stake_cap"]   # extra copies to try in the coupon
MODULE_NAME = ["test", "head", "station 1", "tail", "anchors", "stations 2-4", "chute line", "porch stand", "belt joint"]


def silhouette(mesh):
    """outline of the part seen from above (union of its projected faces), simplified"""
    tri = mesh.triangles[:, :, :2]
    u, v = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    keep = np.abs(u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0]) > 1e-6
    polys = [Polygon(t) for t in tri[keep]]
    if len(polys) > 60000:
        return Polygon(mesh.convex_hull.vertices[:, :2]).convex_hull
    return unary_union(polys).buffer(0.05).simplify(0.2)


class Plate:
    def __init__(self, group):
        self.group, self.items, self.shapes = group, [], []
        self.free = box(MARGIN, MARGIN, BED - MARGIN, BED - MARGIN)
        self.used = None

    def try_place(self, name, outline, pad):
        """bottom-left placement of the outline (grown by pad) in 90 deg steps; True if placed"""
        bed = prep(self.free)
        used = prep(self.used) if self.used is not None else None
        best = None
        for rot in (0, 90, 180, 270):
            shp = affinity.rotate(outline, rot, origin=(0, 0))
            grown = shp.buffer(pad, join_style=2)
            minx, miny, maxx, maxy = grown.bounds
            w, h = maxx - minx, maxy - miny
            if w > BED - 2 * MARGIN + 1e-6 or h > BED - 2 * MARGIN + 1e-6:
                continue
            for y in np.arange(MARGIN, BED - MARGIN - h + 1e-6, 2.0):
                hit = None
                for x in np.arange(MARGIN, BED - MARGIN - w + 1e-6, 2.0):
                    cand = affinity.translate(grown, x - minx, y - miny)
                    if bed.contains(cand) and (used is None or not used.intersects(cand)):
                        hit = (y, x, rot, x - minx, y - miny)
                        break
                if hit:
                    if best is None or (hit[0], hit[1]) < (best[0], best[1]):
                        best = hit
                    break
        if best is None:
            return False
        _, _, rot, dx, dy = best
        placed = affinity.translate(affinity.rotate(outline, rot, origin=(0, 0)).buffer(pad, join_style=2), dx, dy)
        self.used = placed if self.used is None else self.used.union(placed)
        self.items.append((name, rot, dx, dy))
        return True


def write_3mf(path, plate, meshes):
    """plain 3MF (core spec): one object per part type, one build item per copy, in bed coordinates"""
    names = sorted({n for n, *_ in plate.items})
    ids = {n: i + 1 for i, n in enumerate(names)}
    res = []
    for n in names:
        m = meshes[n]
        v = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in m.vertices)
        t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
        res.append(f'<object id="{ids[n]}" name="{n}" type="model"><mesh><vertices>{v}</vertices>'
                   f'<triangles>{t}</triangles></mesh></object>')
    items = []
    for n, rot, dx, dy in plate.items:
        a = np.radians(rot)
        c, s = np.cos(a), np.sin(a)
        items.append(f'<item objectid="{ids[n]}" transform="{c:.6f} {s:.6f} 0 {-s:.6f} {c:.6f} 0 0 0 1 {dx:.4f} {dy:.4f} 0"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             '<metadata name="Application">holoween-shoot make_plates.py</metadata>'
             f'<resources>{"".join(res)}</resources><build>{"".join(items)}</build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


def slice_plate(path, group, gcode):
    _t, walls, infill, layer, brim = GROUPS[group]
    cmd = ["prusa-slicer", "--load", str(PROFILE), "--dont-arrange", "--perimeters", str(walls),
           "--fill-density", f"{infill}%", "--fill-pattern", "rectilinear" if infill >= 100 else "gyroid",
           "--layer-height", str(layer), "--brim-width", str(BRIM if brim else 0),
           "--export-gcode", "-o", str(gcode), str(path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    log = r.stdout + r.stderr
    res = {"ok": r.returncode == 0 and gcode.exists(), "log": [l for l in log.splitlines() if re.search(r"(?i)error|outside|stability|warning", l)]}
    m = re.search(r"Detected print stability issues:\s*\n\s*\n?(.*?)\n\s*\n", log, re.S)
    if m:
        res["alerts"] = " ".join(m.group(1).split())
    if gcode.exists():
        txt = gcode.read_text(errors="ignore")
        for key, pat in (("grams", r"total filament used \[g\] = ([\d.]+)"),
                         ("time", r"estimated printing time \(normal mode\) = (.+)")):
            mm = re.search(pat, txt)
            if mm:
                res[key] = mm.group(1).strip()
        xs, ys = [], []
        for x, y in re.findall(r"G1 X([-\d.]+) Y([-\d.]+) E", txt):
            xs.append(float(x)); ys.append(float(y))
        if xs:
            res["extent"] = [min(xs), min(ys), max(xs), max(ys)]
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-slice", action="store_true")
    a = ap.parse_args()
    V = scad_values()
    qmap = part_qty(V)
    meshes, outlines = {}, {}
    for n, *_ in PARTS:
        m = trimesh.load(str(STL / f"{n}.stl"), force="mesh")
        m.apply_translation([-(m.bounds[0][0] + m.bounds[1][0]) / 2, -(m.bounds[0][1] + m.bounds[1][1]) / 2, -m.bounds[0][2]])
        meshes[n], outlines[n] = m, silhouette(m)
    # the work list: every copy, largest footprint first within each group
    work = []
    for n, q, *_ in PARTS:
        work += [(n, GROUP_OF.get(n, "solid" if dict((p[0], p[3]) for p in PARTS)[n] >= 100 else "frames"))] * qmap.get(n, q)
    work += [(n, "coupon") for n in TEST_PIECES]
    plates = []
    for grp in GROUPS:
        items = sorted([w for w in work if w[1] == grp], key=lambda w: (-outlines[w[0]].area, w[0]))
        pad = (GAP / 2 + (BRIM if GROUPS[grp][4] else 0))
        gplates = []
        for n, _g in items:
            for p in gplates:
                if p.try_place(n, outlines[n], pad):
                    break
            else:
                p = Plate(grp)
                if not p.try_place(n, outlines[n], pad):
                    raise SystemExit(f"{n} does not fit on an empty plate")
                gplates.append(p)
        plates += gplates
    plates.sort(key=lambda p: (min(MODULE[n] for n, *_ in p.items), -len(p.items)))
    OUT.mkdir(exist_ok=True)
    for f in OUT.glob("*.3mf"):
        f.unlink()
    rows, summary = [], []
    tot_g = 0.0
    for i, p in enumerate(plates, start=1):
        counts = {}
        for n, *_ in p.items:
            counts[n] = counts.get(n, 0) + 1
        main_part = max(counts, key=lambda n: outlines[n].area * counts[n])
        fname = f"{i:02d}_{main_part}{'_etc' if len(counts) > 1 else ''}.3mf"
        write_3mf(OUT / fname, p, meshes)
        title, walls, infill, layer, brim = GROUPS[p.group]
        info = {}
        if not a.no_slice:
            info = slice_plate(OUT / fname, p.group, HERE / "stl" / ".slice" / f"plate{i:02d}.gcode")
            tot_g += float(info.get("grams", 0))
        contents = ", ".join(f"{c} x `{n}`" if c > 1 else f"`{n}`" for n, c in sorted(counts.items(), key=lambda kv: MODULE[kv[0]]))
        mods = ", ".join(MODULE_NAME[m] for m in sorted({MODULE[n] for n in counts}))
        rows.append(f"| {i} | `{fname}` | {contents} | {mods} | {walls} walls, {infill} %{', 0.16 mm layers' if layer < 0.2 else ''}{', 5 mm brim' if brim else ''} "
                    f"| {float(info.get('grams', 0)):.0f} | {info.get('time', '-')} |")
        summary.append({"plate": i, "file": fname, "group": p.group, "items": p.items, **{k: v for k, v in info.items() if k != "log"},
                        "log": info.get("log", [])})
        print(f"plate {i:2d} {fname:34s} {p.group:11s} {len(p.items):3d} parts  {info.get('grams', '?'):>7s} g  {info.get('time', '?'):>14s}"
              f"  {info.get('alerts', '')}  {'' if info.get('ok', True) else 'SLICE FAILED ' + '; '.join(info.get('log', []))[:200]}", flush=True)
    md = ["# Print plates", "",
          "Generated by `cad/make_plates.py`. Open a plate file in Bambu Studio (File > Import, or drag it in),",
          "choose the P2S, 0.4 mm nozzle, your PLA and the textured PEI plate, set the plate's walls and infill",
          "(Strength tab: wall loops, sparse infill density) and the brim if listed, then slice and print.",
          "Grams and times are PrusaSlicer's estimate with a P2S-like profile; Bambu Studio's numbers will differ a little.", "",
          "| # | File | Parts | For | Settings | g | Time |", "|---|---|---|---|---|---|---|"] + rows + \
         ["", f"All plates: **{tot_g / 1000:.2f} kg** of filament (test coupon plate included)."]
    (OUT / "plates.md").write_text("\n".join(md) + "\n")
    if not a.no_slice:
        fill_doc("plate-table", "\n".join(md[md.index("| # | File | Parts | For | Settings | g | Time |"):]))
    (OUT / "plates.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()

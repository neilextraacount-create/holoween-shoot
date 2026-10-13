#!/usr/bin/env python3
"""Print-in-place check on the SLICED G-code (from slice_all.py): do the separate bodies of each
print-in-place part stay apart once the slicer has turned them into extrusion lines?

For every layer, each extrusion line is assigned to the body it belongs to (by slicing the STL
there), then:
  - side gap: the smallest distance between deposited plastic (lines buffered by half their width)
    of two different bodies in the same layer;
  - vertical gap: a body's lines lying directly over another body's lines 1, 2 or 3 layers below
    (directly over the layer below = printed onto it = fused).

    python3 gcode_gaps.py            # every multi-body part, writes gcode-gaps.md
"""
import re
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check_parts import PARTS, to_mf   # noqa: E402

STL = HERE / "stl"
WORK = STL / ".slice"
BED_C = np.array([128.0, 128.0])


def parse(path):
    """layers: list of (z_top, height, [(x0, y0, x1, y1, width), ...]) without skirt/brim"""
    layers, segs = [], []
    z = h = 0.0
    x = y = e = 0.0
    w, typ = 0.42, ""
    for ln in Path(path).read_text(errors="ignore").splitlines():
        if ln.startswith(";LAYER_CHANGE"):
            if segs:
                layers.append((z, h, segs))
            segs = []
        elif ln.startswith(";Z:"):
            z = float(ln[3:])
        elif ln.startswith(";HEIGHT:"):
            h = float(ln[8:])
        elif ln.startswith(";WIDTH:"):
            w = float(ln[7:])
        elif ln.startswith(";TYPE:"):
            typ = ln[6:]
        elif ln.startswith("G92"):
            m = re.search(r"E([-\d.]+)", ln)
            if m:
                e = float(m.group(1))
        elif ln.startswith("G1") or ln.startswith("G0"):
            nx, ny, ne = x, y, e
            for k, v in re.findall(r"([XYE])([-\d.]+)", ln.split(";")[0]):
                if k == "X":
                    nx = float(v)
                elif k == "Y":
                    ny = float(v)
                else:
                    ne = float(v)
            if ne > e + 1e-6 and (nx != x or ny != y) and typ not in ("Skirt/Brim", "Skirt", "Brim"):
                segs.append((x, y, nx, ny, w))
            x, y, e = nx, ny, ne
    if segs:
        layers.append((z, h, segs))
    return layers


def cs_polys(cs):
    """manifold CrossSection -> shapely geometry; rings are combined even-odd so holes stay holes"""
    geom = Polygon()
    for ring in cs.to_polygons():
        if len(ring) < 3:
            continue
        p = Polygon(ring)
        geom = geom.symmetric_difference(p if p.is_valid else p.buffer(0))
    return [geom] if not geom.is_empty else []


def body_regions(polys_by_body, segs):
    """assign each segment to a body (point-in-slice, else nearest) and return deposited regions"""
    lines = {i: [] for i in range(len(polys_by_body))}
    shapes = [unary_union(p) if p else None for p in polys_by_body]
    for x0, y0, x1, y1, w in segs:
        mid = Point((x0 + x1) / 2, (y0 + y1) / 2)
        best, bd = None, 1e9
        for i, s in enumerate(shapes):
            if s is None:
                continue
            d = s.distance(mid)
            if d < bd:
                best, bd = i, d
        if best is not None and bd < 1.0:
            lines[best].append(LineString([(x0, y0), (x1, y1)]).buffer(w / 2, cap_style=2, resolution=4)
                               if (x0, y0) != (x1, y1) else Point(x0, y0).buffer(w / 2))
    return {i: unary_union(v) for i, v in lines.items() if v}


def check(name):
    g = WORK / f"{name}.gcode"
    t = trimesh.load(str(STL / f"{name}.stl"), force="mesh")
    t.merge_vertices()
    bodies = t.split(only_watertight=False)
    off = BED_C - (t.bounds[0][:2] + t.bounds[1][:2]) / 2          # the slicer centres the part on the bed
    mfs = [to_mf(b) for b in bodies]
    layers = parse(g)
    side = (1e9, None)
    vert = []
    hist = []
    for z, h, segs in layers:
        polys = []
        for mf in mfs:
            # sample just below and above the layer middle: a face lying exactly in that plane (a
            # counterbore floor) is printed by the slicer but can vanish from a single exact slice
            ps = cs_polys(mf.slice(z - h / 2 - 0.06)) + cs_polys(mf.slice(z - h / 2 + 0.06))
            polys.append([trimesh_shift(p, off) for p in ps])
        reg = body_regions(polys, segs)
        keys = sorted(reg)
        for a in range(len(keys)):
            for b in range(a + 1, len(keys)):
                d = reg[keys[a]].distance(reg[keys[b]])
                if d < side[0]:
                    side = (d, (round(z, 2), keys[a], keys[b]))
        for k, (zb, rb) in enumerate(reversed(hist[-3:]), start=1):
            for i, ri in reg.items():
                for j, rj in rb.items():
                    if i != j and ri.intersection(rj).area > 0.05:
                        vert.append((k, round(z, 2), i, j, round(ri.intersection(rj).area, 2)))
        hist.append((z, reg))
    return len(bodies), side, vert


def trimesh_shift(p, off):
    from shapely import affinity
    return affinity.translate(p, off[0], off[1])


def main():
    names = sys.argv[1:] or [n for n, _q, _w, _i, nb, _t, _d in PARTS if nb > 1]
    out = ["# Print-in-place gaps in the sliced G-code", "",
           "Generated by `cad/gcode_gaps.py` from the G-code `slice_all.py` writes. Side gap: the closest",
           "approach of plastic of two different bodies in one layer (lines counted at their full width).",
           "Vertical: a body printed over another one 1 layer below (fused), 2 layers below (0.2 mm of air)",
           "or 3 layers below (0.4 mm).", "",
           "| Part | Bodies | Smallest side gap | Printed over another body |", "|---|---|---|---|"]
    bad = 0
    for n in names:
        nb, side, vert = check(n)
        fused = [v for v in vert if v[0] == 1]
        thin = [v for v in vert if v[0] == 2]
        v_txt = ("FUSED at z " + ", ".join(str(v[1]) for v in fused[:5])) if fused else \
            (f"{min(v[0] for v in vert) - 1} layer(s) of air at z {min(vert)[1]}" if vert else "never")
        if thin and not fused:
            v_txt += " (only 1 layer of air: may stick lightly; the first twist frees it)"
        ok = side[0] >= 0.30 and not fused
        bad += not ok
        out.append(f"| `{n}` | {nb} | {side[0]:.2f} mm (z {side[1][0] if side[1] else '-'}) | {v_txt} |")
        print(f"{'ok  ' if ok else 'FAIL'} {n:14s} bodies {nb}  side gap {side[0]:.3f} at {side[1]}  vertical {v_txt}", flush=True)
    out += ["", f"Result: {'all gaps open' if not bad else f'{bad} part(s) at risk'} (side gap must be >= 0.30 mm, nothing printed directly on another body)."]
    if not sys.argv[1:]:
        (HERE / "gcode-gaps.md").write_text("\n".join(out) + "\n")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

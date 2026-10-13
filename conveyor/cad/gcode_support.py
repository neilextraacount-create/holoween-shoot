#!/usr/bin/env python3
"""Find what a slicer's stability alerts point at, in the sliced G-code (from slice_all.py).

For every layer, every extrusion line is compared with the plastic deposited in the layer below:
  - bridges ("Bridge infill"): span (line length) and whether each end lands on plastic below;
  - everything else: the longest stretch of a line lying more than half a line width outside the
    plastic below (an overhang or a loose extrusion);
  - first layer: contact area of each separate island on the bed, and its height (tall islands
    with a small footprint can be knocked over).

    python3 gcode_support.py part [part ...]
"""
import sys
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
from shapely.prepared import prep

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gcode_gaps import WORK   # noqa: E402

import re


def parse_typed(path):
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
            if ne > e + 1e-6 and (nx != x or ny != y) and "Brim" not in typ and "Skirt" not in typ:
                segs.append((x, y, nx, ny, w, typ))
            x, y, e = nx, ny, ne
    if segs:
        layers.append((z, h, segs))
    return layers


def region(segs):
    return unary_union([LineString([(a, b), (c, d)]).buffer(w / 2, cap_style=2, resolution=3) for a, b, c, d, w, _ in segs])


def analyse(name, top=6):
    layers = parse_typed(WORK / f"{name}.gcode")
    bridges, loose = [], []
    prev = None
    first = layers[0]
    reg0 = region(first[2])
    islands = list(getattr(reg0, "geoms", [reg0]))
    for z, h, segs in layers:
        if prev is not None:
            sup = prep(prev.buffer(0.01))
            grown = prev.buffer(0.21)                       # half a line width: a normal overhang step
            grown_p = prep(grown)
            for a, b, c, d, w, typ in segs:
                ln = LineString([(a, b), (c, d)])
                if typ.startswith("Bridge"):
                    ends = sum(1 for p in ((a, b), (c, d)) if sup.contains(Point(p)))
                    bridges.append((ln.length, ends, round(z, 2), (round((a + c) / 2, 1), round((b + d) / 2, 1)), typ))
                    continue
                if grown_p.covers(ln):
                    continue
                out = ln.difference(grown)
                L = max((g.length for g in getattr(out, "geoms", [out])), default=0.0) if not out.is_empty else 0.0
                if L > 1.0:
                    loose.append((L, round(z, 2), (round((a + c) / 2, 1), round((b + d) / 2, 1)), typ))
        prev = region(segs)
    bridges.sort(reverse=True)
    loose.sort(reverse=True)
    zmax = layers[-1][0]
    return {"islands": sorted(((round(i.area, 1), [round(v, 1) for v in i.bounds]) for i in islands), reverse=True),
            "height": zmax, "bridges": bridges[:top], "floating_bridges": [b for b in bridges if b[1] == 0][:top],
            "loose": loose[:top]}


def main():
    for n in sys.argv[1:]:
        r = analyse(n)
        print(f"== {n}: height {r['height']:.1f} mm; first-layer islands (area mm2, bounds): {r['islands'][:6]}")
        print("   longest bridges (span mm, ends on plastic, z, xy, type):", [(round(b[0], 1),) + b[1:] for b in r["bridges"]])
        print("   bridges with neither end on plastic:", [(round(b[0], 1),) + b[1:] for b in r["floating_bridges"]])
        print("   longest unsupported stretches (mm, z, xy, type):", [(round(l[0], 1),) + l[1:] for l in r["loose"]])


if __name__ == "__main__":
    main()

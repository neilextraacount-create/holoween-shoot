#!/usr/bin/env python3
"""
Render every printable part from conveyor.scad and check it.

  python3 check_parts.py            # render all parts to stl/, print a report
  python3 check_parts.py --only idler

Checks per part:
  * OpenSCAD renders it without errors or warnings
  * the mesh is watertight (a valid solid the slicer will accept)
  * it fits the Bambu Lab P2S build volume (256 x 256 x 256 mm) with a 10 mm margin
  * filament estimate for each part's slicer profile (walls x 0.42 mm shell over the whole
    surface, the rest at the listed infill %). An estimate, not a slicer result.

Then assembly interference checks: pairs of solids exported from conveyor.scad with
part="chk_<name>" that must NOT overlap (e.g. belt envelope vs rails) or MUST overlap
(e.g. bearing seated in its pocket).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

import trimesh

HERE = Path(__file__).resolve().parent
SCAD = HERE / "conveyor.scad"
OUT = HERE / "stl"
PLA_DENSITY = 1.24          # g/cm3
BUILD = 256.0
MARGIN = 10.0


def parts_from_scad():
    """PARTS table in conveyor.scad:  // PART: name | qty | walls | infill % | description"""
    rows = []
    for line in SCAD.read_text().splitlines():
        m = re.match(r"\s*//\s*PART:\s*(\w+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(.*)", line)
        if m:
            rows.append((m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4)), m.group(5).strip()))
    return rows


def checks_from_scad():
    """// CHECK: a | b | disjoint|overlap | description"""
    rows = []
    for line in SCAD.read_text().splitlines():
        m = re.match(r"\s*//\s*CHECK:\s*(\w+)\s*\|\s*(\w+)\s*\|\s*(disjoint|overlap)\s*\|\s*(.*)", line)
        if m:
            rows.append(m.groups())
    return rows


def min_gap(a, b, n=40000):
    """Smallest distance between two meshes (surface sampling both ways), mm."""
    best = 1e9
    for x, y in ((a, b), (b, a)):
        pts = x.sample(n)
        _, d, _ = trimesh.proximity.closest_point(y, pts)
        best = min(best, float(d.min()))
    return best


def render(part, out):
    cmd = ["openscad", "-o", str(out), "-D", f'part="{part}"', str(SCAD)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    log = r.stdout + r.stderr
    warn = [l for l in log.splitlines() if "WARNING" in l or "ERROR" in l]
    return r.returncode == 0 and out.exists(), warn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--skip-checks", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    failures = 0
    total_g = 0.0
    print(f"{'part':22s} {'qty':>3} {'bbox mm':>22} {'vol cm3':>8} {'g each':>7} {'g total':>8}  status")
    for name, qty, walls, infill, desc in parts_from_scad():
        if a.only and a.only != name:
            continue
        stl = OUT / f"{name}.stl"
        ok, warn = render(name, stl)
        status = []
        if not ok:
            print(f"{name:22s} RENDER FAILED: {warn}")
            failures += 1
            continue
        m = trimesh.load(stl, force="mesh")
        ext = m.bounding_box.extents
        if not m.is_watertight:
            status.append("NOT WATERTIGHT")
        if max(ext) > BUILD - MARGIN:
            status.append("TOO BIG FOR P2S")
        if warn:
            status.append("warnings: " + "; ".join(warn)[:120])
        vol = abs(m.volume) / 1000.0
        shell = min(vol, m.area * walls * 0.42 / 1000.0)
        g = (shell + (vol - shell) * infill / 100.0) * PLA_DENSITY
        total_g += g * qty
        failures += bool(status)
        bbox = "x".join(f"{e:.0f}" for e in ext)
        print(f"{name:22s} {qty:3d} {bbox:>22} {vol:8.1f} {g:7.1f} {g*qty:8.1f}  {'OK' if not status else ' / '.join(status)}")
    print(f"{'':22s} {'':3} {'':>22} {'':>8} {'TOTAL':>7} {total_g:8.0f} g  (~{total_g/1000:.2f} kg PLA, estimate)")

    if not a.skip_checks and not a.only:
        print("\nASSEMBLY CHECKS")
        for p1, p2, mode, desc in checks_from_scad():
            meshes = []
            for p in (p1, p2):
                stl = OUT / f"chk_{p}.stl"
                ok, warn = render(f"chk_{p}", stl)
                if not ok:
                    print(f"  render chk_{p} failed {warn}")
                    meshes = None
                    break
                meshes.append(trimesh.load(stl, force="mesh"))
            if meshes is None:
                failures += 1
                continue
            try:
                inter = trimesh.boolean.intersection(meshes, engine="manifold")
                v = abs(inter.volume) if inter is not None and not inter.is_empty else 0.0
            except Exception as e:  # noqa: BLE001
                print(f"  {p1} vs {p2}: boolean failed ({e})")
                failures += 1
                continue
            good = (v < 1.0) if mode == "disjoint" else (v > 1.0)
            failures += not good
            gap = min_gap(meshes[0], meshes[1]) if mode == "disjoint" else 0.0
            print(f"  {'PASS' if good else 'FAIL'}  {p1:13s} vs {p2:13s} [{mode:8s}] overlap {v:7.1f} mm3"
                  f"  min gap {gap:6.1f} mm - {desc}")
    print("\nRESULT:", "ALL CHECKS PASSED" if failures == 0 else f"{failures} PROBLEM(S)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

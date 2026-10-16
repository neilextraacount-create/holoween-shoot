#!/usr/bin/env python3
"""SIMPLE candy conveyor: slice every part with PrusaSlicer (the engine Bambu Studio is built on),
check the print-in-place gaps in the G-code, lay the parts out on P2S plates and slice each plate.

    python3 make.py            # needs stl/ from build.py; writes plates/SIMPLE_NN_*.3mf, plates/plates.md,
                               # slice-report.md, gcode-gaps.md
"""
import json
import shutil
import sys
from pathlib import Path

import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "cad"))
sys.path.insert(0, str(HERE))
import gcode_gaps                     # noqa: E402
import make_plates as mp              # noqa: E402
from build import PARTS               # noqa: E402
from slice_all import hours, slice_one   # noqa: E402

STL = HERE / "stl"
WORK = STL / ".slice"
OUT = HERE / "plates"

# plate groups: title, walls, infill %, layer mm, brim
GROUPS = {
    "solid":  ("Pins and wedges (solid)", 3, 100, 0.20, True),
    "frames": ("Head and tail frames", 2, 10, 0.20, True),
    "moving": ("Rollers, crank gear, station wheels", 2, 10, 0.20, True),
    "sturdy": ("Crank arm and stakes", 3, 15, 0.20, False),
}
GROUP_OF = {"journal_pin": "solid", "crank_pin": "solid", "wedge": "solid",
            "head_frame": "frames", "tail_frame": "frames",
            "drive_roller": "moving", "tail_roller": "moving", "crank_gear": "moving", "cassette": "moving",
            "crank_arm": "sturdy", "station_stake_1": "sturdy", "station_stake_2": "sturdy",
            "station_stake_3": "sturdy", "anchor_stake": "sturdy"}
ORDER = ["solid", "frames", "moving", "sturdy"]      # print order: the small solid plate first (it checks your fits)
FOR = {"journal_pin": "head, tail", "crank_pin": "crank", "wedge": "tail", "head_frame": "head", "tail_frame": "tail",
       "drive_roller": "head", "tail_roller": "tail", "crank_gear": "crank", "cassette": "stations",
       "crank_arm": "crank", "station_stake_1": "stations", "station_stake_2": "stations", "station_stake_3": "stations",
       "anchor_stake": "head, tail"}


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    # ---- every part alone
    rows, res = [], {}
    for name, qty, nb, _r, what in PARTS:
        _t, w, i, _l, _b = GROUPS[GROUP_OF[name]]
        r = slice_one(name, w, i, out_dir=WORK, stl=STL / f"{name}.stl")
        res[name] = r
        rows.append((name, qty, w, i, r))
        print(f"{name:16s} {r.get('grams', '?'):>7s} g {r.get('time', '?'):>12s}  {', '.join(r['alerts']) or 'no alerts'}", flush=True)
    tot_g = sum(q * float(r.get("grams", 0)) for _n, q, _w, _i, r in rows)
    tot_h = sum(q * hours(r.get("time")) for _n, q, _w, _i, r in rows)
    md = ["# Slicer check, every part alone (PrusaSlicer engine, P2S-like profile)", "",
          "| Part | Qty | Walls | Infill | g each | Time each | Slicer alerts |", "|---|---|---|---|---|---|---|"]
    md += [f"| `{n}` | {q} | {w} | {i} % | {float(r.get('grams', 0)):.0f} | {r.get('time', '?')} | {', '.join(r['alerts']) or 'none'} |"
           for n, q, w, i, r in rows]
    md += ["", f"Whole machine: **{tot_g / 1000:.2f} kg**, about **{tot_h:.0f} h** (parts one at a time; plates save some time)."]
    (HERE / "slice-report.md").write_text("\n".join(md) + "\n")
    # ---- print-in-place gaps in the G-code
    gcode_gaps.STL, gcode_gaps.WORK = STL, WORK
    gl = ["# Print-in-place gaps in the sliced G-code", "", "| Part | Bodies | Smallest side gap | Printed over another body |", "|---|---|---|---|"]
    bad = 0
    for name, _q, nb, *_ in PARTS:
        if nb < 2:
            continue
        n_b, side, vert = gcode_gaps.check(name)
        fused = [v for v in vert if v[0] == 1]
        ok = side[0] >= 0.30 and not fused
        bad += not ok
        gl.append(f"| `{name}` | {n_b} | {side[0]:.2f} mm | {'FUSED' if fused else ('never' if not vert else f'{min(v[0] for v in vert) - 1} layer(s) of air')} |")
        print(f"{'ok  ' if ok else 'FAIL'} gaps {name}: side {side[0]:.3f} mm, vertical {'fused' if fused else 'ok'}", flush=True)
    gl += ["", f"Result: {'all gaps open' if not bad else 'GAPS AT RISK'}."]
    (HERE / "gcode-gaps.md").write_text("\n".join(gl) + "\n")
    # ---- plates
    mp.GROUPS = GROUPS
    meshes, outlines = {}, {}
    for n, *_ in PARTS:
        m = trimesh.load(str(STL / f"{n}.stl"), force="mesh")
        m.apply_translation([-(m.bounds[0][0] + m.bounds[1][0]) / 2, -(m.bounds[0][1] + m.bounds[1][1]) / 2, -m.bounds[0][2]])
        meshes[n], outlines[n] = m, mp.silhouette(m)
    plates = []
    for grp in ORDER:
        items = sorted([(n, q) for n, q, *_ in PARTS if GROUP_OF[n] == grp for _ in range(q)],
                       key=lambda w: (-outlines[w[0]].area, w[0]))
        pad = mp.GAP / 2 + (mp.BRIM if GROUPS[grp][4] else 0)
        best = None
        for rots in ((0, 90, 180, 270), (0, 180), (90, 270)):    # keep the layout with the fewest plates
            gp = []
            for n, _q in items:
                for p in gp:
                    if p.try_place(n, outlines[n], pad, rots):
                        break
                else:
                    p = mp.Plate(grp)
                    if not (p.try_place(n, outlines[n], pad, rots) or p.try_place(n, outlines[n], pad)):
                        raise SystemExit(f"{n} does not fit on an empty plate")
                    gp.append(p)
            if best is None or len(gp) < len(best):
                best = gp
        plates += best
    exe = mp.find_slicer()
    new = HERE / "plates.new"
    shutil.rmtree(new, ignore_errors=True)
    new.mkdir()
    out = ["# SIMPLE print plates", "",
           "Start each plate in a new project (File > New Project), import the plate file, choose the P2S,",
           "0.4 mm nozzle, your PLA and the textured PEI plate, set the plate's walls, infill and brim, slice, print.", "",
           "| # | File | Parts | For | Settings | g | Time |", "|---|---|---|---|---|---|---|"]
    summary, tg, failed = [], 0.0, []
    for k, p in enumerate(plates, start=1):
        counts = {}
        for n, *_ in p.items:
            counts[n] = counts.get(n, 0) + 1
        main = max(counts, key=lambda n: outlines[n].area * counts[n])
        fname = f"SIMPLE_{k:02d}_{main}{'_etc' if len(counts) > 1 else ''}.3mf"
        mp.write_3mf(new / fname, p, meshes)
        title, walls, infill, layer, brim = GROUPS[p.group]
        r = mp.slice_plate(exe, new / fname, p.group, WORK / f"plate{k}.gcode") if exe else {"ok": True}
        if not r["ok"]:
            failed.append(fname)
        g = float(r.get("grams", 0))
        tg += g
        parts = ", ".join(f"{c} x `{n}`" if c > 1 else f"`{n}`" for n, c in counts.items())
        fors = ", ".join(sorted({FOR[n] for n in counts}))
        st = f"{walls} walls, {infill} %{', 5 mm brim' if brim else ''}"
        out.append(f"| {k} | `{fname}` | {parts} | {fors} | {st} | {g:.0f} | {r.get('time', '?')} |")
        summary.append({"plate": k, "file": fname, "group": p.group, "parts": counts, "grams": g, "time": r.get("time"),
                        "alerts": r.get("alerts")})
        print(f"plate {k} {fname:34s} {g:7.1f} g {r.get('time', '?'):>12s}  {r.get('alerts') or ''}", flush=True)
    out += ["", f"All plates: **{tg / 1000:.2f} kg** of PLA."]
    (new / "plates.md").write_text("\n".join(out) + "\n")
    (new / "plates.json").write_text(json.dumps(summary, indent=1))
    if failed:
        raise SystemExit(f"plates failed the slice check: {failed}; plates/ left unchanged")
    shutil.rmtree(OUT, ignore_errors=True)
    new.rename(OUT)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

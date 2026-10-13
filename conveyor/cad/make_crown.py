#!/usr/bin/env python3
"""
Gearbox: cut the 34T crown teeth by sweeping the 17T pinion through the real mesh
motion, build the print-in-place gearbox STL (body + rotor), and check the mesh.

  python3 make_crown.py            # writes stl/gearbox.stl and prints the checks

Frames: everything is in the gearbox PRINT frame of conveyor.scad: crown axis = +z,
male hex on the bed, crown teeth on top. The pinion (on the drive roller) has its
axis along +y through (0, 0, gb_top_s) and its mid-plane at y = -crown_R.
"""
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import manifold3d as m3d
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent


def params():
    ns = {"IN": 25.4}
    for line in (HERE / "params.scad").read_text().splitlines():
        mm = re.match(r"\s*([A-Za-z_]\w*)\s*=\s*([^;]+);", line)
        if mm:
            try:
                ns[mm.group(1)] = eval(mm.group(2), {"__builtins__": {}}, ns)  # noqa: S307 - our own file
            except NameError:
                pass
    return ns


P = params()
PIN_R = P["gear_m"] * P["pinion_z"] / 2
CROWN_R = P["gear_m"] * P["crown_z"] / 2
AXIS_Z = P["gb_top_s"]                      # pz(0): pinion axis height in the print frame
RATIO = P["crown_z"] / P["pinion_z"]


def render(part, out):
    r = subprocess.run(["openscad", "-o", str(out), "-D", f'part="{part}"', str(HERE / "conveyor.scad")],
                       capture_output=True, text=True)
    if r.returncode != 0 or not out.exists():
        sys.exit(f"openscad failed for {part}:\n{r.stderr[-2000:]}")


def to_manifold(path):
    t = trimesh.load(str(path), force="mesh")
    t.merge_vertices()
    mf = m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(t.vertices, dtype=np.float32),
                               tri_verts=np.asarray(t.faces, dtype=np.uint32)))
    if mf.status() != m3d.Error.NoError:
        sys.exit(f"{path.name}: not a manifold ({mf.status()})")
    return mf


def to_trimesh(mf):
    me = mf.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(me.vert_properties)[:, :3], faces=np.asarray(me.tri_verts), process=True)


def rot_y(deg):
    a = math.radians(deg)
    return np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])


def rot_z(deg):
    a = math.radians(deg)
    return np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])


# local pinion frame (extruded along z, centred) -> print frame: local z -> +y, local y -> -z
MAP = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)


def pinion_pose(phi):
    """Pinion turned by phi (deg, about +y), seen from the crown, which has turned by -phi/RATIO about +z."""
    R = rot_z(phi / RATIO) @ rot_y(phi) @ MAP
    t = rot_z(phi / RATIO) @ np.array([0.0, -CROWN_R, AXIS_Z])
    return np.hstack([R, t[:, None]])


def main():
    out_dir = HERE / "stl"
    out_dir.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for part in ("gb_rotor_blank", "gb_body", "pinion_cutter", "pinion_check"):
            render(part, td / f"{part}.stl")
        blank = to_manifold(td / "gb_rotor_blank.stl")
        body = to_manifold(td / "gb_body.stl")
        cutter = to_manifold(td / "pinion_cutter.stl")
        check = to_manifold(td / "pinion_check.stl")

    # keep only the pinion teeth near the mesh (local +y after MAP is print -z): saves time
    keep = m3d.Manifold.cube([80, 40, 60]).translate([-40, 8, -30])
    pitch = 360 / P["pinion_z"]
    steps = 24
    dphi = pitch / steps
    sector = [(cutter.rotate([0, 0, k * dphi]) ^ keep) for k in range(steps)]       # pinion turned by k*dphi
    n_total = int(round(360 * RATIO / dphi))
    cuts = []
    for k in range(n_total):
        phi = k * dphi
        R = rot_z(phi / RATIO) @ MAP
        t = rot_z(phi / RATIO) @ np.array([0.0, -CROWN_R, AXIS_Z])
        cuts.append(sector[k % steps].transform(np.hstack([R, t[:, None]])))
    print(f"sweeping {n_total} pinion positions ({dphi:.2f} deg pinion steps)")
    swept = m3d.Manifold.batch_boolean(cuts, m3d.OpType.Add)
    rotor = blank - swept
    print(f"rotor: volume {rotor.volume()/1000:.1f} cm3, genus {rotor.genus()}")

    # ---------------------------------------------------------------- checks
    ok = True
    # 1. real pinion vs crown through one full pinion tooth pitch of motion (fine steps)
    worst_int, worst_gap = 0.0, 1e9
    for k in range(40):
        phi = 3.0 * pitch + k * pitch / 40
        pin = check.transform(pinion_pose(phi))
        inter = (rotor ^ pin).volume()
        gap = rotor.min_gap(pin, 3.0)
        worst_int = max(worst_int, inter)
        worst_gap = min(worst_gap, gap)
    print(f"mesh sweep (40 positions over one tooth): max interference {worst_int:.3f} mm3, min gap {worst_gap:.3f} mm")
    if worst_int > 0.5:
        ok = False
        print("  FAIL: pinion and crown interfere")
    # 2. flank clearance: for printed PLA gears 0.15-0.35 mm is intended
    if not (0.1 <= worst_gap <= 0.6):
        ok = False
        print("  FAIL: flank clearance outside 0.1-0.6 mm")
    # 3. engagement: with the crown held still, turning the pinion by a few degrees either way
    # must make the teeth collide (otherwise the "mesh" is just empty space)
    phi0 = 3.5 * pitch
    for dphi_test in (-4.0, 4.0):
        R = rot_z(phi0 / RATIO) @ rot_y(phi0 + dphi_test) @ MAP
        t = rot_z(phi0 / RATIO) @ np.array([0.0, -CROWN_R, AXIS_Z])
        inter = (rotor ^ check.transform(np.hstack([R, t[:, None]]))).volume()
        print(f"pinion turned {dphi_test:+.0f} deg against a fixed crown: overlap {inter:.1f} mm3 (must be > 0: teeth engage)")
        if inter <= 1.0:
            ok = False
            print("  FAIL: teeth do not engage")
    # 4. print-in-place: rotor and body must be separate with >= pip_gap - 0.05
    g = body.min_gap(rotor, 5.0)
    print(f"rotor to body min gap {g:.3f} mm (print-in-place gap {P['pip_gap']})")
    if g < P["pip_gap"] - 0.05:
        ok = False
        print("  FAIL: rotor too close to the body")
    if (body ^ rotor).volume() > 0.01:
        ok = False
        print("  FAIL: rotor intersects the body")

    gearbox = body + rotor
    tm = to_trimesh(gearbox)
    tm.export(out_dir / "gearbox.stl")
    if len(sys.argv) > 2 and sys.argv[1] == "--rotor":
        to_trimesh(rotor).export(sys.argv[2])
    print(f"wrote {out_dir/'gearbox.stl'}: watertight {tm.is_watertight}, bodies {len(tm.split(only_watertight=False))},"
          f" bbox {np.round(tm.bounds, 1).tolist()}")
    print("GEARBOX OK" if ok else "GEARBOX CHECK FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

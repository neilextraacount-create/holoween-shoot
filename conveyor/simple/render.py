#!/usr/bin/env python3
"""Pictures of the SIMPLE conveyor's modules (assembled from the checked STLs) for the build guide.

    python3 render.py      # after build.py; writes img/head.png, img/tail.png, img/station.png, img/parts.png
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "cad"))
sys.path.insert(0, str(HERE))
import build as B                                      # noqa: E402
from check_parts import Mx, Rx, Rz, T, xf             # noqa: E402

ASM = B.STL / ".asm"
IMG = HERE / "img"
ORANGE, BLACK, GREY, GREEN, BROWN = "[1.0,0.45,0.05]", "[0.12,0.12,0.12]", "[0.55,0.55,0.55]", "[0.25,0.55,0.2]", "[0.45,0.3,0.15]"


def save(mf, name):
    m = mf.to_mesh()
    trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts)).export(ASM / f"{name}.stl")
    return name


def shot(items, out, eye, center, size=(1400, 1000), extra=""):
    scad = ASM / f"{out}.scad"
    scad.write_text("\n".join(f'color({c}) import("{n}.stl");' for n, c in items) + "\n" + extra)
    cam = ",".join(str(v) for v in list(eye) + list(center))
    subprocess.run(["xvfb-run", "-a", "openscad", "--preview", f"--camera={cam}", "--projection=p", f"--imgsize={size[0]},{size[1]}",
                    "--colorscheme=Tomorrow", "-o", str(IMG / f"{out}.png"), str(scad)], capture_output=True, text=True)


def main():
    ASM.mkdir(parents=True, exist_ok=True)
    IMG.mkdir(exist_ok=True)
    V = B.values()
    psi = json.loads((HERE / "site.json").read_text())["psi"]
    hz, gc, L2 = V["hz"], V["g_c"], V["L_w"] / 2
    belt_c = BLACK
    # ---- head
    it = [(save(B.place("head_frame", np.eye(4)), "h_frame"), ORANGE),
          (save(B.place("drive_roller", T(0, -L2, hz) @ Rx(-90)), "h_roller"), GREY),
          (save(B.place("journal_pin", T(0, -L2 - V["j_len"] - 2, hz) @ Rx(-90)), "h_pin"), GREY),
          (save(B.place("crank_gear", T(gc[0], V["g_y0"], gc[1]) @ Rx(-90) @ Rz(psi)), "h_gear"), GREY),
          (save(B.place("crank_arm", T(gc[0], V["g_y0"] + V["g_face"], gc[1]) @ Rx(-90) @ Rz(200)), "h_arm"), ORANGE),
          (save(B.place("crank_pin", Mx([[0, 1, 0], [-1, 0, 0], [0, 0, 1]], (gc[0], V["g_y0"] + V["g_face"] + V["arm_t"], gc[1] - (V["cp_r"] - 0.5)))), "h_cpin"), GREY),
          (save(B.extrude_y(B.band2d((0, hz), V["drv_rs"], V["belt_t"], 0, 260), V["belt_w"]), "h_belt"), belt_c)]
    for k, x in enumerate((V["h_x"][0] + 20, V["h_x"][1] - 16)):
        it.append((save(B.place("anchor_stake", Mx([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], (x - 11, -11, V["base_t"]))), f"h_anchor{k}"), GREY))
    shot(it, "head", (420, 520, 330), (20, 0, 100))
    # ---- tail (mid take-up)
    tan = math.tan(math.radians(V["wd_ang"]))
    z_tip = V["win_z0"] + 50
    w = V["wd_t0"] + (V["tz"] - z_tip) * tan
    xj = V["x_f"] + w + V["j_r"] + 0.05
    it = [(save(B.place("tail_frame", np.eye(4)), "t_frame"), ORANGE),
          (save(B.place("tail_roller", T(xj, -L2, V["tz"]) @ Rx(-90)), "t_roller"), GREY),
          (save(B.place("journal_pin", T(xj, -L2 - V["j_len"] - 2, V["tz"]) @ Rx(-90)), "t_pin"), GREY),
          (save(B.extrude_y(B.band2d((xj, V["tz"]), V["tail_r"] + 0.3, V["belt_t"], xj, -330), V["belt_w"]), "t_belt"), belt_c)]
    for k, y0 in enumerate((V["w_in"] + 0.2, -V["w_out"] + 0.2)):
        it.append((save(B.place("wedge", Mx([[1, 0, 0], [0, 0, -1], [0, 1, 0]], (V["x_f"], y0 + 5.6, z_tip))), f"t_wedge{k}"), GREY))
    shot(it, "tail", (-520, -520, 380), (-100, 0, 110))
    # ---- station (top of it)
    Mc = Mx([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], (0, -L2, -V["st_carry"]))
    Zm = -V["st_carry"] - V["st_sock_x"]
    off = V["stake_leg"] / 2
    it = [(save(B.place("cassette", Mc), "s_cas"), ORANGE),
          (save(B.place("station_stake_2", Mx([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], (off, -V["spig"] / 2, Zm - 6))), "s_stake"), GREY)]
    import manifold3d as m3d
    it.append((save(xf(m3d.Manifold.cube([300, V["belt_w"], V["belt_t"]]), T(-150, -V["belt_w"] / 2, -V["belt_t"])), "s_top"), belt_c))
    it.append((save(xf(m3d.Manifold.cube([300, V["belt_w"], V["belt_t"]]), T(-150, -V["belt_w"] / 2, -48)), "s_ret"), belt_c))
    shot(it, "station", (330, 420, 120), (0, 0, -90))
    print("wrote", ", ".join(str(p.name) for p in sorted(IMG.glob("*.png"))))


if __name__ == "__main__":
    main()

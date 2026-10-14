# Printing guide (Bambu Lab P2S, PLA)

Everything is laid out on ready-made build plates in [`plates/`](../plates). Each plate holds
parts that print with the same settings, so you load a plate, set two or three things, and
print. The single STLs are in `cad/stl/` (already in print orientation) if you would rather
arrange things yourself.

**About 2.3 kg of PLA and roughly 71 hours of printing** (slicer estimate, see below). You have
about 18 days to Halloween, so start today.

## How the plates were checked

The STLs were not just exported; they were put through a real slicer:

- **Every part** was sliced with PrusaSlicer, the engine Bambu Studio is built on, using a
  P2S-like profile. That run gives the grams, times and stability alerts in
  [`cad/slice-report.md`](../cad/slice-report.md). Every alert was traced to its spot in the
  part, and the real ones were fixed in the design (see "Expected slicer warnings" for the rest).
- **Every print-in-place part** was checked in the sliced G-code, layer by layer, in
  [`cad/gcode-gaps.md`](../cad/gcode-gaps.md):
  - the moving body and its housing stay at least 0.43 mm apart once the slicer has laid down
    its lines (0.34 mm on the test coupon's tightest spinner)
  - no body is ever printed directly onto another one
- **Every plate** was sliced as a whole: everything is on the bed, and the grams and times in
  the plate table come from that slice.

## Settings (Bambu Studio)

Choose **Bambu Lab P2S 0.4 nozzle**, your PLA (Bambu PLA Basic or similar) and the **Textured
PEI Plate**. Most settings stay at Bambu's defaults:

| Setting | Bambu Studio tab | Value |
|---|---|---|
| Layer height | Quality | **0.20 mm**; **0.16 mm** on the rollers-and-gearbox plate |
| Wall generator | Quality | Classic (the default) |
| Elephant foot compensation | Quality | 0.15 mm (the default). It keeps a squashed first layer from gluing a spinning part to its housing. |
| Wall loops | Strength | as the plate table says (2, 3 or 4) |
| Sparse infill density | Strength | as the plate table says (10 %, 12 %, 15 %, 30 % or 100 %) |
| Sparse infill pattern | Strength | Gyroid; **Rectilinear** on the 100 % plates |
| Top / bottom shell layers | Strength | 5 / 4 |
| Supports | Support | **off**. No part needs any. |
| Brim | Others | **Outer brim only, 5 mm** on the plates that say so, otherwise **No brim**. Never use an inner brim: it would fill the print-in-place gaps. |

## Loading a plate

1. Start each plate in a **new project** (File > New Project), or delete the previous plate's
   parts first. Bambu Studio centres an imported plate on the bed and does not move it clear of
   parts already there. Then **File > Import > Import 3MF/STL** and pick a file from
   `plates/`. Bambu Studio may say the file is not from Bambu Lab and load the geometry only.
   That is expected: click OK.
2. The parts arrive already arranged. Don't re-arrange them; if you do, keep at least 6 mm
   between parts (16 mm on brim plates).
3. Set the plate's walls, infill, layer height and brim from the table. These are process
   settings for the whole plate.
4. Slice. Any warning on the list in "Expected slicer warnings" is fine.
5. Print. Then free the print-in-place parts (see "Freeing print-in-place parts").

## Step 1: plate 1, the test coupon (about 2 hours)

Plate 1 has the `test_coupon` and test copies of a `hex_coupler`, a `ring_sleeve`, a
`bolt8_28` and the `stake_cap`. The real ones come on later plates.

The coupon has:

- **3 print-in-place spinners** standing on the bed beside the plate, each next to 1, 2 or 3
  dots on the plate edge: gaps 0.35, 0.45 and 0.55 mm
- the slip fits used on the machine:
  - a 16 mm stake/tray socket
  - a hex socket for the shaft couplers
  - the ring-sleeve counterbore
  - the drive journal hole
  - an M8 nut thread

Try the test pieces in the coupon:

| Result | Do this |
|---|---|
| Spinner 2 (0.45, two dots) turns freely after a firm first twist | ✅ keep `pip_gap = 0.45` |
| Spinner 2 is stuck, spinner 3 turns | set `pip_gap = 0.55` in `cad/params.scad`, then regenerate (see below) |
| Spinner 1 already turns freely | your printer is precise; 0.45 still works (0.35 only if you want less wobble) |
| The coupler, sleeve or spigot won't go in | set `fit_gap = 0.25` (default 0.20) and regenerate |
| They rattle | set `fit_gap = 0.15` and regenerate |
| The bolt won't screw into the coupon's nut thread | set `thread_gap = 0.40` (default 0.32) and regenerate |
| The bolt wobbles in the thread | set `thread_gap = 0.25` and regenerate |

**Regenerate** after any change to `cad/params.scad`. From the `cad` folder, run
`python3 check_parts.py`, then `python3 make_plates.py`; that rewrites the STLs and the plates.
`make_plates.py` checks each plate with PrusaSlicer if it is installed. Without it, run
`python3 make_plates.py --no-slice`: the plates are the same, only the grams and times are left
out. The old plates are kept unless every new plate is written and passes.

## Step 2: print the plates in this order

The plates are in build order. Each module can be tested as soon as all of its parts are
printed, so a problem shows up early and only costs one plate:

- **Head**: assemble it on the table (build guide, section 2). Turn the gearbox's shaft socket
  by hand: the roller turns twice per turn, smoothly, with no tight spots.
- **Station 1**: the wheels spin freely after the first twist.
- **Tail**: the knobs move the take-up blocks along the full window, and the roller spins.
- **Anchors**: screw one ground screw into your lawn and pull on it.
- **Chute line**: stack two segments on the table; both shafts turn together.
- **Porch stand**: slide the upper post fully into the lower one, then out to a pin hole.

Counts are for 2 risers of 7 in. If the calculator changes `seg_count` or `stand_h` for your
steps, regenerate: `cad/parts-table.md` and the plates then match your steps.

<!-- plate-table: written by cad/make_plates.py -->
| # | File | Parts | For | Settings | g | Time |
|---|---|---|---|---|---|---|
| 1 | `FINAL_01_test_coupon_etc.3mf` | `test_coupon`, `hex_coupler`, `ring_sleeve`, `bolt8_28`, `stake_cap` | test | 3 walls, 15 % | 64 | 1h 53m 47s |
| 2 | `FINAL_02_bolt8_28_etc.3mf` | 7 x `hex_coupler`, 17 x `bolt8_28`, 14 x `pin3`, 2 x `takeup_screw` | head, tail | 3 walls, 100 %, 5 mm brim | 91 | 3h 24m 9s |
| 3 | `FINAL_03_washer50_etc.3mf` | `drive_pin`, 6 x `ring_sleeve`, 13 x `nut8`, 2 x `takeup_block`, 2 x `takeup_nut`, 4 x `washer50`, 4 x `stand_shim`, `splice_template` | head, tail, anchors, porch stand, belt joint | 3 walls, 100 % | 111 | 3h 12m 56s |
| 4 | `FINAL_04_head_side_a_etc.3mf` | `head_side_a`, 2 x `foot`, `station_bracket` | head, station 1 | 3 walls, 12 % | 105 | 2h 46m 20s |
| 5 | `FINAL_05_gearbox_etc.3mf` | `gearbox`, `drive_roller`, `tail_roller` | head, tail | 3 walls, 10 %, 0.16 mm layers | 228 | 10h 4m 59s |
| 6 | `FINAL_06_head_side_b_etc.3mf` | `head_side_b`, `foot`, `spike` | head, tail | 3 walls, 12 % | 96 | 2h 26m 58s |
| 7 | `FINAL_07_wheel_unit.3mf` | 8 x `wheel_unit` | station 1 | 3 walls, 10 %, 5 mm brim | 268 | 7h 51m 53s |
| 8 | `FINAL_08_tail_side_r_etc.3mf` | `station_bracket`, `tail_side_r`, 3 x `spike` | station 1, tail | 3 walls, 12 % | 116 | 2h 39m 29s |
| 9 | `FINAL_09_tail_side_l_etc.3mf` | 2 x `station_bracket`, `tail_side_l` | station 1, tail | 3 walls, 12 % | 73 | 1h 59m 13s |
| 10 | `FINAL_10_stake_1_etc.3mf` | `stake_1`, `stake_2`, `stake_3` | station 1, stations 2-4 | 3 walls, 12 % | 112 | 2h 3m 53s |
| 11 | `FINAL_11_crank_arm_etc.3mf` | `stake_cap`, `crank_arm` | station 1, chute line | 4 walls, 30 % | 63 | 2h 9m 22s |
| 12 | `FINAL_12_skid_l_etc.3mf` | `skid_l`, `skid_r` | tail | 3 walls, 12 % | 64 | 1h 37m 31s |
| 13 | `FINAL_13_gs_wrench_etc.3mf` | `gs_wrench`, 4 x `ground_screw` | anchors | 4 walls, 30 %, 5 mm brim | 143 | 6h 7m 36s |
| 14 | `FINAL_14_post_lower_etc.3mf` | `stake_4`, `post_lower` | stations 2-4, porch stand | 3 walls, 12 % | 79 | 1h 30m 51s |
| 15 | `FINAL_15_chute_segment_etc.3mf` | `trap`, 3 x `chute_segment` | chute line | 2 walls, 10 %, 5 mm brim | 306 | 10h 3m 4s |
| 16 | `FINAL_16_chute_segment.3mf` | 2 x `chute_segment` | chute line | 2 walls, 10 %, 5 mm brim | 182 | 6h 10m 33s |
| 17 | `FINAL_17_crank_head.3mf` | `crank_head` | chute line | 3 walls, 10 %, 5 mm brim | 116 | 3h 11m 30s |
| 18 | `FINAL_18_stand_tray.3mf` | `stand_tray` | porch stand | 3 walls, 12 % | 29 | 45m 34s |
| 19 | `FINAL_19_post_upper.3mf` | `post_upper` | porch stand | 3 walls, 12 % | 35 | 51m 50s |

All plates: **2.28 kg** of filament (test coupon plate included).
<!-- /plate-table -->

Times are PrusaSlicer's estimate with Bambu-like speeds and accelerations. Bambu Studio's
numbers will differ, probably shorter. Filament grams are reliable.

**Big plates.** If one part fails mid-print on a multi-part plate, use Bambu's **Skip
objects** (on the printer screen or in Bambu Handy) to stop just that part. Reprint it alone
later: open its plate file and delete the other parts, or load it from `cad/stl/`. Either way,
use the settings in its row of the "All parts" table, including the layer height and brim.

## Expected slicer warnings

Bambu Studio may warn about some of these. All but the trap row come from PrusaSlicer's
stability check; the trap row comes from our own overhang check. Each one was traced to its
spot in the G-code and is intended:

| Part | Warning | Why it's fine |
|---|---|---|
| `crank_arm` | floating region, overhang | The spinning grip's first layer prints 0.4 mm (2 layers of air) above the arm on purpose. That is the print-in-place gap. The first twist breaks it free; if it ever stays stuck, the handle still works as a fixed grip. |
| `gearbox`, `tail_roller`, `crank_head` | low bed adhesion | The rotor, axle or crank shaft inside stands on a small base, but their bearings hold them within 0.45 mm all the way up, so they can't tip over. |
| `stake_*`, `post_lower` | long bridging extrusions, floating bridge anchors | Internal bridges: the first solid layer laid over the part's own infill. Some ends land between infill lines, which is normal. The socket ceilings are 16 mm bridges held on both sides. |
| `trap` | 66 mm bridge (our own check; PrusaSlicer did not flag it) | Across the top of the drop slot at print height 62 mm. Expect a little sag; trim any strands. |
| `test_coupon` and plate 1's test pieces | loose extrusions, low bed adhesion | Small overhangs on the test spinners, and small test copies printed without a brim. They are only test pieces. |

## Freeing print-in-place parts

Let them cool, then twist firmly in both directions. If one won't move, put it in warm water
(45-50 °C, below PLA's 55 °C softening point) for a minute, let it cool, then twist again.
Never force it while it is warm, and never use pliers on the rolling surfaces.

## All parts

A copy of `cad/parts-table.md` for the default site (2 risers of 7 in). The plate files already
contain every copy. Sizes are as the part sits on the bed. "(diagonal)" parts are exported
turned 45° so they fit across the 256 mm bed. Grams are the checker's estimate from the meshes;
the slicer's figures are in the plate table and in `cad/slice-report.md`.

<!-- parts-table: written by cad/check_parts.py -->
| Part (STL) | Qty | Size on the bed, mm | Walls | Infill | Layer | Brim | ~g each (mesh estimate) | What it is |
|---|---|---|---|---|---|---|---|---|
| `test_coupon` | 1 | 150 x 93 x 20 | 3 | 15 % | 0.20 | no | 60 | PRINT FIRST: fit ladder (spinners 0.35/0.45/0.55, sockets, M8 nut) |
| `wheel_unit` | 8 | 30 x 30 x 115 | 3 | 10 % | 0.20 | 5 mm | 28 | station wheel, print-in-place (2 per station) |
| `station_bracket` | 4 | 28 x 109 x 16 | 3 | 12 % | 0.20 | no | 17 | station bracket (holds 2 wheels on the stake) |
| `stake_1` | 1 | 216 x 203 x 24 (diagonal) | 3 | 12 % | 0.20 | no | 44 | station 1 stake (nearest the sidewalk) |
| `stake_2` | 1 | 205 x 191 x 24 (diagonal) | 3 | 12 % | 0.20 | no | 41 | station 2 stake |
| `stake_3` | 1 | 194 x 180 x 24 (diagonal) | 3 | 12 % | 0.20 | no | 39 | station 3 stake |
| `stake_4` | 1 | 182 x 169 x 24 (diagonal) | 3 | 12 % | 0.20 | no | 36 | station 4 stake (nearest the steps) |
| `drive_roller` | 1 | 67 x 67 x 124 | 3 | 10 % | 0.16 | no | 94 | drive roller with 17T pinion |
| `drive_pin` | 1 | 20 x 20 x 35 | 3 | 100 % | 0.20 | no | 5 | drive roller A-side journal pin (press in) |
| `head_side_a` | 1 | 206 x 196 x 6 | 3 | 12 % | 0.20 | no | 57 | head side frame A (round journal hole) |
| `head_side_b` | 1 | 237 x 196 x 6 | 3 | 12 % | 0.20 | no | 68 | head side frame B (open journal slot, gearbox mount) |
| `gearbox` | 1 | 94 x 111 x 91 | 3 | 10 % | 0.16 | no | 99 | gearbox: 34T crown gear rotor in its housing, print-in-place |
| `trap` | 1 | 103 x 37 x 152 | 2 | 10 % | 0.20 | 5 mm | 32 | drop trap (bottom of the chute, rests on the head frames) |
| `foot` | 3 | 36 x 196 x 24 | 3 | 12 % | 0.20 | no | 25 | foot crossbar (2 head, 1 tail rear) |
| `tail_side_l` | 1 | 227 x 218 x 28 | 3 | 12 % | 0.20 | no | 54 | tail side frame, left (-Y) |
| `tail_side_r` | 1 | 227 x 218 x 28 | 3 | 12 % | 0.20 | no | 54 | tail side frame, right (+Y) |
| `tail_roller` | 1 | 45 x 45 x 90 | 3 | 10 % | 0.16 | no | 46 | tail roller, print-in-place |
| `takeup_block` | 2 | 22 x 24 x 36 | 3 | 100 % | 0.20 | no | 13 | take-up block (one per side) |
| `takeup_nut` | 2 | 16 x 16 x 8 | 3 | 100 % | 0.20 | no | 2 | take-up square nut |
| `takeup_screw` | 2 | 21 x 22 x 108 | 3 | 100 % | 0.20 | 5 mm | 11 | take-up screw with knob |
| `skid_l` | 1 | 239 x 59 x 24 | 3 | 12 % | 0.20 | no | 37 | tail skid, left |
| `skid_r` | 1 | 239 x 59 x 24 | 3 | 12 % | 0.20 | no | 37 | tail skid, right |
| `chute_segment` | 5 | 167 x 136 x 230 | 2 | 10 % | 0.20 | 5 mm | 113 | chute segment with print-in-place drive shaft |
| `crank_head` | 1 | 186 x 156 x 180 | 3 | 10 % | 0.20 | 5 mm | 142 | crank head: funnel + crank shaft, print-in-place |
| `crank_arm` | 1 | 138 x 28 x 78 | 4 | 30 % | 0.20 | no | 61 | crank arm with spinning grip, print-in-place |
| `pin3` | 14 | 28 x 7 x 5 | 3 | 100 % | 0.20 | 5 mm | 0 | 3 mm pin: wheel pegs (8), crank arm, crank-head socket, stand height, tray, joint between 2 lower posts if any, spares (2) |
| `splice_template` | 1 | 78 x 82 x 6 | 3 | 100 % | 0.20 | no | 13 | belt sewing template (box-and-X hole pattern) |
| `stand_shim` | 4 | 40 x 22 x 3 | 3 | 100 % | 0.20 | no | 3 | shims to level the porch stand foot |
| `hex_coupler` | 7 | 23 x 13 x 11 | 3 | 100 % | 0.20 | 5 mm | 3 | hex coupler between shafts |
| `ring_sleeve` | 6 | 25 x 25 x 8 | 3 | 100 % | 0.20 | no | 2 | sleeve between bearing rings |
| `post_lower` | 1 | 229 x 233 x 22 (diagonal) | 3 | 12 % | 0.20 | no | 51 | porch stand post, lower |
| `post_upper` | 1 | 226 x 226 x 20 (diagonal) | 3 | 12 % | 0.20 | no | 40 | porch stand post, upper |
| `stand_tray` | 1 | 190 x 236 x 32 | 3 | 12 % | 0.20 | no | 34 | porch stand foot (put the candy bowl on it) |
| `ground_screw` | 4 | 26 x 26 x 150 | 4 | 30 % | 0.20 | 5 mm | 32 | ground screw (head front foot, tail skid rear anchors) |
| `spike` | 4 | 134 x 30 x 30 | 3 | 12 % | 0.20 | no | 20 | L spike with nail head: 2 for the tail skid far pads, 2 optional for the head rear foot |
| `stake_cap` | 1 | 22 x 22 x 28 | 4 | 30 % | 0.20 | no | 8 | push the stakes in through this cap |
| `gs_wrench` | 1 | 160 x 33 x 24 | 4 | 30 % | 0.20 | 5 mm | 31 | T-wrench for the ground screws |
| `bolt8_28` | 17 | 13 x 15 x 33 | 3 | 100 % | 0.20 | 5 mm | 2 | printed M8 bolt (13 frame joints + 4 ground screws) |
| `nut8` | 13 | 13 x 15 x 7 | 3 | 100 % | 0.20 | no | 1 | printed M8 nut |
| `washer50` | 4 | 50 x 50 x 3 | 3 | 100 % | 0.20 | no | 7 | 50 mm washer over a ground screw |
<!-- /parts-table -->

# Printing guide (Bambu Lab P2S, PLA)

Every STL in `cad/stl/` is already in its print orientation: load it and slice it as it is.
**No part needs supports.** Overhangs are 45° or steeper, and the print-in-place gaps are
open to the side. One exception: the `trap` has a 66 mm bridge across the top of its drop slot
(at print height 62 mm). Expect a little sag there and trim any strands.

## Settings for every part

| Setting | Value |
|---|---|
| Filament | PLA (Bambu PLA Basic, eSUN PLA+ or similar), 1.75 mm, dry |
| Nozzle | 0.4 mm |
| Plate | textured PEI, glue stick not needed |
| Layer height | **0.20 mm**; use **0.16 mm** for `gearbox` and `drive_roller` (smoother gear teeth) |
| Walls, infill | as in the part table below (gyroid infill) |
| Top / bottom shells | 5 / 4 layers |
| Supports | **off** |
| Brim | 5 mm on `chute_segment`, `crank_head`, `trap`, `wheel_unit`, `ground_screw`, `takeup_screw` (tall, small footprint) |
| Elephant-foot compensation | **0.15 mm** (Bambu default is 0.15). It matters for print-in-place parts: a squashed first layer can glue a spinning part to its housing. |
| Seam | aligned |

## Step 1: print the test coupon first (about 1 hour, 60 g)

`test_coupon.stl` has:

- **3 print-in-place spinners** standing on the bed beside the plate, each next to 1, 2 or 3
  dots on the plate edge: gaps 0.35, 0.45 and 0.55 mm
- the slip fits used on the machine:
  - a 16 mm stake/tray socket
  - a hex socket for the shaft couplers
  - the ring-sleeve counterbore
  - the drive journal hole
  - an M8 nut thread

Also print one `hex_coupler`, one `ring_sleeve`, one `bolt8_28` and the `stake_cap`, and try
them in the coupon.

| Result | Do this |
|---|---|
| Spinner 2 (0.45, two dots) turns freely after a firm first twist | ✅ keep `pip_gap = 0.45` |
| Spinner 2 is stuck, spinner 3 turns | set `pip_gap = 0.55` in `cad/params.scad`, run `python3 cad/check_parts.py` |
| Spinner 1 already turns freely | your printer is precise; 0.45 still works (0.35 only if you want less wobble) |
| The coupler, sleeve or spigot won't go in | set `fit_gap = 0.25` (default 0.20) and regenerate |
| They rattle | set `fit_gap = 0.15` and regenerate |
| The bolt won't screw into the coupon's nut thread | set `thread_gap = 0.40` (default 0.32) and regenerate |
| The bolt wobbles in the thread | set `thread_gap = 0.25` and regenerate |

**Freeing print-in-place parts:** let them cool, then twist firmly in both directions. If one
won't move, put it in hot tap water (about 60 °C) for a minute and twist again. Never use
pliers on the rolling surfaces.

## Step 2: print in this order

Print each module completely and test it before starting the next, so a problem only costs
one module.

| # | Module | Parts | Test before moving on |
|---|---|---|---|
| 1 | Head | `drive_roller`, `drive_pin`, `head_side_a`, `head_side_b`, `gearbox`, 2 x `foot`, 7 x `bolt8_28`, 7 x `nut8` | assemble it on the table; turn the gearbox shaft socket by hand: the roller turns 2x, smoothly, with no tight spots |
| 2 | One station | `stake_1`, `station_bracket`, 2 x `wheel_unit`, 2 x `pin3`, `stake_cap` | wheels spin freely after the first twist |
| 3 | Tail | `tail_side_l`, `tail_side_r`, `tail_roller`, 2 x `takeup_block`, 2 x `takeup_nut`, 2 x `takeup_screw`, `skid_l`, `skid_r`, 1 x `foot`, 6 x `bolt8_28`, 6 x `nut8`, 2 x `spike` | the knobs move the blocks along the full window; the roller spins |
| 4 | Anchors | 4 x `ground_screw`, `gs_wrench`, 4 x `washer50`, 4 x `bolt8_28` | screw one into your lawn and pull on it |
| 5 | Other stations | `stake_2` to `stake_4`, 3 x `station_bracket`, 6 x `wheel_unit`, 6 x `pin3` | |
| 6 | Line | `trap`, 5 x `chute_segment`, `crank_head`, `crank_arm`, 7 x `hex_coupler`, 6 x `ring_sleeve`, 1 x `pin3` (counts for 2 x 7 in risers; see `cad/parts-table.md`) | stack two segments on the table: both shafts turn together |
| 7 | Porch stand | `post_lower` (2 if `cad/parts-table.md` says so), `post_upper`, `stand_tray`, 4 x `stand_shim`, 3 x `pin3` | slide the upper post fully into the lower one, then out to a pin hole |
| 8 | Belt joint | `splice_template` | |

Optional: 2 more `spike` (for the head's rear foot in soft turf).

## All parts

A copy of `cad/parts-table.md` for the default site (2 risers of 7 in). `cad/check_parts.py`
rewrites `cad/parts-table.md` whenever you change `cad/params.scad`. After you measure your
steps and re-run the calculator, take the quantities from that file: the number of chute
segments, couplers, sleeves and lower posts depends on your steps. Sizes are as the part sits
on the bed. "(diagonal)" parts are exported turned 45° so they fit across the 256 mm bed.
Grams are estimates from the meshes with the listed walls and infill.

| Part (STL) | Qty | Size on the bed, mm | Walls | Infill | ~g each | What it is |
|---|---|---|---|---|---|---|
| `test_coupon` | 1 | 150 x 93 x 20 | 3 | 15 % | 60 | PRINT FIRST: fit ladder (spinners 0.35/0.45/0.55, sockets, M8 nut) |
| `wheel_unit` | 8 | 30 x 30 x 115 | 2 | 15 % | 22 | station wheel, print-in-place (2 per station) |
| `station_bracket` | 4 | 28 x 109 x 16 | 4 | 30 % | 22 | station bracket (holds 2 wheels on the stake) |
| `stake_1` | 1 | 216 x 203 x 24 (diagonal) | 4 | 30 % | 45 | station 1 stake (nearest the sidewalk) |
| `stake_2` | 1 | 205 x 191 x 24 (diagonal) | 4 | 30 % | 43 | station 2 stake |
| `stake_3` | 1 | 194 x 180 x 24 (diagonal) | 4 | 30 % | 40 | station 3 stake |
| `stake_4` | 1 | 182 x 169 x 24 (diagonal) | 4 | 30 % | 38 | station 4 stake (nearest the steps) |
| `drive_roller` | 1 | 67 x 67 x 124 | 3 | 10 % | 94 | drive roller with 17T pinion |
| `drive_pin` | 1 | 20 x 20 x 35 | 4 | 100 % | 5 | drive roller A-side journal pin (press in) |
| `head_side_a` | 1 | 206 x 196 x 6 | 4 | 30 % | 73 | head side frame A (round journal hole) |
| `head_side_b` | 1 | 237 x 196 x 6 | 4 | 30 % | 88 | head side frame B (open journal slot, gearbox mount) |
| `gearbox` | 1 | 94 x 111 x 91 | 3 | 10 % | 99 | gearbox: 34T crown gear rotor in its housing, print-in-place |
| `trap` | 1 | 103 x 37 x 152 | 3 | 15 % | 32 | drop trap (bottom of the chute, rests on the head frames) |
| `foot` | 3 | 36 x 196 x 24 | 4 | 30 % | 30 | foot crossbar (2 head, 1 tail rear) |
| `tail_side_l` | 1 | 227 x 218 x 28 | 4 | 30 % | 70 | tail side frame, left (-Y) |
| `tail_side_r` | 1 | 227 x 218 x 28 | 4 | 30 % | 70 | tail side frame, right (+Y) |
| `tail_roller` | 1 | 45 x 45 x 90 | 3 | 10 % | 46 | tail roller, print-in-place |
| `takeup_block` | 2 | 22 x 24 x 36 | 4 | 40 % | 12 | take-up block (one per side) |
| `takeup_nut` | 2 | 16 x 16 x 8 | 4 | 100 % | 2 | take-up square nut |
| `takeup_screw` | 2 | 21 x 22 x 108 | 4 | 100 % | 11 | take-up screw with knob |
| `skid_l` | 1 | 239 x 59 x 24 | 4 | 30 % | 46 | tail skid, left |
| `skid_r` | 1 | 239 x 59 x 24 | 4 | 30 % | 46 | tail skid, right |
| `chute_segment` | 5 | 167 x 136 x 230 | 2 | 15 % | 114 | chute segment with print-in-place drive shaft |
| `crank_head` | 1 | 186 x 156 x 180 | 3 | 15 % | 134 | crank head: funnel + crank shaft, print-in-place |
| `crank_arm` | 1 | 138 x 28 x 78 | 3 | 25 % | 50 | crank arm with spinning grip, print-in-place |
| `pin3` | 14 | 7 x 7 x 26 | 3 | 100 % | 0 | 3 mm pin: wheel pegs (8), crank arm, crank-head socket, stand height, tray (4), spares (2) |
| `splice_template` | 1 | 78 x 82 x 6 | 3 | 20 % | 13 | belt sewing template (box-and-X hole pattern) |
| `stand_shim` | 4 | 40 x 22 x 3 | 3 | 100 % | 3 | shims to level the porch stand foot |
| `hex_coupler` | 7 | 13 x 11 x 23 | 3 | 100 % | 3 | hex coupler between shafts |
| `ring_sleeve` | 6 | 25 x 25 x 8 | 3 | 100 % | 2 | sleeve between bearing rings |
| `post_lower` | 1 | 229 x 233 x 22 (diagonal) | 4 | 30 % | 53 | porch stand post, lower |
| `post_upper` | 1 | 226 x 226 x 20 (diagonal) | 4 | 30 % | 51 | porch stand post, upper |
| `stand_tray` | 1 | 190 x 236 x 32 | 4 | 20 % | 40 | porch stand foot (put the candy bowl on it) |
| `ground_screw` | 4 | 26 x 26 x 150 | 3 | 30 % | 27 | ground screw (head front foot, tail skid rear anchors) |
| `spike` | 4 | 134 x 30 x 30 | 3 | 30 % | 20 | L spike with nail head: 2 for the tail skid far pads, 2 optional for the head rear foot |
| `stake_cap` | 1 | 22 x 22 x 28 | 3 | 30 % | 6 | push the stakes in through this cap |
| `gs_wrench` | 1 | 160 x 33 x 24 | 3 | 30 % | 27 | T-wrench for the ground screws |
| `bolt8_28` | 17 | 13 x 15 x 33 | 4 | 100 % | 2 | printed M8 bolt (13 frame joints + 4 ground screws) |
| `nut8` | 13 | 13 x 15 x 7 | 4 | 100 % | 1 | printed M8 nut |
| `washer50` | 4 | 50 x 50 x 3 | 3 | 100 % | 7 | 50 mm washer over a ground screw |

Filament for one machine (test coupon excluded): **about 2.49 kg** (estimate from the meshes; your slicer gives the real number).

## Plates (suggested groupings)

| Plate | Parts |
|---|---|
| Small parts 1 | 17 x `bolt8_28`, 13 x `nut8`, 14 x `pin3`, 7 x `hex_coupler`, 6 x `ring_sleeve`, 2 x `takeup_nut`, `drive_pin` |
| Small parts 2 | 4 x `washer50`, 4 x `stand_shim`, `stake_cap`, `splice_template`, 2 x `takeup_block` |
| Wheels | 4 x `wheel_unit` per plate (2 plates) |
| Each frame, skid, stake, post | one per plate (they fill the bed) |
| Chute segments | 1 per plate (230 mm tall; brim on) |

**Printing time** (P2S, PLA, 0.2 mm): roughly 50-70 h in total. Start with the test coupon and
the head module now; you have about 18 days to Halloween.

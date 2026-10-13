# Printing guide (Bambu Lab P2S, PLA)

All STL files are in [`../stl/`](../stl/). Each one is already oriented the way it should sit
on the build plate. **No supports are needed on any part.** Every part fits the P2S's
256 x 256 x 256 mm volume with at least 10 mm to spare.

## 0. Order of work: test first, then print in batches

1. **Wait for the belt** before printing the rollers, sliders, spacers or hood. Measure it
   (width in 3 places, thickness), set `belt_w` / `belt_t` in `cad/params.scad`, and
   re-export (see the end of this page). Plates, crank parts, sprockets and jigs don't
   depend on the belt, so you can print them now.
2. **Print the test set** (about 90 g, about 3 h) and check it against the criteria below.
3. Print everything else.

## 1. Test prints: the smallest set that proves the risky fits

| # | Part (file) | g | Proves | Pass if | If it fails |
|---|---|---|---|---|---|
| T1 | `test_coupon.stl` | 16 | 608 press fit, 1/4 in and 5/16 in clearance holes, both nut traps, spacer slip fit | A bearing presses in with thumb pressure or a vise, can't be pulled out by hand and doesn't rock. Both threaded rods slide through freely. Nuts press into the hex traps and stay. A printed spacer slides into the last hole. | Bearing loose: set `brg_fit` 0.05 smaller. Too tight to press: 0.05 larger. Rod binds: raise `bolt_hole` / `axle_hole` by 0.2. Re-export. |
| T2 | `sprocket16.stl` | 20 | Tooth form against your real chain | Wrapped by hand around half the sprocket, every chain roller drops fully into its seat, nothing rides on a tooth tip, and the chain lifts off without snagging. | Rollers ride high: raise `seat_r` by 0.1 (the `+ 0.15` term in `conveyor.scad`). Chain binds sideways: set `chain_tooth_t` 0.2 thinner. |
| T3 | `tail_half.stl` x 2 | 48 | Roller printing quality, bearings in a real part, the castellated joint, rolling on the axle | Bearings press in. One half turned over locks into the other with no rocking. On a 5/16 in rod with spacers, the roller spins freely for several turns. | Same fixes as T1 (`brg_fit`). If the joint is too tight, sand the teeth. |
| T4 | `slider.stl` x 1 | 5 | Rung fit and belt lip height | Slides onto the 1/4 in rod. With the belt laid across it, the side lips are about level with the belt's top surface and the belt fits between them with about 2 mm on each side. | Re-measure the belt and update `belt_w` / `belt_t`. |

The tail halves and slider are real parts, so a passing test isn't wasted filament.

## 2. Slicer settings

Use Bambu Studio's **Generic PLA** (or your brand's) profile, 0.4 mm nozzle, **0.20 mm**
layers, **4 top and 4 bottom layers**, gyroid infill, brim **off** except where noted.

| Part | Qty | Walls | Infill | Notes |
|---|---|---|---|---|
| `drive_half` | 2 | 2 | 8 % | flange on the plate; the two halves are identical |
| `sprocket16` | 1 | 4 | 30 % | teeth on the plate (accurate first layer matters: clean the plate) |
| `tail_half` | 2 | 2 | 8 % | identical halves |
| `spacer_outer` | 4 | 3 | 100 % | tiny; print together |
| `spacer_inner` | 2 | 3 | 100 % | 3 mm brim (tall, thin) |
| `head_plate` | 2 | 4 | 25 % | same part both sides |
| `tail_plate_left`, `tail_plate_right` | 1 + 1 | 4 | 25 % | mirror images; lug faces up |
| `takeup_block` | 2 | 4 | 40 % | |
| `slider` | 6 | 3 | 15 % | 3 mm brim; print all 6 at once |
| `return_slider` | 5 | 3 | 15 % | 3 mm brim |
| `sprocket24` | 1 | 4 | 25 % | teeth on the plate |
| `crank_arm` | 1 | 4 | 30 % | arm on the plate |
| `crank_spacers` | 1 | 3 | 100 % | 3 spacers on one file |
| `grip` | 1 | 3 | 10 % | |
| `crank_clamp` | 1 | 4 | 30 % | |
| `hood_right`, `hood_left` | 1 + 1 | 3 | 15 % | cheek on the plate |
| `return_plow` | 1 | 3 | 20 % | |
| `drill_jig` | 1 | 3 | 15 % | |
| `test_coupon` | 1 | 3 | 15 % | |

Filament, estimated from the part volumes with these settings (`cad/check_parts.py`):
see the table that script prints. Expect **about 0.6 kg**, and allow 0.7 kg for the tests
and one reprint. Print time isn't calculated here; from the volumes, expect very roughly
**20-25 hours** of printing on the P2S. Your slicer will give the real number.

### Suggested plates

1. `test_coupon`, `sprocket16`, `slider` (test set, part 1)
2. `tail_half` x 2 (test set, part 2)
3. `drive_half` x 2
4. `head_plate` x 2, `tail_plate_left`, `tail_plate_right`, `takeup_block` x 2
5. `slider` x 5, `return_slider` x 5, `spacer_outer` x 4, `spacer_inner` x 2, `crank_spacers`
6. `sprocket24`, `crank_arm`, `grip`, `crank_clamp`
7. `hood_right`, `hood_left`, `return_plow`, `drill_jig`

## 3. PLA outdoors: what to watch

* **Heat.** PLA starts to soften around 55-60 °C. A black part in direct sun, or anything left
  in a closed car, can get there. Print the load-carrying parts (plates, take-up blocks,
  clamp, sprockets, crank) in a light colour, and set the conveyor up in the late afternoon.
  On Halloween night heat is not an issue.
* **Creep.** PLA slowly deforms under constant load. The design keeps sustained loads low:
  the belt tension on each tail plate is about 60 N. Steel threaded rod carries all the
  bending, and PLA only sees bearing and compression. Don't over-tension the belt (see the
  setup guide), and loosen the take-up after Halloween.
* **Cold brittleness.** PLA gets more brittle in the cold. Don't hammer printed parts; tap
  bearings in with a vise or a wooden block.
* **Sunlight (UV).** A few hours or days don't matter. Store the parts indoors between years.

## 4. Re-exporting after a parameter change

You need [OpenSCAD](https://openscad.org) (free). From the `conveyor/cad` folder:

```
python3 check_parts.py            # renders every part to stl/, then runs every check
```

It also re-runs all the collision checks. Copy the parts you need from `cad/stl/` (not the
`chk_*` files) to the printer. To export one part by hand:

```
openscad -o drive_half.stl -D 'part="drive_half"' conveyor.scad
```

Then re-run `python3 ../calc/conveyor_calc.py`, which reads the same parameters, so the
belt length, bolt checks and stake heights stay consistent.

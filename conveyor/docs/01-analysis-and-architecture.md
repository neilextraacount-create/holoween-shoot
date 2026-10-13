# Candy conveyor: engineering analysis and design

Status: **design complete and checked in CAD; not yet built or physically tested.**
Every number on this page comes from [`../calc/conveyor_calc.py`](../calc/conveyor_calc.py)
or [`../cad/check_parts.py`](../cad/check_parts.py), which both read the same parameter file
([`../cad/params.scad`](../cad/params.scad)).

![Side profile, 2 risers](side-profile-2-risers.svg)

## 1. The design in one paragraph

**One straight conveyor, 24.5 ft axle to axle, tilted about 7°, that bridges over the porch
steps** instead of following them. The belt is a single loop of **3 in black polypropylene
webbing**, sewn in place. It slides over thin printed sliders carried on threaded-rod rungs,
between two **1x3 wooden rails** held up by **five pairs of 2x2 stakes**. All three rotating
parts (drive roller, tail roller, crank wheel) **spin on skateboard bearings around fixed
rods**, so no threaded joint ever carries the crank torque. A **bicycle chain** with printed
24T/16T sprockets lifts the crank to about 30 in above the porch floor. Belt tension and
tracking come from **two independent screw take-ups** at the tail.

## 2. Site and geometry

| Item | Value | Status |
|---|---|---|
| Lawn | 250 in at 5° (21.9 in of fall) | given |
| Steps | 20 in horizontal | given |
| Riser height and count | 2 x 7 in (porch 35.9 in above the lawn edge); 3 risers also checked | **riser height ASSUMED: measure it and run the calculator with `--rise` and `--risers`** |
| Basket rim | 7.5 in, so the belt top at the tail is 10.5 in | change with `--basket` |

**Why the conveyor bridges over the steps instead of following them:** the steps are about 35°
steep. At 35°, wrapped candy slides (tan 35° = 0.70 is more than the wrapper-to-webbing
friction). Worse, where the steep part meets the lawn the belt would have to bend through a
valley, and belt tension lifts a belt off its supports at a valley. A straight line has no
bends at all. It costs only taller stakes near the porch.

Results (2 risers; the 3-riser case is in `calc/report-3-risers.txt`):

| | |
|---|---|
| Slope | 6.7° (8.1° with 3 risers); candy stays put up to well over 15° |
| Tightest clearance | return run 4.5 in above the porch edge (4.2 in with 3 risers) |
| Stakes | 5 stations, 54.5 in apart, the last one at least 24 in before the first riser. Belt top 11.8-18.4 in above the grass (12-24 in with 3 risers) |
| Over the steps | the rails span about 4 ft between the last stake and the porch, plus one rails-only rung |
| Tail | 9.8 in past the lawn edge, over the sidewalk; the basket slides under it |

**If the conveyor goes over the steps, nobody can use the steps while it's installed.** If
the steps must stay usable, run it beside them. The geometry is the same.

## 3. Loads (estimates, not measurements)

| Quantity | Value | Basis |
|---|---|---|
| Belt | 0.061 kg/m | 6.2 lb per 150 ft from the seller's listing |
| Candy | 0.15 kg/m | one 15 g fun-size piece every 10 cm (dense) |
| Pretension | 60 N per run | set with the can test |
| Carrying-run sag between stations | 10.4 mm | w·L²/8T over 1.38 m |
| Running resistance | 17 N estimated, **25 N design** | belt sliding on 11 PLA sliders (μ 0.3), belt bending, an allowance for edge rub, bearings; candy going downhill helps a little |
| Drive grip | needed T₁/T₂ = 1.53; inner-tube lagging gives 4.8; **bare PLA when wet gives only 1.87, so the lagging is required** | Euler capstan, 180° wrap |
| Crank | 1.72 N·m, **17 N (3.9 lbf) at the handle** | 25 N x roller radius x 1.5 / 0.9 efficiency |
| Speed | crank 45 rpm, belt 0.29 m/s, **candy reaches the basket in about 26 s (19 turns)** | |
| Rail compression | about 60 N per rail; buckling capacity about 1000 N | Euler, weak axis, 54.5 in span |
| Wind (20 mph) | about 1.2 lbf per station | |

The loads are tiny. Nothing fails by breaking. The real risks are **tracking, wet slip,
belt creep, stakes moving, and PLA creep**, and the design targets those.

## 4. Architecture decisions

### 4.1 One continuous belt, not modules
Modules would mean several sewn loops, several tensioners, a drive linkage across every
joint, and candy hand-offs that jam. One straight belt has exactly one of each. The **frame**
is modular: the rails split into three 8 ft sections for storage.

### 4.2 Belt: 3 in heavy polypropylene webbing
| Option | Verdict |
|---|---|
| Plain rubber or neoprene strip | ❌ stretches about 8 % at belt tension |
| Reinforced PVC conveyor belt (the "tarp" kind) | ✅ technically ideal, ❌ on Amazon only 4 in wide; 50 ft pieces were unavailable; needs metal lacing |
| **3 in heavy polypropylene webbing, Country Brook 50 yd** | ✅ **selected**: 1.7 mm, 2,100 lb; at 60 N it runs at 0.6 % of its break strength; doesn't absorb water; black; can be sewn into a loop |

It is sewn into a loop **in place on the frame** after measuring, with a 75 mm lap and a
box-and-X stitch. The underneath end points toward the porch so its edge trails over the fixed
sliders.

### 4.3 Supports: wooden rails on 2x2 stakes, joined by threaded-rod rungs
* PLA stilts alone can't do the job. The rails are what keep the two rollers apart against
  120 N of belt tension, and what keep 24 ft straight enough for the belt to track.
* Each station has two **1/4-20 threaded-rod rungs** through stake, rail, slider, rail,
  stake. The upper rung carries the belt slider and sets the rail gap; the lower one
  carries the return slider. Nuts on both sides of each stake hold it **wherever it was
  driven**, so stakes need no precise spacing, and the single-rod joint pivots to any slope.
* Height adjustment: you drill the stakes on site at the height the frame actually sits.
  That is unlimited, exact adjustment with no printed slot.

### 4.4 Belt supports: fixed sliders, not rotating idlers
The belt slides over **fixed PLA sliders**: thin sleeves on the rungs with low edge lips.
They also act as the spacers that set the rail gap. Compared with rotating idlers they use
much less filament, have no bearings, and **a slightly crooked slider doesn't steer the
belt** (a crooked roller would). The cost is about 10 N of extra friction, which is in the
budget above.

### 4.5 Drive: chain to a standing-height crank, no gearbox
| | Crank directly on the roller | **Chain + printed sprockets** | Printed bevel gears |
|---|---|---|---|
| Handle height | about 7 in off the porch floor (crouching) | **about 30 in** | about 30 in |
| Tolerates a wooden post flexing | n/a | **yes** | no (gears skip) |

A reduction gear isn't needed. Turning the crank is already easy (4 lbf); the real issue is
the number of turns, so the chain is a 1:1.5 **step-up**.

### 4.6 Rotating parts on fixed rods
The drive roller (two identical halves that lock together, plus a 16T sprocket that drives
it through 3 lugs), the tail roller (two identical halves) and the crank wheel (arm with
bearing hub plus a hex-keyed 24T sprocket) each spin on two 608 bearings around a
**non-rotating** 5/16 in rod. Torque only ever passes through printed lugs and hex sockets.
Nothing can unscrew.

## 5. Risks and what handles them

| Risk | Handled by |
|---|---|
| Belt walks sideways | crowned rollers (0.4 / 0.3 mm), independent left/right tail screws (tracking rule in the setup guide), slider lips as a backstop |
| Drive slips when wet | inner-tube lagging (required); can-test tension; 180° wrap |
| Webbing creeps | sewn in place to the measured length; 30 min run-in; 90 mm take-up (absorbs 150 mm) |
| Candy misses the basket | the basket slides **under** the tail end, rim at least 3 in below the belt |
| Small candy falls into the side gap | the return-run plow wipes it off before the drive roller |
| Fingers at the drive roller and chain | printed hood over the roller and the chain at its sprocket; low tension (60 N) |
| PLA heat and creep | light-coloured parts; nothing printed carries sustained bending; the can test caps tension at 80 N |
| Stakes hit pipes or cables | call 811; flag sprinklers; steel-rod pilot hole |
| Trip hazard in the dark | LED string and reflective tape |
| Unknowns | full driveway trial by Oct 22, site trial by Oct 25 |

## 6. What has and hasn't been verified

Verified in software:
* All 21 printed parts render, are closed solids, and fit the P2S.
* 33 interference checks between the moving and fixed parts at the head, the tail (at both
  ends of take-up travel), a stake station, the crank and the chain all pass, each with a
  measured minimum gap.
* The site geometry, stake heights, belt length, bolt thread engagement, chain length and
  loads are computed from the same parameters.

Not verified (only a build can show these):
* How the belt actually tracks over 24 ft, real friction values, how much the webbing
  creeps, how fast the PLA sliders wear, soil holding. The test prints and the two trial
  runs exist to catch these before Halloween night.

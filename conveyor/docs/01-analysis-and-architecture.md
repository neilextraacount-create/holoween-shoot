# Candy conveyor v4: analysis and design

Status: **designed and checked by computer; not yet built or physically tested.** The numbers
here come from [`../calc/conveyor_calc.py`](../calc/conveyor_calc.py) (site, loads) and
[`../cad/check_parts.py`](../cad/check_parts.py) (geometry, fits, clashes). Both read the same
parameter file, [`../cad/params.scad`](../cad/params.scad).

![Side profile, 2 risers](side-profile-2-risers.svg)

## 1. What you asked for, and what changed

You asked for:

- a handle at the top that is easy to turn and moves the candy fast
- a belt about 6 in off the ground that drops candy into a basket and returns underneath
- small stilts with a wheel on top, the belt going over and under them
- gears at the top
- everything printed in PLA except the belt, as much as possible print-in-place
- coverage of 2 steps (20 in) plus 250 in of lawn at 5°

All of that is in the design, with three changes that make it work better than a literal
version:

| Your idea | What the design does | Why |
|---|---|---|
| Belt starts at the top of the steps | The **belt runs only along the lawn**. A printed **chute** brings the candy down the steps, and a **drive shaft** beside the chute brings your cranking down to the belt. | The steps are about 35° steep. Candy slides on a belt that steep, and where the steep part meets the lawn the belt would have to bend through a valley. Belt tension lifts a belt out of a valley, so it would need hold-down rollers right where the candy is. A chute handles a steep drop easily. |
| One wheel on each stilt | **Two** wheels on each stilt: the belt rides **over** the top one and comes back **under** the bottom one. | That is what keeps the return run off the grass. |
| "A couple of gears that make it move fast" | **One gear pair (2:1 step-up)**: a 34-tooth crown gear on the shaft drives a 17-tooth pinion on the drive roller. | 2:1 gives 0.3 m/s belt speed at a relaxed 45 rpm with 11 N at the handle. More step-up would make the crank harder to turn for little gain, because the belt's friction (not its speed) is what you feel. |

## 2. Site and layout (2 risers; 3 risers is in `calc/report-3-risers.txt`)

| Item | Value | Status |
|---|---|---|
| Lawn | 250 in at 5° (21.9 in of fall) | given |
| Steps | 20 in total run to the porch | given |
| Riser height | 2 x 7 in, so the porch is 35.9 in above the sidewalk | **ASSUMED: measure** |
| Belt | 20.2 ft axle to axle, 4.25° slope; belt top 6 in above the lawn at the head and 9 in above the sidewalk at the tail | |
| Drive roller (head) | 10 in before the first riser | |
| Tail roller | 2 in out over the sidewalk; the basket (rim no higher than 6 in) goes under it | |
| Stilt stations | 4, every 48.4 in; stakes pushed 150 mm into the lawn | |
| Chute | 40.3° to level, 5 segments; its underside clears the first step by 4.6 in | |
| Crank | 23.6 in above the porch floor, 9.9 in behind the porch edge (comfortable sitting on a porch chair; for standing, use 7 segments: 34 in) | |
| Porch stand | post 3.6 in behind the porch edge; socket 552 mm above the floor | |
| Belt loop | 41.0 ft; cut 43 ft and sew it in place | |

## 3. Loads (estimates, not measurements)

| Quantity | Dry PLA bearings | Waxed | Basis |
|---|---|---|---|
| Belt drag | 10.5 N | 6.9 N | tail roller V-bearing (μ 0.35 dry / 0.2 waxed, V-groove factor 1/sin45°), 8 station wheels, belt bending |
| Crank effort | **1.27 N·m = 12 N (2.6 lbf)** | 0.97 N·m = 9 N | drag x roller radius x 2 + journal friction, 85 % gear and 90 % shaft-line efficiency |
| Grip needed on the drive roller | μ ≥ 0.17 | μ ≥ 0.11 | capstan equation, 180° wrap, 20 N pretension per run; ribbed PLA on webbing is roughly 0.3 dry, 0.2 wet |
| Belt sag between stations | 14 mm light candy, 27 mm dense | | w·L²/8T over 1.23 m |
| Speed | crank 45 rpm → belt 0.30 m/s; about 21 s from chute to basket | | |
| Candy speed at the bottom of the chute | 2.6-3.1 m/s | | sliding friction 0.3-0.45; the drop trap stops it |
| Tail tipping | 48 N uplift on the two skid ground screws (24 N each) | | 40 N belt pull acting 207 mm above the ground, 172 mm tipping arm |
| Head tipping | 28 N uplift on the front foot's two ground screws (14 N each) | | 120 mm height, 170 mm arm |

Stresses in the PLA parts are all below 7 MPa at twice the dry crank torque (calculator,
"PLA STRESS CHECKS"), compared with roughly 20-30 MPa for PLA pulled apart across its layers.
**Nothing should break.** The real risks are slip, tracking, print fits and anchors (section 6).

## 4. Architecture

### 4.1 Belt: 3 in heavy polypropylene webbing (the only bought part)

| Option | Verdict |
|---|---|
| Rubber or neoprene strip | ❌ stretches about 8 % under tension, so it would never stay tight |
| PVC conveyor belting (the "tarp" kind) | ❌ only 4 in wide on Amazon, needs metal lacing |
| Nylon webbing | ❌ stretches when wet |
| **Country Brook 3 in heavy polypropylene webbing, 50 yd** | ✅ 76 x 1.7 mm, 2,100 lb, black, does not absorb water, can be sewn into a loop |

Polypropylene webbing barely stretches (about 4.5 mm over the whole 41 ft loop at the design
tension). That makes it easy to over-tighten, so the take-up is a fine screw (3 mm per turn)
and you set the tension with the "can test" (build guide).

### 4.2 Stations: stilts with two print-in-place wheels

Each station is an L-profile stake (printed lying flat, pushed 150 mm into the lawn) with a
socket on top. A bracket plugs into the socket and holds two **cantilevered print-in-place
wheel units**: the belt rides over the top one and comes back under the bottom one. Each wheel
spins on its axle on two 45° V-ridges with a 0.45 mm gap. The V shape holds the wheel on, takes
side loads, and prints without supports. Stakes are cut to length for each station so the belt
runs in a straight line (stake 1 is 284 mm long, stake 4 is 236 mm).

### 4.3 Head: drive roller and crown-gear gearbox

- **Drive roller**: Ø61.6 mm, crowned 0.3 mm (crowning centres the belt), 64 grip ribs, 2.5 mm
  flanges. The 17-tooth pinion (module 2.5) is part of the roller on side B. Side A runs on a
  separate pressed-in journal pin.
- **Frames**: two flat lattice plates (8 mm). Frame B has an open slot for the roller journal,
  because the pinion is bigger than a round hole could pass. Belt tension and the gear force
  both push the journal into the closed end of the slot. Above the belt, guard panels keep
  bouncing candy on the belt.
- **Gearbox (print-in-place)**: a 34-tooth crown gear with its shaft, inside its housing,
  printed as one piece with a 0.45 mm running gap. It bolts to frame B with 3 printed M8 bolts.
  The crown teeth are **generated by simulating the real pinion rolling through the mesh**
  (`make_crown.py`, 816 positions). The check finds no overlap at any position, 0.27 mm flank
  clearance, and the teeth engage within ±4° of pinion rotation.

### 4.4 Line: chute and drive shaft over the steps

Five identical segments, each 210 mm long and printed standing up. Each segment has:

- a **U-shaped candy chute**: 66 mm wide inside, 0.9 mm walls, with a socket at the lower end.
  The next segment's plain end slides into the socket from above, like roof shingles, so candy
  never meets a lip.
- a **print-in-place drive shaft**: Ø14 mm hollow, with one V-ridge bearing in a ring at each
  end, and hex sockets at both ends.
- two struts tying the rings to the chute.

Separate printed **hex couplers** join the shafts and **ring sleeves** line up the bearing rings.
The bottom of the line is a **drop trap**: an end wall and lid stop the candy, and it drops
33 mm through a floor slot onto the belt. The trap's upper end sits in segment 1's socket. Its
ledges rest just above the head frames' guard bars, and a stop post on each frame stops it
sliding downhill.

### 4.5 Crank head and porch stand

The crank head has the funnel, the top bearing pair, and a square drive for the crank arm. The
arm (110 mm) has a print-in-place spinning grip. A world-vertical socket under the funnel takes
the porch post (two L-profile pieces) on a cross-shaped foot. The foot needs weight on it: your
candy bowl. Hold the funnel rim with your other hand while cranking and the stand hardly feels
the crank. Without that it sways: 11 N at the handle pushes the stand sideways.

### 4.6 Tail: print-in-place roller and screw take-up

The tail roller (Ø40 mm, crowned) turns on a fixed axle. The axle's square ends sit in square
sockets in two **take-up blocks** that slide in windows in the tail frames. A knob screw
(Ø10 mm, 3 mm pitch) on each side pulls its block toward the sidewalk through a square nut.
That gives 60 mm of travel. Turning one knob more than the other steers the belt.

The tail frames bolt to two **skids** that reach 292 mm back onto the lawn. Ground screws hold
them down 120 mm in from the lawn edge (the uplift side) and spikes locate them at the far end.
A foot crossbar ties the frames together at the sidewalk end.

### 4.7 Fasteners and anchors (all printed)

- **M8 bolts and nuts**: round 2 mm thread, printed standing, used for clamping only.
- **Ground screws**: Ø15 mm shaft with a 45° buttress flight, so they print standing with the
  head down. A printed bolt and 50 mm washer clamp a foot onto the head. Driven with a printed
  T-wrench.
- **L-spikes** with nail heads, for the feet that are only pushed down.
- **Ballast instead of anchors**: if your soil won't hold screws, put 5 kg on the tail rear
  foot and 3 kg on the head front foot. Water jugs or bricks work.

## 5. What was checked by computer

`cad/check_parts.py` writes `cad/check-report.txt`. It checks:

- **Every part**: it renders without warnings, the mesh is watertight, it has the expected
  number of bodies (print-in-place parts have 2, with a gap of at least 0.30 mm), and it fits
  a 246 mm square on the P2S bed. Long stakes and posts are exported turned 45° so they lie
  across the diagonal.
- **Every mating pair, in its assembled position, with exact mesh booleans**:
  - **Slip fits**: journals 0.30 mm, sockets and spigots 0.20 mm, chute sockets 0.30 mm,
    sleeves 0.20 mm, hex couplers 0.20 mm.
  - **Clearances**: belt to frames, trap and feet; candy space above the belt; crown gear to
    roller; basket space under the tail roller; trap to the head frames.
  - **Tail positions**: the take-up blocks and screws are checked at in, middle and out.
  - **Full crank turn**: the crank arm is swept around the funnel.
  - **Steps**: the chute line is checked against a model of the steps and the stand foot
    against the porch edge.
- **Gear mesh**: in `make_crown.py`.

## 6. Risks, and what will tell you early

| Risk | How likely | Early warning / fix |
|---|---|---|
| Print-in-place parts fused | medium (depends on the printer) | **test coupon**: if the 0.45 mm spinner is stiff but 0.55 mm turns, set `pip_gap = 0.55` and re-export |
| Belt slips on the drive roller (wet) | medium | rub candle wax on the bearings (not on the roller); raise tension slightly; the calculator says μ 0.17 is needed and ribbed PLA gives about 0.2-0.3 |
| Belt walks off to one side | medium | crowned rollers centre it; steer with the two tail knobs (build guide) |
| Stakes lean in soft lawn | medium | pre-soak, push straight; the belt load on each stake is under 10 N |
| Ground screws pull out | low-medium | 24 N each is needed; if they spin freely, use ballast |
| Candy bounces out of the trap | low | the lid covers the impact zone; light candy is slower |
| Crank head sways | medium | hold the funnel rim while cranking; candy bowl on the foot |
| Riser height different from 7 in | **certain to need checking** | measure and re-run the calculator **before printing the chute and stand** |

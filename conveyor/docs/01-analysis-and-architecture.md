# Candy Conveyor: Stage 1 & 2, Engineering Analysis and Architecture

Status: **analysis complete, architecture selected, CAD not started.**
No part of this design has been built or physically tested. All numbers come from
[`../calc/conveyor_calc.py`](../calc/conveyor_calc.py). Re-run that script after you measure the site.

![Side profile](side-profile-2-risers.svg)

---

## 0. The recommendation in one paragraph

Build **one straight conveyor, about 24 ft between roller centres, tilted at about 7°**. It
**bridges over the porch steps** instead of following them. The belt is a single sewn loop
of **3-inch black polypropylene webbing**. It rides on small printed idler rollers between two **wooden
1×3 furring-strip rails**, and those rails are held up by **pairs of wooden stakes** with
printed height-adjustable saddles. The head roller (Ø80 mm) is driven directly through
a **bicycle chain and two printed sprockets (24T crank → 16T roller, 1:1.5)**, so the crank
sits at a standing-friendly height. The tail roller (Ø50 mm) has **independent left/right
screw take-ups**, which handle belt tension and belt tracking together. No gearbox is needed:
the belt needs only about 1 N·m to run, and the hand force is about 3 lbf.

---

## 1. Stage 1: Analysis

### 1.1 Site geometry (provisional)

| Item | Value used | Status |
|---|---|---|
| Lawn run / slope | 250 in @ 5° → 21.9 in fall | given |
| Steps run | 20 in | given |
| Step risers | 2 × 7 in (porch 35.9 in above lawn edge) | **ASSUMED: must measure** |
| Head roller position | 12 in back from porch edge, belt top 9 in above porch floor | design choice |
| Tail roller position | overhangs lawn edge by 4 in, belt top 9 in above ground | depends on basket height |

### 1.2 Why the steps decide the architecture

The lawn is 5°, but the steps are about 35° (14 in of rise in 20 in of run). A belt can't follow that
profile without serious problems:

* **The lawn-to-steps transition is concave (a valley).** Belt tension pulls the belt
  *off* the idlers at a valley and straight across it. Keeping it down needs hold-down rollers
  *on top of the belt*, and those would block the candy.
* **At 35°, candy slides and tumbles.** tan 35° = 0.70, which is more than the friction between a wrapper and webbing
  (typically 0.3 to 0.6). On a 7° belt (tan 7° = 0.12), candy stays put by a wide margin.
* **A straight line has no transitions at all.** It only needs to be steeper than the lawn,
  so that it clears the porch edge.

Result from the calculator (2-riser case):

| Point | Belt top above ground | Return run above ground |
|---|---|---|
| Porch edge | 7.5 in | **4.2 in** (tightest spot) |
| Top of first riser | 12.0 in | 8.8 in |
| Mid lawn | 14.2 in | 11.6 in |
| Lawn edge (basket end) | 9.5 in | 7.3 in |

If the porch has **3 risers** (two treads + porch), the line steepens to 8.5° and the
upper lawn stakes need about 25 in of height, which still works (see `calc/report-3-risers.txt`).
Either way, the steps cost us **taller stakes near the porch, not a more complicated machine**.

> ⚠️ **Practical point:** if the conveyor passes *over* the steps, nobody can use the steps
> while it's installed. If the steps must stay usable, run it **beside** the steps (over a
> flowerbed or the lawn next to them). The geometry is identical; only the ground under it changes.

### 1.3 Loads (estimated, not measured)

| Quantity | Estimate | Basis |
|---|---|---|
| Belt mass | ≤ 0.10 kg/m | assumed upper bound for heavy 3" PP webbing |
| Candy on belt | 0.15 kg/m | one 15 g fun-size piece every 10 cm (dense) |
| Belt pretension | 40 N per run | set with take-up |
| Carrying-run sag, 24 in idler pitch | 3.9 mm | w·L²/8T |
| Return-run sag, 48 in pitch | 3.7 mm | w·L²/8T |
| Running resistance | ≈ 8 N estimated → **20 N design** | idler bushings + belt bending + 5 N edge-rub allowance; candy going downhill *helps* slightly |
| Rail compression from belt tension | ~40 N per rail | belt tension is reacted *inside* the frame |
| Rail buckling capacity (48 in span) | ~1300 N | Euler, weak axis, pine E = 1.2 Mpsi |
| Rail sag between stations | 0.1 mm | negligible |
| Wind, 20 mph | ~6 lbf total, ~1 lbf per station | 0.00256·V² × side area × 1.2 |
| Drive bearing load | ~80 N | trivial for 608 ball bearings |

**Takeaway:** the forces are tiny. Nothing fails from overload. The realistic failure
modes are all about **alignment and slip**:

1. **Belt tracking.** A 24-ft belt wandering sideways and rubbing a rail.
2. **Drive slip when wet.** Dew on the lawn wets the webbing.
3. **Belt stretch/creep.** Polypropylene creeps, so the belt loses tension over the evening.
4. **The ground moving.** A stake loosens and the line goes out of straight.
5. **PLA creep under constant load.** Mainly the take-up parts, which hold tension for hours.

The design work below goes into those five, not into raw strength.

### 1.4 Drive calculation

| | |
|---|---|
| Head (drive) roller | Ø80 mm over rubber lagging |
| Chain | 24T on crank → 16T on roller = 1 : 1.5 step-up |
| Crank 45 rpm | → roller 68 rpm → belt **0.28 m/s (0.9 ft/s)** |
| Candy transit, 7.3 m | **≈ 26 s ≈ 19 crank turns** |
| Torque at roller | 20 N × 0.040 m = 0.8 N·m |
| Torque at crank | 0.8 × 1.5 / 0.9 = 1.33 N·m |
| Hand force (100 mm crank arm) | **≈ 13 N ≈ 3 lbf** |
| Drive grip check (Euler capstan, 180° wrap) | needed T₁/T₂ = 1.67; rubber lagging (μ≈0.5) gives 4.8, bare PLA (μ≈0.25) gives 2.2. **OK with margin.** |

**Is a reduction gear needed? No.** A reduction makes cranking *easier* but *slower*,
and cranking is already easy (3 lbf). The real problem is the number of turns, so a
modest **step-up** (1:1.5) is the right direction. You can push it to 1:2 by swapping
one printed sprocket if you want faster delivery; the hand force rises to about 4 lbf.

Note that because the carrying run moves *away* from the drive roller, the **carrying run is the
slack side** and the return run is the tight side. That's fine at these loads, and the calculator
already uses the lower tension for carrying-run sag.

### 1.5 Major risks and how the design addresses them

| Risk | Mitigation |
|---|---|
| Belt walks off sideways | Crowned head and tail rollers, plus independent L/R tail take-up screws to steer it, plus rails act as last-resort edge guides |
| Drive slips when dew-wet | Bicycle inner-tube lagging on the drive roller; 180° wrap; tension adjustable while running |
| Webbing stretches over the evening | Pre-stretch before sewing (hang under load overnight); 150 mm take-up travel absorbs 300 mm (2 %) of growth |
| PLA creep/softening | No PLA part carries tension in bending or tension; steel bolts and threaded rod carry the load and PLA only sees bearing/compression. Print loaded parts in a light colour; never leave them in hot sun or a hot car |
| Crank at floor level | Chain tower puts the crank axle about 30 in above the porch (standing operation) |
| Pinch points | Belt-to-roller nips are on the *inside* of the belt, below the rail tops. Printed guards over the head roller and chain. Low tension (40 N) limits the severity, but it's still a machine: keep small children's hands off it |
| Steps blocked | Route beside the steps if they must stay usable |

### 1.6 Measurements that must be verified before CAD is finalised

1. **Porch floor height above the lawn** where the conveyor crosses the porch edge, plus the
   number of risers and the horizontal run of the steps along the conveyor's path. *(Critical: this sets the slope,
   stake lengths and chain/crank height.)*
2. **Basket rim height**. Belt top at the tail should be about 1.5 in above the rim. Provisional: 9 in belt top, rim ≤ 7.5 in.
3. Lawn slope along the *actual* path (a phone level app on a straight board is good enough).
4. Whether the conveyor goes **over** or **beside** the steps.

---

## 2. Stage 2: Architecture selection

### 2.1 Options compared

| Criterion | **A: One continuous straight belt** | A′: One belt that follows steps + lawn | B: Modular sections |
|---|---|---|---|
| Belt loops to make | 1 | 1 | one per module (3–6) |
| Splices that can fail | 1 | 1 | 3–6 |
| Rollers with bearings | 2 | 2 + hold-down rollers at the valley | 2 per module |
| Candy hand-off between belts | none | none | at every joint, where candy jams or drops |
| Drive | one crank drives everything | same | every module must be driven (linked shafts/chains across joints) |
| Steepest candy slope | ~7–8.5° | ~35° on the step section (candy slides) | can be stepped, but each drop is a jam point |
| Tension/tracking adjustments | 1 set | 1 set + hold-downs | 1 set per module |
| Printed parts | fewest | more | most (≈ 2–3× A) |
| Transport/storage | rails come apart into 8-ft pieces; belt rolls up | same | slightly shorter pieces |
| Stake height | up to ~19–25 in near the porch | short everywhere | short everywhere |

### 2.2 Decision: **Option A, one continuous straight belt**

Modular construction would mean **several splices, several tensioners, and a drive linkage
crossing every joint**, plus candy transfer points, all to avoid taller stakes on the last
few feet of lawn. A′ fights belt physics at the valley and makes candy slide on the step section.
A straight belt has exactly one of everything.

*Modularity is kept where it actually helps:* the **frame** (rails) splits into 8-ft
lengths for storage, and every stake station is identical and interchangeable. The
**belt** is the one continuous part.

### 2.3 Belt material selection

| Option | Stretch at 40 N, 14.9 m loop | Joining | Cost (see sources) | Verdict |
|---|---|---|---|---|
| Unreinforced rubber/EPDM/neoprene strip | ~8 % (≈1.2 m!) plus creep, from E ≈ 4 MPa | glue | moderate | ❌ stretches far too much |
| PVC/rubber *fabric-reinforced* conveyor belting | very low | vulcanised or metal lacing, by the supplier | quote-only; typically sold to industry | ✅ technically ideal, ❌ cost/availability |
| Treadmill belts | low | would need 5–6 belts spliced | free–cheap used | ❌ too many splices |
| **3" black heavy polypropylene webbing** | small at 40 N vs a multi-kN break strength; creeps a little | **sewn lap splice** | ~$18 for 25 yd (one listing, see BOM) | ✅ **selected** |
| 3–4" polyester webbing | lowest stretch/creep, better UV | sewn lap splice | 4" is sold in 100-yd rolls (~$174 in one listing) | ✅ upgrade if PP creeps too much |

**Why webbing works:** it is woven, so it's strong and has low stretch along its length, flexible enough to wrap a
Ø50 mm roller easily, black, slightly textured (candy won't slide at 7°), and **it can be made
endless with a needle and thread.** Polypropylene doesn't absorb water, which helps on a dewy lawn.

**Belt width:** 3 in (76 mm). Fun-size bars ride lengthwise. The rails stand 20 mm above
the belt as side walls, with 95 mm between them, so anything that turns sideways is still channelled.

**Splice (preview, full instructions in Stage 7):** pre-stretch the webbing, cut to about 49.3 ft,
overlap 125 mm, sew a **box-and-X pattern** with heavy bonded polyester thread (or a
Speedy-Stitcher awl), and heat-seal the cut ends. Lay the outer layer so its free edge
**trails** (points uphill on the carrying run), so nothing can catch it at the discharge.

### 2.4 Support structure decision

**PLA stilts alone can't do this job**, for three reasons:

1. **The belt tension has to be held between the rollers.** Stilts alone would let the head
   and tail lean toward each other. The rails carry about 40 N each in compression, and
   that's what keeps the loop tight.
2. **24 ft has to stay straight within a few mm** or the belt won't track. Separate stilts
   can't hold that line; continuous rails can.
3. **A PLA spike hammered into turf shatters,** and PLA creeps when loaded in bending for hours.

So the cheapest, stiffest structure is:

* **Rails:** 1×3 furring strips (actual 0.656 × 2.375 in), 3 per side, with spliced joints. About $2.50
  per 8-ft strip in a 10-pack. Printing an equivalent printed rail would take several kg of PLA.
* **Stakes:** pointed wooden grade/survey stakes, 24–36 in, driven in pairs every 48 in (6 stations).
* **Printed parts only where they add value:** a **saddle** that clamps the rail to the stake
  with a **vertical slot for ±1 in height adjustment** without re-drilling, and that also carries the
  return idler. Every station uses the same saddle part.
* **No cables or extra bracing needed:** the rail and stake rectangle, with stakes 12 in deep, has a large
  margin against about 1 lbf of wind per station and against bumps.

### 2.5 Drive selection

| | Direct crank on roller | Printed gear reduction | **Chain + printed sprockets** | Printed bevel gears + vertical shaft |
|---|---|---|---|---|
| Crank height | ~7 in above porch (crouching) | same | **~30 in (standing)** | ~30 in |
| Parts | fewest | +2–4 gears | +2 sprockets, 1 bought chain | +2 gears, needs a rigid tower |
| Tolerance to tower flex | n/a | n/a | **high** | low (gears skip) |
| Ratio change | no | reprint | reprint one sprocket | reprint |

**Selected: chain + printed sprockets.** The chain is the only option that lifts the crank to
standing height while tolerating a wooden tower that flexes a little. A standard 112–116 link
1/2 × 1/8 in bicycle chain fits at 23 in sprocket centres (112 links calculated).

### 2.6 Preliminary dimensions (to be frozen in Stage 3 after site measurements)

| Parameter | Value |
|---|---|
| Belt | 3 in (76 mm) PP webbing, ≈ 2 mm thick, loop ≈ 48.9 ft |
| Head (drive) roller | Ø80 mm incl. lagging, crowned, 2 × 608 bearings, 8 mm (M8 or 5/16") threaded-rod shaft |
| Tail roller | Ø50 mm, crowned, 2 × 608 bearings inside the roller, fixed 5/16" axle in slotted take-up brackets, 150 mm travel |
| Carrying idlers | Ø25 × 90 mm printed sleeves on 1/4" × 7 in bolts through both rails, every 24 in (~11) |
| Return idlers | same sleeve, every station under the rails (6) |
| Rail spacing (inside) | 95 mm |
| Stations | 6 stake pairs @ 48 in + porch head stand |
| Crank | 100 mm arm, rotating grip on a bolt, removable (wing nut) |
| Chain | 24T / 16T printed sprockets, 23 in centres |

### 2.7 Printed part count and filament (rough estimate)

| Part | Qty | ≈ g each | ≈ g total |
|---|---|---|---|
| Head roller (2 halves) | 1 | 70 | 70 |
| Tail roller | 1 | 45 | 45 |
| Head bearing blocks | 2 | 30 | 60 |
| Tail take-up brackets | 2 | 35 | 70 |
| Idler sleeves | 17 | 12 | 204 |
| Stake saddles | 12 | 20 | 240 |
| Sprockets 24T + 16T | 2 | 30 | 60 |
| Crank arm + grip | 1 | 50 | 50 |
| Crank-tower bearing block | 1 | 35 | 35 |
| Guards (head roller, chain) | 2 | 30 | 60 |
| Drilling jig | 1 | 30 | 30 |
| **Total** | | | **≈ 0.9 kg, one 1 kg spool** |

Every part fits the P2S build volume (256 × 256 × 256 mm) with a large margin.

---

## 3. Preliminary bill of materials

Prices are **estimates** unless a source is given. Prices change; check before buying.

### Essential

| Item | Qty | Est. cost | Note |
|---|---|---|---|
| 3" black heavy polypropylene webbing, 25 yd | 1 | ~$18 + shipping | one Walmart listing at $18.25 + $7.92 shipping |
| 1×3×8 ft furring strips | 10 (box) | ~$25 | Home Depot 10-pack listing $25.08 |
| Wooden grade/survey stakes, 36 in | 12–14 | $10–20 (est.) | 24 in suffices for the bottom station |
| 608-2RS bearings | 4 (10-pack) | $5–10 | Amazon/eBay listings $4.99–$6.79 |
| 1/4"-20 × 7" hex bolts + nuts + washers | ~20 | $15–25 (est.) | idler axles; the smooth shank is the bearing surface |
| 5/16"-18 (or M8) threaded rod, 36 in, + nuts/washers | 1 | $5–8 (est.) | drive shaft, crank shaft, tail axle |
| 1/2 × 1/8 in single-speed bicycle chain, 112–116 links | 1 | $10–15 (est.) | plus chain breaker if you don't own one |
| Heavy bonded polyester thread + needle or sewing awl | 1 | ~$10 (est.) | belt splice |
| Bicycle inner tube (used is fine) | 1 | $0–6 | drive roller lagging |
| Wood screws, wing nuts, 1/4" carriage bolts | assorted | ~$10 (est.) | |
| PLA | ~1 kg | $15–20 (est.) | light colour for structural parts |
| **Essential total** | | **≈ $125–165** | |

### Optional upgrades

| Item | Why |
|---|---|
| Polyester webbing instead of polypropylene | less creep, better UV resistance |
| Sandbag on the head stand | extra stability on a smooth porch |
| Exterior paint/sealer on the rails | longevity across several Halloweens |

---

## 4. What happens next

1. **You measure** the items in §1.6 (most importantly the porch height and step geometry).
2. I re-run the calculator, then **freeze Stage 3**: the final dimensions and the drawings of
   the head end, tail take-up and station.
3. **Stage 6 test prints first (about 150 g total):** one idler sleeve plus one stake saddle (fit on
   real bolt and stake), a **head-roller slice** (bearing fit and lagging), and the
   **16T sprocket** (chain engagement). Only after these pass does the full OpenSCAD
   model get printed.
4. Then the parametric OpenSCAD source, the STL list, print settings, assembly and setup guide.

### Sources
* Bambu Lab P2S build volume: https://wiki.bambulab.com/en/p2s/manual/p2s-faq
* 3" black polypropylene webbing, 25 yd: https://www.walmart.com/ip/1020004666
* 4" polyester webbing, 300 ft: https://www.fastenersplus.com/products/4-x-300-20k-polyester-cargo-webbing-black
* PVC conveyor belting (quote only): https://texasbelting.com/pages/belt-pn-10945
* 1×3×8 furring strip 10-pack: https://homedepot.com/p/1-in-x-3-in-x-8-ft-Spruce-Pine-Fir-Furring-Strip-Common-Board-10-Per-box-EHD0000368/326303094
* Furring strip dimensions (0.656 × 2.375 in): https://homedepot.com/p/Furring-Strip-Board-Common-1-in-x-3-in-x-8-ft-Actual-0-656-in-x-2-375-in-x-96-in-164704/100088011
* 608-2RS bearing 10-pack: https://ebay.com/itm/204366987316

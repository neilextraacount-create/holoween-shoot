# Shopping list (bill of materials)

**Order the belt first.** Every belt-dependent printed part (rollers, sliders, spacers) is
sized from the belt's measured width and thickness. Measure the belt when it arrives and
change two numbers in `cad/params.scad` before printing those parts. Everything else can
be bought or printed now.

Prices: Amazon pages could not be opened from the environment where this was written, so
the prices below come from search-result snapshots or are marked **est.** (estimate). Check
the live listing before buying. "Seen" means a price appeared in a search result for that
listing; it is not a guarantee.

## 1. The belt ("the black thing the candy rides on")

| | |
|---|---|
| **Buy** | **Country Brook Design 3 in Black Heavy Polypropylene Webbing, 50 yd**: <https://www.amazon.com/dp/B0BJ7X4THD> |
| Specs (from the listings) | 3 in (76 mm) wide, about 1.7 mm (0.067 in) thick, 2,100 lb break strength, black |
| Price | not visible on Amazon in search; the same roll was seen at $34.50 on Country Brook's own site and $38.50 on eBay |
| Why 50 yd, not 25 yd | The loop needs **one unbroken piece of about 50 ft** (calculator: 50.0 ft including the sewn lap). Country Brook says its rolls *may contain factory splices*. A 150 ft roll guarantees a clean 50 ft piece and gives you a spare belt. |
| Before ordering | Send the seller a message through Amazon and ask for a roll with no factory splices. |
| Fits the printed parts? | Yes. The design is built around exactly this belt (`belt_w = 76.2`, `belt_t = 1.7`). When it arrives, measure its real width in 3 places and its thickness, and update `belt_w` and `belt_t` in `cad/params.scad` if they differ by more than 0.5 mm. The rollers, sliders and spacers regenerate automatically. |

**Do not buy:**
* Pieces shorter than 17 yd (for example 10 yd lots). Two pieces mean two splices.
* Plain rubber or neoprene strip ("1/8 in x 4 in x 50 ft rubber"). It is unreinforced and stretches about 8 % at belt tension.
* Nylon webbing. It stretches when wet, and lawns are wet at night.

**Backup:** MECCANIXITY 3 in black polypropylene webbing, 25 yd (<https://www.amazon.com/dp/B0CSDKQ2Y6>, about $23 seen).
It is thinner (1.1 mm, "lightweight"), so it is floppier and stretches more. If you use it,
set `belt_t = 1.1` and re-export the STLs.

**About real conveyor belting** (black PVC-coated fabric, the "tarp" kind): it exists on
Amazon only 4 in wide. The 50 ft pieces showed "no featured offers" and a 25 ft piece was
$41.50. It needs metal lacing to join, and every printed part would have to be resized for
4 in. It is not worth the extra cost and risk here.

## 2. Hardware (hardware store or Amazon)

| Item | Qty | Use | Est. cost |
|---|---|---|---|
| 608-2RS ball bearings (8 x 22 x 7 mm), 10-pack, e.g. <https://www.amazon.com/dp/B07JJ526NX> | 1 pack (6 used) | rollers and crank | $5-10 (seen $4.99-6.79 for 10) |
| 1/2 x 1/8 in single-speed bicycle chain **with chain breaker**, e.g. OugeWood kit, 114 links: <https://www.amazon.com/dp/B09L482JF1> | 1 | crank drive | $14.89 seen |
| 5/16-18 x 36 in zinc threaded rod | 1 | the 3 axles (cut 173 + 195 + 89 mm) | $4-5 est. in store |
| 1/4-20 x 36 in zinc threaded rod | 4 | 10 station rungs (245 mm), 1 steps rung (153 mm), 2 take-up pull rods (150 mm) | $3-4 each est. |
| 5/16-18 nylon-insert lock nuts | 6 | axles | $3 est. |
| 5/16-18 wing nut | 1 | removable crank | $1 est. |
| 5/16 in flat washers (SAE) | 12 | axles | $2 est. |
| 1/4-20 hex nuts | 60 | rungs, pull rods | $6 est. (100-pack) |
| 1/4-20 nylon-insert lock nuts | 20 | plate, post and clamp bolts | $4 est. |
| 1/4 in flat washers | 80 | everywhere | $5 est. (100-pack) |
| 1/4-20 x 1-1/2 in hex bolts | 10 | head plates (4), tail plates (4), crank clamp (2) | $4 est. |
| 1/4-20 x 2 in hex bolts | 6 | crank post (2), other head leg (2), brace to post (2) | $3 est. |
| 1/4-20 x 2-1/2 in hex bolts | 2 | brace to rail (through a spacer block) | $1 est. |
| 1/4-20 x 4 in hex bolt | 1 | crank handle | $1 est. |
| #8 x 1-1/4 in exterior wood screws | 50 | rail splices, post stiffener, head-stand foot | $6 est. |
| #8 x 3/4 in wood screws | 10 | return plow (2), corner braces (8) | $2 est. |
| 1-1/2 in steel corner braces (L-brackets) | 2 | join the head-stand foot to the post and leg | $3 est. |

Every bolt length above was checked in `calc/conveyor_calc.py` so the nut lands on the
threaded part. Don't substitute longer bolts: hex bolts over 6 in long have only 1 in of thread.

## 3. Lumber

| Item | Qty | Use | Est. cost |
|---|---|---|---|
| 1x3 x 8 ft furring strip (actual 0.656 x 2.375 in) | **12**, chosen one at a time (sight down each; reject bowed or twisted ones) | 6 rails, 4 splice blocks (24 in), crank post, stiffener, brace, head leg, foot, spare | about $2.50 each (Home Depot 10-pack listed at $25.08) |
| 2x2 x 8 ft furring strip (actual 1.5 x 1.5 in) | 4 (5 for a 3-riser porch) | 10 stakes, cut to the lengths the calculator prints, with a point sawn on | $3-4 each est. |

## 4. Belt joining, lagging, misc.

| Item | Qty | Use | Est. cost |
|---|---|---|---|
| Speedy Stitcher sewing awl kit (includes waxed polyester thread), e.g. <https://www.amazon.com/dp/B0DP3H15R4> | 1 | sewing the belt loop | $15-25 est. |
| Bicycle inner tube, 26 x 1.9-2.125 in (used is fine) | 1 | grip lagging on the drive roller | $0-8 |
| Contact cement or rubber-compatible CA glue | 1 | gluing the lagging | $5 est. |
| PLA filament, light colour (white or grey) | about 0.7 kg incl. test prints | all printed parts | $12-20 per kg (eSUN 1 kg seen at $11.99) |

## 5. Optional

| Item | Why |
|---|---|
| Battery LED string (about 33 ft) and reflective tape | Makes the 24 ft rail visible in the dark so nobody trips on it |
| 40-50 lb sandbag or a few gallon water jugs | Extra weight on the head-stand foot |
| Exterior wood glue | Stronger rail splices |
| Exterior paint for the rails | Lets the rails last several Halloweens |
| A second 114-link chain | Raises the crank from 30 in to about 35 in above the porch floor (join the two chains and re-run the calculator with `chain_links`) |

## Totals (estimates)

| Group | Approx. |
|---|---|
| Belt | $35-45 |
| Bearings, chain, threaded rod, bolts, nuts, washers | $65-80 |
| Lumber | $45-50 |
| Sewing awl, lagging, glue, PLA | $35-55 |
| **Essential total** | **about $180-230** |

This is more than the first estimate ($125-165), for three reasons: the belt is the 50 yd roll
(splice-safe), the stakes are 2x2 instead of thin 1x2, and threaded rod and nuts replace the
long bolts that would not have clamped. If you already own filament, a sewing awl or
bike tubes, subtract those.

## Tools you need

Drill with 1/4 in and 5/16 in bits; hand saw; hacksaw (threaded rod); 7/16 in and 1/2 in
wrenches (two of each helps); tape measure; carpenter's square; string line; mallet; utility
knife; lighter (to seal webbing ends); 2 clamps.

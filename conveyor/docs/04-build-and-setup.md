# Build, install and run

This guide assumes the design in this repository, unchanged, and a porch reached by the
steps described in the calculator. Numbers in **[brackets]** come from
`calc/conveyor_calc.py`. Re-run it with your measured riser height (`--rise`), number of
risers (`--risers`) and basket rim height (`--basket`). It reprints the stake table, the
belt length and the post length for your site.

Nothing here has been built or tested yet. The plan below includes a full-size trial run
before Halloween for exactly that reason.

---

## 0. Timeline (today is Oct 13; Halloween is Saturday Oct 31)

| By | Do |
|---|---|
| **Oct 14** | Order the belt (ask the seller for a roll with no factory splice), chain kit and bearings. **Call 811 or file online** (free) so buried lines get marked before you drive stakes. Buy the lumber and hardware. Print the test parts that don't depend on the belt: `test_coupon`, `sprocket16` (T1, T2). |
| belt arrives | Measure the belt and update `cad/params.scad` if needed. Re-export. Print T3 and T4, then all parts. |
| **Oct 20** | Woodwork done, frame assembled. |
| **Oct 22** | **Driveway trial**: frame on sawhorses or blocks, belt sewn in place, tensioned and tracked, 30 min of cranking with real candy. |
| **Oct 25** | **Site trial**: mow, flag sprinkler heads, drive and drill the stakes, run 30 min at dusk. Then remove the frame and leave the drilled stakes in the ground, flagged. |
| **Oct 31, 3 pm** | Bolt the frame back onto the stakes, check tension and tracking, put out the basket. |

## 1. Woodwork

### 1.1 Rails
1. Pick the 6 straightest 1x3 strips. Label them L1, L2, L3 (left = the -Y side, away from
   the chain) and R1, R2, R3. Piece 1 is at the tail (sidewalk) end. Check that all 6 are the
   same length (they're usually 96 in, sometimes 96-1/8 in).
2. Sand the inside faces (the faces that will face the belt) with 120 grit and round their
   top inside edges. Rough furring strips fray webbing edges.
3. Clamp L1 to R1 face to face, tops and ends flush. Do the same with L2/R2 and L3/R3.
   **Every hole is drilled through both rails of a pair at once**, so the left and right
   holes match exactly. That keeps the rollers square.
4. All rail holes sit at one height: **26.7 mm (1-1/16 in) below the top edge**. The printed
   `drill_jig` hooks over the clamped pair and guides a 1/4 in bit at that height. Line the
   jig's sight hole up with a pencil mark and drill straight through.

| Piece | Hole positions, measured from that piece's TAIL end (mm) | What goes there |
|---|---|---|
| 1 | 18, 62 | tail plates |
| 1 | 305, 1689 | stations 1 and 2 |
| 2 | 635, 2020 | stations 3 and 4 |
| 3 | 965 | station 5 |
| 3 | 1742 | rung over the steps (rails only) |
| 3 | 2313, 2343 | crank post (R3) / head leg (L3) |
| 3 | 2376, 2420 | head plates |

5. **Splices.** Joints fall at 96 in and 192 in. Cut four 24 in splice blocks from 1x3. Each
   block goes on the **outside** face, centred on a joint. **Glue and screw it to the
   downhill piece** (4 screws, #8 x 1-1/4 in) and **screw it only, no glue, to the uphill
   piece** (4 screws). The rails then come apart into 8 ft sections for storage. Assemble
   the splices with the station rungs pushed through both rails, lying on a flat floor
   along a string line, so the holes set the alignment.

### 1.2 Head stand (porch end)
* **Crank post** (1x3): [29.1 in] long; cut it 1/2 in long and trim at assembly. It bolts to
  the outside of rail R3 with two 1/4 x 2 in bolts through the holes at 2313 and 2343 mm. It
  stands on the porch floor, plumb.
* **Post stiffener** (1x3): the post length minus 4 in. Screw it along the post's tail-side
  edge so the two make an L (5 screws). It stops 4 in below the top, where the crank clamp goes.
* **Brace** (1x3, about 30 in): from the post, about 18 in above the rail, down to rail R3
  about 18 in toward the tail. Bolt it to the post with two 1/4 x 2 in bolts. At the rail end,
  put a 3 in offcut of 1x3 between the brace and the rail and use one 1/4 x 2-1/2 in bolt.
  Drill those holes on assembly; keep them at least 1-1/2 in from board ends.
* **Head leg** (1x3): [8.9 in] plus the height of the foot; same holes on rail L3.
* **Foot** (1x3, 18 in): lies flat on the porch, across the bottoms of the post and the leg,
  joined to each with a 1-1/2 in steel corner brace. Put strips of inner tube under it so it
  doesn't scratch or slide, and set a sandbag or two water jugs on it.

### 1.3 Stakes
Cut ten 2x2 stakes to the lengths in the calculator's table [25-36 in], plus 2 spares.
Saw a 4-sided point on each. Write the station number on each one.

## 2. Hardware prep

* Cut threaded rod with a hacksaw: thread a nut on first, cut, file the end, then unscrew
  the nut to clean up the thread.
  * 1/4-20: 10 station rungs [245 mm], 1 steps rung [153 mm], 2 pull rods [150 mm].
  * 5/16-18: drive axle [173 mm], tail axle [195 mm], crank axle [89 mm].
* Press the bearings in with a vise or a block of wood, never a hammer: one into each roller
  half (4 in total) and two into the crank arm (one in each end of the hub).
* Press a 1/4 in nut into each take-up block's hex slot, and a 5/16 in nut into the hex
  pocket on the inside face of the crank clamp.

## 3. Assemble the frame (driveway trial)

Lay the three rail pairs on sawhorses or blocks, splice them (1.1 step 5), and push in the
**steps rung** with its slider: rod, washer, nut on the outside of each rail; snug. The
sliders are the spacers that set the rail gap, so don't crush them: snug plus 1/4 turn.
Station rungs go through the rails the same way, with the extra rod sticking out
equally on both sides (for the stakes later).

### 3.1 Drive roller (porch end)
1. Fit the two `drive_half` parts together: turn one over and rotate it until the teeth
   lock into the other. Glue the inner-tube lagging around the joined roller between the
   flanges. Slit a 26 in bike tube lengthwise and cut a strip as wide as the space between the flanges and
   [242 mm] long, so the ends **butt** with no overlap. Use contact cement.
2. Put `sprocket16` on the chain-side (+Y, rail R) flange; its 3 lugs drop into the 3 sockets.
3. Bolt both `head_plate`s to the outsides of the rails (1/4 x 1-1/2 in, nylon lock nuts).
4. Stack on the 5/16 in drive axle, from the left: nylon lock nut and washer, `hood_left`
   cheek, left head plate, `spacer_outer`, roller (with `spacer_inner` inside, between its two
   bearings), `spacer_outer` (it passes through the sprocket's centre), right head plate,
   `hood_right` cheek, washer, nylon lock nut. Tighten until snug. The roller must spin freely.

### 3.2 Tail roller and take-up (sidewalk end)
1. Bolt `tail_plate_left` to L1 and `tail_plate_right` to R1, with the lugs facing out.
2. Put a take-up block on each plate's outer face with its tongue in the slot. Run a pull rod
   through the lug into the block's nut, with two nuts jammed together outside the lug as a
   "head".
3. Stack the tail axle the same way as the drive axle (no hood, no sprocket):
   block, plate, `spacer_outer`, tail roller, `spacer_outer`, plate, block. Tighten the axle
   nuts until snug, then **back off 1/4 turn**. The blocks must still slide when you turn the
   pull rods; the nylon lock nuts won't work loose.
4. Turn both pull rods until the axle is **15 mm out from the inner end of the slot**.

### 3.3 Head stand, crank and chain
1. Bolt the post, stiffener, brace, leg and foot to the head end (section 1.2).
2. Slide the `crank_clamp` over the post top, cheek on the outside face. Drill the post
   through the two cheek slots (1/4 in) and fit two 1/4 x 1-1/2 in bolts.
3. Crank axle: put a 5/16 in nut and washer on the outside of the clamp, then screw the rod
   through the clamp into the captured nut so the rod is locked to the clamp. Then add the
   2 mm spacer, the crank arm with `sprocket24` on its hex hub (teeth toward the clamp),
   the 12 mm spacer, a washer and the **wing nut**. Take the wing nut off and the whole
   crank lifts off for storage.
4. Fit the `grip` on the crank arm with the 1/4 x 4 in bolt and a nylon lock nut; leave it
   loose enough to spin.
5. Chain: put it over both sprockets with the clamp at the bottom of its slots, join it with
   the master link, then slide the clamp up until the chain has about 1/4 in (5 mm) of play
   at mid-span. Tighten the clamp bolts. The 114-link kit fits the design length; if yours
   is different, remove links with the breaker.
6. Screw the `return_plow` to the bottom edges of both rails, [260 mm] from the head end
   of the rails, with the blade hanging down.

## 4. The belt

### 4.1 Thread it
1. Seal both cut ends of the webbing with a lighter.
2. Starting at the drive roller, lay the webbing **candy face up** along the tops of the
   sliders to the tail, around the tail roller, back underneath (over the return sliders if
   the stakes are in), and up around the drive roller. Chalk an arrow on the candy face every
   couple of feet so you can see there is no half twist.
3. Bring the ends together on the carrying run halfway along, where it's easy to reach.
   **Overlap 75 mm.** The end that is underneath (touching the sliders) must point
   **toward the porch**, so its edge trails and can't catch on a slider.
4. Pull out the slack by hand (don't tension it), clamp the overlap with two spring clamps,
   and draw a line across both layers at each end of the overlap.

### 4.2 Sew it
Lift the overlap off the sliders onto a scrap board. With the Speedy Stitcher (lock stitch,
5-6 mm stitches) sew a **75 x 65 mm box with an X** through both layers, plus one straight
row 3 mm from each free end. Line up the centre lines of both ends to within 1 mm before
sewing. Trim the 4 corners round (about 10 mm radius) and seal them with the lighter.

### 4.3 Tension: the can test
Hang a **full 12 oz can** (in a plastic bag) on the carrying run, midway between two
stations, and measure how far the belt dips there:

| Dip | Tension | Do |
|---|---|---|
| more than 1-1/2 in (38 mm) | under 35 N | too slack: tighten both pull rods equally |
| **about 7/8-1 in (22-26 mm)** | **50-60 N** | **correct** |
| under 5/8 in (16 mm) | over 80 N | too tight: the PLA plates will slowly creep. Loosen. |

First run-in: set it to about 7/8 in, crank for 30 minutes, then re-check. A new belt and
splice stretch a little at first.

### 4.4 Tracking
Crank slowly and watch the belt at the tail roller.
**If it drifts toward one side, tighten that side's pull rod by 1/6 turn (one flat of the nut).**
Crank for 2 minutes (2 trips around the loop), then look again. The flanges on the sliders
and rollers are a last-resort catch, not a guide; the belt should run without leaning on them.
Mark the nut flats with a paint pen once it tracks, so you can return to the setting.

### 4.5 Crank test
* Turning the handle so the **top of the belt moves toward the street** should take
  [about 4 lbf] at the grip. Candy reaches the end in [about 19 turns], 26 s at 45 turns per minute.
* Load 20-30 pieces of real candy and run them through. Watch for: belt slip at the drive
  roller (add tension), candy dragging on the rails (re-track), anything on the return run
  (the plow should flick it off).

## 5. Site installation

1. **Before you dig:** wait for the 811 marks. Turn the sprinklers **off** for Oct 30-31 and
   flag every sprinkler head; keep stakes at least 12 in away from heads and the pipe runs
   between them. Mow the strip.
2. Stretch a string from the drive axle position on the porch [12 in back from the edge] to
   the tail position over the sidewalk. Check from above that it misses trees and beds. If the
   steps must stay usable, run the line beside them.
3. Set the head stand on the porch and support the tail end on a block so the belt top is
   [10.5 in] above the sidewalk. The rails now follow a straight line; prop the middle on
   bricks at about the heights in the stake table.
4. At each station, drive two stakes **plumb and snug against the outside of the rails**,
   centred on that station's rung, to the depth in the table [12-16 in]. If the ground is
   hard, drive and pull a 1/2 in steel rod as a pilot first; it also tells you if you've hit
   something.
5. One station at a time: take that station's rung out, mark the stakes through the rail
   holes, drill each stake 5/16 in (a little oversize so the rod goes in easily), and push
   the rung back through stake, rail, slider, rail, stake. Use nut and washer pairs **on both sides of each
   stake** so the stake is held where it stands and nothing pulls the rails sideways.
6. Return rungs: drill both stakes of each station **3/4 in (20 mm) below the rail's bottom
   edge** and fit a rung with a `return_slider` between the stakes, under the return run.
7. Sight along the rail tops from the porch end; they should look straight. Fix any station
   that is visibly off by moving its nuts.
8. Put the basket **under** the tail end, with its back rim 1-2 in behind the tail axle. Its
   rim must be at least 3 in below the belt top [rim at most 7.5 in high with the default
   layout].
9. Zip-tie a battery LED string along the outside of one rail and put reflective tape on the
   stakes and the tail end.
10. Re-check tension (can test) and tracking.

**After the site trial:** take the belt off by cutting the splice stitches (re-sew on the 31st
in the same holes, or sew a fresh 75 mm lap), unbolt the rungs from the stakes, and carry the frame
away in its three sections. Leave the stakes in the ground and flag them.

## 6. On Halloween

* Start by 3 pm. Bolt up, thread and sew the belt, can test, track, test-run.
* Stand at the crank post, place candy **in the middle of the belt** just downhill of the
  rail ends, and crank steadily. You can keep loading; the belt carries a line of candy.
* Re-check tension at dusk and once mid-evening (can test). If the belt slips or wanders,
  stop and fix it rather than cranking harder.
* Keep children's hands away from the porch end. The hood covers the roller and the
  chain at the sprocket, but the chain run up to the crank is open.

## 7. After Halloween

Loosen the pull rods (PLA creeps under constant load), cut the splice stitches, take the
frame apart at the three splices, and store the rails flat (on a wall or floor) so they
stay straight. Keep the printed parts indoors, out of hot cars and sunny windows. Next
year, re-sew the belt in place.

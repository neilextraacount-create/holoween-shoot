# Build and setup guide

Nothing in this guide has been tried on a real build yet. The steps follow the CAD and the
automated checks, but expect small surprises and read each section before starting it. Part
names match the STL files in `cad/stl/`.

**Timeline to October 31** (start today):

| When | What |
|---|---|
| Day 1 | order the belt; print **plate 1** (test coupon); measure the risers; re-run the calculator |
| Days 1-4 | **plates 2-6**: small parts, head frames, rollers and gearbox. Assemble the head on the table and turn the gearbox by hand: it should spin freely and mesh smoothly with the roller's pinion. |
| Days 4-8 | **plates 7-13**: wheels, tail frames, stakes, spikes, skids, ground screws. Dry-fit one station and the tail in the yard. |
| Days 8-12 | **plates 14-18**: chute segments, trap, crank head and porch stand |
| When the belt arrives | sew the belt in place, tension it, track it, run candy tests |
| Final week | spares and reprints; full rehearsal at dusk |

The plates and their settings are in [03-printing.md](03-printing.md); roughly 67 hours of
printing in all.

## 0. Before printing the big parts

1. **Print plate 1, `plates/FINAL_01_test_coupon_etc.3mf`** (see [03-printing.md](03-printing.md)),
   and check the fits.
2. **Measure your steps**:
   - the number of risers
   - the height of each riser (top of one step to the top of the next)
   - the total horizontal run from the foot of the steps to the porch edge (you said 20 in)
3. Put them in `cad/params.scad` (`site_risers`, `site_rise`, `site_run`) and run the calculator:
   ```
   python3 calc/conveyor_calc.py --svg side-profile-2-risers.svg
   ```
   It prints three things to copy into `cad/params.scad`:
   - the number of chute segments (`seg_count`, the line marked `<- use`)
   - the stand height (`stand_h = ...`)
   - a ready-made line `stake_len = [...]`

   Copy that `stake_len` line as it is: these are leg lengths, and each stake is 32 mm longer
   overall.
4. Run `python3 cad/check_parts.py`. It re-exports every STL into `cad/stl/` and re-checks
   everything, including the chute against your steps. Then run `python3 cad/make_plates.py`
   to rebuild the plates in `plates/` for your steps (add `--no-slice` if PrusaSlicer isn't
   installed).

## 1. Choose the line

- The belt runs straight from the foot of the steps to the sidewalk. The chute runs straight up
  the steps from the same line. Put the line **along one side of the steps** so people can
  still use them, and keep the crank, stand and funnel out of the walking path.
- Stretch a string from the sidewalk edge to the foot of the steps where the head goes, 10 in
  in front of the first riser. Mark the spots for the tail, the 3 stations (every 60.5 in from
  the tail, see the calculator) and the head. The string is the **belt centreline**.
- The station stakes stand **beside** the belt, not under it: each one goes **2 1/4 in (56 mm)
  to one side of the string**, all on the same side (away from where people walk). The wheels
  then hang out over the string.
- The tail roller sits **2 in out over the sidewalk**. The basket goes on the sidewalk under
  it. Its rim must be **no higher than 6 in**.

## 2. Head module (foot of the steps)

![Head module](img/head-assembly.png)

*Head module: frames (orange), drive roller, gearbox on frame B (crown gear gold), drop trap and
the first chute segments (purple), feet (brown), belt (black).*

Parts:
- `head_side_a`, `head_side_b`, `drive_roller`, `drive_pin`, `gearbox`, 2 x `foot`
- 7 x `bolt8_28` + 7 x `nut8` (4 for the feet, 3 for the gearbox)
- 2 ground screws with 2 `washer50` and 2 `bolt8_28`, and optionally 2 spikes

1. Bolt each foot crossbar between the frames: each frame's tab drops between a pair of cheeks.
   Frame B (the one with the open slot and the 3 extra holes) goes on the **left** when you look
   from the sidewalk toward the porch. The gearbox, and the drive shaft beside the chute, are on
   that side, so leave the walkable part of the steps on the right.
2. Slide the drive roller's **pinion end** into frame B's slot from the open (porch) side until
   it sits in the round end.
3. Line up frame A's hole with the roller's bore and **press the drive pin** in from outside.
   Its ribs make it a tight fit on purpose: push with the heel of your hand or a clamp until the
   flange is about 1 mm off the frame. The roller should turn freely.
4. Hold the gearbox against the outside of frame B with its crown gear meshing with the pinion.
   Turn the gearbox's shaft socket a little to let the teeth slide together. Bolt it on with
   3 bolts: heads on the gearbox side, nuts inside the frame. **Snug, not tight**: PLA cracks if
   you crank on printed bolts.
5. Set the head on the lawn at its mark, square to the string. The belt top should be about
   6 in above the grass. Anchor the **front foot** (the one nearest the steps) with 2 ground
   screws (section 5): it is the foot that lifts when the belt is tight. The rear foot only
   presses down; give it 2 spikes in soft turf, or nothing.

## 3. Stations (stilts)

![Station](img/station-assembly.png)

*A station: the belt rides over the upper wheel and comes back over the lower wheel.*

Parts per station: `stake_N`, `station_bracket`, 2 x `wheel_unit`, 2 x `pin3`. Plus one
`stake_cap` for pushing.

1. Stake 1 is the longest and goes nearest the sidewalk. Push each stake straight down
   **2 1/4 in (56 mm) beside its mark**, with the flat faces of its square socket parallel to
   the string: put the `stake_cap` in the stake's socket and push on the cap. Stop when the socket top
   is at the height the calculator lists ("stake head", e.g. 5.3 in above the grass at
   station 1). In hard soil, make a pilot hole with a long screwdriver first, or water the lawn
   the day before.
2. Push a bracket's spigot into the stake socket. Its wheel holes face the belt.
3. Push a wheel unit's square peg through each hole of the bracket, collar first against the
   bracket. Push a `pin3` through the peg: it is meant to be snug, because it pulls the collar
   tight against the bracket so the wheel can't droop. The wheels should spin freely.
4. Sight along the string: the tops of all the upper wheels should make a straight line from
   the head roller to the tail roller. Push a stake deeper or pull it up a little to adjust.
   Each wheel's centre should be over the string, with its axle square to it; twist or move
   the stake if not.

## 4. Tail module (sidewalk end)

![Tail module](img/tail-assembly.png)

*Tail: knob screws (gold) pull the take-up blocks; the skids reach back onto the lawn.*

Parts:
- `tail_side_l`, `tail_side_r`, `tail_roller`, 2 x `takeup_block`, 2 x `takeup_nut`,
  2 x `takeup_screw`, `skid_l`, `skid_r`, 1 x `foot`
- 6 x `bolt8_28` + 6 x `nut8`
- 2 ground screws with 2 `washer50` and 2 `bolt8_28`, and 2 spikes

1. Bolt each tail frame into its skid's two cheek pairs (2 bolts each). Then bolt the foot
   crossbar across the two frames' rear tabs (the end over the sidewalk).
2. Hold the tail roller between the frames, centred in the windows.
3. Push one take-up block in through its window from outside, square boss first, so the boss
   enters the roller's end counterbore and slides over the square axle end. Turn the axle with
   a finger to line up the square. Do the other side the same way.
4. Drop a square nut into each block's pocket. Thread a take-up screw from the rear through the
   frame's lug hole and into the nut. Leave both blocks **fully forward** (toward the head) for
   now.
5. Set the tail in place: roller 2 in out over the sidewalk, skids along the lawn.
6. Anchor each skid:
   - a **ground screw in its rear pad** (the pad nearer the sidewalk, about 70 mm onto the
     lawn). These hold the tail down against the belt tension.
   - a **spike in the far pad**

## 5. Anchors

- **Ground screws**:
  1. Make a pilot hole with a screwdriver and push the tip in.
  2. Put the T-wrench on the hex head and turn **clockwise** until the head is level with the
     grass.
  3. Put the foot's anchor hole over it, then a `washer50`, and screw a `bolt8_28` down into
     the head. Snug only.
- The belt pulls each end toward the other with about 40 N. Weight on its own only holds
  that with a lot of it: on wet grass about 13 kg at the head and 8 kg at the tail. So
  something should still go into the ground:
  - **A screw won't go in** (a root or a stone): move the pilot hole a few cm and try again.
    For hard clay, water the spot the day before.
  - **A screw spins without biting** (sand, mulch): leave it in its hole as a peg; it still
    takes the sideways pull. At the head, also push 2 spikes into the rear foot's anchor
    holes, or tie the head frames back to a step railing post with a rope. Then add weight
    against lifting (water jugs or bricks):
    - **Tail:** about **5 kg on the rear skid pads or the rear foot crossbar** (the sidewalk
      end). Weight on the far pads doesn't stop the tail tipping.
    - **Head:** about **3 kg on the front foot**.
  - **Nothing can go into the ground at all** (paving, for example): put at least **13 kg on
    the head's front foot** and **8 kg on the tail's rear pads or crossbar**, or tie the head
    back to a railing.

## 6. Chute line, crank and porch stand

![Porch end](img/porch-assembly.png)

*Porch end: last chute segment, crank head with funnel, crank arm, and the stand.*

Parts (the counts are for 2 risers of 7 in; `cad/parts-table.md` has them for your steps):
- `trap`, 5 x `chute_segment` (`seg_count`), `crank_head`, `crank_arm`
- 7 x `hex_coupler` (`seg_count` + 2, 1 spare), 6 x `ring_sleeve` (`seg_count` + 1)
- `post_lower` (2 for a tall stand), `post_upper`, `stand_tray`, `stand_shim` (as needed)
- 4 x `pin3`: crank arm, crank-head socket, stand height, tray (one more between two lower
  posts)

Have a helper, or a stool or box on the steps, to hold the line up while you stack it. **Never
leave the line hanging from the gearbox.**

1. **Trap**: set it between the head frames, with its ledges just above the frames' guard bars
   and just uphill of the two small stop posts. It tips forward on its own (its weight is
   uphill of the ledges), so hold its upper end up until segment 1 is on.
2. Put a ring sleeve into the counterbore on top of the gearbox housing, and a hex coupler into
   the gearbox shaft's hex socket.
3. Lower **segment 1** onto them. Four things engage at once:
   - its ring onto the sleeve
   - its shaft's hex socket onto the coupler (turn the shaft slightly until it drops)
   - its chute socket over the trap's upper end, which slides about 20 mm in
   - the trap is now locked: it can't turn or slip
4. Repeat with a sleeve and a coupler for each segment up to the last one, then the crank
   head. Prop the top end as you go.
5. **Porch stand.** It goes in under the crank head once the line is complete:
   1. On the bench, plug the lower post's short spigot into the tray socket. **Don't pin the
      tray yet.** With 2 lower posts, first plug one's short spigot into the other's head
      socket and pin that joint.
   2. Slide the upper post's long spigot **all the way** into the lower post's head (no pin
      yet). The stand is now at least 35 mm shorter than its working height.
   3. Stand it on the porch with the upper post's short spigot just under the socket beneath
      the crank-head funnel. Turn the tray so its long arm points onto the porch and its short
      arm toward the edge.
   4. Lift the upper post straight up into that socket until its shoulder seats, and push a
      `pin3` through the socket's pin hole.
   5. Push a `pin3` through the lower post's head and whichever of the 6 spigot holes lines up.
      The holes are 6 mm apart, so the height adjusts from 12 mm up to 18 mm down. Put
      `stand_shim`s under the tray arms if it rocks.
   6. Check the tray's long arm still points onto the porch, then push a `pin3` through
      whichever of the tray's two crossing holes lines up with the lower post.
6. **Steady the stand**, then take the prop away. Cranking pushes sideways on the top of the line, hard enough to tip
   the stand over. Do one of these:
   - tie the post to a porch railing or column with a strap or rope (best)
   - put about **8 kg on the tray**: two full 1-gallon water jugs on the side arms, plus your
     candy bowl
   - hold the funnel rim with your free hand while cranking
7. Slide the crank arm onto the square drive and push a `pin3` through.

Turn the crank: the belt's top run should move toward the sidewalk. If it runs backward, turn
the other way.

## 7. Belt: thread it, sew it in place

1. Seal one end of the webbing with a lighter flame (melt it just enough to stop fraying).
2. With the take-up blocks fully forward, thread the webbing:
   - **over** the drive roller's top
   - **over** each station's **upper** wheel
   - **around** the tail roller
   - back along the bottom, **over** each station's **lower** wheel
   - **under** the drive roller, to meet the start

   The black face that carries candy faces outward all the way round.
3. Pull it snug by hand. Mark where it overlaps by 75 mm, cut, and seal that end too.
4. Do the joint on the **bottom run** near the middle, where you can reach it.
   1. Lay the `splice_template` on the overlap with its lip against the top end.
   2. Mark every hole through the template with a fine-tip marker, then lift the template off.
   3. Pierce each mark with a hot nail or soldering iron, or an awl. Never push a hot tool
      through the template: PLA melts.
   4. Sew through the holes: round the box and both diagonals of the X, twice, pulling each
      stitch tight.

   The joint must be flat, or it will thump over every wheel.

## 8. Tension and tracking

**Tension: the 100 g test.**

1. Put 100 g in a small flat bag: 20 US nickels, or candy weighed on a kitchen scale.
2. Pull a string taut along the top run between stations 2 and 3, resting on the belt over
   both upper wheels, along the belt's centreline.
3. Lay the bag **across the middle of the belt**, midway between the two stations. Don't hang
   it off one edge: that twists the belt and the reading comes out far too big.
4. Measure from the string down to the belt's centreline, right beside the bag, with and
   without the bag. The difference is the dip. **Target: 13-22 mm.** It is about 15-18 mm at
   the design tension of 20 N per run.
5. Tighten both knobs **1/8 turn at a time**, the same on each side, until the dip is in range.
   - Polypropylene hardly stretches, so 1/8 turn (0.4 mm) is already a noticeable change.
   - **Don't over-tighten**: a tight belt makes the crank harder to turn and pulls up on the tail
     anchors.

**Tracking.** Turn the crank slowly (about one turn per second) and watch the belt at the tail
roller:

- If it drifts toward one flange, **tighten the knob on that side by 1/8 turn** and run it
  again. The belt moves away from the tightened side.
- When it runs centred for 2 minutes, it's done. Re-check after the first evening.

## 9. Test with candy

- Use wrapped candy only.
- Crank at a relaxed pace (about 45 turns a minute).
- Drop candy into the funnel **one or two pieces at a time**. It slides down, stops in the trap
  and lands on the belt about 20 s before it reaches the basket.
- **Size limits**: up to about **30 mm thick** (the trap's headroom) and **110 mm long** (longer
  bars bridge the trap's drop slot). Break up anything bigger.
- Watch the first 20 pieces:
  - Candy bouncing out of the trap: drop it more gently.
  - Candy tumbling off the belt edge between stations: the belt is too slack (more than 22 mm in
    the 100 g test).
  - Candy stuck in the trap: it's over the size limits.

## 10. Halloween night

- **Trip hazards**: the chute over the steps, the stand and the anchors. Mark them with tape
  or battery lights.
- Rain: PLA and the belt don't mind. Wet belts grip a little less; if it slips, tighten 1/8
  turn each side (stay inside the 13-22 mm range).
- Keep small hands away from the head roller and the gears: the guard panels cover the belt
  sides, not the gearbox.

## 11. Take it down and store it

The belt can stay sewn. Take things down in this order:

1. **Line**:
   1. Take off the crank arm.
   2. Have a helper hold the funnel, or set the stool or box under the crank head, at its
      working height. Keep the top of the line held or propped until it is all off: never
      leave it hanging from the gearbox.
   3. Pull the height pin and the crank-head socket pin. Push the upper post down
      into the lower post (the stand drops at least 35 mm while the line stays held) and lift
      the stand out.
   4. Lift off the crank head, then the chute segments (top first, moving the prop down as you
      go), then the trap.
2. **Tail**: unscrew the knobs and pull both take-up blocks out through their windows. Lift the
   roller out of the belt loop.
3. **Head**:
   1. Unbolt the gearbox; the crown gear locks the roller in its slot while it is on.
   2. Unbolt both feet, so frame A can move.
   3. Pull the drive pin out by its flange (pliers help), or slide frame A off the pin.
   4. Slide the roller out of frame B's slot toward the porch side.
4. Stations: pull the wheels' pins, lift the brackets off, pull the stakes.

Store everything out of direct sun: PLA softens around 55 °C, for example in a hot car.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Crank stiff even without the belt | a print-in-place part not fully freed, or elephant's foot on the first layer | turn it back and forth by hand; if needed, warm it in 45-50 °C water, let it cool, then twist again (printing guide, "Freeing print-in-place parts"); check the test coupon results |
| Belt slips on the drive roller | tension too low, or the belt is wet | tighten 1/8 turn each side (100 g dip 13-22 mm); rub wax on the **bearings**, never on the roller |
| Clicking once per turn of the belt | the splice is lumpy | re-sew it flatter |
| Wheel droops or wobbles | its pin is missing or loose | push the collar against the bracket and fit the pin |
| Chute segments separate | the line isn't sitting on the stand | check the stand pin height and the shims |
| Stand tips while cranking | nothing holding it | tie it to a railing, add 8 kg, or hold the funnel rim |
| Candy jams in the trap | piece over 30 mm thick or 110 mm long | lift the trap lid area by tilting the piece out; break up big bars |

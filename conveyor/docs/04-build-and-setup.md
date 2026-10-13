# Build and setup guide

Nothing in this guide has been tried on a real build yet. The steps follow the CAD and the
checks, but expect small surprises and read each section before starting it. Part names match
the STL files in `cad/stl/`.

**Timeline to October 31** (start today):

| When | What |
|---|---|
| Day 1 | order the belt; print the **test coupon**; measure the risers; re-run the calculator |
| Days 1-4 | print the head module (drive roller, gearbox, frames, feet, bolts). Turn the gearbox by hand: it should spin freely and mesh smoothly with the roller's pinion. |
| Days 3-8 | print one station and the tail module; dry-fit them in the yard |
| Days 6-12 | print the chute segments, trap, crank head, crank arm and porch stand |
| When the belt arrives | sew the belt in place, tension it, track it, run candy tests |
| Final week | the rest of the stations and spares; full rehearsal at dusk |

## 0. Before printing the big parts

1. **Print `test_coupon.stl`** (see [03-printing.md](03-printing.md)) and check the fits.
2. **Measure your steps**: the height of each riser (top of one step to the top of the next)
   and the total horizontal run from the foot of the steps to the porch edge (you said 20 in).
3. Run the calculator with your numbers:
   ```
   python3 calc/conveyor_calc.py --risers 2 --rise 7.25 --steps-run 20
   ```
   It prints the number of chute segments, `stand_h` and the 4 stake lengths. Put them in
   `cad/params.scad` (`seg_count`, `stand_h`, `stake_len`, and `site_rise` / `site_run`), then
   run `python3 cad/check_parts.py`. It re-exports the STLs and re-checks everything, including
   the chute against your steps.

## 1. Choose the line

- The belt runs straight from the foot of the steps to the sidewalk. The chute runs straight up
  the steps from the same line. Put the line **along one side of the steps** so people can
  still use them, and keep the crank, stand and funnel out of the walking path.
- Stretch a string from the sidewalk edge to the foot of the steps where the head goes, 10 in
  in front of the first riser. Mark the spots for the tail, the 4 stations (every 48.4 in from
  the tail, see the calculator) and the head.
- The tail roller sits **2 in out over the sidewalk**. The basket goes on the sidewalk under
  it. Its rim must be **no higher than 6 in**.

## 2. Head module (foot of the steps)

![Head module](img/head-assembly.png)

*Head module: frames (orange), drive roller, gearbox on frame B (crown gear gold), drop trap and
the first chute segments (purple), feet (brown), belt (black).*

Parts: `head_side_a`, `head_side_b`, `drive_roller`, `drive_pin`, `gearbox`, 2 x `foot`,
7 x `bolt8_28` + 7 x `nut8` (4 for the feet, 3 for the gearbox), 2 ground screws, 2 spikes.

1. Bolt each foot crossbar between the frames: each frame's tab drops between a pair of cheeks.
   Frame B (the one with the open slot and the 3 extra holes) goes on the **left** when you look
   from the sidewalk toward the porch. The gearbox, and the drive shaft beside the chute, are on
   that side, so leave the walkable part of the steps on the right. (For the mirror-image layout,
   mirror every head, line and porch part in the slicer.)
2. Slide the drive roller's **pinion end** into frame B's slot from the open (porch) side until
   it sits in the round end. Line up frame A's hole with the roller's bore and **press the drive
   pin** through frame A into the roller (it's a tight fit on purpose: push with the heel of
   your hand or a clamp). The roller should turn freely.
3. Hold the gearbox against the outside of frame B with its crown gear meshing with the
   pinion. Turn the gearbox's shaft socket a little to let the teeth slide together. Bolt it on
   with 3 bolts: heads on the gearbox side, nuts inside the frame. **Snug, not tight**: PLA
   cracks if you crank on printed bolts.
4. Set the head on the lawn at its mark, square to the string. The belt top should be about
   6 in above the grass. Anchor the **front foot (the one nearest the steps)** with 2 ground
   screws (section 5). It is the foot that lifts when the belt is tight. The rear foot gets
   2 spikes, or nothing in firm turf.

## 3. Stations (stilts)

![Station](img/station-assembly.png)

*A station: the belt rides over the upper wheel and comes back over the lower wheel.*

Parts per station: `stake_N`, `station_bracket`, 2 x `wheel_unit`, 2 x `pin3`. Plus one
`stake_cap` for pushing.

1. Stake 1 is nearest the sidewalk and is the longest. Push each stake straight down at its
   mark through the `stake_cap` (put the cap in the stake's socket and push on it) until the
   socket top is at the height the calculator lists ("stake head", e.g. 5.3 in above the
   grass at station 1). In hard soil, make a pilot hole with a long screwdriver first, or water
   the lawn the day before.
2. Push a bracket's spigot into the stake socket. Its wheel holes face the belt.
3. Plug a wheel unit into each square hole of the bracket and lock it with a `pin3` through the
   peg. The wheels should spin freely.
4. Sight along the string: the tops of all the upper wheels should make a straight line from
   the head roller to the tail roller. Push a stake deeper or pull it up a little to adjust.

## 4. Tail module (sidewalk end)

![Tail module](img/tail-assembly.png)

*Tail: knob screws (gold) pull the take-up blocks; the skids reach back onto the lawn.*

Parts: `tail_side_l`, `tail_side_r`, `tail_roller`, 2 x `takeup_block`, 2 x `takeup_nut`,
2 x `takeup_screw`, `skid_l`, `skid_r`, 1 x `foot`, 6 x `bolt8_28` + 6 x `nut8`,
2 ground screws, 2 spikes.

1. Bolt each tail frame into its skid's two cheek pairs (2 bolts each), then bolt the foot
   crossbar across the two frames' rear tabs (the end over the sidewalk).
2. Push each take-up block through its frame window from the outside, the square boss inward.
   Hold the tail roller between the two bosses so the square axle ends drop into the bosses'
   square sockets.
3. Drop a square nut into each block's pocket. Thread a take-up screw from the rear through
   the frame's lug hole and into the nut. Leave both blocks **fully forward** (toward the head)
   for now.
4. Set the tail in place: roller 2 in out over the sidewalk, skids along the lawn. Anchor each
   skid with a ground screw in its **rear pad** (the one 120 mm from the sidewalk; these hold the
   tail down against belt tension) and a spike in the far pad.

## 5. Anchors

- **Ground screws**: make a pilot hole with a screwdriver. Push the tip in, put the T-wrench
  on the hex head and turn **clockwise** until the head is level with the grass. Put the
  foot's anchor hole over it, then a `washer50`, and screw a `bolt8_28` down into the head.
  Snug only.
- If a screw spins without biting (sand, mulch) or won't go in (roots, clay), use ballast
  instead: about **5 kg on the tail's skid pads** and **3 kg on the head's front foot** (water
  jugs, bricks).

## 6. Belt: thread it, sew it in place

1. Seal one end of the webbing with a lighter flame (melt it just enough to stop fraying).
2. With the take-up blocks fully forward, thread the webbing:
   - **over** the drive roller's top
   - **over** each station's **upper** wheel
   - **around** the tail roller
   - back along the bottom, **over** each station's **lower** wheel
   - **under** the drive roller, to meet the start

   The black face that carries candy faces outward all the way round.
3. Pull it snug by hand. Mark where it overlaps by 75 mm, cut, and seal that end too.
4. Do the joint on the **bottom run** near the middle, where you can reach it. Lay the
   `splice_template` on the overlap with its lip against the top end. Pierce every hole with a
   hot nail (or an awl), then sew through the holes. Go round the box and both diagonals of the
   X twice, and pull each stitch tight. The joint must be flat, or it will thump over every
   wheel.

## 7. Tension and tracking

**Tension (the can test).** Hang a full 15 oz food can (about 0.45 kg) from the top run, midway
between stations 2 and 3. Measure how far the belt dips under it. **Target: 55-90 mm
(2¼-3½ in).** Tighten both knobs half a turn at a time, the same on each side, until the dip
is in range. Polypropylene hardly stretches, so a few turns go a long way. **Don't
over-tighten**: a tight belt makes the crank harder to turn and lifts the tail anchors.

**Tracking.** Turn the crank slowly (about one turn per second) and watch the belt at the tail
roller:

- If it drifts toward one flange, **tighten the knob on that side** by a quarter turn and run
  it again. The belt moves away from the tightened side.
- When it runs centred for 2 minutes, it's done. Re-check after the first evening.

## 8. Chute line, crank and porch stand

![Porch end](img/porch-assembly.png)

*Porch end: last chute segment, crank head with funnel, crank arm, and the stand on its foot.*

Parts: `trap`, 5 x `chute_segment`, `crank_head`, `crank_arm`, 6 x `hex_coupler`,
6 x `ring_sleeve`, `pin3`, `post_lower`, `post_upper`, `stand_tray`, `stand_shim` (as needed).

1. Set the **trap** between the head frames: its ledges hang just above the frames' guard bars,
   just uphill of the two small stop posts. Its open upper end points up the steps.
2. Put a ring sleeve into the counterbore on top of the gearbox housing, and a hex coupler into
   the hex socket in the gearbox shaft.
3. Lower **segment 1** onto them. Three things engage at once:
   - its ring onto the sleeve
   - its shaft's hex socket onto the coupler (turn the shaft slightly until it drops)
   - its chute socket over the trap's upper end
4. Repeat with a sleeve and a coupler for segments 2-5, then the crank head.
5. **Porch stand**: plug the upper post into the socket under the crank head funnel, the lower
   post into the upper post, and the tray onto the lower post. Turn the tray so the long arm
   points onto the porch and the short arm toward the edge. If the tray doesn't sit flat on the
   floor, slide shims under the arms. **Put your candy bowl on the tray**: it's the ballast.
6. Slide the crank arm onto the square drive and push a `pin3` through.

Turn the crank: the belt should move with candy-carrying side going toward the sidewalk. If it
runs backward, you are turning the wrong way (or the gearbox was mounted on the other side):
just turn the other way.

## 9. Test with candy

- Use wrapped candy only.
- Crank at a relaxed pace (about 45 turns a minute).
- Drop candy into the funnel **one or two pieces at a time**. It slides down, stops in the
  trap and lands on the belt about 20 s before it reaches the basket.
- Hold the funnel rim with your free hand while cranking: it keeps the top of the line steady.
- Watch the first 20 pieces:
  - Candy bouncing out of the trap: drop it more gently.
  - Candy tumbling off the belt edge between stations: the belt is too slack (more dip than
    90 mm in the can test).
  - Candy sticking under the trap: it's over 30 mm tall. Check your candy.

## 10. Halloween night

- **Trip hazards**: the chute over the steps, the stand and the anchors. Mark them with tape
  or battery lights.
- Rain: PLA and the belt don't mind. Wet belts grip a little less; if it slips, tension it a
  little more (stay inside the can-test range).
- Keep small hands away from the head roller and the gears: the guard panels cover the belt
  sides, not the gearbox.

## 11. Take it down and store it

The belt can stay sewn. To get it off the rollers:

- **Tail**: unscrew the knobs, pull the take-up blocks out through their windows, and lift the
  roller out of the loop.
- **Head**: pull the drive pin out of frame A and slide the roller out of frame B's slot.

The chute segments, stations and stand just pull apart. Store everything out of direct sun:
PLA softens around 55 °C, for example in a hot car.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Crank stiff even without the belt | a print-in-place part not fully freed, or elephant's foot on the first layer | turn it back and forth by hand (in hot tap water if needed); check the test coupon results |
| Belt slips on the drive roller | tension too low, or the belt is wet | tighten half a turn each side (can-test range); rub wax on the **bearings**, never on the roller |
| Clicking once per turn of the belt | the splice is lumpy | re-sew it flatter |
| Wheel wobbles | its peg isn't pinned, or the bracket isn't fully on the stake | push the bracket down; fit the pin |
| Chute segments separate | the line isn't sitting on the stand | check the stand height and the shims |

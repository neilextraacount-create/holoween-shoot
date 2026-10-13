// =====================================================================
// Candy conveyor - shared parameters (millimetres unless noted)
// conveyor.scad includes this file; calc/conveyor_calc.py parses it,
// so keep every line in the form   name = <number or simple expression>;
// =====================================================================
IN = 25.4;

// ---------------------------------------------------------------- belt
belt_w        = 76.2;    // 3" webbing (Country Brook heavy polypro: 3")
belt_t        = 1.7;     // 0.067" stated by seller; measure yours
belt_clear    = 2.0;     // belt-to-flange clearance each side

// ---------------------------------------------------------------- wooden rails (1x3 furring strip)
rail_h        = 60.3;    // 2.375" actual
rail_t        = 16.7;    // 0.656" actual
rail_gap      = belt_w + 18.8;  // inside face to inside face (= slider length); 95.0 for 3" webbing
rail_piece    = 96*IN;   // 8 ft
rail_pieces   = 3;       // per side
rail_above_belt = 20.0;  // rail top edge stands this far above the belt surface (side wall)
splice_len    = 16*IN;   // splice block on the outside face, centred on each joint

// ---------------------------------------------------------------- fasteners
bolt_d        = 6.35;    // 1/4"-20 structural bolts
bolt_hole     = 6.9;     // printed clearance hole for 1/4"
nut14_af      = 11.11;   // 7/16" across flats (1/4"-20 hex nut)
nut14_h       = 5.6;
axle_d        = 7.94;    // 5/16" bolt shank = the three fixed axles
axle_hole     = 8.4;     // printed clearance hole for 5/16"
nut516_af     = 12.7;    // 1/2" across flats (5/16"-18 hex nut)
nut516_h      = 6.8;
woodscrew_hole = 4.6;    // #8 wood screw clearance

// ---------------------------------------------------------------- 608 bearing
brg_od        = 22.0;
brg_w         = 7.0;
brg_id        = 8.0;
brg_race_od   = 12.0;    // inner-race land: spacers must stay inside this
brg_fit       = 0.15;    // pocket = brg_od + brg_fit (tune with test coupon)
spacer_od     = 11.5;
spacer_id     = 8.4;

// ---------------------------------------------------------------- sliders (fixed, belt slides over them; also rail spacers)
slider_od     = 10.0;    // thin sleeve over the 1/4" bolt
slider_flange_od = slider_od + 2 * (belt_t + 0.3); // lip ends 0.3 mm above the belt surface
slider_flange_t  = 1.6;
station_first = 12*IN;   // first stake station from the tail end of the rails
station_pitch = 54.5*IN; // stake stations (each carries one carry slider + one return slider)
stations      = 5;       // last one lands >= 24 in before the first riser (see calc)
stake_t       = 38.1;    // 2x2 stakes (1.5" actual); stations are threaded-rod rungs, any stake size works

// ---------------------------------------------------------------- rollers
drive_core_d  = 77.0;    // printed diameter under the lagging
lagging_t     = 1.5;     // bicycle inner tube, approx (measure)
tail_d        = 50.0;
crown_drive   = 0.4;     // radial crown at belt centre, drive roller (measured over the lagging)
crown_tail    = 0.3;     // radial crown, tail roller
flange_lip    = 2.5;     // flange radius above the roller surface (last-resort edge catch)
flange_t      = 3.0;
roller_face   = belt_w + 10;  // between flanges: 5 mm each side (crown does the steering)

// ---------------------------------------------------------------- chain drive (1/2" x 1/8" bicycle chain)
chain_p       = 12.7;
chain_roller_d = 7.75;
chain_tooth_t = 2.8;     // tooth thickness (chain inner width 3.18)
chain_half_w  = 4.9;     // half the overall chain width (rivet ends) incl. margin
sprocket_drive_t = 16;   // on drive roller
sprocket_crank_t = 24;   // on crank wheel
chain_links   = 114;     // as bought (OugeWood kit = 114); must be even

// ---------------------------------------------------------------- crank
crank_r       = 100.0;   // crank arm radius
grip_len      = 80.0;
grip_od       = 22.0;

// ---------------------------------------------------------------- end plates
plate_t       = 6.0;
head_axis_out = 80.0;    // drive axle centre beyond the rail end (gives chain clearance over the rail end)
tail_slot_len = 90.0;    // take-up travel (absorbs 180 mm = 1.2 % belt growth)
tail_axis_min = 45.0;    // tail axle centre beyond rail end at minimum take-up

// ---------------------------------------------------------------- print tolerances
fit           = 0.25;    // general clearance for sliding/loose fits
$fn           = 72;

// ---------------------------------------------------------------- added for v2 layout
flange_w      = 4.0;     // flange thickness at each roller end
spr_body      = 7.3;     // sprocket part thickness (teeth flush with the outer face)
post_setback  = 110.0;   // crank post centre, measured back from the head end of the rails
slope_deg     = 7.2;     // belt slope (site dependent; only tilts the post in the checks)
chain_plate_h = 12.0;    // chain side-plate height (KMC Z410 ~11.7)
clamp_t       = 6.0;     // crank clamp wall
clamp_slot    = 25.0;    // chain-tension travel of the crank clamp
hood_r        = 50.0;    // inner radius of the drive-roller hood
hood_t        = 2.4;

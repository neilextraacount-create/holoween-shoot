// =====================================================================
// Candy conveyor v4 (all printed except the belt): shared parameters, mm
// conveyor.scad includes this file; calc/conveyor_calc.py and the Python
// checkers parse it, so keep each line as   name = <number or expression>;
// =====================================================================
IN = 25.4;

// ---------------------------------------------------------------- belt (the only bought part)
belt_w        = 76.2;    // 3 in heavy polypropylene webbing (Country Brook): measure yours
belt_t        = 1.7;     // 0.067 in per the listing: measure yours
face          = belt_w + 10;   // roller / wheel width between flanges (5 mm each side)
flange_lip    = 2.5;     // flange height above the rolling surface
flange_t      = 2.0;

// ---------------------------------------------------------------- printing fits
pip_gap       = 0.45;    // print-in-place running gap (tune with test_coupon: 0.35 / 0.45 / 0.55)
fit_gap       = 0.20;    // slip fit between separate parts (pegs into sockets)
pin_d         = 3.0;     // printed cross pins
pin_hole      = 3.5;

// ---------------------------------------------------------------- station wheel unit (cantilever, print-in-place)
wu_r          = 15.0;    // rolling radius (crown added on top)
wu_crown      = 0.3;
wu_axle_r     = 6.0;     // axle core radius
wu_ridge_r    = 8.0;     // V-ridge peak radius (the two V-ridges carry load and hold the wheel on)
wu_peg        = 12.0;    // square peg that plugs into the station bracket
bracket_t     = 8.0;

// ---------------------------------------------------------------- double-supported print-in-place rollers (tail, snub)
tail_r        = 20.0;    // tail roller radius (small = candy drops off cleanly)
snub_r        = 15.0;    // (not used in v4: no snub roller)
roll_crown    = 0.3;
dr_axle_r     = 6.0;
dr_ridge_r    = 8.0;     // smaller V-ridge = less bearing friction
dr_cb_r       = 10.5;    // counterbore at each roller end (the side-frame boss goes in here)
dr_cb_d       = 9.0;
dr_end_sq     = 8.0;     // square end of the fixed axle (gripped by the boss)
boss_r        = 9.6;     // boss radius (must clear dr_cb_r by >= 0.8)

// ---------------------------------------------------------------- drive roller
drive_r       = 30.0;    // core radius
drive_crown   = 0.3;
rib_h         = 0.5;     // grip ribs on the drive surface
ribs          = 64;
journal_r     = 8.0;     // Ø16 journals run in the side frames
journal_gap   = 0.30;

// ---------------------------------------------------------------- gears: spur pinion on the drive roller, crown gear on the line shaft
gear_m        = 2.5;
pinion_z      = 17;
crown_z       = 34;      // ratio 2:1 step-up (crank 1 turn -> roller 2 turns)
gear_pa       = 20;
gear_face     = 10;
backlash      = 0.15;    // per flank

// ---------------------------------------------------------------- frames
side_t        = 8.0;     // side frame thickness
frame_gap     = 1.0;     // roller end to side frame
web           = 7.0;     // lattice member width in the side frames

// ---------------------------------------------------------------- line (shaft + candy chute down the steps)
line_deg      = 36;      // line angle to the belt, at the head (about 40 deg to level on a 5 deg lawn)
seg_len       = 210;     // structural length of one chute/shaft segment
shaft_or      = 7.0;     // shaft tube outer radius (Ø14)
shaft_ir      = 3.5;
shaft_ridge   = 9.5;     // V-ridge peak radius at each bearing ring
ring_or       = 13.0;    // bearing ring outer radius
hex_af        = 8.0;     // hex coupler across flats (separate printed coupler joins female sockets)
trough_w      = 66;      // inside width of the candy chute
trough_h      = 24;      // inside wall height
trough_wall   = 0.9;     // 2 perimeters
trough_floor  = 1.3;
trough_n      = 100;     // chute floor offset from the shaft axis (perpendicular to the line)
crank_r       = 110;     // crank arm radius

// ---------------------------------------------------------------- stakes
spike_leg     = 30;      // L-profile stake
spike_t       = 3.2;
spike_head    = 36;      // square head block (also the station socket)
spike_sock    = 16.0;    // square socket for the station bracket spigot
spike_embed   = 170;     // depth driven into the lawn

// ---------------------------------------------------------------- take-up
takeup_travel = 60;      // tail take-up travel (fully in = +20 mm, fully out = -40 mm)
screw_r       = 5.0;     // printed take-up screw, Ø10 round thread
screw_pitch   = 3.0;

$fn           = 64;

// ---------------------------------------------------------------- layout along the line (distance s from the drive axle line, along the line)
gb_top_s      = 110;     // top face of the gearbox (rotor end with a hex socket) = start of chute segment 1
crank_head_len = 150;    // crank head unit above the last segment
head_h        = 6 * IN;  // belt top above the lawn at the drive roller
tail_h        = 9 * IN;  // belt top above the sidewalk at the tail roller (basket rim must be <= tail_h - 3 in)
stations      = 4;       // stake stations between head and tail
T0            = 20;      // belt pretension per run, N (set with the can test)

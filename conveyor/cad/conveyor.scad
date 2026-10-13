// =====================================================================
// Hand-cranked Halloween candy conveyor - all printed parts (OpenSCAD 2021+)
//
//   openscad -o stl/drive_half.stl -D 'part="drive_half"' conveyor.scad
//   python3 check_parts.py        (renders every PART below and runs every CHECK)
//
// Every part is modelled in its PRINT orientation (flat face on the bed, +Z up).
// Assembly frame used by the chk_* solids:  X along the rails (0 = tail end of
// the rails, + toward the porch), Y across (0 = belt centreline, +Y = chain
// side), Z perpendicular to the rails (0 = top surface of the carrying belt).
//
// Design rule: no threaded joint ever carries crank torque. The drive roller,
// tail roller and crank wheel all spin on 608 bearings around fixed bolts; torque
// passes only through printed lugs and hex sockets.
// =====================================================================
include <params.scad>

part = "assembly";

// ---------------------------------------------------------------- printed parts
// Columns: name | qty | walls | infill % | description   (walls of 0.42 mm, 4 top/bottom layers)
// PART: drive_half       | 2  | 2 | 8  | drive roller half (print 2 identical; flange down)
// PART: sprocket16       | 1  | 4 | 30 | 16T sprocket, drives the roller through 3 lugs (teeth down)
// PART: tail_half        | 2  | 2 | 8  | tail roller half (print 2 identical; flange down)
// PART: spacer_outer     | 4  | 3 | 100 | axle spacer, bearing inner race to end plate
// PART: spacer_inner     | 2  | 3 | 100 | axle spacer between the two bearings in a roller
// PART: head_plate       | 2  | 4 | 25 | drive-axle plate, bolts to rail end (same part both sides)
// PART: tail_plate_left  | 1  | 4 | 25 | take-up plate, -Y rail
// PART: tail_plate_right | 1  | 4 | 25 | take-up plate, +Y rail (mirror of left)
// PART: takeup_block     | 2  | 4 | 40 | sliding axle block with captured 1/4" nut
// PART: slider           | 6  | 3 | 15 | carrying-run slider + rail spacer: 5 stations + 1 rung over the steps
// PART: return_slider    | 5  | 3 | 15 | return-run slider between the stakes, one per station
// PART: sprocket24       | 1  | 4 | 25 | 24T crank sprocket, hex bore (teeth down)
// PART: crank_arm        | 1  | 4 | 30 | crank arm with bearing hub (arm down)
// PART: crank_spacers    | 1  | 3 | 100 | the three crank-axle spacers, printed together
// PART: grip             | 1  | 3 | 10 | rotating handle sleeve
// PART: crank_clamp      | 1  | 4 | 30 | bearing block that clamps the top of the crank post
// PART: hood_right       | 1  | 3 | 15 | guard over the drive roller + sprocket, chain side (+Y)
// PART: hood_left        | 1  | 3 | 15 | guard over the drive roller, -Y side (mirror of hood_right)
// PART: return_plow      | 1  | 3 | 20 | sweeps anything on the return run off before the drive roller
// PART: drill_jig        | 1  | 3 | 15 | drilling guide for the station holes through both rails
// PART: test_coupon      | 1  | 3 | 15 | fit test: 608 pocket, 1/4" + 5/16" holes, nut traps, spacer bore

// ---------------------------------------------------------------- derived geometry
rail_len   = rail_piece * rail_pieces;
rail_top   = rail_above_belt;
rail_bot   = rail_above_belt - rail_h;
rail_mid   = (rail_top + rail_bot) / 2;
rail_in    = rail_gap / 2;
rail_out   = rail_gap / 2 + rail_t;
belt_half  = belt_w / 2;
guide_in   = belt_half + belt_clear;          // flange inner faces at +-guide_in
half_len   = flange_w + roller_face / 2;      // one roller half, flange face to joint
pocket_d   = brg_od + brg_fit;
bore_r     = 7.0;                             // clearance around the 11.5 mm spacer

drive_r0      = drive_core_d / 2;
drive_flange_r = drive_r0 + lagging_t + flange_lip;
drive_z       = -belt_t - (drive_r0 + lagging_t + crown_drive);
tail_r0       = tail_d / 2;
tail_flange_r = tail_r0 + flange_lip;
tail_z        = -belt_t - (tail_r0 + crown_tail);
slider_z      = -belt_t - slider_od / 2;
ret_slider_z  = rail_bot - 20;

hx = rail_len + head_axis_out;                // drive axle X
spacer_out_len = rail_out - half_len;         // 18.2
spacer_in_len  = 2 * (half_len - brg_w);      // 78
y_spr_out  = half_len + spr_body;             // outer (teeth) face of both sprockets
y_chain    = y_spr_out - chain_tooth_t / 2;   // chain centre plane

function st_x(i) = station_first + i * station_pitch;   // stake stations along the rails
function spr_pd(n) = chain_p / sin(180 / n);
function spr_od(n) = chain_p * (0.6 + 1 / tan(180 / n));
seat_r = 0.505 * chain_roller_d + 0.069 * pow(chain_roller_d, 1 / 3) + 0.15;

// chain centre distance for the chain as bought
chain_S = (sprocket_drive_t + sprocket_crank_t) / 2;
chain_k = pow((sprocket_crank_t - sprocket_drive_t) / (2 * PI), 2);
chain_C = ((chain_links - chain_S) + sqrt(pow(chain_links - chain_S, 2) - 8 * chain_k)) * chain_p / 4;

// crank axle: on the (world-vertical) post axis, chain_C from the drive axle
post_x  = rail_len - post_setback;
post_zb = rail_mid;
tsl = tan(slope_deg);
cA = post_x - hx;
cB = post_zb - drive_z;
cu = (-(cA * tsl + cB) + sqrt(pow(cA * tsl + cB, 2) - (tsl * tsl + 1) * (cA * cA + cB * cB - chain_C * chain_C))) / (tsl * tsl + 1);
crank_x = post_x + cu * tsl;
crank_z = post_zb + cu;
clamp_bridge = 26;
post_top_u = cu / cos(slope_deg) - clamp_bridge / 2;   // along the post axis

// crank wheel stack along Y (inboard of the post)
crank_hub_top = y_spr_out + 0.4;              // hex hub end, 1 mm short of the clamp
clamp_in_y    = crank_hub_top + 2.0;          // clamp bridge inner face (2 mm spacer)
y_arm0        = crank_hub_top - 25.2;         // arm bottom face (arm 8 thick)

echo(str("half_len ", half_len, " y_spr_out ", y_spr_out, " CHAIN centre distance ", chain_C, " mm; crank axle at X=", crank_x - rail_len,
         " from rail end, Z=", crank_z, "; y_chain=", y_chain));

// ---------------------------------------------------------------- helpers
module hexagon(af, h) { cylinder(d = af / cos(30), h = h, $fn = 6); }
module bearing_pocket(depth = brg_w) { cylinder(d = pocket_d, h = depth); }

// crowned roller half as a solid of revolution, print frame (flange on bed)
module roller_half(r0, rf, crown, lugs) {
    n = 16;
    prof = concat(
        [[bore_r, brg_w], [pocket_d / 2, brg_w], [pocket_d / 2, 0], [rf, 0], [rf, flange_w], [r0, flange_w]],
        [for (i = [0 : n]) let(z = flange_w + (half_len - flange_w) * i / n,
                                y = half_len - z)   // distance from the joint
            [r0 + crown * (1 - pow(y / (roller_face / 2), 2)), z]],
        [[bore_r, half_len]]);
    difference() {
        union() {
            rotate_extrude($fn = 120) polygon(prof);
            dog_ring(r0, true);
        }
        dog_ring(r0, false);
        // three sockets in the flange face for the sprocket lugs (drive roller only)
        if (lugs) for (a = [30, 150, 270]) rotate(a) translate([19, 0, -0.01]) cube([8.6, 8.6, 8.6], center = true);
    }
}

// castellated joint: teeth on sectors [0,60]+120k stick up, the rest is recessed,
// so two identical halves (one turned over) interlock and share torque
module dog_ring(r0, teeth) {
    ri = bore_r + 2.5; ro = r0 - 7; h = 3;
    for (k = [0 : 2]) rotate(k * 120 + (teeth ? 0 : 60) - (teeth ? 0 : 1.5))
        translate([0, 0, teeth ? half_len - 0.01 : half_len - h - 0.3])
            linear_extrude(h + (teeth ? 0.01 : 0.31))
                intersection() {
                    difference() { circle(ro + (teeth ? 0 : 0.3)); circle(ri - (teeth ? 0 : 0.3)); }
                    polygon([[0, 0], [2 * ro, 0], [2 * ro * cos(60 + (teeth ? 0 : 3)), 2 * ro * sin(60 + (teeth ? 0 : 3))]]);
                }
}

module drive_half() { roller_half(drive_r0, drive_flange_r, crown_drive, true); }
module tail_half()  { roller_half(tail_r0,  tail_flange_r, crown_tail, false); }

// ---------------------------------------------------------------- sprockets
module sprocket2d(n) {
    pd = spr_pd(n); rr = pd / 2;
    difference() {
        union() {
            circle(r = rr - seat_r + 0.6, $fn = n * 6);
            for (k = [0 : n - 1]) intersection() {
                circle(d = spr_od(n), $fn = n * 6);
                rotate(k * 360 / n) translate([rr, 0]) circle(r = chain_p - seat_r, $fn = 60);
                rotate((k + 1) * 360 / n) translate([rr, 0]) circle(r = chain_p - seat_r, $fn = 60);
            }
        }
        for (k = [0 : n - 1]) rotate(k * 360 / n) translate([rr, 0]) circle(r = seat_r, $fn = 40);
    }
}

// teeth ring (chamfered toward the tips on both faces) + body inside the chain plates
module sprocket_teeth(n) {
    rr = spr_pd(n) / 2; ro = spr_od(n) / 2;
    intersection() {
        linear_extrude(chain_tooth_t) sprocket2d(n);
        rotate_extrude($fn = n * 6) polygon([[0, 0], [rr, 0], [ro + 0.01, 0.6], [ro + 0.01, chain_tooth_t - 0.6],
                                             [rr, chain_tooth_t], [0, chain_tooth_t]]);
    }
}

function chain_clear_r(n) = spr_pd(n) / 2 - chain_plate_h / 2 - 1.0;   // body radius limit

module sprocket16() {
    rb = chain_clear_r(sprocket_drive_t);
    difference() {
        union() {
            sprocket_teeth(sprocket_drive_t);
            cylinder(r = rb, h = spr_body);
            for (a = [30, 150, 270]) rotate(a) translate([19, 0, spr_body]) translate([-4, -4, 0]) cube([8, 8, 3.7]);
        }
        translate([0, 0, -1]) cylinder(r = bore_r, h = 30);
    }
}

module sprocket24() {
    rb = chain_clear_r(sprocket_crank_t);
    difference() {
        union() {
            sprocket_teeth(sprocket_crank_t);
            cylinder(r = rb, h = spr_body);
        }
        translate([0, 0, -1]) hexagon(34 + 0.35, 30);
        for (a = [0 : 60 : 300]) rotate(a + 30) translate([(rb + 21) / 2, 0, -1]) cylinder(d = 11, h = 30);
    }
}

// ---------------------------------------------------------------- spacers
module tube(od, id, h) { difference() { cylinder(d = od, h = h); translate([0, 0, -1]) cylinder(d = id, h = h + 2); } }
module spacer_outer() { tube(spacer_od, spacer_id, spacer_out_len); }
module spacer_inner() { tube(spacer_od, spacer_id, spacer_in_len); }

// ---------------------------------------------------------------- end plates
head_bolts_x = [-18, -62];                    // rail-end bolts, relative to the rail end
module head_plate2d() {
    difference() {
        hull() {
            for (x = head_bolts_x) translate([x, rail_mid]) circle(r = 13);
            translate([head_axis_out, drive_z]) circle(r = 14);
        }
        translate([head_axis_out, drive_z]) circle(d = axle_hole);
        for (x = head_bolts_x) translate([x, rail_mid]) circle(d = bolt_hole);
    }
}
module head_plate() { linear_extrude(plate_t) head_plate2d(); }

tail_x_min = -tail_axis_min;
tail_x_max = -(tail_axis_min + tail_slot_len);
tail_lug_x = tail_x_max - 15 - 12;            // lug inner face sits 15 mm past the block
tail_bolts_x = [18, 62];
module tail_plate2d() {
    difference() {
        union() {
            hull() for (x = tail_bolts_x) translate([x, rail_mid]) circle(r = 13);
            hull() {
                translate([tail_bolts_x[0], rail_mid]) circle(r = 13);
                translate([tail_lug_x, tail_z - 13]) square([12, 26]);
            }
        }
        hull() { translate([tail_x_min, tail_z]) circle(d = axle_hole); translate([tail_x_max, tail_z]) circle(d = axle_hole); }
        for (x = tail_bolts_x) translate([x, rail_mid]) circle(d = bolt_hole);
    }
}
// print frame: inner face on the bed, lug grows up (= outward from the rail)
module tail_plate_base() {
    linear_extrude(plate_t) tail_plate2d();
    // lug: 12 mm along X, protrudes 14 mm outward, holds the 1/4" pull rod
    difference() {
        translate([tail_lug_x, tail_z - 13, plate_t - 0.01]) cube([12, 26, 14]);
        translate([tail_lug_x - 1, tail_z, plate_t + 7]) rotate([0, 90, 0]) cylinder(d = bolt_hole, h = 14);
    }
}
module tail_plate_left()  { tail_plate_base(); }
module tail_plate_right() { mirror([0, 1, 0]) tail_plate_base(); }

// take-up block: rides on the plate's outer face with a tongue in the slot
module takeup_block() {
    difference() {
        union() {
            translate([-15, -13, 0]) cube([32, 26, 14]);
            translate([-8, -(axle_hole - 0.3) / 2, -plate_t + 1]) cube([16, axle_hole - 0.3, plate_t - 1 + 0.01]);  // tongue
        }
        translate([0, 0, -10]) cylinder(d = axle_hole, h = 30);
        // 1/4" pull rod enters from the -X end; nut captured, loaded toward -X
        translate([-16, 0, 7]) rotate([0, 90, 0]) cylinder(d = bolt_hole, h = 40);
        translate([-12, 0, 7]) rotate([0, 90, 0]) rotate(30) hexagon(nut14_af + 0.3, nut14_h + 0.4);
        translate([-12, -(nut14_af + 0.3) / 2, 7]) cube([nut14_h + 0.4, nut14_af + 0.3, 10]);
    }
}

// ---------------------------------------------------------------- sliders
module slider_body(len) {
    difference() {
        union() {
            cylinder(d = slider_od, h = len);
            for (z = [len / 2 - guide_in - slider_flange_t, len / 2 + guide_in])
                translate([0, 0, z]) cylinder(d = slider_flange_od, h = slider_flange_t);
            // printable 45 deg ramps under each flange (on the side away from the belt)
            translate([0, 0, len / 2 - guide_in - slider_flange_t - (slider_flange_od - slider_od) / 2])
                cylinder(d1 = slider_od, d2 = slider_flange_od, h = (slider_flange_od - slider_od) / 2);
        }
        translate([0, 0, -1]) cylinder(d = bolt_hole, h = len + 2);
    }
}
module slider()        { slider_body(rail_gap); }
module return_slider() { slider_body(2 * rail_out); }

// ---------------------------------------------------------------- crank
module crank_arm() {
    hub_h = crank_hub_top - y_arm0;           // 25.2
    difference() {
        union() {
            hull() { cylinder(r = 22, h = 8); translate([crank_r, 0, 0]) cylinder(r = 13, h = 8); }
            cylinder(r = 17, h = hub_h - spr_body - 0.4);
            translate([0, 0, hub_h - spr_body - 0.4 - 0.01]) rotate(30) hexagon(34, spr_body + 0.4 + 0.01);
        }
        translate([0, 0, -0.01]) bearing_pocket();
        translate([0, 0, hub_h - brg_w + 0.01]) bearing_pocket();
        translate([0, 0, -1]) cylinder(r = bore_r, h = 40);
        translate([crank_r, 0, -1]) cylinder(d = bolt_hole, h = 20);
    }
}
module grip() { tube(grip_od, bolt_d + 0.6, grip_len); }

// spacers for the crank axle: 2 mm (hub to clamp), between the bearings, 12 mm (bearing to wing nut)
crank_inner_sp = (crank_hub_top - y_arm0) - 2 * brg_w;
module crank_spacers() {
    tube(spacer_od, spacer_id, 2.0);
    translate([16, 0, 0]) tube(spacer_od, spacer_id, crank_inner_sp);
    translate([32, 0, 0]) tube(spacer_od, spacer_id, 12);
}

// clamp over the top of the (world-vertical) 1x3 crank post, print frame:
// x across the post width, y = assembly Y measured from the post outer face, z along the post
module crank_clamp() {
    pw = rail_h; pt = rail_t;                 // the post is a furring strip: 60.3 x 16.7
    bridge_depth = pt + (rail_out - clamp_in_y);  // bridge reaches inboard past the post
    bw = 44;                                  // bridge width across the post
    difference() {
        union() {
            hull() {                                                                         // outer cheek
                translate([-pw / 2 - 4, 0, 0]) cube([pw + 8, clamp_t, 1]);
                translate([-bw / 2, 0, 70 + clamp_bridge - 1]) cube([bw, clamp_t, 1]);
            }
            translate([-bw / 2, 0, 70]) cube([bw, clamp_t + bridge_depth, clamp_bridge]);  // bridge over the post top
        }
        translate([0, -1, 70 + clamp_bridge / 2]) rotate([-90, 0, 0]) cylinder(d = axle_hole, h = 80);
        for (z = [18, 48]) hull() for (dz = [0, clamp_slot]) translate([0, -1, z + dz - clamp_slot / 2 + 4])
            rotate([-90, 0, 0]) cylinder(d = bolt_hole, h = 20);
    }
}

// ---------------------------------------------------------------- guards
// Hood: two identical halves. Each is a cheek that slips over the drive axle outside a
// head plate (clamped by the axle nut) plus a quarter-shell over the roller. Print frame:
// cheek on the bed, z = distance inboard from the cheek; shell covers -60..105 deg
// (0 = toward the porch, 90 = straight up), leaving the carrying run free to leave.
hood_y0 = rail_out + plate_t;                 // cheek inner face
hood_a0 = -60; hood_a1 = 105;
module hood_half() {
    w = hood_y0 + 3;                          // half width incl. 3 mm cheek
    difference() {
        union() {
            // cheek: hub around the axle + two spokes to the shell
            cylinder(r = 11, h = 3);
            for (a = [hood_a0 + 8, hood_a1 - 8]) rotate(a) translate([0, -5, 0]) cube([hood_r + 1, 10, 3]);
            // shell
            rotate(hood_a0) rotate_extrude(angle = hood_a1 - hood_a0, $fn = 120)
                translate([hood_r, 0]) square([hood_t, w]);
        }
        translate([0, 0, -1]) cylinder(d = axle_hole, h = 10);
        // slot for the chain where it leaves the sprocket (both halves, so the part is symmetric)
        translate([0, 0, w - (y_chain + chain_half_w + 2)]) rotate(70) rotate_extrude(angle = 45, $fn = 60)
            translate([hood_r - 1, 0]) square([hood_t + 2, 2 * chain_half_w + 4]);
    }
}

// Return-run plow: screws up into the bottom edges of both rails just before the drive
// roller; a 45 deg blade 4 mm above the return run's inner face sweeps debris off sideways.
plow_x = rail_len - 260;
function ret_line_z(x) = let(x0 = st_x(stations - 1), z0 = ret_slider_z + slider_od / 2,
                             z1 = drive_z - (drive_r0 + lagging_t + crown_drive))
                         z0 + (z1 - z0) * (x - x0) / (hx - x0);
plow_depth = rail_bot - (ret_line_z(plow_x) + 4);     // blade height below the rail bottoms
module return_plow() {
    difference() {
        union() {
            translate([-10, -rail_out, 0]) cube([20, 2 * rail_out, 4]);
            intersection() {
                rotate(45) translate([-1.2, -80, 0]) cube([2.4, 160, plow_depth]);
                translate([-60, -belt_half - 6, 0]) cube([120, belt_w + 12, plow_depth]);
            }
        }
        for (s = [-1, 1]) translate([0, s * (rail_in + rail_t / 2), -1]) cylinder(d = woodscrew_hole, h = 10);
    }
}

// ---------------------------------------------------------------- jigs and tests
module drill_jig() {
    w = 2 * rail_t + 0.8; depth = rail_top - slider_z;   // station hole centre below the rail top
    difference() {
        translate([-14, -w / 2 - 8, 0]) cube([28, w + 16, depth + 10]);
        translate([-15, -w / 2, -1]) cube([30, w, depth + 1]);
        // guide bore through both legs (drill straight through the clamped pair)
        translate([0, -w / 2 - 20, depth]) rotate([-90, 0, 0]) cylinder(d = bolt_d + 0.25, h = w + 40);
        translate([0, 0, depth + 4]) cylinder(d = 3, h = 20);   // sight hole to line up with pencil marks
    }
}
module test_coupon() {
    difference() {
        translate([-16, -16, 0]) cube([92, 32, 9]);
        translate([0, 0, 2]) bearing_pocket(8);
        translate([0, 0, -1]) cylinder(r = bore_r, h = 20);
        translate([24, 0, -1]) cylinder(d = bolt_hole, h = 20);
        translate([38, 0, -1]) cylinder(d = axle_hole, h = 20);
        translate([38, 0, 9 - nut516_h]) hexagon(nut516_af + 0.3, 10);
        translate([56, 0, -1]) cylinder(d = spacer_od + 0.6, h = 20);  // spacer slip fit
        translate([68, 0, -1]) cylinder(d = bolt_hole, h = 20);
        translate([68, 0, 9 - nut14_h]) rotate(30) hexagon(nut14_af + 0.3, 10);
    }
}

// =====================================================================
// assembly-frame solids for interference checks (chk_*)
// =====================================================================
module at_y_out(y_outer) { translate([0, y_outer, 0]) rotate([90, 0, 0]) children(); }   // print z -> -Y
module at_y_in(y_inner)  { translate([0, y_inner, 0]) rotate([-90, 0, 0]) children(); }  // print z -> +Y

module rails_between(x0, x1) {
    for (s = [-1, 1]) translate([x0, s > 0 ? rail_in : -rail_out, rail_bot]) cube([x1 - x0, rail_t, rail_h]);
}
module drive_roller_asm() {
    translate([hx, 0, drive_z]) {
        at_y_in(-half_len) drive_half();
        rotate([0, 60, 0]) at_y_out(half_len) drive_half();
        at_y_out(y_spr_out) sprocket16();
    }
}
module tail_roller_asm(t) {
    translate([tail_x_min - t, 0, tail_z]) {
        at_y_in(-half_len) tail_half();
        rotate([0, 60, 0]) at_y_out(half_len) tail_half();
    }
}
module plates_head() {
    for (s = [-1, 1]) translate([rail_len, s * (rail_out + (s > 0 ? plate_t : 0)), 0])
        rotate([90, 0, 0]) linear_extrude(plate_t) head_plate2d();
}
module plates_tail() {
    translate([0, -rail_out, 0]) rotate([90, 0, 0]) linear_extrude(plate_t) tail_plate2d();
    translate([0, rail_out + plate_t, 0]) rotate([90, 0, 0]) linear_extrude(plate_t) tail_plate2d();
}
module takeup_blocks(t) {
    for (s = [-1, 1]) translate([tail_x_min - t, s * (rail_out + plate_t), tail_z])
        rotate([s > 0 ? -90 : 90, 0, 0]) takeup_block();
}
// belt as a thin skin: carrying run, wrap around a roller and the return run
module belt_end(xa, za, r_belt, xback, zback_ret) {
    // xa,za = axle; r_belt = radius of belt inner surface
    translate([0, -belt_half, 0]) rotate([90, 0, 0]) mirror([0, 0, 1]) linear_extrude(belt_w) {
        difference() { translate([xa, za]) circle(r = r_belt + belt_t); translate([xa, za]) circle(r = r_belt); }
        polygon([[xback, 0], [xa, za + r_belt + belt_t], [xa, za + r_belt], [xback, -belt_t]]);
        polygon([[xback, zback_ret], [xa, za - r_belt], [xa, za - r_belt - belt_t], [xback, zback_ret - belt_t]]);
    }
}
module chain_env() {
    pd1 = spr_pd(sprocket_drive_t); pd2 = spr_pd(sprocket_crank_t); m = chain_plate_h / 2 + 0.5;
    translate([0, y_chain + chain_half_w, 0]) rotate([90, 0, 0]) linear_extrude(2 * chain_half_w)
        difference() {
            hull() { translate([hx, drive_z]) circle(r = pd1 / 2 + m); translate([crank_x, crank_z]) circle(r = pd2 / 2 + m); }
            hull() { translate([hx, drive_z]) circle(r = pd1 / 2 - m); translate([crank_x, crank_z]) circle(r = pd2 / 2 - m); }
        }
}
module post() {
    translate([post_x, rail_out, post_zb]) rotate([0, slope_deg, 0])
        translate([-rail_h / 2, 0, -300]) cube([rail_h, rail_t, 300 + post_top_u]);
}
module crank_clamp_asm() {
    translate([post_x, 0, post_zb]) rotate([0, slope_deg, 0]) translate([0, rail_out + rail_t + clamp_t, post_top_u - 70])
        mirror([0, 1, 0]) crank_clamp();
}
module crank_wheel_asm() {
    translate([crank_x, 0, crank_z]) {
        at_y_in(y_arm0) crank_arm();
        at_y_out(y_spr_out) sprocket24();
    }
}
module crank_sweep() {      // everything the crank arm and grip can reach in one turn
    translate([crank_x, 0, crank_z]) {
        at_y_in(y_arm0) cylinder(r = crank_r + 13, h = 8);
        at_y_in(y_arm0 - grip_len) difference() { cylinder(r = crank_r + grip_od / 2, h = grip_len); translate([0, 0, -1]) cylinder(r = crank_r - grip_od / 2, h = grip_len + 2); }
    }
}
module hood_asm() {
    translate([hx, 0, drive_z]) {
        at_y_out(hood_y0 + 3) hood_half();                       // +Y (chain side) = hood_right
        mirror([0, 1, 0]) at_y_out(hood_y0 + 3) hood_half();     // -Y = hood_left (mirror image)
    }
}
module plow_asm() { translate([plow_x, 0, rail_bot]) mirror([0, 0, 1]) return_plow(); }
module mid_rung() { translate([(st_x(stations - 1) + hx) / 2, 0, slider_z]) at_y_in(-rail_in) slider(); }
module station(xs) {        // a stake station: carry slider + return slider on stakes
    translate([xs, 0, slider_z]) at_y_in(-rail_in) slider();
    translate([xs, 0, ret_slider_z]) at_y_in(-rail_out) return_slider();
}
module stakes(xs) {
    for (s = [-1, 1]) translate([xs, s > 0 ? rail_out : -rail_out - stake_t, rail_mid]) rotate([0, slope_deg, 0])
        translate([-18, 0, -250]) cube([36, stake_t, 250 + rail_top - rail_mid + 30]);
}
module belt_station(xs) {
    translate([xs - 300, -belt_half, -belt_t]) cube([600, belt_w, belt_t]);
    translate([xs - 300, -belt_half, ret_slider_z + slider_od / 2]) cube([600, belt_w, belt_t]);
}

// CHECK: drive_roller | head_plates  | disjoint | drive roller + sprocket clear the head plates
// CHECK: drive_roller | rails_head   | disjoint | drive roller clears the rail ends
// CHECK: belt_head    | rails_head   | disjoint | belt edges and return run clear the rails at the head
// CHECK: belt_head    | head_plates  | disjoint | belt clears the head plates
// CHECK: chain        | rails_head   | disjoint | chain clears the rail ends
// CHECK: chain        | head_plates  | disjoint | chain clears the head plates
// CHECK: chain        | post         | disjoint | chain clears the crank post
// CHECK: chain        | crank_clamp  | disjoint | chain clears the crank clamp
// CHECK: chain        | crank_sweep  | disjoint | crank arm and grip never touch the chain
// CHECK: crank_sweep  | post         | disjoint | crank arm and grip never touch the post
// CHECK: crank_sweep  | rails_head   | disjoint | crank arm and grip never touch the rails
// CHECK: crank_wheel  | crank_clamp  | disjoint | crank wheel clears the clamp
// CHECK: crank_wheel  | post         | disjoint | crank wheel clears the post
// CHECK: tail_min     | tail_plates  | disjoint | tail roller clears plates (take-up fully in)
// CHECK: tail_max     | tail_plates  | disjoint | tail roller clears plates (take-up fully out)
// CHECK: tail_min     | rails_tail   | disjoint | tail roller clears the rail ends
// CHECK: tail_min     | takeup_min   | disjoint | tail roller clears the take-up blocks
// CHECK: belt_tail    | rails_tail   | disjoint | belt clears the rails at the tail
// CHECK: belt_tail    | tail_plates  | disjoint | belt clears the tail plates
// CHECK: belt_station | station      | disjoint | belt runs between the slider flanges
// CHECK: belt_station | rails_mid    | disjoint | belt clears the rails mid-span
// CHECK: belt_station | stakes       | disjoint | return belt clears the stakes
// CHECK: station      | rails_mid    | disjoint | sliders fit between rails / stakes without overlap
// CHECK: belt_skin    | station      | overlap  | belt actually rests on the sliders (0.2 mm skin)
// CHECK: hood         | drive_roller | disjoint | hood clears the drive roller and sprocket
// CHECK: hood         | chain        | disjoint | chain passes through the hood slot
// CHECK: hood         | belt_head    | disjoint | hood clears the belt
// CHECK: hood         | head_plates  | disjoint | hood clears the head plates
// CHECK: plow         | belt_head    | disjoint | plow blade clears the return run
// CHECK: plow         | post         | disjoint | plow clears the crank post
// CHECK: mid_rung     | belt_head    | disjoint | rung over the steps sits under the belt without cutting it
// CHECK: belt_skin_hd | mid_rung     | overlap  | belt rests on the rung over the steps

if (part == "drive_half") drive_half();
else if (part == "sprocket16") sprocket16();
else if (part == "tail_half") tail_half();
else if (part == "spacer_outer") spacer_outer();
else if (part == "spacer_inner") spacer_inner();
else if (part == "head_plate") head_plate();
else if (part == "tail_plate_left") tail_plate_left();
else if (part == "tail_plate_right") tail_plate_right();
else if (part == "takeup_block") takeup_block();
else if (part == "slider") slider();
else if (part == "return_slider") return_slider();
else if (part == "sprocket24") sprocket24();
else if (part == "crank_arm") crank_arm();
else if (part == "crank_spacers") crank_spacers();
else if (part == "grip") grip();
else if (part == "crank_clamp") crank_clamp();
else if (part == "drill_jig") drill_jig();
else if (part == "test_coupon") test_coupon();
// ---- check solids
else if (part == "chk_drive_roller") drive_roller_asm();
else if (part == "chk_head_plates") plates_head();
else if (part == "chk_rails_head") rails_between(rail_len - 600, rail_len);
else if (part == "chk_rails_tail") rails_between(0, 600);
else if (part == "chk_rails_mid") rails_between(st_x(3) - 300, st_x(3) + 300);
else if (part == "chk_belt_head") belt_end(hx, drive_z, drive_r0 + lagging_t + crown_drive, rail_len - 600, ret_slider_z + slider_od / 2 + belt_t);
else if (part == "chk_belt_tail") mirror([1, 0, 0]) belt_end(-(tail_x_min - 20), tail_z, tail_r0 + crown_tail, -600, ret_slider_z + slider_od / 2 + belt_t);
else if (part == "chk_chain") chain_env();
else if (part == "chk_post") post();
else if (part == "chk_crank_clamp") crank_clamp_asm();
else if (part == "chk_crank_wheel") crank_wheel_asm();
else if (part == "chk_crank_sweep") crank_sweep();
else if (part == "chk_tail_min") tail_roller_asm(0);
else if (part == "chk_tail_max") tail_roller_asm(tail_slot_len);
else if (part == "chk_tail_plates") plates_tail();
else if (part == "chk_takeup_min") takeup_blocks(0);
else if (part == "chk_station") station(st_x(3));
else if (part == "chk_stakes") stakes(st_x(3));
else if (part == "chk_belt_station") belt_station(st_x(3));
else if (part == "chk_hood") hood_asm();
else if (part == "chk_plow") plow_asm();
else if (part == "chk_mid_rung") mid_rung();
else if (part == "chk_belt_skin_hd") translate([(st_x(stations - 1) + hx) / 2 - 100, -belt_half, -belt_t - 0.2]) cube([200, belt_w, 0.21]);
else if (part == "hood_right") hood_half();
else if (part == "hood_left") mirror([0, 1, 0]) hood_half();
else if (part == "return_plow") return_plow();
else if (part == "chk_belt_skin") translate([st_x(3) - 300, -belt_half, -belt_t - 0.2]) cube([600, belt_w, 0.2 + 0.01]);
else if (part == "assembly") {
    color("tan") { rails_between(rail_len - 600, rail_len); rails_between(0, 600); }
    color("orange") { drive_roller_asm(); tail_roller_asm(30); crank_wheel_asm(); }
    color("gray") { plates_head(); plates_tail(); takeup_blocks(30); crank_clamp_asm(); }
    color("sienna") post();
    color("black", 0.4) chain_env();
    color("lightgray", 0.6) hood_asm();
    color("gray") plow_asm();
}

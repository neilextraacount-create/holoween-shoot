// =====================================================================
// Hand-cranked Halloween candy conveyor, v4: everything printed except the belt
//
//   openscad -o out.stl -D 'part="wheel_unit"' conveyor.scad
//   python3 check_parts.py      (renders every PART, runs every CHECK)
//
// Parts are modelled in PRINT orientation (flat face down, +Z up).
// Assembly frames used by the chk_* solids are described at each module.
// =====================================================================
include <params.scad>
use <lib.scad>

part = "wheel_unit";

// ---------------------------------------------------------------- derived
L_w        = face + 2 * flange_t;            // wheel / roller length, flange face to flange face
half_w     = L_w / 2;
side_in    = half_w + frame_gap;             // side frame inner face |Y|
side_out   = side_in + side_t;
pin_r      = gear_m * pinion_z / 2;          // pinion pitch radius
crown_R    = gear_m * crown_z / 2;           // crown pitch radius
pin_od     = 2 * (pin_r + gear_m);

// ---------------------------------------------------------------- wheel unit (stations): cantilever, print-in-place
// Print frame: wheel axis = Z, wheel occupies z 0..L_w, axle continues up into
// a collar and a square peg. In use the peg end plugs into the station bracket.
wu_ridges   = [14, L_w - 14];
wu_collar0  = L_w + 0.6;
wu_peg0     = wu_collar0 + 2.4;
wu_peg_len  = bracket_t + 7;
module wheel_unit() {
    // wheel
    difference() {
        rotate_extrude($fn = 96) polygon(concat(
            [[0, 0], [wu_r + flange_lip, 0], [wu_r + flange_lip, flange_t]],
            [for (i = [0 : 12]) let(z = flange_t + face * i / 12, y = (z - L_w / 2) / (face / 2))
                [wu_r + wu_crown * (1 - y * y), z]],
            [[wu_r + flange_lip, L_w - flange_t], [wu_r + flange_lip, L_w], [0, L_w]]));
        vbore(wu_axle_r, wu_ridge_r, wu_ridges, -1, L_w + 1, pip_gap);
    }
    // axle with V-ridges, collar (bracket stop) and square peg
    vaxle(wu_axle_r, wu_ridge_r, wu_ridges, 0, wu_collar0 + 0.3);
    translate([0, 0, wu_collar0]) cylinder(r1 = wu_axle_r, r2 = wu_axle_r + 2.4, h = 2.4 + 0.3, $fn = 64);   // 45 deg collar
    difference() {
        translate([-wu_peg / 2, -wu_peg / 2, wu_peg0]) cube([wu_peg, wu_peg, wu_peg_len]);
        translate([-wu_peg, 0, wu_peg0 + bracket_t + 3.5]) rotate([0, 90, 0]) cylinder(d = pin_hole, h = 2 * wu_peg, $fn = 24);
    }
}

// ---------------------------------------------------------------- station bracket
// Station frame: belt frame (X along the belt, Y across, Z up, Z=0 = belt top).
st_carry_z  = -(belt_t + wu_r + wu_crown);           // carry wheel axle
st_ret_top  = -48;                                   // return run's lower face rides here
st_ret_z    = st_ret_top - (wu_r + wu_crown);        // return wheel axle
st_y0       = half_w + pip_gap + 2.4 + 0.6;          // bracket inner face (wheel end + gap + collar)
st_bot      = st_ret_z - 16;                          // bracket bottom = top of the stake head
spig        = spike_sock - 2 * fit_gap;
module station_bracket2d() {
    difference() {
        hull() {
            translate([0, st_carry_z]) circle(r = 13);
            translate([0, st_ret_z]) circle(r = 13);
            translate([-spig / 2 - 6, st_bot]) square([spig + 12, 1]);
        }
        for (z = [st_carry_z, st_ret_z]) translate([-(wu_peg + 2 * fit_gap) / 2, z - (wu_peg + 2 * fit_gap) / 2])
            square(wu_peg + 2 * fit_gap);
    }
}
// print frame: plate lying flat (z = Y - st_y0), spigot block on the bed next to it
module station_bracket() {
    linear_extrude(bracket_t) station_bracket2d();
    translate([-spig / 2, st_bot - 28, 0]) cube([spig, 28 + 0.01, spig]);   // spigot (Y from st_y0 to st_y0+spig)
}

// ---------------------------------------------------------------- stakes
sock_depth = 30;
module stake_part(len) { stake(len, spike_leg, spike_t, spike_head, spike_sock, sock_depth); }

// ---------------------------------------------------------------- double-supported print-in-place roller (tail, snub)
// Print frame: axis = Z, roller z 0..L_w. Fixed axle with square ends sits inside
// counterbores; frame bosses enter the counterbores and grip the square ends.
dr_ridges = [dr_cb_d + 6, L_w - dr_cb_d - 6];
module dr_roller(r) {
    difference() {
        rotate_extrude($fn = 96) polygon(concat(
            [[dr_cb_r, 0], [r + flange_lip, 0], [r + flange_lip, flange_t]],
            [for (i = [0 : 12]) let(z = flange_t + face * i / 12, y = (z - L_w / 2) / (face / 2))
                [r + roll_crown * (1 - y * y), z]],
            [[r + flange_lip, L_w - flange_t], [r + flange_lip, L_w], [dr_cb_r, L_w], [dr_cb_r, L_w - dr_cb_d],
             [dr_axle_r + pip_gap, L_w - dr_cb_d], [dr_axle_r + pip_gap, dr_cb_d], [dr_cb_r, dr_cb_d]]));
        vbore(dr_axle_r, dr_ridge_r, dr_ridges, dr_cb_d - 0.5, L_w - dr_cb_d + 0.5, pip_gap);
    }
    // axle
    vaxle(dr_axle_r, dr_ridge_r, dr_ridges, dr_end_sq, L_w - dr_end_sq);
    for (z = [0, L_w - dr_end_sq - 0.5]) translate([-dr_end_sq / 2, -dr_end_sq / 2, z]) cube([dr_end_sq, dr_end_sq, dr_end_sq + 0.5]);
}
module tail_roller() { dr_roller(tail_r); }
module snub_roller() { dr_roller(snub_r); }
// boss that grips the axle end (part of the frames / take-up blocks), +Z = into the counterbore
module dr_boss(len = dr_cb_d - 1) {
    difference() {
        cylinder(r = boss_r, h = len);
        translate([-(dr_end_sq + 0.4) / 2, -(dr_end_sq + 0.4) / 2, len - (dr_end_sq - 0.5)]) cube([dr_end_sq + 0.4, dr_end_sq + 0.4, dr_end_sq]);
    }
}

// ---------------------------------------------------------------- drive roller with integral pinion
// Print frame: axis = Z. z 0..L_w roller (A side at z=0), journal stub through
// side frame B, 45 deg cone, then the 17T pinion. A separate pin forms the A journal.
drv_rs      = drive_r + drive_crown + rib_h;          // rib-tip radius at the centre
drv_jlen    = frame_gap + side_t + 1.0;               // journal length through the side frame
drv_cone_h  = pin_r + gear_m - journal_r;            // 45 deg cone up to the pinion tip radius
drv_pin_z0  = L_w + drv_jlen + drv_cone_h;           // pinion bottom
pin_shank_r = 5.0;
module drive_body2d() {
    difference() {
        circle(r = drive_r + rib_h, $fn = ribs * 2);
        for (k = [0 : ribs - 1]) rotate(k * 360 / ribs + 180 / ribs) translate([drive_r + rib_h, 0]) circle(r = 1.0, $fn = 12);
    }
}
module drive_roller() {
    difference() {
        union() {
            // flanges
            for (z = [0, L_w - flange_t]) translate([0, 0, z]) cylinder(r = drv_rs + flange_lip, h = flange_t, $fn = 96);
            // ribbed, crowned body
            intersection() {
                translate([0, 0, flange_t - 0.3]) linear_extrude(face + 0.6) drive_body2d();
                rotate_extrude($fn = 96) polygon(concat([[0, flange_t - 0.3]],
                    [for (i = [0 : 12]) let(z = flange_t + face * i / 12, y = (z - L_w / 2) / (face / 2))
                        [drive_r + rib_h + drive_crown * (1 - y * y), z]], [[0, L_w - flange_t + 0.3]]));
            }
            // journal stub, cone, pinion
            translate([0, 0, L_w - 0.01]) cylinder(r = journal_r, h = drv_jlen + 0.02);
            translate([0, 0, L_w + drv_jlen]) cylinder(r1 = journal_r, r2 = pin_r + gear_m, h = drv_cone_h, $fn = 96);
            translate([0, 0, drv_pin_z0 - 0.5]) linear_extrude(gear_face + 0.5) spur2d(pinion_z, gear_m, gear_pa, 2 * backlash);
        }
        translate([0, 0, -1]) cylinder(r = pin_shank_r + 0.12, h = 26);          // bore for the A-side journal pin
    }
}
module drive_pin() {     // A-side journal: journal + press-fit shank, printed standing on the journal end
    cylinder(r = journal_r, h = drv_jlen);
    translate([0, 0, drv_jlen - 0.01]) cylinder(r = pin_shank_r, h = 24);
}

// =====================================================================
// printed M8 fasteners (round thread, tolerant and strong enough for clamping frames)
// =====================================================================
b8_r = 4.0; b8_p = 2.0; b8_d = 0.9; hole8 = 8.6;
module bolt8(len) {                 // print: head on the bed
    rotate(30) hexagon(13, 5);
    translate([0, 0, 4.99]) intersection() {
        rthread(b8_r, b8_p, len, b8_d);
        union() { cylinder(r = b8_r + 1, h = len - 1.5); translate([0, 0, len - 1.51]) cylinder(r1 = b8_r + 1, r2 = b8_r - 1.2, h = 1.51); }
    }
}
module nut8() { difference() { rotate(30) hexagon(13, 7); translate([0, 0, -1]) rthread(b8_r, b8_p, 9, b8_d, 0.32); } }
module washer50() { tube(50, hole8, 3); }

// =====================================================================
// feet: crossbars on the grass; cheeks clamp a side frame tab; square holes take an L stake or a ground screw stud
// =====================================================================
foot_t = 6; foot_w = 30; cheek_t = 4.5; cheek_h = 24; anchor_y = 80; anchor_sq = 31.5; tab_bolt_z = foot_t + 12;
foot_len = 2 * (anchor_y + anchor_sq / 2 + 6);
module cheeks(len_x) {
    for (sg = [-1, 1]) for (yy = [side_in - 0.2 - cheek_t, side_out + 0.2])
        translate([-len_x / 2, sg > 0 ? yy : -yy - cheek_t, 0]) cube([len_x, cheek_t, cheek_h]);
}
module foot() {
    difference() {
        union() { translate([-foot_w / 2, -foot_len / 2, 0]) cube([foot_w, foot_len, foot_t]); cheeks(foot_w); }
        translate([0, -foot_len, tab_bolt_z]) rotate([-90, 0, 0]) cylinder(d = hole8, h = 2 * foot_len, $fn = 32);
        for (sg = [-1, 1]) translate([-anchor_sq / 2, sg * anchor_y - anchor_sq / 2, -1]) cube([anchor_sq, anchor_sq, foot_t + 2]);
    }
}
// side-frame tab that drops between a pair of cheeks (2D, frame plane X-Z), bolt hole at the tab centre
module tab2d(xc, zg) { translate([xc - foot_w / 2, zg + foot_t + 0.3]) square([foot_w, cheek_h - foot_t - 0.3]); }
module tabhole2d(xc, zg) { translate([xc, zg + tab_bolt_z]) circle(d = hole8, $fn = 32); }
module strut2d(a, b, w = web) { hull() { translate(a) circle(d = w); translate(b) circle(d = w); } }

// =====================================================================
// HEAD MODULE (frame: origin = drive axle, X toward the porch, Z up perpendicular to the belt, Y = gear side)
// =====================================================================
hz_g     = belt_t + drv_rs - head_h;          // ground under the head module
h_feet   = [-110, 60];                        // rear and front foot centres
gb_c     = [0, 0];
ua = line_deg;                                 // line angle in this frame
function uv(u, n) = [u * cos(ua) - n * sin(ua), u * sin(ua) + n * cos(ua)];
gb_holes = [uv(40, -5), uv(95, -12), uv(68, 22)];
Y_p      = half_w + drv_jlen + drv_cone_h + gear_face / 2;    // pinion mid-plane
Y_c      = Y_p + crown_R;                                    // crown axis offset

module head_side2d(is_b) {
    zg = hz_g;
    difference() {
        union() {
            circle(r = 20);
            for (xf = h_feet) { tab2d(xf, zg); strut2d([0, 0], [xf, zg + cheek_h - 4]); }
            strut2d([h_feet[0], zg + cheek_h - 4], [h_feet[1], zg + cheek_h - 4], 10);
            strut2d([0, 0], [0, zg + cheek_h - 4]);
            // candy guard frame above the belt (landing zone)
            strut2d([-130, belt_t + drv_rs + 36], [8, belt_t + drv_rs + 36], 8);
            strut2d([-130, belt_t + drv_rs + 36], [h_feet[0], zg + cheek_h - 4]);
            strut2d([0, 0], [8, belt_t + drv_rs + 36]);
            if (is_b) {
                for (h = gb_holes) { translate(h) circle(r = 10); strut2d([0, 0], h, 9); }
                strut2d(gb_holes[0], gb_holes[2], 9); strut2d(gb_holes[1], gb_holes[2], 9); strut2d(gb_holes[0], gb_holes[1], 9);
                strut2d(gb_holes[2], [8, belt_t + drv_rs + 36], 8);
            }
        }
        for (xf = h_feet) tabhole2d(xf, zg);
        if (is_b) {
            hull() { circle(r = journal_r + journal_gap); translate([60, 0]) circle(r = journal_r + journal_gap); }   // U-slot open to +X
            translate([14, -30]) square([pin_hole, 60]);                                                          // latch pin
            for (h = gb_holes) translate(h) circle(d = hole8, $fn = 32);
        } else circle(r = journal_r + journal_gap);
    }
}
// candy guard panel (thin, on the inner face) between the guard bar and the belt top
module guard2d() { translate([-128, belt_t + drv_rs + 2]) square([134, 30]); }
// print frame: inner face on the bed. A = -Y side, B = +Y side (mirror of A plus gearbox pads)
module head_side_a() { linear_extrude(side_t) head_side2d(false); linear_extrude(3) guard2d(); }
module head_side_b() { mirror([0, 1, 0]) { linear_extrude(side_t) head_side2d(true); linear_extrude(3) guard2d(); } }
module latch_pin() { cylinder(d = pin_d, h = 56); cylinder(d = 7, h = 2); }

// =====================================================================
// GEARBOX: print-in-place. Rotor = 34T crown gear + back cone + stub + male hex;
// body = bearing housing + arm + slab that bolts to head side frame B.
// Gearbox frame: u along the line (0 at the drive axle line), n perpendicular, y' = Y - Y_c.
// Print frame: z = gb_top_s - u (male hex end on the bed, crown teeth on top).
// =====================================================================
gb_tip_u   = pin_r - gear_m;                 // crown tooth tips (toward the pinion)
gb_root_u  = pin_r + 1.25 * gear_m;
gb_disk_u  = gb_root_u + 4;                  // back of the crown disk
crown_or   = crown_R + gear_face / 2 + 1.5;  // crown blank outer radius
gb_cone_u  = gb_disk_u + (crown_or - shaft_or);   // where the 45 deg back cone meets the stub
gb_hex0    = gb_top_s - 12;
gb_ridges  = [gb_cone_u + 7, gb_hex0 - 7];
gb_h0      = gb_cone_u + 2.5;                // housing from here up to gb_hex0 - 1
slab_y     = [side_out - Y_c, side_out + 8 - Y_c];
function pz(u) = gb_top_s - u;               // print z of line position u
module gb_rotor_blank() {      // print frame, includes a plain crown disk; teeth are cut by make_crown.py
    rotate_extrude($fn = 96) polygon(concat(
        [[0, pz(gb_top_s)], [hex_af / 2 / cos(30) * 0, pz(gb_top_s)]],
        [[shaft_or, pz(gb_hex0)], [shaft_or, pz(gb_ridges[1] + 2.5)], [shaft_ridge, pz(gb_ridges[1])], [shaft_or, pz(gb_ridges[1] - 2.5)],
         [shaft_or, pz(gb_ridges[0] + 2.5)], [shaft_ridge, pz(gb_ridges[0])], [shaft_or, pz(gb_ridges[0] - 2.5)],
         [shaft_or, pz(gb_cone_u)], [crown_or, pz(gb_disk_u)], [crown_or, pz(gb_tip_u)], [0, pz(gb_tip_u)]]));
    translate([0, 0, 0]) rotate(30) hexagon(hex_af, 12.01);     // male hex (couples into chute segment 1)
}
module gb_body() {
    difference() {
        union() {
            // housing tube with 45 deg conical base around the hex
            rotate_extrude($fn = 96) polygon([[ring_or, pz(gb_h0)], [ring_or, pz(gb_hex0 - 1)],
                                              [hex_af / 2 / cos(30) + pip_gap + 0.6, pz(gb_hex0 - 1) - (ring_or - hex_af / 2 / cos(30) - pip_gap - 0.6)],
                                              [hex_af / 2 / cos(30) + pip_gap + 0.6, pz(gb_h0)]]);
            // arm from the housing to the slab (stands on the bed)
            translate([-8, slab_y[1] - 0.01, 0]) cube([16, -slab_y[1] - ring_or + 3, pz(gb_h0)]);
            // slab
            difference() {
                hull() for (h = gb_holes) let(un = [h[0] * cos(ua) + h[1] * sin(ua), -h[0] * sin(ua) + h[1] * cos(ua)])
                    translate([un[1], slab_y[0], 0]) cube([1, 8, 1], center = false);
                translate([0, 0, 0]) cube(0);
            }
            gb_slab();
        }
        vbore(shaft_or, shaft_ridge, [pz(gb_ridges[0]), pz(gb_ridges[1])], -5, pz(gb_h0) + 5, pip_gap);
        cylinder(r = hex_af / 2 / cos(30) + pip_gap, h = 13, $fn = 6);
    }
}
module gb_slab() {
    // slab in the (n, z) plane at y' = slab_y; holes at the bolt positions; clear the drive cone (r 26 around u=0,n=0)
    difference() {
        hull() for (h = gb_holes) let(u = h[0] * cos(ua) + h[1] * sin(ua), nn = -h[0] * sin(ua) + h[1] * cos(ua))
            for (dz = [-12, 12]) for (dn = [-12, 12]) translate([nn + dn, slab_y[0], max(0, pz(u) + dz)]) cube([0.01, 8, 0.01]);
        for (h = gb_holes) let(u = h[0] * cos(ua) + h[1] * sin(ua), nn = -h[0] * sin(ua) + h[1] * cos(ua))
            translate([nn, slab_y[0] - 1, pz(u)]) rotate([-90, 0, 0]) cylinder(d = hole8, h = 10, $fn = 32);
        translate([0, slab_y[0] - 1, pz(0)]) rotate([-90, 0, 0]) cylinder(r = pin_r + gear_m + 3, h = 10);
    }
    // web from the slab bottom to the arm
    translate([-8, slab_y[0], 0]) cube([16, 8, max([for (h = gb_holes) pz(h[0] * cos(ua) + h[1] * sin(ua))]) ]);
}

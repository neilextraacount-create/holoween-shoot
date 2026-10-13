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
        union() {
            translate([-foot_w / 2, -foot_len / 2, 0]) cube([foot_w, foot_len, foot_t]);
            for (sg = [-1, 1]) translate([-(anchor_sq + 12) / 2, sg * anchor_y - (anchor_sq + 12) / 2, 0]) cube([anchor_sq + 12, anchor_sq + 12, foot_t]);
            cheeks(foot_w);
        }
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
gb_holes = [uv(50, -8), uv(100, -10), uv(75, 22)];   // >= 46 mm from the axle: nuts clear the roller flange
Y_p      = half_w + drv_jlen + drv_cone_h + gear_face / 2;    // pinion mid-plane
Y_c      = Y_p + crown_R;                                    // crown axis offset

module head_side2d(is_b) {
    zg = hz_g; zc = zg + cheek_h - 4;            // bottom chord height
    gtop = belt_t + drv_rs + 36;                 // candy guard bar
    difference() {
        union() {
            circle(r = 20);
            for (xf = h_feet) { tab2d(xf, zg); strut2d([0, 0], [xf, zc]); }
            strut2d([h_feet[0], zc], [h_feet[1], zc], 10);
            strut2d([0, 0], [0, zc]);
            // candy guard frame above the belt (landing zone)
            strut2d([-130, gtop], [8, gtop], 8);
            strut2d([-130, gtop], [h_feet[0], zc]);
            strut2d([0, 0], [8, gtop]);
            if (is_b) {
                // jaws above and below the open journal slot
                strut2d([0, 14.5], [48, 14.5], 12);
                strut2d([0, -14.5], [16, -14.5], 12);
                for (h = gb_holes) translate(h) circle(r = 10);
                strut2d(gb_holes[0], gb_holes[2], 9); strut2d(gb_holes[1], gb_holes[2], 9); strut2d(gb_holes[0], gb_holes[1], 9);
                strut2d(gb_holes[0], [30, 14.5], 9); strut2d([48, 14.5], gb_holes[1], 9);
                strut2d(gb_holes[2], [8, gtop], 8);
            }
        }
        for (xf = h_feet) tabhole2d(xf, zg);
        if (is_b) {
            hull() { circle(r = journal_r + journal_gap); translate([80, 0]) circle(r = journal_r + journal_gap); }   // slot open to +X
            for (h = gb_holes) translate(h) circle(d = hole8, $fn = 32);
        } else circle(r = journal_r + journal_gap);
    }
}
// candy guard panel (thin, on the inner face) between the guard bar and the belt top
module guard2d() { translate([-128, belt_t + drv_rs + 2]) square([134, 30]); }
// print frame: inner face on the bed. A = -Y side, B = +Y side (mirror of A plus gearbox pads)
module head_side_a() { linear_extrude(side_t) head_side2d(false); linear_extrude(3) guard2d(); }
module head_side_b() { mirror([0, 1, 0]) { linear_extrude(side_t) head_side2d(true); linear_extrude(3) guard2d(); } }

// =====================================================================
// GEARBOX: print-in-place. Rotor = 34T crown gear + back cone + stub + male hex;
// body = bearing housing + arm + slab that bolts to head side frame B.
// Gearbox frame: u along the line (0 at the drive axle line), n perpendicular, y' = Y - Y_c.
// Print frame: z = gb_top_s - u (male hex end on the bed, crown teeth on top).
// =====================================================================
gb_tip_u   = pin_r - gear_m;                 // crown tooth tips (toward the pinion)
gb_root_u  = pin_r + 1.25 * gear_m;
gb_disk_u  = gb_root_u + 4;                  // back of the crown disk
crown_or   = crown_R + gear_face / 2 - 0.5;  // crown blank outer radius (no rim: the roller's cone passes just outside)
gb_cone_u  = gb_disk_u + (crown_or - shaft_or);   // where the 45 deg back cone meets the stub
gb_hex0    = gb_top_s - 12;               // line position of the coupler socket bottom
gb_ridges  = [gb_cone_u + 7, gb_hex0 - 7];
gb_h0      = gb_cone_u + 2.5;                // housing from here up to gb_hex0 - 1
slab_y     = [side_out - Y_c, side_out + 8 - Y_c];
function pz(u) = gb_top_s - u;               // print z of line position u
module gb_rotor_blank() {      // print frame, includes a plain crown disk; teeth are cut by make_crown.py
    difference() {
        rotate_extrude($fn = 96) polygon(concat(
            [[0, 0], [shaft_or, 0]],
            [[shaft_or, pz(gb_ridges[1] + 2.5)], [shaft_ridge, pz(gb_ridges[1])], [shaft_or, pz(gb_ridges[1] - 2.5)],
             [shaft_or, pz(gb_ridges[0] + 2.5)], [shaft_ridge, pz(gb_ridges[0])], [shaft_or, pz(gb_ridges[0] - 2.5)],
             [shaft_or, pz(gb_cone_u)], [crown_or, pz(gb_disk_u)], [crown_or, pz(gb_tip_u)], [0, pz(gb_tip_u)]]));
        translate([0, 0, -1]) hexagon(hex_af + 2 * fit_gap, 13);       // socket for the hex coupler
    }
}
// ring sleeve: a short printed tube that plugs into counterbores at the ends of the
// bearing rings (gearbox, chute segments, crank head) and keeps the shaft line coaxial
slv_ri   = shaft_or + 0.9; slv_ro = 10.5; slv_len = 8;
cb_r     = slv_ro + fit_gap; cb_d = slv_len / 2 + 0.3;
module ring_sleeve() { difference() { cylinder(r = slv_ro, h = slv_len); translate([0, 0, -1]) cylinder(r = slv_ri, h = slv_len + 2); } }
module hex_coupler() {   // joins the hex sockets of two shafts (12 mm into each); printed standing
    intersection() {
        hexagon(hex_af, 23);
        hull() { cylinder(r = hex_af / 2, h = 23); translate([0, 0, 1]) cylinder(r = hex_af / 2 / cos(30) + 1, h = 21); }
    }
}
module gb_body() {
    difference() {
        union() {
            rotate_extrude($fn = 96) polygon([[shaft_or, 0], [ring_or, 0], [ring_or, pz(gb_h0)], [shaft_or, pz(gb_h0)]]);   // bearing housing
            translate([-8, slab_y[1] - 0.01, 0]) cube([16, -slab_y[1] - ring_or + 3, pz(gb_h0)]);                       // arm to the slab
            gb_slab();
        }
        vbore(shaft_or, shaft_ridge, [pz(gb_ridges[0]), pz(gb_ridges[1])], -5, pz(gb_h0) + 5, pip_gap);
        translate([0, 0, -1]) cylinder(r = cb_r, h = cb_d + 1);                                                       // sleeve counterbore
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

// =====================================================================
// TAIL MODULE (frame: origin = tail axle at mid take-up, X toward the head, Z up, Y across)
// The take-up block slides in a window in each side frame; a printed screw pulls it
// toward the rear (away from the head) through a square nut in the block.
// =====================================================================
tz_g     = -(tail_h - belt_t - tail_r - roll_crown);   // ground under the tail
tz_c     = tz_g + cheek_h - 4;                         // bottom chord
t_tabs   = [30, 90, 150];                              // rear foot, skid cheeks, skid cheeks
tu_in    = 20; tu_out = -40;                           // take-up travel of the axle (X)
tb_len   = 22; tb_h = 13.4;                            // take-up block length (X), height (Z)
tw       = [tu_out - tb_len / 2 - 0.5, tu_in + tb_len / 2 + 0.5];   // window X range
tw_h     = tb_h + 0.4;
t_rail   = 9;
t_rear   = tw[0] - 13.5;
t_front  = tw[1] + 10;
lug_x    = [t_rear, t_rear + 12];
scr_y    = 11;                                         // screw axis, outboard of the frame outer face
scr_hole = 2 * screw_r + 0.8;
tb_pad   = 22;                                         // pad thickness outboard of the frame (Y)
tn_sq    = 16; tn_t = 8;                               // square nut
scr_len  = 98;
module hole_x(r, len) {      // hole along +X with a 45 deg roof toward +Z (no support needed)
    rotate([0, 90, 0]) linear_extrude(len) union() { circle(r = r, $fn = 32); rotate(135) square(r); }
}
module tail_side2d() {
    n1 = [12, -tw_h / 2 - t_rail + 3.5]; n2 = [t_front - 4, -tw_h / 2 - t_rail + 3.5];
    difference() {
        union() {
            translate([t_rear, -tw_h / 2 - t_rail]) square([t_front - t_rear, tw_h + 2 * t_rail]);
            for (xt = t_tabs) tab2d(xt, tz_g);
            strut2d([t_tabs[0], tz_c], [t_tabs[2], tz_c], 10);
            strut2d(n1, [t_tabs[0], tz_c]);
            strut2d(n2, [t_tabs[0], tz_c]);
            strut2d(n2, [t_tabs[1], tz_c]);
            strut2d(n2, [t_tabs[2], tz_c]);
        }
        translate([tw[0], -tw_h / 2]) square([tw[1] - tw[0], tw_h]);
        for (xt = t_tabs) tabhole2d(xt, tz_g);
    }
}
// print frame (= -Y side): x = X, y = Z, z = distance outboard of the inner face
module tail_side_l() {
    linear_extrude(side_t) tail_side2d();
    difference() {
        translate([lug_x[0], -13, side_t - 0.01]) cube([lug_x[1] - lug_x[0], 26, scr_y + 11 + 0.01]);
        translate([lug_x[0] - 1, 0, side_t + scr_y]) hole_x(scr_hole / 2, 14);
    }
}
module tail_side_r() { mirror([0, 1, 0]) tail_side_l(); }
// take-up block, print frame: x = X - Xa, y = Z, z = 0 at the pad's outboard face, up = inward
module takeup_block() {
    zp = tb_pad - 0.2;                 // pad top = frame outer face (+0.2 running clearance)
    zi = tb_pad + side_t;              // frame inner face
    difference() {
        union() {
            translate([-tb_len / 2, -12, 0]) cube([tb_len, 24, zp]);
            translate([-tb_len / 2, -tb_h / 2, zp - 0.01]) cube([tb_len, tb_h, zi - zp + 0.02]);
            translate([-tb_h / 2, -tb_h / 2, zi]) cube([tb_h, tb_h, 9]);            // boss into the roller counterbore
        }
        translate([-(dr_end_sq + 0.4) / 2, -(dr_end_sq + 0.4) / 2, zi + 9 - 10]) cube([dr_end_sq + 0.4, dr_end_sq + 0.4, 11]);
        translate([-(tn_t + 0.4) / 2, -(tn_sq + 0.4) / 2, -1]) cube([tn_t + 0.4, tn_sq + 0.4, tb_pad - scr_y + tn_sq / 2 + 0.2 + 1]);
        translate([-tb_len / 2 - 1, 0, tb_pad - scr_y]) hole_x(scr_hole / 2, tb_len + 2);
    }
}
module takeup_nut() {
    difference() {
        translate([-tn_sq / 2, -tn_sq / 2, 0]) cube([tn_sq, tn_sq, tn_t]);
        translate([0, 0, -1]) rthread(screw_r, screw_pitch, tn_t + 2, 1.2, 0.35);
        translate([0, 0, -0.01]) cylinder(r1 = screw_r + 0.8, r2 = screw_r - 0.4, h = 1.2);    // lead-in chamfers
        translate([0, 0, tn_t - 1.19]) cylinder(r1 = screw_r - 0.4, r2 = screw_r + 0.8, h = 1.2);
    }
}
module takeup_screw() {     // knob on the bed
    difference() {
        cylinder(r = 11, h = 10, $fn = 64);
        for (k = [0 : 5]) rotate(k * 60) translate([13.2, 0, -1]) cylinder(r = 4, h = 12, $fn = 24);
    }
    translate([0, 0, 9.99]) intersection() {
        rthread(screw_r, screw_pitch, scr_len, 1.2);
        union() { cylinder(r = screw_r + 1, h = scr_len - 2); translate([0, 0, scr_len - 2.01]) cylinder(r1 = screw_r + 1, r2 = screw_r - 1.5, h = 2.01); }
    }
}
// skid (print frame = +Y side, base on the bed: x = X, y = Y, z = Z - tz_g)
sk_x     = [75, 314];
sk_y     = [side_in - 0.2 - cheek_t - 3, side_out + 0.2 + cheek_t + 3];
sk_anch  = [120, 292];
module skid_r() {
    difference() {
        union() {
            translate([sk_x[0], sk_y[0], 0]) cube([sk_x[1] - sk_x[0], sk_y[1] - sk_y[0], foot_t]);
            for (xa = sk_anch) translate([xa - (anchor_sq + 12) / 2, anchor_y - (anchor_sq + 12) / 2, 0]) cube([anchor_sq + 12, anchor_sq + 12, foot_t]);
            for (xt = [t_tabs[1], t_tabs[2]]) for (yy = [side_in - 0.2 - cheek_t, side_out + 0.2])
                translate([xt - foot_w / 2, yy, 0]) cube([foot_w, cheek_t, cheek_h]);
        }
        for (xt = [t_tabs[1], t_tabs[2]]) translate([xt, sk_y[0] - 1, tab_bolt_z]) rotate([-90, 0, 0]) cylinder(d = hole8, h = 40, $fn = 32);
        for (xa = sk_anch) translate([xa - anchor_sq / 2, anchor_y - anchor_sq / 2, -1]) cube([anchor_sq, anchor_sq, foot_t + 2]);
    }
}
module skid_l() { mirror([0, 1, 0]) skid_r(); }

// gear helpers for make_crown.py (not printed): the crown teeth are cut by sweeping
// a slightly fat pinion (backlash + tip clearance) through the true mesh motion
module pinion_cutter() { linear_extrude(height = gear_face + 6, center = true) spur2d(pinion_z, gear_m, gear_pa, -2 * backlash, 0.25, 0.3); }
module pinion_check()  { linear_extrude(height = gear_face, center = true) spur2d(pinion_z, gear_m, gear_pa, 2 * backlash); }

// =====================================================================
// part dispatch
// =====================================================================
if (part == "wheel_unit")      wheel_unit();
if (part == "station_bracket") station_bracket();
if (part == "tail_roller")     tail_roller();
if (part == "drive_roller")    drive_roller();
if (part == "drive_pin")       drive_pin();
if (part == "foot")            foot();
if (part == "bolt8_40")        bolt8(40);
if (part == "nut8")            nut8();
if (part == "washer50")        washer50();
if (part == "head_side_a")     head_side_a();
if (part == "head_side_b")     head_side_b();
if (part == "gb_rotor_blank")  gb_rotor_blank();
if (part == "gb_body")         gb_body();
if (part == "tail_side_l") tail_side_l();
if (part == "tail_side_r") tail_side_r();
if (part == "takeup_block") takeup_block();
if (part == "takeup_nut") takeup_nut();
if (part == "takeup_screw") takeup_screw();
if (part == "skid_r") skid_r();
if (part == "skid_l") skid_l();
if (part == "pinion_cutter") pinion_cutter();
if (part == "pinion_check")  pinion_check();
if (part == "ring_sleeve")   ring_sleeve();
if (part == "hex_coupler")   hex_coupler();

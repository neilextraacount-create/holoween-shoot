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
bk_boss     = 9;                                    // boss around each peg hole (longer hole = less wheel tilt)
wu_peg_len  = bracket_t + bk_boss + 7;
wu_rim      = 16;                                   // rim width at each end (the belt rides on its edges)
wu_foot_r   = 9.0;                                  // axle foot on the bed (inside a matching recess in the spool)
module wu_foot2d() { polygon([[0, 0], [wu_foot_r, 0], [wu_foot_r, 1.6], [wu_axle_r, 1.6 + wu_foot_r - wu_axle_r], [0, 1.6 + wu_foot_r - wu_axle_r]]); }
module wheel_unit() {
    R = wu_r + wu_crown; Rf = wu_r + flange_lip; rh = wu_axle_r + 4.5; ft = flange_t;
    // spool: two rims + a thin hub; 45 deg steps so nothing overhangs
    difference() {
        rotate_extrude($fn = 96) polygon([[0, 0], [Rf, 0], [Rf, ft], [R, ft], [R, ft + wu_rim], [rh, ft + wu_rim + R - rh],
            [rh, L_w - ft - wu_rim - (R - rh)], [R, L_w - ft - wu_rim], [R, L_w - ft - (Rf - R)], [Rf, L_w - ft], [Rf, L_w], [0, L_w]]);
        vbore(wu_axle_r, wu_ridge_r, wu_ridges, -1, L_w + 1, pip_gap);
        rotate_extrude($fn = 96) intersection() { offset(delta = pip_gap) wu_foot2d(); translate([0, -1]) square([50, 50]); }   // recess round the foot
    }
    // axle with V-ridges, collar (bracket stop) and square peg; a wide foot under it so the 115 mm
    // tall axle stands on 250 mm2 of bed, not 95
    vaxle(wu_axle_r, wu_ridge_r, wu_ridges, 0, wu_collar0 + 0.3);
    rotate_extrude($fn = 96) wu_foot2d();
    translate([0, 0, wu_collar0]) cylinder(r1 = wu_axle_r, r2 = wu_axle_r + 2.4, h = 2.4 + 0.3, $fn = 64);   // 45 deg collar
    difference() {
        translate([-wu_peg / 2, -wu_peg / 2, wu_peg0]) cube([wu_peg, wu_peg, wu_peg_len]);
        translate([-wu_peg, 0, wu_peg0 + 0.45 + bracket_t + bk_boss + 1.2]) rotate([0, 90, 0]) cylinder(d = pin_hole, h = 2 * wu_peg, $fn = 24);   // pin pulls the collar against the bracket
    }
}

// ---------------------------------------------------------------- station bracket
// Station frame: belt frame (X along the belt, Y across, Z up, Z=0 = belt top).
st_carry_z  = -(belt_t + wu_r + wu_crown);           // carry wheel axle
st_ret_top  = -48;                                   // return run's lower face rides here
st_ret_z    = st_ret_top - (wu_r + wu_crown);        // return wheel axle
st_y0       = half_w + pip_gap + 2.4 + 0.6;          // bracket inner face (wheel end + gap + collar)
st_bot      = st_ret_z - 22;                          // bracket bottom = top of the stake head (clears the return wheel flange)
spig        = spike_sock - 2 * fit_gap;
module station_bracket2d() {
    difference() {
        hull() {
            translate([0, st_carry_z]) circle(r = 13);
            translate([0, st_ret_z]) circle(r = 13);
            translate([-spig / 2 - 6, st_bot]) square([spig + 12, 1]);
        }
        for (z = [st_carry_z, st_ret_z]) translate([-(wu_peg + 0.2) / 2, z - (wu_peg + 0.2) / 2])
            square(wu_peg + 0.2);
    }
}
// print frame: plate lying flat (z = Y - st_y0), spigot block on the bed next to it
module station_bracket() {
    linear_extrude(bracket_t) station_bracket2d();
    for (z = [st_carry_z, st_ret_z]) translate([0, z, bracket_t - 0.01]) linear_extrude(bk_boss + 0.01) difference() {
        square(wu_peg + 8, center = true); square(wu_peg + 0.2, center = true); }
    translate([-spig / 2, st_bot - 28, 0]) cube([spig, 28 + 0.01, spig]);   // spigot (Y from st_y0 to st_y0+spig)
}

// ---------------------------------------------------------------- stakes
sock_depth = 30;
sk_hd = sock_depth + 2;                       // stake / post socket tube length
sk_c  = 3 + spike_sock / 2;                   // socket axis offset from the L corner (y and z)
module stake_part(len) { stake(len, spike_leg, spike_t, spike_sock, sock_depth); }

// ---------------------------------------------------------------- double-supported print-in-place roller (tail, snub)
// Print frame: axis = Z, roller z 0..L_w. Fixed axle with square ends sits inside
// counterbores; frame bosses enter the counterbores and grip the square ends.
dr_ridges = [dr_cb_d + 8, L_w - dr_cb_d - 8];
module dr_roller(r) {
    difference() {
        rotate_extrude($fn = 96) polygon(concat(
            [[dr_cb_r, 0], [r + flange_lip, 0], [r + flange_lip, flange_t]],
            [for (i = [0 : 12]) let(z = flange_t + (face - flange_lip) * i / 12, y = (z - L_w / 2) / (face / 2))
                [r + roll_crown * (1 - y * y), z]],                                  // crowned face up to the cone
            [[r + flange_lip, L_w - flange_t], [r + flange_lip, L_w], [dr_cb_r, L_w], [dr_cb_r, L_w - dr_cb_d],   // 45 deg cone under the top flange
             [dr_axle_r + pip_gap, L_w - dr_cb_d], [dr_axle_r + pip_gap, dr_cb_d + dr_cb_r - dr_axle_r - pip_gap], [dr_cb_r, dr_cb_d]]));   // 45 deg ceiling
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
        circle(r = drive_r + rib_h + drive_crown, $fn = ribs * 2);                    // the crown intersection below trims this to 30.5 at the ends
        for (k = [0 : ribs - 1]) rotate(k * 360 / ribs + 180 / ribs) translate([drive_r + rib_h, 0]) circle(r = 1.0, $fn = 12);
    }
}
module drive_roller() {
    difference() {
        union() {
            // flanges
            for (z = [0, L_w - flange_t]) translate([0, 0, z]) cylinder(r = drv_rs + flange_lip, h = flange_t, $fn = 96);
            translate([0, 0, L_w - flange_t - (drv_rs + flange_lip - drive_r + 1)]) cylinder(r1 = drive_r - 1, r2 = drv_rs + flange_lip, h = drv_rs + flange_lip - drive_r + 1.01, $fn = 96);   // 45 deg under the top flange, closes the rib grooves
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
module drive_pin() {     // A-side journal: pull flange + journal + shank with 4 crush ribs (press fit in the roller bore), printed standing
    cylinder(r = 10, h = 2);                                                   // flange to pull it out by (sits 1 mm off frame A)
    translate([0, 0, 1.99]) cylinder(r = journal_r, h = drv_jlen + 0.01);
    translate([0, 0, drv_jlen + 2 - 0.01]) {
        cylinder(r = pin_shank_r, h = 24);
        for (k = [0 : 3]) rotate(k * 90) translate([pin_shank_r - 0.5, -0.4, 2]) cube([0.85, 0.8, 22]);   // ribs to r 5.35 (bore 5.12)
        translate([0, 0, 24]) cylinder(r1 = pin_shank_r, r2 = pin_shank_r - 1, h = 1);                    // lead-in
    }
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
module nut8() { difference() { rotate(30) hexagon(13, 7); translate([0, 0, -1]) rthread(b8_r, b8_p, 9, b8_d, thread_gap); } }
module washer50() { tube(50, hole8, 3); }

// =====================================================================
// feet: crossbars on the grass; cheeks clamp a side frame tab; square holes take an L stake or a ground screw stud
// =====================================================================
foot_t = 4; foot_w = 24; cheek_t = 4.5; cheek_h = 24; anchor_y = 80; anchor_sq = 26.5; tab_bolt_z = foot_t + 12;
foot_len = 2 * (anchor_y + anchor_sq / 2 + 4.5);
module cheeks(len_x) {
    for (sg = [-1, 1]) for (yy = [side_in - 0.2 - cheek_t, side_out + 0.2])
        translate([-len_x / 2, sg > 0 ? yy : -yy - cheek_t, 0]) cube([len_x, cheek_t, cheek_h]);
}
module foot() {
    difference() {
        union() {
            translate([-foot_w / 2, -foot_len / 2, 0]) cube([foot_w, foot_len, foot_t]);
            for (sg = [-1, 1]) translate([-(anchor_sq + 9) / 2, sg * anchor_y - (anchor_sq + 9) / 2, 0]) cube([anchor_sq + 9, anchor_sq + 9, foot_t]);
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
gb_holes = [uv(50, -8), uv(100, -20), uv(75, 22)];   // >= 46 mm from the axle: nuts clear the roller flange
Y_p      = half_w + drv_jlen + drv_cone_h + gear_face / 2;    // pinion mid-plane
Y_c      = Y_p + crown_R;                                    // crown axis offset

module head_side2d(is_b) {
    zg = hz_g; zc = zg + cheek_h - 4;            // bottom chord height
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
            translate([stop_x[0], gtop - 4]) square([stop_x[1] - stop_x[0], 16]);     // trap stop post
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
slv_ri   = shaft_or + 0.9; slv_ro = shaft_or + 3.5; slv_len = 8;
cb_r     = slv_ro + fit_gap; cb_d = slv_len / 2 + 0.3;
module ring_sleeve() { difference() { cylinder(r = slv_ro, h = slv_len); translate([0, 0, -1]) cylinder(r = slv_ri, h = slv_len + 2); } }
// printed lying on a flat face: torsion then shears across the layers, not along a layer line
module hex_coupler_print() { translate([0, 0, hex_af / 2]) rotate([0, 90, 0]) rotate(30) hex_coupler(); }
module hex_coupler() {   // joins the hex sockets of two shafts (12 mm into each); axis = z
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
        cb_bottom();                                                                                                   // sleeve counterbore
    }
}
module gb_slab() {
    // slab in the (n, z) plane at y' = slab_y, web down to the bed; the bolt holes and the cone clearance cut both
    difference() {
        union() {
            hull() for (h = gb_holes) let(u = h[0] * cos(ua) + h[1] * sin(ua), nn = -h[0] * sin(ua) + h[1] * cos(ua))
                for (dz = [-12, 12]) for (dn = [-12, 12]) for (zz = [max(0, pz(u) + dz), 0]) translate([nn + dn, slab_y[0], zz]) cube([0.01, 8, 0.01]);   // reaches the bed: no overhang
            translate([-8, slab_y[0], 0]) cube([16, 8, max([for (h = gb_holes) pz(h[0] * cos(ua) + h[1] * sin(ua))]) ]);
        }
        for (h = gb_holes) let(u = h[0] * cos(ua) + h[1] * sin(ua), nn = -h[0] * sin(ua) + h[1] * cos(ua))
            translate([nn, slab_y[0] - 1, pz(u)]) rotate([-90, 0, 0]) cylinder(d = hole8, h = 10, $fn = 32);
        translate([0, slab_y[0] - 1, pz(0)]) rotate([-90, 0, 0]) cylinder(r = pin_r + gear_m + 3, h = 10);
    }
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
            translate([-tb_h / 2, -tb_h / 2, zi]) cube([tb_h, tb_h, 8.5]);          // boss into the roller counterbore (0.5 axle play)
        }
        translate([-(dr_end_sq + 0.4) / 2, -(dr_end_sq + 0.4) / 2, zi + 8.5 - 10]) cube([dr_end_sq + 0.4, dr_end_sq + 0.4, 11]);
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
sk_y     = [side_in - 0.2 - cheek_t - 3, max(side_out + 0.2 + cheek_t + 3, anchor_y - (anchor_sq + 9) / 2 + 3)];
sk_anch  = [120, 292];
module skid_r() {
    difference() {
        union() {
            translate([sk_x[0], sk_y[0], 0]) cube([sk_x[1] - sk_x[0], sk_y[1] - sk_y[0], foot_t]);
            for (xa = sk_anch) translate([xa - (anchor_sq + 9) / 2, anchor_y - (anchor_sq + 9) / 2, 0]) cube([anchor_sq + 9, anchor_sq + 9, foot_t]);
            for (xt = [t_tabs[1], t_tabs[2]]) for (yy = [side_in - 0.2 - cheek_t, side_out + 0.2])
                translate([xt - foot_w / 2, yy, 0]) cube([foot_w, cheek_t, cheek_h]);
        }
        for (xt = [t_tabs[1], t_tabs[2]]) translate([xt, sk_y[0] - 1, tab_bolt_z]) rotate([-90, 0, 0]) cylinder(d = hole8, h = 40, $fn = 32);
        for (xa = sk_anch) translate([xa - anchor_sq / 2, anchor_y - anchor_sq / 2, -1]) cube([anchor_sq, anchor_sq, foot_t + 2]);
    }
}
module skid_l() { mirror([0, 1, 0]) skid_r(); }

// =====================================================================
// LINE: candy chute + drive shaft from the porch down to the head.
// Print frame of every line part: x = Y, y = n, z = u - (part start); the shaft
// axis is at (x = Y_c, y = 0). The plain upper end of one trough slides into the
// socket at the lower end of the next; ring sleeves join the bearing rings and hex
// couplers join the shafts.
// =====================================================================
tr_in    = trough_w / 2;  tr_out = tr_in + trough_wall;
so_in    = tr_out + 0.3;  so_out = so_in + trough_wall;
fl_top   = trough_n;      fl_bot = fl_top - trough_floor;
sf_top   = fl_bot - 0.3;  sf_bot = sf_top - trough_floor;
wl_top   = trough_n + trough_h;
sock_len = 20; sock_tr = 2.0;               // socket length, 45 deg transition into the trough
rg_len   = 18; rg_ridge = 11;               // bearing ring length; V-ridge position from the ring end
lw_ang   = 52;                              // slope of the inclined webs (print overhang limit 45)
module sect(z0, z1, w, f, top) { translate([-w, f, z0]) cube([2 * w, top - f, z1 - z0]); }
module trough_body(L, socket = true, top = wl_top) {
    zt = socket ? sock_len + sock_tr : 0;
    difference() {
        union() {
            if (socket) {
                sect(0, sock_len, so_out, sf_bot, top);
                hull() { sect(sock_len - 0.01, sock_len, so_out, sf_bot, top); sect(zt, zt + 0.01, tr_out, fl_bot, top); }
            }
            sect(zt, L, tr_out, fl_bot, top);
        }
        if (socket) {
            sect(-1, sock_len, so_in, sf_top, top + 1);
            hull() { sect(sock_len - 0.01, sock_len, so_in, sf_top, top + 1); sect(zt, zt + 0.01, tr_in, fl_top, top + 1); }
        }
        sect(socket ? zt : -1, L + 1, tr_in, fl_top, top + 1);
    }
}
// bottom web (flat on the bed) and top web (rising at lw_ang) from a ring to the trough's outer lower corner
module web_bottom(fy) { linear_extrude(5) hull() { translate([Y_c - ring_or - 4, -3]) square([7.5, 6]); translate([so_out - 8, fy - 3.5]) square([8, 3.5]); } }
module web_top(zr, fy, wx) {
    d = norm([Y_c - ring_or - wx, fy]);
    hull() {
        translate([Y_c - ring_or - 4, -3, zr - 6]) cube([7.5, 6, 6]);
        translate([wx - 8, fy - 3.5, zr - 6 - tan(lw_ang) * (d - 7)]) cube([8, 3.5, 6]);
    }
}
// vertical (in print) web plate from p2 to p1, z 0..L, with diamond lightening holes [s, z, half-diagonal]
module web_plate(L, p1, p2, holes = []) {
    v = p1 - p2;
    translate([p2[0], p2[1], 0]) rotate(atan2(v[1], v[0])) difference() {
        translate([0, -0.6, 0]) cube([norm(v), 1.2, L]);
        for (h = holes) translate([h[0], 0, h[1]]) rotate([90, 0, 0]) rotate(45) cube([h[2] * sqrt(2), h[2] * sqrt(2), 4], center = true);
    }
}
// bearing ring around the shaft; the top ring of a part gets a 45 deg cone underneath so it prints
module bearing_ring(z0, cone) {
    rb = shaft_or + pip_gap;
    translate([Y_c, 0, 0]) rotate_extrude($fn = 96) polygon(cone ?
        [[0, z0], [rb, z0], [ring_or, z0 + ring_or - rb], [ring_or, z0 + rg_len], [0, z0 + rg_len]] :
        [[0, z0], [ring_or, z0], [ring_or, z0 + rg_len], [0, z0 + rg_len]]);
}
module cb_bottom() {                        // sleeve counterbore open at the bed, 45 deg ceiling (no flat ledge)
    translate([0, 0, -1]) cylinder(r = cb_r, h = cb_d + 1);
    translate([0, 0, cb_d - 0.01]) cylinder(r1 = cb_r, r2 = shaft_or + pip_gap, h = cb_r - shaft_or - pip_gap);
}
module line_bore(L, top_cb = true) {       // shaft bore with V-grooves + sleeve counterbores
    translate([Y_c, 0, 0]) {
        vbore(shaft_or, shaft_ridge, [rg_ridge, L - rg_ridge], -1, L + 1, pip_gap);
        cb_bottom();
        if (top_cb) translate([0, 0, L - cb_d]) cylinder(r = cb_r, h = cb_d + 1);
    }
}
module line_shaft(L, top_hex = true, extra = 0, bore_top = undef) {
    translate([Y_c, 0, 0]) difference() {
        vaxle(shaft_or, shaft_ridge, [rg_ridge, L - rg_ridge], 0, L + extra);
        translate([0, 0, -1]) cylinder(r = shaft_ir, h = (bore_top == undef ? L + extra + 2 : bore_top + 1));
        translate([0, 0, -0.01]) hexagon(hex_af + 2 * fit_gap, 12);
        if (top_hex) translate([0, 0, L - 12]) hexagon(hex_af + 2 * fit_gap, 12.01);
    }
}
plain_ext = sock_len - 0.5;                 // each chute's upper end reaches this far into the next piece's socket
module floor_bevel(ztop) {                  // bevel the top edge of a plain end so candy meets a ramp, not a step
    rotate([90, 0, 90]) linear_extrude(height = 2 * tr_in, center = true)
        polygon([[fl_top, ztop - 2.5], [fl_top + 5, ztop - 2.5], [fl_top + 5, ztop + 1], [fl_bot - 0.01, ztop + 1], [fl_bot - 0.01, ztop]]);
}
module chute_static(L) {
    difference() {
        union() {
            trough_body(L + plain_ext, true);
            bearing_ring(0, false); bearing_ring(L - rg_len, true);
            translate([Y_c, 0, rg_len - 0.01]) tube(2 * (shaft_or + pip_gap + 0.9), 2 * shaft_or + 0.4, L - 2 * rg_len + 1.0);    // carries the top ring (1 mm into its cone)
            web_bottom(sf_bot + 0.5);
            web_top(L, fl_bot + 0.5, tr_out);
        }
        line_bore(L);
        floor_bevel(L + plain_ext);
    }
}
module chute_segment() { chute_static(seg_len); line_shaft(seg_len); }

// ---------------------------------------------------------------- drop trap (bottom of the chute, between the head frames)
// Candy arrives at about 3 m/s, hits the end wall under the lid and falls through the floor slot onto the belt.
// Line position: u = tp_u0 (end wall) .. tp_u0 + tp_len (plain end inside segment 1's socket).
tp_u0    = -22;
tp_len   = gb_top_s + plain_ext - tp_u0;       // plain upper end reaches into segment 1's socket
tp_slot  = [2, 62];                         // floor slot, z range (u = -20 .. 40): passes 110 mm candy bars
tp_lid   = 72;                              // lid length from the end wall
tp_top   = trough_n + 34;                   // inside height under the lid: 34 mm (candy up to about 30 mm thick)
gtop     = belt_t + drv_rs + 36;            // guard bar centre line on the head frames (bar is 8 wide)
lg_z0    = gtop + 4 + 0.3;                  // ledge underside: 0.3 above the guard bar
lg_x     = [(tp_u0 + 1 - (lg_z0 + 2) * sin(ua)) / cos(ua),         // ledge X range (head frame) where it overlaps the trap walls
            ((lg_z0 + 2) * cos(ua) - fl_bot - 0.5) / sin(ua)];
stop_x   = [lg_x[0] - 8, lg_x[0] - 2];      // stop post on the head frames' guard bars
function head2line(X, Z) = [X * cos(ua) + Z * sin(ua), -X * sin(ua) + Z * cos(ua)];
module trap() {
    intersection() { translate([-500, -500, 0]) cube(1000); trap_raw(); }
}
module trap_raw() {
    zr = tp_lid + 4; hr = tp_top + 1.2 - wl_top;                                   // raised zone, then a 45 deg ramp down
    difference() {
        union() {
            trough_body(tp_len, false);
            sect(0, zr, tr_out, fl_bot, tp_top + 1.2);                                 // taller walls under the lid
            hull() { sect(zr - 0.01, zr, tr_out, fl_bot, tp_top + 1.2); sect(zr + hr, zr + hr + 0.01, tr_out, fl_bot, wl_top); }
            translate([-tr_out, tp_top - 0.01, 0]) cube([2 * tr_out, 1.21, tp_lid]);     // lid
            // ledges over the guard bars (modelled in head coordinates, then mapped to this print frame)
            for (sg = [-1, 1]) multmatrix([[0, 1, 0, 0], [-sin(ua), 0, cos(ua), 0], [cos(ua), 0, sin(ua), -tp_u0], [0, 0, 0, 1]])
                translate([lg_x[0], sg > 0 ? tr_out - 0.5 : -(side_in + side_t - 0.5), lg_z0])
                    cube([lg_x[1] - lg_x[0], side_in + side_t - 0.5 - tr_out + 0.5, 4]);
        }
        translate([-tr_in, fl_bot - 1, tp_slot[0]]) cube([2 * tr_in, trough_floor + 1.01, tp_slot[1] - tp_slot[0]]);   // drop slot
        translate([-tr_in, fl_top, 2]) cube([2 * tr_in, tp_top - fl_top - 0.01, tp_lid - 2]);                           // under the lid
        translate([-tr_in, fl_top, tp_lid]) cube([2 * tr_in, 300, tp_len]);                                             // open above
        floor_bevel(tp_len);
    }
}

// ---------------------------------------------------------------- crank head (top of the line, on the porch)
// Socket for segment N at the bottom, funnel above, crank shaft with a square drive on top,
// and a socket underneath for the porch stand post (world-vertical, diamond so it prints).
ch_len   = crank_head_len;
fn_z     = [60, 80];                         // funnel flare (45 deg) z range
fn_w     = 20;                               // funnel flare per side (and extra wall height)
sq_drv   = 12.4; sq_z = [4, 30];             // square drive above the top ring (z relative to ch_len)
aw       = line_deg + belt_deg;              // line angle to level
st_len   = 40;
st_pin   = st_len - 15;                     // locking pin, 15 mm inside the socket mouth
st_q     = [22, fl_bot, 12 + st_len * sin(aw)];   // stand socket axis meets the floor here; mouth corner rests on the bed
// The funnel's upper end is closed by a back wall that leans at 50 deg from the print bed
// (nearly vertical in use) instead of a flat roof, so it prints without support.
fn_k     = 1.2;                              // back wall rise (z) per mm of n
module below_plane(L, dz) {                  // half-space under the back-wall plane (+ dz)
    za = L - 2 - fn_k * (wl_top + fn_w - fl_top);
    rotate([90, 0, 90]) linear_extrude(height = 400, center = true)
        polygon([[-50, -1000], [-50, za + dz + fn_k * (-50 - fl_top)], [400, za + dz + fn_k * (400 - fl_top)], [400, -1000]]);
}
module funnel_body(L) {
    zt = sock_len + sock_tr;
    difference() {
        intersection() {
            union() {
                sect(0, sock_len, so_out, sf_bot, wl_top);
                hull() { sect(sock_len - 0.01, sock_len, so_out, sf_bot, wl_top); sect(zt, zt + 0.01, tr_out, fl_bot, wl_top); }
                sect(zt, fn_z[0], tr_out, fl_bot, wl_top);
                hull() { sect(fn_z[0] - 0.01, fn_z[0], tr_out, fl_bot, wl_top); sect(fn_z[1], fn_z[1] + 0.01, tr_out + fn_w, fl_bot, wl_top + fn_w); }
                sect(fn_z[1], L, tr_out + fn_w, fl_bot, wl_top + fn_w);
            }
            below_plane(L, 2);
        }
        funnel_inner(L);
    }
}
// the candy space inside the socket, chute and funnel (cut from the funnel and from everything bolted on)
module funnel_inner(L) {
    zt = sock_len + sock_tr;
    sect(-1, sock_len, so_in, sf_top, wl_top + 1);
    hull() { sect(sock_len - 0.01, sock_len, so_in, sf_top, wl_top + 1); sect(zt, zt + 0.01, tr_in, fl_top, wl_top + 1); }
    sect(zt, fn_z[0], tr_in, fl_top, wl_top + 1);
    hull() { sect(fn_z[0] - 0.01, fn_z[0], tr_in, fl_top, wl_top + 1); sect(fn_z[1], fn_z[1] + 0.01, tr_in + fn_w, fl_top, wl_top + fn_w + 1); }
    intersection() { sect(fn_z[1], L + 1, tr_in + fn_w, fl_top, wl_top + fn_w + 1); below_plane(L, 0); }
}
// world-vertical stand socket: local +z points down to the porch; local z 0..st_len, mouth at st_len
module stand_frame() { translate(st_q) rotate([90 + aw, 0, 0]) children(); }     // local +z = straight down (world)
module crank_head_static() {
    difference() {
        union() {
            funnel_body(ch_len);
            bearing_ring(0, false); bearing_ring(ch_len - rg_len, true);
            translate([Y_c, 0, rg_len - 0.01]) tube(2 * (shaft_or + pip_gap + 0.9), 2 * shaft_or + 0.4, ch_len - 2 * rg_len + 1.0);
            web_bottom(sf_bot + 0.5);
            web_plate(ch_len, [tr_out - 2, fl_bot + 0.3], [Y_c - ring_or + 1, 0]);   // solid: a lightening hole left thin, fragile strips
            stand_frame() rotate(45) translate([-(spike_sock + 7) / 2, -(spike_sock + 7) / 2, -6]) cube([spike_sock + 7, spike_sock + 7, st_len + 6]);
            // foot: a 4 mm fin from the block's lowest ridge down to the bed, so the block does not
            // start from a point on the plate; never in front of the mouth face, never above the socket floor
            intersection() {
                hull() {
                    stand_frame() rotate(45) translate([-(spike_sock + 7) / 2, -(spike_sock + 7) / 2, -6]) cube([4, 4, st_len + 6]);
                    translate([st_q[0] - 2, 60, 0]) cube([4, sf_bot + 0.5 - 60, 0.01]);
                }
                stand_frame() rotate(45) translate([-50, -50, -6]) cube([100, 100, st_len + 6]);
                translate([-500, -500, 0]) cube([1000, sf_bot + 0.5 + 500, 1000]);
            }
        }
        line_bore(ch_len, false);
        funnel_inner(ch_len);                                                              // socket, channel and funnel stay clear of the web plate and stand block
        stand_frame() rotate(45) translate([-spike_sock / 2, -spike_sock / 2, st_len - 30]) cube([spike_sock, spike_sock, 31]);
        stand_frame() rotate(45) translate([-20, 0, st_pin]) rotate([0, 90, 0]) cylinder(d = pin_hole, h = 40, $fn = 16);   // locking pin
    }
}
module crank_head_shaft() {
    line_shaft(ch_len, false, sq_z[0], ch_len + sq_z[0] - 10);      // solid under the square drive
    translate([Y_c, 0, 0]) difference() {
        translate([-sq_drv / 2, -sq_drv / 2, ch_len + sq_z[0] - 0.01]) cube([sq_drv, sq_drv, sq_z[1] - sq_z[0] + 0.01]);
        translate([-10, 0, ch_len + 22]) rotate([0, 90, 0]) cylinder(d = pin_hole, h = 20, $fn = 16);
    }
}
module crank_head() { intersection() { translate([-500, -500, 0]) cube(1000); crank_head_static(); } crank_head_shaft(); }

// ---------------------------------------------------------------- crank arm with a print-in-place spinning grip
ca_hub   = 22; ca_t = 8; ca_w = 16;
gr_r     = 6.5; gr_peak = 8.5; gr_out = 14; gr_len = 70;
module crank_arm() {
    difference() {
        union() {
            cylinder(r = 14, h = ca_hub);
            hull() { cylinder(r = ca_w / 2, h = ca_t); translate([crank_r, 0, 0]) cylinder(r = gr_out, h = ca_t); }
            translate([crank_r, 0, 0]) vaxle(gr_r, gr_peak, [ca_t + 10, ca_t + gr_len - 10], 0, ca_t + gr_len);
        }
        translate([-(sq_drv + 0.4) / 2, -(sq_drv + 0.4) / 2, -1]) cube([sq_drv + 0.4, sq_drv + 0.4, ca_hub + 2]);
        translate([-15, 0, 18]) rotate([0, 90, 0]) cylinder(d = pin_hole, h = 30, $fn = 16);
    }
    // grip sleeve (separate body): a 3 mm flat ring prints pip_gap above the arm top (2 layers of air,
    // like a support interface), then a 45 deg flare out to the full grip
    translate([crank_r, 0, 0]) difference() {
        rb = gr_r + pip_gap; z0 = ca_t + pip_gap;
        rotate_extrude($fn = 64) polygon([[rb, z0], [rb + 3, z0], [gr_out, z0 + gr_out - rb - 3], [gr_out, ca_t + gr_len], [rb, ca_t + gr_len]]);
        vbore(gr_r, gr_peak, [ca_t + 10, ca_t + gr_len - 10], 0, ca_t + gr_len + 1, pip_gap);
    }
}
// 3 mm pin with a head, printed lying on a 0.3 mm flat so its layers run along it (strong in shear)
module pin3() {
    fl = pin_d / 2 - 0.3;                                                     // axis height above the bed
    intersection() {
        translate([0, 0, fl]) rotate([0, 90, 0]) union() {
            cylinder(d = pin_d, h = 26, $fn = 24);
            translate([0, 0, -1.6]) cylinder(d = 7, h = 1.6, $fn = 32);       // head
        }
        translate([-10, -10, 0]) cube([50, 20, 20]);
    }
}
// belt splice: lay this on the 75 mm overlap, mark every hole, lift it off, pierce the marks, then sew box-and-X
module splice_template() {
    w = belt_w; lap = 75; e = 4;
    a = [e, e]; b = [lap - e, e]; c = [lap - e, w - e]; d = [e, w - e];
    function edge(p, q, n) = [for (k = [0 : n - 1]) p + (q - p) * k / n];          // n points, p included, q not
    function inner(p, q, n) = [for (k = [1 : n - 1]) p + (q - p) * k / n];
    nb = 11; nd = 15;                                                              // ~6 mm stitch spacing; odd nd keeps the X centre clear
    pts = concat(edge(a, b, nb), edge(b, c, nb), edge(c, d, nb), edge(d, a, nb), inner(a, c, nd), inner(b, d, nd));
    difference() {
        union() { cube([lap, w, 1.6]); translate([-3, -3, 0]) cube([3.01, w + 6, 6]); }   // lip butts against the belt end
        for (q = pts) translate([q[0], q[1], -1]) cylinder(d = 2.0, h = 4, $fn = 12);
    }
}
module stand_shim() { difference() { cube([40, 22, 3]); translate([20, 11, -1]) cylinder(d = 6, h = 5, $fn = 16); } }   // levels the porch stand arms

// ---------------------------------------------------------------- porch stand: tray + two L posts (spigot/socket joints)
spig_len = 28;
// The upper post's long bottom spigot slides into the lower post's deep head socket; a pin through one
// of 6 holes sets the height (+12 / -18 mm, 6 mm steps). Pins at the crank head and the tray carry uplift.
// From any hole the joint can collapse at least 35 mm, more than the 28 mm end spigots, so the stand goes
// in under (and comes out from under) a crank head that is already seated on the line. Every pin is
// 15 mm from its shoulder.
pu_dmin  = 24; pu_dmax = 54;                 // spigot insertion at the highest / lowest height hole (nominal 36)
ph_len   = 93;                               // lower post head tube (91 mm deep socket)
pu_spig  = pu_dmax + 35;                     // upper post bottom spigot: 35 mm of collapse left at the lowest hole
pu_gap   = pu_spig - 36;                     // nominal spigot showing between the lower head and the upper post
post_n   = spig_len + ph_len + (stand_h - sk_hd - pu_gap - ph_len) / 2 <= 315 ? 1 : 2;   // lower posts (two stacked for tall stands; 315 fits the bed diagonal)
post_b   = post_n == 1 ? (stand_h - sk_hd - pu_gap - ph_len) / 2 : (stand_h - sk_hd - pu_gap - 2 * ph_len) / 3;
post_ub  = stand_h - sk_hd - pu_gap - post_n * (post_b + ph_len);    // upper post body
module spigot_x(x0, len = spig_len) { translate([x0, 0, 0]) cube([len + 0.01, spig, spig]); }   // corner-aligned (prints on the bed); axis at (spig/2, spig/2)
pst_leg = 20; pst_t = 2.4;                    // porch post L profile
module post_l(len) { cube([len, pst_leg, pst_t]); cube([len, pst_t, pst_leg]); }
module zpin(x, y) { translate([x, y, -1]) cylinder(d = pin_hole, h = 40, $fn = 16); }   // vertical pin hole (print frame)
module post_lower() {       // spigot (into the tray, pinned) at x < 0, deep socket head at the top
    difference() {
        union() {
            spigot_x(-spig_len);
            post_l(post_b);
            translate([post_b, 0, 0]) cube([ph_len, spike_sock + 6, spike_sock + 6]);
        }
        translate([post_b + 2, 3, 3]) cube([ph_len, spike_sock, spike_sock + 0.3]);       // +0.3: the bridged ceiling sags
        zpin(-15, spig / 2);                                                             // tray pin (or the joint pin into another lower post)
        zpin(post_b + ph_len - 15, 3 + spike_sock / 2);                                  // height pin
    }
}
module post_upper() {
    difference() {
        union() { spigot_x(-pu_spig, pu_spig); post_l(post_ub); spigot_x(post_ub - 0.01); }
        for (d = [pu_dmin : 6 : pu_dmax]) zpin(-pu_spig + d - 15, spig / 2);             // height holes (nominal: 36 mm in)
        zpin(post_ub + spig_len - 13, spig / 2);                                         // crank head pin
    }
}
// tray: diamond socket so the arms line up with the line; long arm toward the porch, short arm
// toward the porch edge, side arms for stability. Put the candy bowl on it.
st_arms  = [150, 40, 118];                  // toward the porch, toward the edge, each side
module stand_tray() {
    at = 4; aw2 = 16;
    difference() {
        union() {
            translate([-st_arms[1], -aw2 / 2, 0]) cube([st_arms[0] + st_arms[1], aw2, at]);
            translate([-aw2 / 2, -st_arms[2], 0]) cube([aw2, 2 * st_arms[2], at]);
            rotate(45) translate([-(spike_sock + 6) / 2, -(spike_sock + 6) / 2, 0]) cube([spike_sock + 6, spike_sock + 6, sk_hd]);
        }
        rotate(45) translate([-spike_sock / 2, -spike_sock / 2, sk_hd - sock_depth]) cube([spike_sock, spike_sock, sock_depth + 1]);
        for (a = [45, 135]) rotate(a) translate([-20, 0, sk_hd - 15]) rotate([0, 90, 0]) cylinder(d = pin_hole, h = 40, $fn = 16);   // tray pin (either way round)
    }
}
// ---------------------------------------------------------------- anchors
// Ground screw: printed head-down. Hex head with an M8 female thread (a printed bolt clamps
// the foot down onto it), shaft with a helical buttress ridge (flat face toward the tip, 45 deg
// face toward the head so it prints), conical tip. Turn clockwise (seen from above) to drive it in.
gs_r = 7.0; gs_ridge = 6; gs_p = 14; gs_w = 1.5; gs_len = 150; gs_head = 12; gs_af = 22;
module gs_ridge2d() {
    rt = gs_r + gs_ridge;
    n = 24;
    polygon(concat([[gs_r - 1, 0], [rt, 0]],
        [for (i = [0 : 4]) let(a = gs_w * 360 / gs_p * i / 4) [rt * cos(a), rt * sin(a)]],
        [for (i = [0 : n]) let(r = rt - gs_ridge * i / n, a = (rt - r + gs_w) * 360 / gs_p) [r * cos(a), r * sin(a)]],
        [for (i = [0 : 8]) let(a = (gs_ridge + gs_w) * 360 / gs_p * (1 - i / 8)) [(gs_r - 1) * cos(a), (gs_r - 1) * sin(a)]]));
}
module ground_screw() {
    z0 = gs_head + 6; z1 = gs_len - 45;
    difference() {
        union() {
            rotate(30) hexagon(gs_af, gs_head);
            translate([0, 0, gs_head - 0.01]) cylinder(r1 = gs_af / 2, r2 = gs_r, h = gs_af / 2 - gs_r + 0.01);
            cylinder(r = gs_r, h = z1 + 0.01);
            translate([0, 0, z1]) cylinder(r1 = gs_r, r2 = 1.5, h = gs_len - z1);
            intersection() {
                translate([0, 0, z0]) linear_extrude(height = z1 - z0 + 30, twist = -360 * (z1 - z0 + 30) / gs_p, slices = 160, convexity = 6) gs_ridge2d();
                union() { translate([0, 0, z0]) cylinder(r1 = gs_r, r2 = gs_r + gs_ridge, h = gs_ridge);           // 45 deg run-in
                          translate([0, 0, z0 + gs_ridge - 0.01]) cylinder(r = gs_r + gs_ridge, h = z1 - z0 - gs_ridge);
                          translate([0, 0, z1 - 0.02]) cylinder(r1 = gs_r + gs_ridge, r2 = 1.5, h = (gs_len - z1) * 0.8); }
            }
        }
        translate([0, 0, -1]) rthread(b8_r, b8_p, 30, b8_d, thread_gap);  // 29 mm deep: a 28 mm bolt through washer + foot never bottoms out
        translate([0, 0, -0.01]) cylinder(r1 = b8_r + 0.9, r2 = b8_r - 0.3, h = 1.2);
    }
}
module gs_wrench() {     // T-wrench for the ground screw head
    difference() {
        union() {
            cylinder(r = gs_af / 2 / cos(30) + 4, h = 24);
            translate([-80, -8, 0]) cube([160, 16, 12]);
        }
        translate([0, 0, -1]) rotate(30) hexagon(gs_af + 0.5, 26);
    }
}
module spike() { nail_spike(130, spike_leg, spike_t, 30); }
module bolt8_28() { bolt8(28); }
module station_stake(i) { stake_part(stake_len[i - 1]); }
module stake_cap() {     // push the stakes in through this, not on the socket rim
    translate([-11, -11, 0]) cube([22, 22, 8]);
    translate([-spig / 2, -spig / 2, 7.99]) cube([spig, spig, 20]);
}

// ---------------------------------------------------------------- test coupon: print this first
// three print-in-place spinners (gap 0.35 / 0.45 / 0.55), the slip fits used on the machine
// (square socket, hex coupler socket, ring-sleeve counterbore, journal hole) and an M8 nut.
module tc_spinner(gap) {      // sleeve and axle both on the bed (as in the wheels, rollers and shafts)
    vaxle(4.5, 6.5, [6], 0, 17);
    translate([-2, -7, 16.99]) cube([4, 14, 3]);                                  // grip bar on the axle
    difference() {
        cylinder(r = 11, h = 12, $fn = 48);
        vbore(4.5, 6.5, [6], -1, 13, gap);
    }
}
module test_coupon() {
    gaps = [0.35, 0.45, 0.55];
    difference() {
        translate([-14, -14, 0]) cube([150, 64, 3]);
        for (i = [0 : 2]) for (k = [0 : i]) translate([i * 26 - 4 + k * 3, -11, 2]) cylinder(d = 1.6, h = 2, $fn = 8);   // 1/2/3 dots
    }
    for (i = [0 : 2]) translate([i * 26, -32, 0]) tc_spinner(gaps[i]);                    // beside the plate, on the bed
    translate([0, 24, 2.99]) difference() {
        translate([-12, -12, 0]) cube([136, 24, 12]);
        translate([-spike_sock / 2, -spike_sock / 2, 2]) cube([spike_sock, spike_sock, 11]);                 // stake / tray socket (spigot 15.6)
        translate([28, 0, 2]) hexagon(hex_af + 2 * fit_gap, 11);                                          // shaft hex socket (coupler)
        translate([56, 0, 2]) cylinder(r = cb_r, h = 11);                                                 // ring-sleeve counterbore
        translate([84, 0, -1]) cylinder(r = journal_r + journal_gap, h = 14);                             // drive journal hole
        translate([110, 0, -1]) rthread(b8_r, b8_p, 14, b8_d, thread_gap);                                // M8 nut thread
    }
}

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
if (part == "hex_coupler")   hex_coupler_print();
if (part == "chute_segment") chute_segment();
if (part == "trap")          trap();
if (part == "crank_head") crank_head();
if (part == "crank_arm") crank_arm();
if (part == "pin3") pin3();
if (part == "splice_template") splice_template();
if (part == "stand_shim") stand_shim();
if (part == "post_lower") post_lower();
if (part == "post_upper") post_upper();
if (part == "stand_tray") stand_tray();
if (part == "ground_screw") ground_screw();
if (part == "gs_wrench") gs_wrench();
if (part == "spike") spike();
if (part == "bolt8_28") bolt8_28();
if (part == "test_coupon") test_coupon();
if (part == "stake_1") station_stake(1);
if (part == "stake_2") station_stake(2);
if (part == "stake_3") station_stake(3);
if (part == "stake_4") station_stake(4);
if (part == "stake_cap")     stake_cap();

// =====================================================================
// SIMPLE candy conveyor (v5): 20 printed parts + the belt, no bolts.
//   head  (foot of the steps): frame, drive roller + pin, crank gear + pin, 2 anchors
//   tail  (sidewalk):          frame, roller + pin, 2 wedges, 2 anchors
//   3 stations (lawn):         stake + wheel cassette (2 print-in-place wheels)
// World frame: X along the belt toward the sidewalk, Y across (+Y = crank side), Z up.
// Each part is modelled in its PRINT orientation (flat face down); asm_* modules place
// the parts in their module's frame for the checks (build.py).
//   openscad -D 'part="head_frame"' -o head_frame.stl simple.scad
// =====================================================================
use <../cad/lib.scad>

part = "none";
$fn = 64;
IN = 25.4;

// ---------------------------------------------------------------- belt and fits
belt_w = 76.2; belt_t = 1.7;              // 3 in polypropylene webbing: measure yours
face = belt_w + 10; flange_t = 2; flange_lip = 2.5;
L_w = face + 2 * flange_t;                // roller / wheel length between flange faces (90)
pip_gap = 0.45;                           // print-in-place running gap
fit_gap = 0.2;                            // slip fit
j_gap = 0.3;                              // journal in its slot (radial)

// ---------------------------------------------------------------- frames
wall_t = 4;
w_in = L_w / 2 + 1; w_out = w_in + wall_t;   // side wall faces |Y| = 46 .. 52
base_t = 4;
web = 8;                                  // frame strut width
hole_sq = 24.6;                           // anchor-stake holes in the frame bases

// ---------------------------------------------------------------- rollers
j_r = 8;                                  // every journal is Ø16 (both rollers, both ends)
drive_r = 30; drive_crown = 0.3; rib_h = 0.5; ribs = 64;
drv_rs = drive_r + drive_crown + rib_h;   // rib-tip radius at the middle
tail_r = 20; tail_crown = 0.3;
pin_shank_r = 5.0;                        // press-in journal pin (one per roller)
j_len = 8;                                // journal length: flange face -> 1 mm past the wall

// ---------------------------------------------------------------- head and crank
head_h = 6 * IN;                          // belt top above the lawn at the head
hz = head_h - belt_t - drv_rs;            // drive roller axis height
gm = 2; z_pin = 16; z_gear = 40; g_face = 8; backlash = 0.15;   // 2.5 : 1 step-up
C = gm * (z_pin + z_gear) / 2;            // centre distance 56
mesh_a = 60;                              // gear sits up and toward the tail: its push holds the roller down in the slots
g_c = [C * cos(mesh_a), hz + C * sin(mesh_a)];
pin_tip_r = gm * z_pin / 2 + gm;
p_y0 = L_w / 2 + j_len + (pin_tip_r - j_r);   // pinion inboard face (Y 63)
p_face = 7.5;
g_y0 = p_y0 + 0.5;                        // gear Y 63.5 .. 71.5 (clear of the cone under the pinion), arm 71.5 .. 78.5
arm_t = 7; crank_r = 100;
boss_y1 = g_y0 - 0.5;                     // pin boss on wall B, outer face
cp_r = 6;                                 // crank pin
gr_r = 6.5; gr_peak = 8.5; gr_out = 11.5; gr_len = 70;   // spinning grip
h_x = [-46, 74];                          // head base X range
h_back = [-46, -42];                      // back wall (4 mm)
h_top = 150;

// ---------------------------------------------------------------- tail and take-up
tail_h = 9 * IN;                          // belt top above the sidewalk at the tail
tz = tail_h - belt_t - tail_r - tail_crown;   // tail axis height (207)
x_f = -60;                                // wedge window front face
win_w = 26;                               // wedge window width (X)
win_z0 = tz - 140;                        // window bottom (the wedge tip can go this low)
slot_end = -20;                           // closed rear end of the journal slot
wd_ang = 8; wd_t0 = 3; wd_len = 175;      // wedge: 8 deg taper, 3 mm tip
t_x = [-200, 0];                          // tail base X range (x = 0 is the lawn edge)
t_top = tz + j_r + j_gap + 9;

// ---------------------------------------------------------------- stations
wu_r = 12.5; wu_crown = 0.3; wu_axle_r = 5.5; wu_ridge_r = 7.5; wu_rim = 16; wu_foot_r = 9;
wu_ridges = [14, L_w - 14];
st_carry = belt_t + wu_r + wu_crown;      // carry axle below the belt top (14.5)
st_ret = 48 + wu_r + wu_crown;            // return axle below the belt top (60.8)
st_dx = st_ret - st_carry;                // axle spacing in the cassette (46.3)
cs_plate = [L_w + 6.6, L_w + 12.6];       // cassette top plate (print z)
cs_blk_x = [st_dx + wu_r + flange_lip + 2.7, st_dx + wu_r + flange_lip + 32.7];   // socket block (print x)
cs_blk_z = 33;
spig = 14; sock_d = 25;                   // stake spigot and its socket
st_sock_x = cs_blk_x[1];                  // socket mouth (print x)
stake_leg = 22; stake_t = 2.4; tip = 50;
station_len = [255, 235, 215];            // station stakes, tip to shoulder (build.py checks these)
anchor_len = 200;

// =====================================================================
// helpers
// =====================================================================
module strut(a, b, w = web) { hull() { translate(a) circle(d = w); translate(b) circle(d = w); } }
// 2D shape in the XZ plane -> wall between y0 and y1
module xz(y0, y1) { translate([0, y1, 0]) rotate([90, 0, 0]) linear_extrude(y1 - y0) children(); }
// 2D shape in the YZ plane -> wall between x0 and x1
module yz(x0, x1) { translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(x1 - x0) children(); }
// hole through a printed-upright wall: round with a 45 deg roof (prints without support)
module tear2d(r) { union() { circle(r = r); rotate(45) square(r); } }
// jack-o'-lantern face (holes); every top edge is 60 deg or steeper so it prints upright.
// s = face width / 100
module pumpkin2d(s = 1) {
    scale(s) {
        for (sg = [-1, 1]) polygon([[sg * 12, 16], [sg * 40, 16], [sg * 26, 40]]);           // eyes
        polygon([[-8, 0], [8, 0], [0, 13]]);                                                  // nose
        for (t = [[-34, -12], [-17, -19], [0, -21], [17, -19], [34, -12]])                    // grin: a row of teeth gaps
            translate(t) polygon([[-7.5, -6], [7.5, -6], [0, 8]]);
    }
}
// L-profile stake lying on one leg along +X from x = 0 (tip at x = len)
module stake_body(len) {
    hull() { cube([len - tip, stake_leg, stake_t]); translate([len - 0.5, 0, 0]) cube([0.5, stake_t, stake_t]); }
    hull() { cube([len - tip, stake_t, stake_leg]); translate([len - 0.5, 0, 0]) cube([0.5, stake_t, stake_t]); }
}

// =====================================================================
// HEAD FRAME (print = world, z up; origin on the ground under the roller axis)
// =====================================================================
module head_wall2d(b) {
    difference() {
        union() {
            strut([-43, 5], [-43, h_top - 2]);                              // back post
            strut([-43, h_top - 25], [-20, h_top - 2]);                     // top rail at 45 deg (prints without sagging)
            strut([-43, 40], [-20, 110]);
            translate([-20.5, 0]) square([41, h_top]);                      // slot block (12 mm columns each side)
            strut([57, 5], [57, 113]);                                      // front post
            strut([20, 30], [57, 100]);
            strut([20, h_top], [57, 113]);                                // front guard rail at 45 deg
            strut([-43, 5], [70, 5]);                                       // bottom chord
            if (b) {
                hull() { translate(g_c) rotate(180) tear2d(14); translate([8, 136]) square([12.5, 14]); }   // boss on the slot block
                strut([57, 113], g_c);
            }
        }
        hull() { translate([0, hz]) circle(r = j_r + j_gap); translate([0, hz + 200]) circle(r = j_r + j_gap); }   // open-top journal slot
        if (b) translate(g_c) tear2d(cp_r + fit_gap);
    }
}
module head_base() {
    difference() {
        union() {
            for (s = [-1, 1]) translate([h_x[0], s > 0 ? w_in - 14 : -w_out, 0]) cube([h_x[1] - h_x[0], 14 + wall_t, base_t]);   // rails
            translate([h_x[0], -w_out, 0]) cube([36, 2 * w_out, base_t]);                    // back strip
            translate([h_x[1] - 32, -w_out, 0]) cube([32, 2 * w_out, base_t]);               // front strip
        }
        for (x = [h_x[0] + 20, h_x[1] - 16]) translate([x - hole_sq / 2, -hole_sq / 2, -1]) cube([hole_sq, hole_sq, base_t + 2]);
    }
}
module head_frame() {
    head_base();
    xz(w_in, w_out) head_wall2d(true);
    xz(-w_out, -w_in) head_wall2d(false);
    // back wall with a jack-o'-lantern face (the side you sit at)
    yz(h_back[0], h_back[1]) difference() {
        translate([-w_out, 0]) square([2 * w_out, 112]);
        translate([0, 58]) pumpkin2d(0.95);
    }
    // pin boss on wall B: teardrop section so it prints upright
    translate([g_c[0], w_out - 0.01, g_c[1]]) rotate([-90, 0, 0]) difference() {
        linear_extrude(boss_y1 - w_out + 0.01) tear2d(11);
        translate([0, 0, -1]) linear_extrude(20) rotate(180) tear2d(cp_r + fit_gap);
    }
}

// =====================================================================
// DRIVE ROLLER (print: axis = z, flange A on the bed; world Y = z - L_w/2)
// =====================================================================
module drive_body2d() {
    difference() {
        circle(r = drv_rs, $fn = ribs * 2);
        for (k = [0 : ribs - 1]) rotate(k * 360 / ribs + 180 / ribs) translate([drive_r + rib_h, 0]) circle(r = 1.0, $fn = 12);
    }
}
module drive_roller() {
    rf = drv_rs + flange_lip;
    difference() {
        union() {
            cylinder(r = rf, h = flange_t, $fn = 96);                                           // flange A (on the bed)
            translate([0, 0, L_w - flange_t]) cylinder(r = rf, h = flange_t, $fn = 96);        // flange B
            translate([0, 0, L_w - flange_t - (rf - drive_r + 1)]) cylinder(r1 = drive_r - 1, r2 = rf, h = rf - drive_r + 1.01, $fn = 96);
            intersection() {
                translate([0, 0, flange_t - 0.3]) linear_extrude(face + 0.6) drive_body2d();
                rotate_extrude($fn = 96) polygon(concat([[0, flange_t - 0.3]],
                    [for (i = [0 : 12]) let(z = flange_t + face * i / 12, y = (z - L_w / 2) / (face / 2))
                        [drive_r + rib_h + drive_crown * (1 - y * y), z]], [[0, L_w - flange_t + 0.3]]));
            }
            translate([0, 0, L_w - 0.01]) cylinder(r = j_r, h = j_len + 0.02);                 // journal B
            translate([0, 0, L_w + j_len]) cylinder(r1 = j_r, r2 = pin_tip_r, h = pin_tip_r - j_r, $fn = 96);
            translate([0, 0, p_y0 + L_w / 2 - 0.5]) linear_extrude(p_face + 0.5) spur2d(z_pin, gm, 20, 2 * backlash);
        }
        translate([0, 0, -1]) cylinder(r = pin_shank_r + 0.12, h = 27);                     // bore for the A-side journal pin
    }
}
// press-in journal pin (one per roller): pull flange, journal, ribbed shank
module journal_pin() {
    cylinder(r = 10, h = 2);
    translate([0, 0, 1.99]) cylinder(r = j_r, h = j_len + 0.01);
    translate([0, 0, j_len + 2 - 0.01]) {
        cylinder(r = pin_shank_r, h = 24);
        for (k = [0 : 3]) rotate(k * 90) translate([pin_shank_r - 0.5, -0.4, 2]) cube([0.85, 0.8, 22]);
        translate([0, 0, 24]) cylinder(r1 = pin_shank_r, r2 = pin_shank_r - 1, h = 1);
    }
}

// =====================================================================
// CRANK GEAR (print: inboard face on the bed; world Y = z + g_y0): 40T gear with a hex hub
// CRANK ARM  (print: inboard face on the bed; world Y = z + g_y0 + g_face): slides on the hex
//            hub, print-in-place spinning grip. The crank pin holds both on wall B.
// =====================================================================
hub_af = 22;
module crank_gear() {
    difference() {
        union() {
            linear_extrude(g_face) difference() {
                spur2d(z_gear, gm, 20, 2 * backlash);
                for (k = [0 : 5]) rotate(k * 60 + 30) translate([25, 0]) circle(r = 8);     // lightening holes
            }
            translate([0, 0, g_face - 0.01]) rotate(30) hexagon(hub_af, arm_t - 0.5 + 0.01);  // hub (the arm's socket)
        }
        translate([0, 0, -1]) cylinder(r = cp_r + 0.25, h = 40);
    }
}
module crank_arm() {
    w0 = hub_af + 12; w1 = 2 * gr_out;
    difference() {
        union() {
            linear_extrude(arm_t) hull() { circle(d = w0); translate([crank_r, 0]) circle(d = w1); }
            translate([crank_r, 0, 0]) vaxle(gr_r, gr_peak, [arm_t + 10, arm_t + gr_len - 10], 0, arm_t + gr_len);
        }
        translate([0, 0, -1]) rotate(30) hexagon(hub_af + 2 * fit_gap, arm_t + 2);              // hex socket
    }
    translate([crank_r, 0, 0]) difference() {                                                 // grip sleeve
        rb = gr_r + pip_gap; z0 = arm_t + pip_gap; zt = arm_t + gr_len;
        rotate_extrude($fn = 64) polygon([[rb, z0], [rb + 3, z0], [gr_out, z0 + gr_out - rb - 3], [gr_out, zt], [rb, zt]]);
        vbore(gr_r, gr_peak, [arm_t + 10, arm_t + gr_len - 10], 0, zt + 1, pip_gap);
    }
}
// crank pin: printed lying (axis along x on a 0.5 mm flat); head outboard on the arm, split snap tip
// inboard: its catch face sits 0.3 mm inside wall B's inner face
cp_shank = (g_y0 + g_face + arm_t) - (w_in - 0.3);   // arm outer face -> catch face
cp_len = cp_shank + 3;
module crank_pin() {
    intersection() {
        translate([0, 0, cp_r - 0.5]) rotate([0, 90, 0]) difference() {
            union() {
                translate([0, 0, -3]) cylinder(r = 10, h = 3);                                // head
                cylinder(r = cp_r, h = cp_shank + 0.01);
                translate([0, 0, cp_shank]) cylinder(r1 = cp_r + 0.8, r2 = cp_r - 0.8, h = 3);   // barb: flat catch face, sloped lead-in
            }
            translate([-cp_r - 2, -1.5, cp_len - 15]) cube([2 * cp_r + 4, 3, 16]);           // split: the halves squeeze through the hole
        }
        translate([-10, -20, 0]) cube([cp_len + 20, 40, 30]);
    }
}

// =====================================================================
// TAIL FRAME (print = world; origin on the ground at the lawn edge, X toward the sidewalk)
// =====================================================================
module tail_wall2d() {
    fl = tz - j_r - j_gap;                                                   // slot floor
    difference() {
        union() {
            strut([t_x[0] + 6, 5], [t_x[0] + 6, 145]);                           // front post
            strut([t_x[0] + 6, 145], [x_f - 6, t_top - 6]);                       // top chord
            translate([x_f - 12, 0]) square([12, t_top]);                         // wedge post (its back face takes the wedge)
            strut([t_x[0] + 6, 5], [slot_end + 5, 5]);                            // bottom chord
            strut([t_x[0] + 6, 70], [x_f - 6, 15]);
            strut([t_x[0] + 6, 75], [x_f - 6, 150]);
            // rear tower: two posts and X braces; it carries the slot floor and the end stop
            strut([x_f + win_w + 6, 6], [x_f + win_w + 6, fl - 6], 12);
            strut([slot_end + 6, 6], [slot_end + 6, tz], 12);
            for (z = [5, 65, 125]) { strut([x_f + win_w + 5, z], [slot_end + 5, z + 60]); strut([x_f + win_w + 5, z + 60], [slot_end + 5, z]); }
            translate([x_f + win_w, fl - 10]) square([slot_end - x_f - win_w + 10, 10]);   // slot floor
            strut([x_f - 6, 12], [x_f + win_w + 5, 58]); strut([x_f - 6, 58], [x_f + win_w + 5, 12]);   // X-brace under the window
        }
        translate([x_f, fl]) square([slot_end - x_f, 2 * (j_r + j_gap)]);        // journal slot (end stop at slot_end)
        translate([x_f, win_z0]) square([win_w, 500]);                           // wedge window, open at the top
    }
}
module tail_base() {
    difference() {
        union() {
            for (s = [-1, 1]) translate([t_x[0], s > 0 ? w_in - 14 : -w_out, 0]) cube([t_x[1] - t_x[0], 14 + wall_t, base_t]);
            translate([t_x[0], -w_out, 0]) cube([34, 2 * w_out, base_t]);
            translate([t_x[1] - 36, -w_out, 0]) cube([36, 2 * w_out, base_t]);
        }
        for (x = [t_x[0] + 17, t_x[1] - 18]) translate([x - hole_sq / 2, -hole_sq / 2, -1]) cube([hole_sq, hole_sq, base_t + 2]);
    }
}
module tail_frame() {
    tail_base();
    for (s = [-1, 1]) {
        xz(s > 0 ? w_in : -w_out, s > 0 ? w_out : -w_in) tail_wall2d();
    }
    // front tie wall (below the return run)
    yz(t_x[0], t_x[0] + 6) { strut([-w_out + 5, 5], [w_out - 5, 110]); strut([w_out - 5, 5], [-w_out + 5, 110]); }
}
// wedge: lies flat (print), wall_t - 0.4 thick; in use it hangs in the wall's window, tip down, sloped face toward the journal
module wedge() {
    t = wall_t - 0.4;
    linear_extrude(t) polygon([[0, 0], [wd_t0, 0], [wd_t0 + (wd_len - 12) * tan(wd_ang), wd_len - 12],
                               [win_w + 6, wd_len - 12], [win_w + 6, wd_len], [-6, wd_len], [-6, wd_len - 12], [0, wd_len - 12]]);
}

// =====================================================================
// TAIL ROLLER (print: axis = z, flange A on the bed; world Y = z - L_w/2)
// =====================================================================
module tail_roller() {
    rf = tail_r + flange_lip;
    difference() {
        union() {
            rotate_extrude($fn = 96) polygon(concat(
                [[0, 0], [rf, 0], [rf, flange_t]],
                [for (i = [0 : 12]) let(z = flange_t + (face - flange_lip - 1) * i / 12, y = (z - L_w / 2) / (face / 2))
                    [tail_r + tail_crown * (1 - y * y), z]],
                [[rf, L_w - flange_t], [rf, L_w], [0, L_w]]));
            translate([0, 0, L_w - 0.01]) cylinder(r = j_r, h = j_len + 0.01);
        }
        translate([0, 0, -1]) cylinder(r = pin_shank_r + 0.12, h = 27);
        translate([0, 0, 27]) cylinder(r = 12, h = L_w - 27 - 12);                             // hollow middle (light, still 8 mm walls)
        translate([0, 0, 26 - 0.01]) cylinder(r1 = pin_shank_r + 0.12, r2 = 12, h = 12 - pin_shank_r - 0.12 + 0.02);
    }
}

// =====================================================================
// STATION: stake + wheel cassette (2 print-in-place wheels)
// cassette print frame: carry axle at the origin, return axle at x = st_dx, axles along z;
// world: print z -> Y - (-L_w/2), print x -> -(Z + st_carry) (down), print y -> X
// =====================================================================
module wu_foot2d() { polygon([[0, 0], [wu_foot_r, 0], [wu_foot_r, 1.6], [wu_axle_r, 1.6 + wu_foot_r - wu_axle_r], [0, 1.6 + wu_foot_r - wu_axle_r]]); }
module wu_spool() {
    R = wu_r + wu_crown; Rf = wu_r + flange_lip; rh = wu_axle_r + 4.5; ft = flange_t;
    difference() {
        rotate_extrude($fn = 96) polygon([[0, 0], [Rf, 0], [Rf, ft], [R, ft], [R, ft + wu_rim], [rh, ft + wu_rim + R - rh],
            [rh, L_w - ft - wu_rim - (R - rh)], [R, L_w - ft - wu_rim], [R, L_w - ft - (Rf - R)], [Rf, L_w - ft], [Rf, L_w], [0, L_w]]);
        vbore(wu_axle_r, wu_ridge_r, wu_ridges, -1, L_w + 1, pip_gap);
        rotate_extrude($fn = 96) intersection() { offset(delta = pip_gap) wu_foot2d(); translate([0, -1]) square([50, 50]); }
    }
}
module wu_axle() {
    vaxle(wu_axle_r, wu_ridge_r, wu_ridges, 0, cs_plate[0] + 0.5);
    rotate_extrude($fn = 96) wu_foot2d();
    translate([0, 0, L_w + 0.6]) cylinder(r1 = wu_axle_r, r2 = wu_axle_r + 6, h = 6.01, $fn = 64);   // 45 deg collar up to the plate
}
module cassette() {
    for (x = [0, st_dx]) translate([x, 0, 0]) { wu_spool(); wu_axle(); }
    difference() {
        union() {
            translate([0, 0, cs_plate[0]]) linear_extrude(cs_plate[1] - cs_plate[0]) hull() {
                circle(r = 11.5); translate([cs_blk_x[1] - 10, -10]) square([10, 20]);
            }
            translate([cs_blk_x[0], -10, cs_blk_z]) cube([cs_blk_x[1] - cs_blk_x[0], 20, 31]);                     // socket block
            translate([cs_blk_x[0], -4, cs_blk_z + 30]) cube([cs_blk_x[1] - cs_blk_x[0], 8, cs_plate[0] - cs_blk_z - 30]);   // web up to the plate
            hull() {
                translate([cs_blk_x[0], -4, cs_plate[0] - 6]) cube([cs_blk_x[1] - cs_blk_x[0], 8, 0.01]);
                translate([cs_blk_x[0], -10, cs_plate[0]]) cube([cs_blk_x[1] - cs_blk_x[0], 20, cs_plate[1] - cs_plate[0]]);
            }
            hull() {                                                                                                   // fin to the bed + 45 deg
                translate([cs_blk_x[0], -2, 0]) cube([cs_blk_x[1] - cs_blk_x[0], 4, cs_blk_z - 8]);
                translate([cs_blk_x[0], -10, cs_blk_z]) cube([cs_blk_x[1] - cs_blk_x[0], 20, 0.01]);
            }
        }
        // socket (mouth at +x), square with a 45 deg roof, centred on the belt centreline (print z = L_w / 2)
        translate([st_sock_x - sock_d, 0, L_w / 2]) rotate([90, 0, 90]) linear_extrude(sock_d + 1)
            let(h = (spig + 2 * fit_gap) / 2) polygon([[-h, -h], [h, -h], [h, h], [0, 2 * h], [-h, h]]);
    }
}
// station stake: lies on one leg; spigot and shoulder at x < 0, tip at x = len
module station_stake(len) {
    stake_body(len);
    translate([-6, -1, 0]) cube([6.01, stake_leg + 2, stake_leg]);                           // shoulder (the cassette rests on it)
    translate([-6 - 24, (stake_leg - spig) / 2, 0]) cube([24.01, spig, spig]);                // spigot (on the bed)
}
// anchor stake: lies on one leg; a 32 mm head stops it on the frame base
module anchor_stake() {
    stake_body(anchor_len);
    translate([-8, -5, 0]) cube([8.01, 32, 32]);
}

// =====================================================================
// part dispatch (print orientation)
// =====================================================================
if (part == "head_frame") head_frame();
if (part == "drive_roller") drive_roller();
if (part == "journal_pin") journal_pin();
if (part == "crank_gear") crank_gear();
if (part == "crank_arm") crank_arm();
if (part == "crank_pin") crank_pin();
if (part == "tail_frame") tail_frame();
if (part == "tail_roller") tail_roller();
if (part == "wedge") wedge();
if (part == "cassette") cassette();
if (part == "station_stake_1") station_stake(station_len[0]);
if (part == "station_stake_2") station_stake(station_len[1]);
if (part == "station_stake_3") station_stake(station_len[2]);
if (part == "anchor_stake") anchor_stake();
if (part == "pumpkin_test") linear_extrude(2) pumpkin2d(1);
if (part == "dump") {
    echo(str("VAL hz = ", hz)); echo(str("VAL tz = ", tz)); echo(str("VAL g_c = ", g_c)); echo(str("VAL C = ", C));
    echo(str("VAL p_y0 = ", p_y0)); echo(str("VAL st_carry = ", st_carry)); echo(str("VAL st_ret = ", st_ret));
    echo(str("VAL st_dx = ", st_dx)); echo(str("VAL st_sock_x = ", st_sock_x)); echo(str("VAL station_len = ", station_len));
    echo(str("VAL L_w = ", L_w)); echo(str("VAL drv_rs = ", drv_rs)); echo(str("VAL x_f = ", x_f)); echo(str("VAL win_z0 = ", win_z0));
    echo(str("VAL wd_ang = ", wd_ang)); echo(str("VAL wd_t0 = ", wd_t0)); echo(str("VAL wd_len = ", wd_len)); echo(str("VAL win_w = ", win_w));
    echo(str("VAL slot_end = ", slot_end)); echo(str("VAL j_r = ", j_r)); echo(str("VAL j_gap = ", j_gap)); echo(str("VAL tail_r = ", tail_r));
    echo(str("VAL w_in = ", w_in)); echo(str("VAL w_out = ", w_out)); echo(str("VAL g_y0 = ", g_y0)); echo(str("VAL g_face = ", g_face));
    echo(str("VAL arm_t = ", arm_t)); echo(str("VAL crank_r = ", crank_r)); echo(str("VAL gr_out = ", gr_out)); echo(str("VAL gr_len = ", gr_len));
    echo(str("VAL cp_r = ", cp_r)); echo(str("VAL cp_len = ", cp_len)); echo(str("VAL cp_shank = ", cp_shank)); echo(str("VAL anchor_len = ", anchor_len)); echo(str("VAL tip = ", tip));
    echo(str("VAL stake_leg = ", stake_leg)); echo(str("VAL spig = ", spig)); echo(str("VAL head_h = ", head_h)); echo(str("VAL tail_h = ", tail_h));
    echo(str("VAL wu_r = ", wu_r)); echo(str("VAL belt_t = ", belt_t)); echo(str("VAL belt_w = ", belt_w)); echo(str("VAL face = ", face));
    echo(str("VAL z_pin = ", z_pin)); echo(str("VAL z_gear = ", z_gear)); echo(str("VAL gm = ", gm)); echo(str("VAL t_top = ", t_top));
    echo(str("VAL cs_blk_x = ", cs_blk_x)); echo(str("VAL cs_plate = ", cs_plate)); echo(str("VAL h_x = ", h_x)); echo(str("VAL t_x = ", t_x));
    echo(str("VAL hole_sq = ", hole_sq)); echo(str("VAL base_t = ", base_t)); echo(str("VAL drive_r = ", drive_r)); echo(str("VAL flange_lip = ", flange_lip));
    echo(str("VAL pin_tip_r = ", pin_tip_r)); echo(str("VAL p_face = ", p_face)); echo(str("VAL boss_y1 = ", boss_y1)); echo(str("VAL j_len = ", j_len)); echo(str("VAL hub_af = ", hub_af)); echo(str("VAL wu_r = ", wu_r)); echo(str("VAL flange_t = ", flange_t)); echo(str("VAL win_w = ", win_w)); echo(str("VAL pin_shank_r = ", pin_shank_r));
}

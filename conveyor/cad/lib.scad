// =====================================================================
// Candy conveyor v4 - geometry library (no top-level geometry here)
// =====================================================================

module hexagon(af, h) { cylinder(d = af / cos(30), h = h, $fn = 6); }
module tube(od, id, h) { difference() { cylinder(d = od, h = h); translate([0, 0, -1]) cylinder(d = id, h = h + 2); } }

// ---------------------------------------------------------------- involute spur gear (2D)
// Standard involute flanks, root circle, backlash removed from each flank.
function deg(rad) = rad * 180 / PI;
function inv(a_rad) = tan(deg(a_rad)) - a_rad;                     // involute function
function flank_ang(rb, r) = inv(acos(rb / r) * PI / 180);         // polar angle of the involute at radius r
module spur2d(z, m, pa = 20, bl = 0.15, clearance = 0.25, tip_extra = 0) {
    rp = m * z / 2; rb = rp * cos(pa); ra = rp + m + tip_extra; rf = rp - (1 + clearance) * m;
    half = PI / (2 * z) - bl / rp / 2 + inv(pa * PI / 180);       // half tooth angle at the base-circle start
    n = 10;
    r0 = max(rb, rf);
    flank = [for (i = [0 : n]) let(r = r0 + (ra - r0) * i / n) [r, half - flank_ang(rb, r)]];
    union() {
        circle(r = rf + 0.01, $fn = z * 6);
        for (k = [0 : z - 1]) rotate(k * 360 / z)
            polygon(concat(
                [[rf * cos(deg(half)), -rf * sin(deg(half))]],
                [for (p = flank) [p[0] * cos(deg(p[1])), -p[0] * sin(deg(p[1]))]],
                [for (i = [n : -1 : 0]) let(p = flank[i]) [p[0] * cos(deg(p[1])), p[0] * sin(deg(p[1]))]],
                [[rf * cos(deg(half)), rf * sin(deg(half))]]));
    }
}

// ---------------------------------------------------------------- print-in-place V-bearing profiles
// An axle profile (r, z) with 45-degree V-ridges; the matching bore is this
// profile grown by the running gap, so every surface pair is >= gap apart and
// every overhang is 45 degrees (prints without supports).
function vaxle_prof(r_core, r_peak, ridges, z0, z1) =
    concat([[0, z0], [r_core, z0]],
           [for (zc = ridges) each [[r_core, zc - (r_peak - r_core)], [r_peak, zc], [r_core, zc + (r_peak - r_core)]]],
           [[r_core, z1], [0, z1]]);
module vaxle(r_core, r_peak, ridges, z0, z1) { rotate_extrude($fn = 64) polygon(vaxle_prof(r_core, r_peak, ridges, z0, z1)); }
module vbore(r_core, r_peak, ridges, z0, z1, gap) {
    rotate_extrude($fn = 64) intersection() {
        offset(delta = gap) polygon(vaxle_prof(r_core, r_peak, ridges, z0, z1));
        translate([0, z0 - 10]) square([1000, z1 - z0 + 20]);
    }
}

// ---------------------------------------------------------------- printed round thread (twisted eccentric circle)
// A single-start rounded thread: tolerant and strong in PLA. Nut = screw grown by gap.
module rthread(r, pitch, len, depth = 1.2, gap = 0) {
    linear_extrude(height = len, twist = -360 * len / pitch, slices = ceil(len / pitch * 24), convexity = 6)
        translate([depth / 2, 0]) circle(r = r - depth / 2 + gap, $fn = 48);
}

// ---------------------------------------------------------------- L-profile stake (printed lying on one leg)
// Print frame: the stake lies along +X; leg A on the bed (z 0..t), leg B vertical (y 0..t).
// Head block at x <= 0 holds a square socket along the stake axis.
module stake(len, leg, t, head, sock, sock_depth) {
    tip = 60;
    difference() {
        union() {
            // legs, tapering to a point over the last `tip` mm
            hull() { translate([0, 0, 0]) cube([len - tip, leg, t]); translate([len - 0.5, 0, 0]) cube([0.5, t, t]); }
            hull() { translate([0, 0, 0]) cube([len - tip, t, leg]); translate([len - 0.5, 0, 0]) cube([0.5, t, t]); }
            // head block (square, centred on the corner diagonal so the leg corner sits inside it)
            translate([-sock_depth - 6, -(head - leg) / 2 - t / 2, 0]) cube([sock_depth + 6, head, head]);
        }
        translate([-sock_depth - 6 - 1, -(head - leg) / 2 - t / 2 + (head - sock) / 2, (head - sock) / 2])
            cube([sock_depth + 1, sock, sock]);
    }
}

#!/usr/bin/env python3
"""
Candy conveyor v4 (all printed except the belt): site layout, loads and checks.

  python3 conveyor_calc.py                      # 2 risers of 7 in (default)
  python3 conveyor_calc.py --risers 3 --rise 7.5
  python3 conveyor_calc.py --svg side-profile-2-risers.svg

Machine dimensions come from ../cad/params.scad (the file the CAD uses).

Layout: the belt runs only along the lawn, from a drive roller at the foot of the
steps to a tail roller over the sidewalk. A printed chute + drive shaft runs from a
crank/funnel on the porch down the steps to the drive roller.
World frame (side view): x = horizontal inches from the lawn/sidewalk edge toward
the porch, y = inches above the sidewalk.
"""
import argparse
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARAMS = HERE.parent / "cad" / "params.scad"
IN = 25.4
G = 9.81


def load_params():
    ns = {"IN": IN}
    for line in PARAMS.read_text().splitlines():
        m = re.match(r"\s*([A-Za-z_]\w*)\s*=\s*([^;]+);", line)
        if m and not m.group(1).startswith("$"):
            try:
                ns[m.group(1)] = eval(m.group(2), {"__builtins__": {}}, ns)  # noqa: S307 - our own file
            except NameError:
                pass
    return ns


P = load_params()
g = P.__getitem__

# ---------------------------------------------------------------- derived machine numbers (mm)
L_w = g("face") + 2 * g("flange_t")
drv_rs = g("drive_r") + g("drive_crown") + g("rib_h")
r_dp = drv_rs + g("belt_t") / 2                      # drive pitch radius (belt centre line)
r_tp = g("tail_r") + g("roll_crown") + g("belt_t") / 2
r_wp = g("wu_r") + g("wu_crown") + g("belt_t") / 2
head_axle_below_top = g("belt_t") + drv_rs           # 32.5
tail_axle_below_top = g("belt_t") + g("tail_r") + g("roll_crown")
st_ret_z = -48 - (g("wu_r") + g("wu_crown"))
st_bot = st_ret_z - 22                               # station bracket bottom (stake head top), belt frame
pin_r = g("gear_m") * g("pinion_z") / 2
ratio = g("crown_z") / g("pinion_z")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--risers", type=int, default=2)
    ap.add_argument("--rise", type=float, default=7.0, help="riser height in (ASSUMED until measured)")
    ap.add_argument("--lawn", type=float, default=250.0)
    ap.add_argument("--lawn-deg", type=float, default=5.0)
    ap.add_argument("--steps-run", type=float, default=20.0)
    ap.add_argument("--head-gap", type=float, default=10.0, help="drive axle distance before the first riser, in")
    ap.add_argument("--tail-x", type=float, default=-2.0, help="tail axle x (negative = over the sidewalk), in")
    ap.add_argument("--crank-min", type=float, default=22.0, help="lowest acceptable crank height above the porch, in")
    ap.add_argument("--svg", default=None)
    a = ap.parse_args()
    out = []
    p = out.append

    # ------------------------------------------------------------ site
    tl = math.tan(math.radians(a.lawn_deg))
    porch_x = a.lawn + a.steps_run
    porch_y = a.lawn * tl + a.risers * a.rise
    treads = a.risers - 1
    riser_xs = [a.lawn + i * a.steps_run / max(treads, 1) for i in range(treads)] + [porch_x]

    def ground(x):
        if x < 0:
            return 0.0
        if x < a.lawn:
            return x * tl
        return a.lawn * tl + a.rise * sum(1 for r in riser_xs if x >= r)

    # ------------------------------------------------------------ belt line
    xh = a.lawn - a.head_gap
    xt = a.tail_x
    yh = ground(xh) + g("head_h") / IN          # belt top at the drive roller
    yt = g("tail_h") / IN                        # belt top at the tail roller (over the sidewalk)
    sb = (yh - yt) / (xh - xt)
    tb = math.atan(sb)
    C = math.hypot(xh - xt, yh - yt) * IN        # belt-top length between the roller apexes ~ axle distance
    p("=" * 78)
    p(f"CANDY CONVEYOR v4 (all printed except the belt) - {a.risers} risers x {a.rise:.2f} in (riser height ASSUMED)")
    p("=" * 78)
    p(f"Porch floor {porch_y:.1f} in above the sidewalk; lawn rises {a.lawn*tl:.1f} in over {a.lawn:.0f} in")
    p(f"Belt: drive roller at x={xh:.0f} in ({a.head_gap:.0f} in before the first riser), belt top {g('head_h')/IN:.1f} in above the lawn")
    p(f"      tail roller at x={xt:.0f} in (over the sidewalk), belt top {g('tail_h')/IN:.1f} in -> basket rim <= {g('tail_h')/IN-3:.1f} in")
    p(f"      slope {math.degrees(tb):.2f} deg; axle to axle {C:.0f} mm ({C/IN/12:.2f} ft)")

    # ------------------------------------------------------------ stations
    n = int(g("stations"))
    span = (xh - xt) / (n + 1)
    p(f"\nSTAKE STATIONS ({n}, every {span:.1f} in)")
    p(f"  {'#':>2} {'x in':>7} {'ground':>7} {'belt top':>9} {'stake head':>11} {'stake length':>13}")
    stake_lens = []
    for i in range(1, n + 1):
        x = xt + i * span
        bt = yt + sb * (x - xt)
        h = (bt - ground(x)) * IN                   # belt top above the grass, mm
        head_top = h + st_bot                       # stake head top above the grass, mm
        total = head_top + g("spike_embed")
        stake_lens.append(round(total - 32))          # leg length; the socket head adds 32 mm
        p(f"  {i:2d} {x:7.1f} {ground(x):7.1f} {h/IN:9.1f} {head_top/IN:9.1f} in {total:9.0f} mm (STL: stake_{i})")

    # ------------------------------------------------------------ drive line (shaft + chute) to the porch
    alpha = math.radians(g("line_deg")) + tb
    ca, sa = math.cos(alpha), math.sin(alpha)
    ax = xh + (head_axle_below_top / IN) * math.sin(tb)
    ay = yh - (head_axle_below_top / IN) * math.cos(tb)

    def line_pt(s_mm, nperp_mm=0.0):
        return (ax + (s_mm * ca - nperp_mm * sa) / IN, ay + (s_mm * sa + nperp_mm * ca) / IN)

    p(f"\nDRIVE LINE (chute + shaft) at {math.degrees(alpha):.1f} deg to level, from the drive axle up to the porch")
    st_len = 40.0
    n_m = (g("trough_n") - g("trough_floor")) - st_len * math.cos(alpha)

    def stand_at(N):
        # porch stand post: plugs into a world-vertical socket under the crank head funnel; its mouth sits
        # 12 mm (along the line) above the crank head's lower end and st_len below the funnel floor
        return line_pt(g("gb_top_s") + N * g("seg_len") + 12.0, n_m)

    best = None
    for N in range(4, 10):
        s_crank = g("gb_top_s") + N * g("seg_len") + g("crank_head_len") + 15
        cx, cy = line_pt(s_crank)
        sx, sy = stand_at(N)
        hc = cy - porch_y
        ok = sx - porch_x >= 1.0 and hc >= a.crank_min
        tag = "  <- use" if ok and best is None else ""
        if ok and best is None:
            best = (N, s_crank, cx, cy, hc)
        p(f"  {N} segments: crank {hc:.1f} in above the porch floor, {cx - porch_x:+.1f} in behind the edge;"
          f" stand post {sx - porch_x:+.1f} in behind the edge{tag}")
    if best is None:
        p("  -> no segment count works: change --head-gap or line_deg")
        N = 6
        s_crank = g("gb_top_s") + N * g("seg_len") + g("crank_head_len") + 15
    else:
        N, s_crank, cx, cy, hc = best
    worst = 1e9
    for name, xr in [(f"riser {i+1} top", r) for i, r in enumerate(riser_xs)]:
        lo, hi = 0.0, 3000.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if line_pt(mid, -g("ring_or"))[0] < xr:
                lo = mid
            else:
                hi = mid
        y_under = line_pt(lo, -g("ring_or"))[1]
        clr = y_under - ground(xr + 1e-6)
        worst = min(worst, clr)
        p(f"  underside over {name} (x={xr:.0f}): {clr:.1f} in")
    p(f"  -> minimum clearance {worst:.1f} in {'OK' if worst >= 1.5 else 'TOO LOW: increase line_deg or --head-gap'}")
    lx, ly = stand_at(N)
    leg = (ly - porch_y) * IN
    p(f"  porch stand: post {lx - porch_x:.1f} in behind the porch edge; socket mouth {leg:.0f} mm above the porch floor"
      f" -> stand_h = {leg:.0f} in params.scad")
    chute_len = (N * g("seg_len") + g("gb_top_s")) / 1000

    # ------------------------------------------------------------ belt length
    loop = 2 * C + math.pi * (r_dp + r_tp) + (r_dp - r_tp) ** 2 / C
    p("\nBELT (3 in heavy polypropylene webbing, Country Brook 50 yd)")
    p(f"  Loop about {loop:.0f} mm = {loop/IN/12:.1f} ft; cut {loop/IN/12 + 2:.0f} ft and sew in place with a 75 mm lap")

    # ------------------------------------------------------------ loads and friction (printed PLA bearings)
    T0 = g("T0")
    w_belt = 0.061 * G
    w_light, w_dense = 0.05 * G, 0.15 * G
    span_m = span * IN / 1000
    r_v = (g("dr_axle_r") + g("dr_ridge_r")) / 2
    r_vw = (g("wu_axle_r") + g("wu_ridge_r")) / 2
    p("\nLOADS (estimates; PLA-on-PLA plain bearings)")
    rows = []
    for label, mu in (("dry PLA", 0.35), ("waxed PLA", 0.20)):
        mu_v = mu / math.sin(math.radians(45))
        tail = mu_v * (2 * T0) * r_v / r_tp
        wheels = n * mu_v * (w_belt + w_light) * span_m * r_vw / r_wp + n * mu_v * w_belt * span_m * r_vw / r_wp
        R = tail + wheels + 2.0
        T1, T2 = T0 + R / 2, T0 - R / 2
        need = math.log(T1 / T2) / math.pi
        journal = 0.35 * (2 * T0 + 15) * g("journal_r") / 1000
        torque_roller = R * r_dp / 1000 + journal
        torque_crank = torque_roller * ratio / (0.85 * 0.9)
        F = torque_crank / (g("crank_r") / 1000)
        rows.append((label, tail, wheels, R, T2, need, torque_crank, F))
        p(f"  {label:9s}: tail bearing {tail:4.1f} N + {2*n} wheels {wheels:3.1f} N + bending 2 N = {R:4.1f} N belt drag;"
          f" slack side {T2:.1f} N; drive needs mu >= {need:.2f}; crank {torque_crank:.2f} N.m = {F:.0f} N ({F/4.448:.1f} lbf)")
    p("  Ribbed PLA on dry webbing is roughly mu 0.3, wet roughly 0.2: grip is adequate; wax the bearings.")
    T_c = T0 - rows[0][3] / 2
    for nm, w in (("light candy", w_belt + w_light), ("dense candy", w_belt + w_dense)):
        p(f"  Carrying-run sag between stations ({span_m:.2f} m, {T_c:.0f} N): {nm} {w*span_m**2/(8*T_c)*1000:.0f} mm")
    v = math.pi * 2 * r_dp / 1000 * 45 * ratio / 60
    p(f"  Crank 45 rpm x {ratio:.0f} -> belt {v:.2f} m/s; candy rides the belt in {C/1000/v:.0f} s ({C/1000/(2*math.pi*r_dp/1000*ratio):.0f} turns)")
    for mu in (0.3, 0.45):
        acc = G * (math.sin(alpha) - mu * math.cos(alpha))
        vc = math.sqrt(max(0, 2 * acc * chute_len))
        p(f"  Candy leaves a {chute_len:.2f} m chute at {vc:.1f} m/s (wrapper friction {mu}); the drop trap at the bottom stops it")

    # ------------------------------------------------------------ anchoring
    H = 2 * T0
    tail_axle_h = (g("tail_h") - tail_axle_below_top) / 1000
    head_axle_h = (g("head_h") - head_axle_below_top) / 1000
    p("\nANCHORING (belt tension must go into the ground at both ends)")
    for nm, hgt, base, where in (("tail", tail_axle_h, 0.172, "the 2 skid anchors nearest the sidewalk (ground screws)"),
                                 ("head", head_axle_h, 0.170, "the 2 anchors of the foot nearest the steps (ground screws)")):
        M = H * hgt
        p(f"  {nm}: {H:.0f} N pull at {hgt*1000:.0f} mm -> {M:.1f} N.m; tipping arm {base*1000:.0f} mm -> {M/base:.0f} N uplift on"
          f" {where}: {M/base/2:.0f} N each, or {M/base/G:.1f} kg of ballast")

    # ------------------------------------------------------------ PLA stress checks
    p("\nPLA STRESS CHECKS (parts printed with layers across the load are the weak case)")
    d = 2 * g("dr_axle_r")
    M = (2 * T0) * (L_w / 1000) / 4
    s_ax = M / (math.pi * (d / 1000) ** 3 / 32) / 1e6
    p(f"  tail axle Ø{d:.0f} (layers across): {s_ax:.1f} MPa bending  (PLA interlayer ~20-30 MPa)")
    tc = rows[0][6] * 2
    J = math.pi / 32 * ((2 * g("shaft_or")) ** 4 - (2 * g("shaft_ir")) ** 4)
    p(f"  line shaft Ø{2*g('shaft_or'):.0f}/{2*g('shaft_ir'):.0f} at 2x the dry crank torque ({tc:.1f} N.m): "
      f"{tc*1000*g('shaft_or')/J:.1f} MPa shear across layers")
    Ft = rows[0][6] * 0.85 * 0.9 / (g("gear_m") * g("crown_z") / 2000) * 2
    sl = Ft / (g("gear_face") * g("gear_m") * 0.3)
    p(f"  gear teeth at 2x dry torque: {Ft:.0f} N tooth force -> {sl:.1f} MPa (Lewis); crown teeth are printed with layers across")
    p("  station wheel axles: < 3 MPa")
    Mg = 30 * 0.035
    p(f"  crank grip axle Ø13 with a 30 N hand load at mid-grip: {32*Mg/(math.pi*0.013**3)/1e6:.1f} MPa bending across layers")

    text = "\n".join(out)
    print(text)
    (HERE / f"report-{a.risers}-risers.txt").write_text(text + "\n")
    (HERE / f"stakes-{a.risers}-risers.txt").write_text("\n".join(str(s) for s in stake_lens) + f"\nsegments {N}\nstand_h {leg:.0f}\n")
    if a.svg:
        svg(a, ground, riser_xs, porch_x, porch_y, xh, xt, yh, yt, sb, line_pt, s_crank, n, span, lx, ly)


def svg(a, ground, riser_xs, porch_x, porch_y, xh, xt, yh, yt, sb, line_pt, s_crank, n, span, lx, ly):
    VX, VY = 4.0, 8.0
    x0, x1, ymax = -20, porch_x + 30, porch_y + 30
    W, H = (x1 - x0) * VX + 40, ymax * VY + 70

    def P(x, y):
        return (x - x0) * VX + 20, H - 45 - y * VY

    def pt(x, y):
        u, v = P(x, y)
        return f"{u:.1f},{v:.1f}"

    pts = [pt(x0, -3), pt(x0, 0), pt(0, 0), pt(a.lawn - 0.01, ground(a.lawn - 0.01))]
    for r in riser_xs:
        pts += [pt(r, ground(r - 0.01)), pt(r, ground(r))]
    pts += [pt(x1, porch_y), pt(x1, -3)]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" font-family="sans-serif" font-size="14">',
         '<rect width="100%" height="100%" fill="#fff"/>',
         f'<polygon points="{" ".join(pts)}" fill="#d5e8c8" stroke="#4a6b3a"/>',
         f'<text x="20" y="24" font-size="16" font-weight="bold">v4 all-printed layout, {a.risers} risers x {a.rise} in (vertical x2)</text>']
    s.append(f'<polyline points="{pt(xt, yt)} {pt(xh, yh)}" stroke="#111" stroke-width="3" fill="none"/>')
    s.append(f'<polyline points="{pt(xt, yt - 2)} {pt(xh, yh - 2.6)}" stroke="#111" stroke-width="2" stroke-dasharray="6 4" fill="none"/>')
    for i in range(1, n + 1):
        x = xt + i * span
        bt = yt + sb * (x - xt)
        s.append(f'<line x1="{P(x, ground(x)-6)[0]:.1f}" y1="{P(x, ground(x)-6)[1]:.1f}" x2="{P(x, bt-1)[0]:.1f}" y2="{P(x, bt-1)[1]:.1f}" stroke="#a0522d" stroke-width="4"/>')
        s.append(f'<circle cx="{P(x, bt-0.7)[0]:.1f}" cy="{P(x, bt-0.7)[1]:.1f}" r="5" fill="#f0a020"/>')
    for x, y, lab in ((xh, yh - 1.3, "drive"), (xt, yt - 0.9, "tail")):
        s.append(f'<circle cx="{P(x, y)[0]:.1f}" cy="{P(x, y)[1]:.1f}" r="9" fill="#f0a020" stroke="#000"/>'
                 f'<text x="{P(x, y)[0]-20:.0f}" y="{P(x, y)[1]+28:.0f}">{lab}</text>')
    a0, a1 = line_pt(0), line_pt(s_crank)
    t0, t1 = line_pt(40, 82), line_pt(s_crank, 82)
    s.append(f'<polyline points="{pt(*a0)} {pt(*a1)}" stroke="#555" stroke-width="4"/>')
    s.append(f'<polyline points="{pt(*t0)} {pt(*t1)}" stroke="#8a2be2" stroke-width="6" opacity="0.6"/>')
    s.append(f'<line x1="{P(lx, ly)[0]:.1f}" y1="{P(lx, ly)[1]:.1f}" x2="{P(lx, ground(lx))[0]:.1f}" y2="{P(lx, ground(lx))[1]:.1f}" stroke="#a0522d" stroke-width="4"/>')
    s.append(f'<circle cx="{P(*a1)[0]:.1f}" cy="{P(*a1)[1]:.1f}" r="10" fill="#c60"/>'
             f'<text x="{P(*a1)[0]-150:.0f}" y="{P(*a1)[1]-16:.0f}">crank + funnel</text>')
    s.append(f'<text x="{P(*t1)[0]-260:.0f}" y="{P(*t1)[1]+40:.0f}" fill="#8a2be2">candy chute</text>')
    bx = xt - 5
    s.append(f'<rect x="{P(bx, 6)[0]:.0f}" y="{P(bx, 6)[1]:.0f}" width="{10*VX:.0f}" height="{6*VY:.0f}" fill="none" stroke="#e67e22" stroke-width="2"/>')
    s.append(f'<text x="{(100-x0)*VX:.0f}" y="{H-20:.0f}">lawn {a.lawn:.0f} in at {a.lawn_deg:.0f} deg; stake stations every {span:.0f} in</text>')
    s.append("</svg>")
    (HERE.parent / "docs" / a.svg).write_text("\n".join(s))


if __name__ == "__main__":
    main()

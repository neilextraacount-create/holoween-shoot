#!/usr/bin/env python3
"""
Candy conveyor - site layout, loads and hardware calculator (v2).

  python3 conveyor_calc.py                    # 2 risers of 7 in (default)
  python3 conveyor_calc.py --risers 3         # two treads + porch
  python3 conveyor_calc.py --rise 7.5         # measured riser height, inches
  python3 conveyor_calc.py --basket 8         # basket rim height, inches

All machine dimensions come from ../cad/params.scad (the same file the CAD uses),
so the calculator and the printed parts cannot drift apart.

World frame (side view): x = horizontal inches from the lawn/sidewalk edge toward the
porch, y = inches above the lawn edge. Rail frame (mm): X along the rails from their tail
end, Z perpendicular (0 = top of the carrying belt) - the same frame as conveyor.scad.
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
        if m:
            ns[m.group(1)] = eval(m.group(2), {"__builtins__": {}}, ns)  # noqa: S307 - our own file
    return ns


P = load_params()


def g(name):
    return P[name]


# ----------------------------------------------------------------------------- derived machine geometry
rail_len = g("rail_piece") * g("rail_pieces")
rail_top = g("rail_above_belt")
rail_bot = rail_top - g("rail_h")
rail_mid = (rail_top + rail_bot) / 2
rail_out = g("rail_gap") / 2 + g("rail_t")
belt_t = g("belt_t")
drive_r_belt = g("drive_core_d") / 2 + g("lagging_t") + g("crown_drive")
tail_r_belt = g("tail_d") / 2 + g("crown_tail")
drive_z = -belt_t - drive_r_belt
tail_z = -belt_t - tail_r_belt
slider_z = -belt_t - g("slider_od") / 2
ret_slider_z = rail_bot - 20
ret_belt_z = ret_slider_z + g("slider_od") / 2           # inner face of return run on the slider
hx = rail_len + g("head_axis_out")
stations = [g("station_first") + i * g("station_pitch") for i in range(int(g("stations")))]


def spr_pd(n):
    return g("chain_p") / math.sin(math.pi / n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--risers", type=int, default=2)
    ap.add_argument("--rise", type=float, default=7.0, help="riser height, in (ASSUMED 7 until measured)")
    ap.add_argument("--head", type=float, default=9.0, help="belt top above porch floor at the drive roller, in")
    ap.add_argument("--setback", type=float, default=12.0, help="drive axle distance back from porch edge, in")
    ap.add_argument("--basket", type=float, default=7.5, help="basket rim height, in (belt top at the tail = rim + 3 in)")
    ap.add_argument("--lawn", type=float, default=250.0)
    ap.add_argument("--lawn-deg", type=float, default=5.0)
    ap.add_argument("--steps-run", type=float, default=20.0)
    ap.add_argument("--svg", default=None)
    a = ap.parse_args()

    out = []
    p = out.append

    # ------------------------------------------------------------------ site
    lawn_rise = a.lawn * math.tan(math.radians(a.lawn_deg))
    porch_x = a.lawn + a.steps_run
    porch_y = lawn_rise + a.risers * a.rise
    treads = a.risers - 1
    riser_xs = [a.lawn + i * a.steps_run / max(treads, 1) for i in range(treads)] + [porch_x]

    def ground(x):
        if x < 0:
            return 0.0                     # sidewalk, assumed flush with the lawn edge
        if x < a.lawn:
            return x * math.tan(math.radians(a.lawn_deg))
        return lawn_rise + a.rise * sum(1 for r in riser_xs if x >= r)

    # ------------------------------------------------------------------ place the machine
    tail_axis = g("tail_axis_min") + 0.25 * g("tail_slot_len")   # take-up 25 % out once tensioned
    C = hx + tail_axis                                           # axle to axle along the rails, mm
    x_head = porch_x + a.setback
    y_head_belt = porch_y + a.head
    y_tail_belt_target = a.basket + 3.0          # rim 3 in below the belt so the basket slides under the tail
    dh = y_head_belt - y_tail_belt_target
    span = math.sqrt((C / IN) ** 2 - dh ** 2)
    slope = math.asin(dh / (C / IN))
    ca, sa = math.cos(slope), math.sin(slope)

    def world(X, Z):
        """rail-frame mm -> world inches, anchored at the drive axle's belt-top point"""
        dx, dz = X - hx, Z
        return x_head + (dx * ca - dz * sa) / IN, y_head_belt + (dx * sa + dz * ca) / IN

    x_tail, y_tail = world(-tail_axis, 0)
    p("=" * 78)
    p(f"CANDY CONVEYOR - {a.risers} risers x {a.rise:.2f} in (riser height ASSUMED unless measured)")
    p("=" * 78)
    p(f"Porch floor {porch_y:.1f} in above the lawn edge (lawn rise {lawn_rise:.1f} + {a.risers} x {a.rise:.2f})")
    p(f"Axle-to-axle {C:.0f} mm ({C/IN/12:.2f} ft) with the take-up at 25 % travel")
    p(f"Slope {math.degrees(slope):.2f} deg (tan {math.tan(slope):.3f}); horizontal span {span:.1f} in")
    p(f"Drive axle {a.setback:.0f} in back from the porch edge; belt top there {a.head:.1f} in above the porch floor")
    p(f"Tail axle at x = {x_tail:.1f} in ({'over the sidewalk' if x_tail < 0 else 'ON THE LAWN - move the head back'}),"
      f" belt top {y_tail:.1f} in -> basket rim {y_tail - 3.0:.1f} in; slide the basket under the tail so its"
      " back rim is 1-2 in behind the tail axle")

    # ------------------------------------------------------------------ stations
    p("\nSTAKE STATIONS (heights in inches above the ground at that stake)")
    p(f"  {'#':>2} {'rail X mm':>9} {'x in':>7} {'ground':>7} {'belt top':>9} {'upper rung':>11} {'lower rung':>11} {'stake (cut)':>12}")
    ok = True
    for i, X in enumerate(stations):
        x, yb = world(X, 0)
        gy = ground(x)
        _, y_up = world(X, slider_z)
        _, y_lo = world(X, ret_slider_z)
        above = (y_up - gy) + 1.5                            # stake top 1.5 in above the upper rung
        embed = 12 if (y_up - gy) <= 12 else 16
        stake = above + embed
        flag = ""
        if not (0 < x < a.lawn - 24):
            flag = "  <-- NOT ON LAWN or < 24 in from the first riser"
            ok = False
        if y_lo - gy < 3.0:
            flag += "  <-- lower bolt < 3 in above ground"
        p(f"  {i+1:2d} {X:9.0f} {x:7.1f} {gy:7.1f} {yb-gy:9.1f} {y_up-gy:11.1f} {y_lo-gy:11.1f} {stake:7.1f} in"
          f" ({embed} in deep){flag}")
    p("  -> 2x2 stakes (1.5 in actual); drive plumb; the rung heights are where you drill the 5/16 in holes")
    p("  -> every station is on the lawn and >= 24 in from the first riser" if ok
      else "  -> MOVE THE HEAD (--setback) so every station is on the lawn, >= 24 in from the riser")
    x_mid, _ = world((stations[-1] + hx) / 2, 0)
    p(f"  + one rails-only rung (carry slider, no stakes) at rail X {(stations[-1] + hx) / 2:.0f} mm (x = {x_mid:.1f} in)")

    # ------------------------------------------------------------------ clearances near the porch
    p("\nCLEARANCE OVER THE STEPS / PORCH EDGE (inches)")
    X_last = stations[-1]
    z0 = ret_belt_z - belt_t                                 # outer face of return run at the slider
    z1 = drive_z - drive_r_belt - belt_t                     # outer face at the drive roller bottom
    worst = 1e9
    for name, xs in [("porch edge", porch_x)] + [(f"riser {i+1} top", r) for i, r in enumerate(riser_xs[:-1])]:
        X = X_last
        for _ in range(40):
            xw, _ = world(X, 0)
            X += (xs - xw) * IN / ca
        f = min(max((X - X_last) / (hx - X_last), 0), 1)
        z = z0 + f * (z1 - z0)
        _, yr = world(X, z)
        _, yrail = world(X, rail_bot)
        gy = ground(xs + 0.01)
        worst = min(worst, yr - gy)
        p(f"  {name:14s} x={xs:6.1f}  ground {gy:5.1f}  rail bottom +{yrail-gy:5.1f}  return run +{yr-gy:5.1f}")
    p(f"  -> minimum {worst:.1f} in {'OK' if worst >= 2.0 else 'TOO LOW: raise --head'}")
    x_post, _ = world(rail_len - g("post_setback"), rail_mid)
    p(f"  crank post at x = {x_post:.1f} in ({x_post - porch_x:+.1f} in from the porch edge; must be > +1)")

    # ------------------------------------------------------------------ belt
    D1 = 2 * drive_r_belt + belt_t
    D2 = 2 * tail_r_belt + belt_t
    sew_C = hx + g("tail_axis_min") + 15                     # snug with the take-up 15 mm out
    loop = 2 * sew_C + math.pi * (D1 + D2) / 2 + (D1 - D2) ** 2 / (4 * sew_C)
    lap = 125
    p("\nBELT (3 in heavy polypropylene webbing)")
    p(f"  Loop length on the belt centre line: {loop:.0f} mm = {loop/IN/12:.2f} ft (take-up 15 mm out)")
    p(f"  Cut length incl. {lap} mm sewn lap: {loop+lap:.0f} mm = {(loop+lap)/IN:.1f} in = {(loop+lap)/IN/12:.2f} ft")
    p(f"  Take-up travel {g('tail_slot_len'):.0f} mm absorbs {2*(g('tail_slot_len')-15):.0f} mm of growth "
      f"({200*(g('tail_slot_len')-15)/loop:.1f} % of the loop)")
    p(f"  MEASURE axle-to-axle C on the assembled frame first: loop = 2 C + {math.pi*(D1+D2)/2:.0f} mm")

    # ------------------------------------------------------------------ loads
    T0 = 60.0                                                # pretension per run, N
    w_belt = 0.061 * G                                       # 6.2 lb / 150 ft (Country Brook listing)
    w_candy = 0.15 * G                                       # dense: a 15 g piece every 10 cm
    span_m = g("station_pitch") / 1000
    R_design = 25.0
    T_carry = T0 - R_design / 2                             # carrying run is the slack side
    sag_c = (w_belt + w_candy) * span_m ** 2 / (8 * T_carry) * 1000
    sag_r = w_belt * span_m ** 2 / (8 * (T0 + R_design / 2)) * 1000
    N_c = (w_belt + w_candy) * span_m
    N_r = w_belt * span_m + (T0 + R_design / 2) * 2 * (abs(z1 - ret_belt_z) / 1000) / ((hx - X_last) / 1000)
    mu_slide = 0.3
    n = len(stations)
    f_slide = mu_slide * ((n + 1) * N_c + n * N_r)
    candy_help = 0.15 * (C / 1000) * G * math.sin(slope)
    est = f_slide + 2.0 + 5.0 + 1.0 - candy_help
    p("\nLOADS (estimates, not measurements)")
    p(f"  Pretension {T0:.0f} N per run; design running resistance {R_design:.0f} N")
    p(f"  Carrying-run sag over {span_m:.2f} m between sliders: {sag_c:.1f} mm; return-run sag {sag_r:.1f} mm")
    can = 0.385 * G                                         # full 12 oz can incl. contents, N
    for T in (40, 60, 80):
        p(f"  Tension check: a full 12 oz can hung mid-span between two stations sags the belt"
          f" {can*span_m/(4*T)*1000:.0f} mm ({can*span_m/(4*T)/0.0254:.2f} in) at {T} N")
    p(f"  Belt sliding on {2*n+1} PLA sliders (mu {mu_slide}): {f_slide:.1f} N; + bending 2 N + edge rub 5 N"
      f" + bearings/chain 1 N - candy downhill {candy_help:.1f} N = {est:.1f} N  (design {R_design:.0f} N)")
    T1, T2 = T0 + R_design / 2, T0 - R_design / 2
    for name, mu in (("inner-tube lagging", 0.5), ("bare PLA, wet", 0.2)):
        cap = math.exp(mu * math.pi)
        p(f"  Drive grip, {name:18s} mu={mu}: capstan limit {cap:.2f}, needed {T1/T2:.2f} -> "
          f"{'OK' if cap >= 1.25 * T1 / T2 else 'MARGINAL - use lagging'}")
    ratio = g("sprocket_crank_t") / g("sprocket_drive_t")
    rpm = 45
    v = math.pi * (2 * drive_r_belt + belt_t) / 1000 * rpm * ratio / 60
    torque = R_design * (drive_r_belt + belt_t / 2) / 1000 * ratio / 0.9   # step-up: crank torque = roller torque x ratio
    F = torque / (g("crank_r") / 1000)
    turns = (C / 1000) / (math.pi * (2 * drive_r_belt + belt_t) / 1000 * ratio)
    p(f"  Crank {rpm} rpm x {ratio:.2f} -> belt {v:.2f} m/s; candy reaches the basket in {C/1000/v:.0f} s = {turns:.0f} turns")
    p(f"  Crank torque {torque:.2f} N.m -> hand force {F:.0f} N ({F/4.448:.1f} lbf) at {g('crank_r'):.0f} mm")

    # ------------------------------------------------------------------ chain and crank height
    L = g("chain_links")
    S = (g("sprocket_drive_t") + g("sprocket_crank_t")) / 2
    k = ((g("sprocket_crank_t") - g("sprocket_drive_t")) / (2 * math.pi)) ** 2
    Cc = ((L - S) + math.sqrt((L - S) ** 2 - 8 * k)) * g("chain_p") / 4
    tsl = math.tan(slope)
    A_ = (rail_len - g("post_setback")) - hx
    B_ = rail_mid - drive_z
    u = (-(A_ * tsl + B_) + math.sqrt((A_ * tsl + B_) ** 2 - (tsl ** 2 + 1) * (A_ ** 2 + B_ ** 2 - Cc ** 2))) / (tsl ** 2 + 1)
    Xc, Zc = rail_len - g("post_setback") + u * tsl, rail_mid + u
    _, yc = world(Xc, Zc)
    _, y_post_top = world(Xc, Zc - 13 / math.cos(slope))
    _, y_leg_top = world(rail_len - g("post_setback"), rail_top)
    p("\nCHAIN AND CRANK")
    p(f"  {L} links -> sprocket centres {Cc:.1f} mm; crank axle {yc - porch_y:.1f} in above the porch floor"
      f" (handle sweeps {yc - porch_y - g('crank_r')/IN:.0f}-{yc - porch_y + g('crank_r')/IN:.0f} in)")
    p(f"  Crank post (1x3): porch floor to post top = {y_post_top - porch_y:.1f} in (cut it 1/2 in long; trim to fit)")
    p(f"  Other head leg (1x3): porch floor to rail top = {y_leg_top - porch_y:.1f} in")
    p(f"  Ratio is a step-UP: the belt moves {ratio:.2f} x faster than a direct crank, with {ratio:.2f} x the effort")
    for nn in (g("sprocket_drive_t"), g("sprocket_crank_t")):
        p(f"  {nn}T pitch diameter {spr_pd(nn):.2f} mm")

    # ------------------------------------------------------------------ bolt stacks (thread engagement)
    p("\nBOLT STACKS (grip = everything clamped under the head; the nut must sit on threads)")

    def stack(name, nominal_in, thread_in, grip_mm, nut_mm):
        L_ = nominal_in * IN
        t0 = L_ - thread_in * IN
        okk = (t0 < grip_mm - 1.0) and (grip_mm + nut_mm <= L_ + 0.01)
        p(f"  {name:40s} {nominal_in:4.2f}\": grip {grip_mm:6.1f} mm, threads from {t0:6.1f}, "
          f"nut ends {grip_mm+nut_mm:6.1f} of {L_:6.1f} -> {'OK' if okk else 'FAIL'}")
        return okk

    wa = 1.6  # SAE washer
    allok = True
    allok &= stack("rail-end plates (x8)", 1.5, 0.75, g("rail_t") + g("plate_t") + 2 * wa, 7.1)
    allok &= stack("crank post / head leg to rail (x4)", 2.0, 0.75, 2 * g("rail_t") + 2 * wa, 7.1)
    allok &= stack("crank clamp to post (x2)", 1.5, 0.75, g("rail_t") + g("clamp_t") + 2 * wa, 7.1)
    allok &= stack("grip on crank arm (x1)", 4.0, 0.75, 8 + g("grip_len") + 2 * wa, 7.1)
    p(f"  -> {'all bolt stacks OK' if allok else 'FIX THE FAILING STACKS'}  (thread lengths per ASME B18.2.1:"
      " 2D+1/4 in up to 6 in long, 2D+1/2 in over 6 in)")
    head_axle = 2 * (rail_out + g("plate_t") + 3 + wa) + 2 * 8.7 + 6      # +3 mm hood cheeks
    tail_axle = 2 * (rail_out + g("plate_t") + 14 + wa) + 2 * 8.7 + 6
    crank_axle = 25.2 + 2 + 12 + (16.7 + 6) + 2 * wa + 8.7 + 9.5 + 6
    rung = 2 * g("stake_t") + 2 * rail_out + 4 * (wa + 5.6) + 12
    mid = 2 * rail_out + 2 * (wa + 5.6) + 10
    p(f"  1/4\"-20 threaded rod rungs: {2*len(stations)} station rungs x {rung:.0f} mm ({rung/IN:.1f} in) + 1 steps rung x"
      f" {mid:.0f} mm = {2*len(stations)*rung + mid:.0f} mm -> {math.ceil((2*len(stations)*rung + mid)/(914-20)):.0f} x 36 in rods"
      " (4 nuts + 4 washers per station rung, 2 + 2 on the steps rung)")
    p(f"  5/16\"-18 threaded rod cut list: drive axle {head_axle:.0f} mm, tail axle {tail_axle:.0f} mm,"
      f" crank axle {crank_axle:.0f} mm = {head_axle+tail_axle+crank_axle:.0f} mm of a 914 mm (36 in) rod")

    # ------------------------------------------------------------------ structure
    p("\nSTRUCTURE")
    comp = T0
    I_w = (g("rail_h") / IN) * (g("rail_t") / IN) ** 3 / 12
    Pcr = math.pi ** 2 * 1.2e6 * I_w / (g("station_pitch") / IN) ** 2 * 4.448
    p(f"  Each rail is compressed ~{comp:.0f} N by the belt tension; buckling between stations {Pcr:.0f} N"
      f" -> factor {Pcr/comp:.0f}")
    area = (g("rail_h") / IN / 12) * (C / IN / 12)
    p(f"  Wind 20 mph on {area:.1f} ft2: {0.00256*400*area*1.2:.1f} lbf total, "
      f"{0.00256*400*area*1.2/len(stations):.1f} lbf per station")

    text = "\n".join(out)
    print(text)
    (HERE / f"report-{a.risers}-risers.txt").write_text(text + "\n")
    if a.svg:
        draw_svg(a, ground, world, riser_xs, porch_x, porch_y, slope, Xc, Zc)


def draw_svg(a, ground, world, riser_xs, porch_x, porch_y, slope, Xc, Zc):
    VX, VY = 4.0, 8.0
    x0, x1, ymax = -30, porch_x + 40, porch_y + 45
    W, H = (x1 - x0) * VX + 40, ymax * VY + 80

    def P(x, y):
        return (x - x0) * VX + 20, H - 50 - y * VY

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
         f'<text x="20" y="24" font-size="16" font-weight="bold">Side profile, {a.risers} risers x {a.rise} in '
         f'(vertical scale x2) - belt slope {math.degrees(slope):.1f} deg</text>']

    def line(X0, Z0, X1, Z1, style):
        (xa, ya), (xb, yb) = world(X0, Z0), world(X1, Z1)
        (ua, va), (ub, vb) = P(xa, ya), P(xb, yb)
        s.append(f'<line x1="{ua:.1f}" y1="{va:.1f}" x2="{ub:.1f}" y2="{vb:.1f}" {style}/>')

    tail_X = -(g("tail_axis_min") + 0.25 * g("tail_slot_len"))
    line(0, rail_top, rail_len, rail_top, 'stroke="#b08a5a" stroke-width="2"')
    line(0, rail_bot, rail_len, rail_bot, 'stroke="#b08a5a" stroke-width="2"')
    line(tail_X, 0, hx, 0, 'stroke="#111" stroke-width="3"')
    pts_r = [(tail_X, tail_z - tail_r_belt)] + [(X, ret_belt_z) for X in stations] + [(hx, drive_z - drive_r_belt)]
    for (X0, Z0), (X1, Z1) in zip(pts_r, pts_r[1:]):
        line(X0, Z0, X1, Z1, 'stroke="#111" stroke-width="2" stroke-dasharray="7 4"')
    for X in stations:
        xs, _ = world(X, 0)
        _, ytop = world(X, slider_z)
        (ua, va), (ub, vb) = P(xs, ground(xs) - 3), P(xs, ytop + 1.5)
        s.append(f'<line x1="{ua:.1f}" y1="{va:.1f}" x2="{ub:.1f}" y2="{vb:.1f}" stroke="#7a5a2a" stroke-width="4"/>')
    for X, Z, r, lab in ((hx, drive_z, drive_r_belt, "drive roller"), (tail_X, tail_z, tail_r_belt, "tail + take-up")):
        cx, cy = world(X, Z)
        u, v = P(cx, cy)
        s.append(f'<ellipse cx="{u:.1f}" cy="{v:.1f}" rx="{r/IN*VX:.1f}" ry="{r/IN*VY:.1f}" fill="#f0a020" stroke="#000"/>')
        s.append(f'<text x="{u-40:.0f}" y="{v+r/IN*VY+18:.0f}">{lab}</text>')
    cx, cy = world(Xc, Zc)
    px, _ = world(rail_len - g("post_setback"), rail_mid)
    u, v = P(cx, cy)
    ua, va = P(px, porch_y)
    s.append(f'<line x1="{ua:.1f}" y1="{va:.1f}" x2="{u:.1f}" y2="{v:.1f}" stroke="#7a5a2a" stroke-width="5"/>')
    s.append(f'<circle cx="{u:.1f}" cy="{v:.1f}" r="10" fill="#c60"/>'
             f'<text x="{u-210:.0f}" y="{v-14:.0f}">crank, {cy-porch_y:.0f} in above the porch</text>')
    hxw, hyw = world(hx, drive_z)
    ub, vb = P(hxw, hyw)
    s.append(f'<line x1="{u:.1f}" y1="{v:.1f}" x2="{ub:.1f}" y2="{vb:.1f}" stroke="#555" stroke-dasharray="3 3"/>')
    tx, _ = world(tail_X, 0)
    bw = 10
    bu, bv = P(tx - bw / 2, a.basket)
    s.append(f'<rect x="{bu:.0f}" y="{bv:.0f}" width="{bw*VX:.0f}" height="{a.basket*VY:.0f}" fill="none" '
             f'stroke="#e67e22" stroke-width="2"/><text x="{bu:.0f}" y="{H-28:.0f}">basket</text>')
    s.append(f'<text x="{(100-x0)*VX:.0f}" y="{H-28:.0f}">lawn {a.lawn:.0f} in at {a.lawn_deg:.0f} deg; '
             f'{len(stations)} stake stations every 48 in; dashed = return run</text>')
    s.append("</svg>")
    (HERE.parent / "docs" / a.svg).write_text("\n".join(s))


if __name__ == "__main__":
    main()

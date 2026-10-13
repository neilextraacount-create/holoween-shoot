#!/usr/bin/env python3
"""
Candy conveyor - Stage 1 geometry and load calculator.

Run:  python3 conveyor_calc.py            (prints report, writes ../docs/side-profile.svg)

Every number marked ASSUMED below is a provisional placeholder until the site
is measured. Change it here and re-run; the report and the profile drawing update.

Coordinate system (side view):
  x = horizontal distance in inches, measured from the lawn/sidewalk edge toward the porch.
  y = height in inches above the sidewalk/lawn edge at x = 0.
"""
import math
from pathlib import Path

IN = 25.4  # mm per inch
G = 9.81

# ---------------------------------------------------------------- site (inches)
LAWN_RUN = 250.0          # horizontal lawn distance (given)
LAWN_SLOPE_DEG = 5.0      # lawn slope (given)
STEP_RISERS = 2           # ASSUMED: "two steps" read as two risers (one tread + porch).
                          # Use --risers 3 for two treads + porch (3 risers). MUST BE MEASURED.
STEP_RUN_TOTAL = 20.0     # horizontal distance covered by the steps (given)
STEP_RISE = 7.0           # ASSUMED riser height
HEAD_SETBACK = 12.0       # ASSUMED: head roller axis sits 12" back from the porch edge
TAIL_OVERHANG = 4.0       # tail roller axis overhangs the lawn edge by 4"
TAIL_BELT_TOP = 9.0       # ASSUMED belt-top height at the tail (basket rim must be ~1.5" lower)
HEAD_BELT_TOP_ABOVE_PORCH = 9.0  # belt top above porch floor at the head roller

# ---------------------------------------------------------------- machine (mm unless noted)
BELT_W = 76.0             # 3" webbing
BELT_T = 2.0              # ASSUMED webbing thickness, measure when it arrives
D_HEAD = 80.0             # drive roller diameter over lagging
D_TAIL = 50.0             # tail roller diameter
D_IDLER = 25.0
IDLER_BORE = 6.35         # 1/4" bolt
RAIL_H = 60.3             # 1x3 furring strip actual 0.656" x 2.375"
RAIL_T = 16.7
RAIL_ABOVE_BELT = 20.0    # rail top edge sits this far above belt surface (side wall)
CARRY_IDLER_PITCH = 24.0  # inches, horizontal
STATION_PITCH = 48.0      # inches, horizontal (stake pairs)
STAKE_EMBED = 12.0        # inches driven into soil

# ---------------------------------------------------------------- loads / operation
BELT_MASS_PER_M = 0.10    # kg/m, ASSUMED upper bound for 3" heavy polypropylene webbing
CANDY_MASS_PER_M = 0.15   # kg/m, ~ one 15 g fun-size piece every 10 cm (dense loading)
PRETENSION_N = 40.0       # set by take-up, per belt run
RESIST_DESIGN_N = 20.0    # design value for total running resistance (2x the estimate below)
MU_LAGGING = 0.5          # rubber inner-tube lagging on drive roller vs webbing (conservative)
MU_BARE_PLA = 0.25        # bare PLA roller vs webbing (fallback / wet)
CRANK_ARM = 100.0         # mm
CRANK_RPM = 45.0
SPROCKET_CRANK_T = 24
SPROCKET_ROLLER_T = 16
CHAIN_PITCH = 12.7        # 1/2" bicycle chain
CHAIN_CENTER = 23.0       # inches, crank axle above head roller axle (sets crank height)
E_PINE_PSI = 1.2e6        # conservative modulus for SPF lumber


def lawn_ground(x):
    return x * math.tan(math.radians(LAWN_SLOPE_DEG))


def riser_xs():
    """x of each riser face; the last one is the porch edge."""
    treads = STEP_RISERS - 1
    tread = STEP_RUN_TOTAL / max(treads, 1)
    return [LAWN_RUN + i * tread for i in range(treads)] + [LAWN_RUN + STEP_RUN_TOTAL]


def ground(x):
    """Ground profile: lawn, then the steps, then porch floor. A riser at x belongs to the upper level."""
    if x < LAWN_RUN:
        return lawn_ground(x)
    level = sum(1 for r in riser_xs() if x >= r)
    return lawn_ground(LAWN_RUN) + STEP_RISE * level


def main():
    global STEP_RISERS, HEAD_BELT_TOP_ABOVE_PORCH
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--risers", type=int, default=STEP_RISERS)
    ap.add_argument("--head", type=float, default=HEAD_BELT_TOP_ABOVE_PORCH,
                    help="belt top above porch floor at the head roller, inches")
    ap.add_argument("--svg", default="side-profile.svg")
    args = ap.parse_args()
    STEP_RISERS, HEAD_BELT_TOP_ABOVE_PORCH = args.risers, args.head
    porch_x = LAWN_RUN + STEP_RUN_TOTAL
    porch_y = lawn_ground(LAWN_RUN) + STEP_RISE * STEP_RISERS
    x_tail = -TAIL_OVERHANG
    x_head = porch_x + HEAD_SETBACK
    y_tail = TAIL_BELT_TOP
    y_head = porch_y + HEAD_BELT_TOP_ABOVE_PORCH
    slope = (y_head - y_tail) / (x_head - x_tail)
    ang = math.degrees(math.atan(slope))
    cosA = math.cos(math.atan(slope))

    def belt_top(x):
        return y_tail + slope * (x - x_tail)

    # return run: line through the roller bottoms (vertical offset ~ D+2t, / cos for slope)
    off_tail = (D_TAIL + 2 * BELT_T) / IN / cosA
    off_head = (D_HEAD + 2 * BELT_T) / IN / cosA

    def return_run(x):
        f = (x - x_tail) / (x_head - x_tail)
        return belt_top(x) - (off_tail + f * (off_head - off_tail))

    def rail_bottom(x):
        return belt_top(x) + (RAIL_ABOVE_BELT - RAIL_H) / IN / cosA

    out = []
    p = out.append
    p("=" * 72)
    p("CANDY CONVEYOR - STAGE 1 CALCULATIONS (provisional site data)")
    p("=" * 72)
    p(f"Porch floor height above lawn edge: {porch_y:6.1f} in (lawn rise {lawn_ground(LAWN_RUN):.1f} + {STEP_RISERS} risers x {STEP_RISE:.1f})")
    p(f"Tail roller axis x = {x_tail:.1f} in, belt top {y_tail:.1f} in")
    p(f"Head roller axis x = {x_head:.1f} in, belt top {y_head:.1f} in ({HEAD_BELT_TOP_ABOVE_PORCH:.1f} in above porch)")
    p(f"Single straight belt line: slope {slope:.4f}  =  {ang:.2f} deg")
    C_in = (x_head - x_tail) / cosA
    C = C_in * IN
    p(f"Roller centre distance along incline: {C_in:.1f} in = {C/1000:.3f} m ({C_in/12:.2f} ft)")

    # ---- clearances over steps and lawn
    p("\nCLEARANCE CHECK (inches)  belt-top / return-run above local ground")
    checks = [("porch edge (nose)", porch_x)]
    for i, xr in reversed(list(enumerate(riser_xs()[:-1]))):
        checks.append((f"tread {i+1} nose" if i else "first riser top", xr))
    checks.append(("mid lawn", LAWN_RUN / 2))
    checks.append(("lawn edge", 0.0))
    worst = 1e9
    for name, x in checks:
        gy = ground(x)
        bt, rr = belt_top(x), return_run(x)
        worst = min(worst, rr - gy)
        p(f"  {name:20s} x={x:6.1f}  ground {gy:5.1f}  belt {bt:5.1f} ({bt-gy:5.1f})  return {rr:5.1f} ({rr-gy:5.1f})")
    p(f"  -> minimum return-run clearance: {worst:.1f} in  {'OK' if worst >= 3.5 else 'TOO LOW'}")

    # ---- stations
    p("\nSUPPORT STATIONS (stake pairs).  Heights in inches above local ground")
    stations = []
    x = 8.0
    while x < LAWN_RUN - 2:
        stations.append(x)
        x += STATION_PITCH
    stations.append(LAWN_RUN - 4.0)  # last lawn station just below the steps
    p(f"  {'x':>6} {'ground':>7} {'beltTop':>8} {'railBot':>8} {'return':>7} {'stake len':>10}")
    for x in stations:
        gy = ground(x)
        rb = rail_bottom(x) - gy
        stake = rb + 2.5 + STAKE_EMBED   # stake reaches 2.5" above rail bottom (saddle)
        stake_buy = 24 if stake <= 23 else 36 if stake <= 35 else 48
        p(f"  {x:6.1f} {gy:7.1f} {belt_top(x)-gy:8.1f} {rb:8.1f} {return_run(x)-gy:7.1f} {stake:6.1f} -> {stake_buy}\"")
    p(f"  {len(stations)} lawn stations + head stand (porch) + tail at last station; "
      f"span over steps = {x_head - stations[-1]:.0f} in (rails only)")

    # ---- belt loop
    L = 2 * C + math.pi * (D_HEAD + D_TAIL) / 2 + (D_HEAD - D_TAIL) ** 2 / (4 * C)
    lap = 125.0
    p("\nBELT")
    p(f"  Closed loop length (on pitch line): {L/1000:.2f} m = {L/IN/12:.1f} ft")
    p(f"  Cut length incl. {lap:.0f} mm sewn lap: {(L+lap)/1000:.2f} m = {(L+lap)/IN/12:.1f} ft "
      f"(25 yd roll = 75 ft leaves {75 - (L+lap)/IN/12:.0f} ft spare)")
    takeup = 150.0
    p(f"  Take-up travel {takeup:.0f} mm absorbs {2*takeup:.0f} mm of belt growth = {200*takeup/L:.1f} % of loop")

    # ---- sag
    w_carry = (BELT_MASS_PER_M + CANDY_MASS_PER_M) * G
    w_ret = BELT_MASS_PER_M * G
    T_carry = PRETENSION_N - RESIST_DESIGN_N / 2   # carrying run is the SLACK side (see doc)
    span_c = CARRY_IDLER_PITCH * IN / 1000 / cosA
    span_r = STATION_PITCH * IN / 1000 / cosA
    sag_c = w_carry * span_c ** 2 / (8 * T_carry) * 1000
    sag_r = w_ret * span_r ** 2 / (8 * (PRETENSION_N + RESIST_DESIGN_N / 2)) * 1000
    p("\nSAG  (parabolic approx, sag = w L^2 / 8T)")
    p(f"  Carrying run: w={w_carry:.2f} N/m, span {span_c:.2f} m, T={T_carry:.0f} N -> sag {sag_c:.1f} mm")
    p(f"  Return run:   w={w_ret:.2f} N/m, span {span_r:.2f} m, T={PRETENSION_N+RESIST_DESIGN_N/2:.0f} N -> sag {sag_r:.1f} mm")

    # ---- running resistance estimate
    n_carry = int((x_head - x_tail) // CARRY_IDLER_PITCH)
    n_ret = len(stations)
    N_idler = w_carry * span_c
    f_idler = 0.25 * N_idler * (IDLER_BORE / 2) / (D_IDLER / 2)
    belt_len_m = C / 1000
    candy_gravity = -CANDY_MASS_PER_M * belt_len_m * G * math.sin(math.radians(ang))
    est = (n_carry + n_ret) * f_idler + 2.0 + 5.0 + 1.0 + candy_gravity
    p("\nRUNNING RESISTANCE (estimate)")
    p(f"  {n_carry} carrying + {n_ret} return idlers, PLA bushing on steel mu=0.25: {f_idler*(n_carry+n_ret):.2f} N")
    p(f"  belt bending at 2 rollers ~2 N, edge rub allowance 5 N, chain/bearings ~1 N")
    p(f"  full candy load running downhill: {candy_gravity:+.1f} N (helps)")
    p(f"  estimated total {est:.1f} N  -> design value {RESIST_DESIGN_N:.0f} N")

    # ---- drive capacity (Euler capstan)
    T1 = PRETENSION_N + RESIST_DESIGN_N / 2
    T2 = PRETENSION_N - RESIST_DESIGN_N / 2
    for name, mu in (("rubber lagging", MU_LAGGING), ("bare PLA", MU_BARE_PLA)):
        cap = math.exp(mu * math.pi)
        p(f"  Drive grip, {name:15s} mu={mu}: allowed T1/T2 = {cap:.2f}, needed {T1/T2:.2f} "
          f"-> {'OK' if cap > 1.3 * T1 / T2 else 'MARGINAL'}")

    # ---- crank
    ratio = SPROCKET_CRANK_T / SPROCKET_ROLLER_T
    roller_rpm = CRANK_RPM * ratio
    v = math.pi * D_HEAD / 1000 * roller_rpm / 60
    torque_roller = RESIST_DESIGN_N * D_HEAD / 2000
    torque_crank = torque_roller * ratio / 0.9   # 90% chain+bearing efficiency
    F_hand = torque_crank / (CRANK_ARM / 1000)
    turns = C / 1000 / (math.pi * D_HEAD / 1000 * ratio)
    p("\nDRIVE")
    p(f"  Chain {SPROCKET_CRANK_T}T crank -> {SPROCKET_ROLLER_T}T roller = 1:{ratio:.2f} step-up")
    p(f"  Crank {CRANK_RPM:.0f} rpm -> roller {roller_rpm:.0f} rpm -> belt {v:.2f} m/s ({v/0.3048:.2f} ft/s)")
    p(f"  Candy transit {C/1000:.2f} m takes {C/1000/v:.0f} s = {turns:.0f} crank turns")
    p(f"  Roller torque {torque_roller:.2f} N.m, crank torque {torque_crank:.2f} N.m, "
      f"hand force at {CRANK_ARM:.0f} mm arm = {F_hand:.0f} N ({F_hand/4.448:.1f} lbf)")
    links = 2 * CHAIN_CENTER * IN / CHAIN_PITCH + (SPROCKET_CRANK_T + SPROCKET_ROLLER_T) / 2 \
        + ((SPROCKET_CRANK_T - SPROCKET_ROLLER_T) / (2 * math.pi)) ** 2 / (CHAIN_CENTER * IN / CHAIN_PITCH)
    p(f"  Chain length at {CHAIN_CENTER:.0f} in centres: {links:.1f} links -> use {2*math.ceil(links/2)} "
      f"(standard 112-116 link bike chain {'fits' if links <= 116 else 'TOO SHORT'})")
    head_axis_above_porch = HEAD_BELT_TOP_ABOVE_PORCH - (D_HEAD / 2 + BELT_T) / IN
    p(f"  Crank axle {head_axis_above_porch + CHAIN_CENTER:.1f} in above porch floor; handle sweeps "
      f"{head_axis_above_porch + CHAIN_CENTER - CRANK_ARM/IN:.0f}-{head_axis_above_porch + CHAIN_CENTER + CRANK_ARM/IN:.0f} in")
    for t in (SPROCKET_CRANK_T, SPROCKET_ROLLER_T):
        p(f"  {t}T sprocket pitch diameter {CHAIN_PITCH / math.sin(math.pi / t):.1f} mm")

    # ---- structure
    p("\nSTRUCTURE")
    rail_comp = 2 * PRETENSION_N / 2   # each rail carries half of both runs' tension
    I_weak = (RAIL_H / IN) * (RAIL_T / IN) ** 3 / 12
    Lb = STATION_PITCH
    Pcr = math.pi ** 2 * E_PINE_PSI * I_weak / Lb ** 2 * 4.448
    p(f"  Belt tension reacted inside the frame: each rail compressed ~{rail_comp:.0f} N; "
      f"Euler buckling (weak axis, {Lb:.0f} in pinned) {Pcr:.0f} N -> factor {Pcr/rail_comp:.0f}")
    I_strong = (RAIL_T / IN) * (RAIL_H / IN) ** 3 / 12
    w_rail = (w_carry + w_ret) / 2 / 175.1  # N/m -> lbf/in
    w_rail += 0.6 / 12  # rail self weight ~0.6 lb/ft (estimate) per rail
    d = 5 * w_rail * Lb ** 4 / (384 * E_PINE_PSI * I_strong)
    p(f"  Rail deflection between stations ({Lb:.0f} in span): {d*IN:.2f} mm")
    q_psf = 0.00256 * 20 ** 2   # 20 mph
    area = (RAIL_H / IN / 12) * (C_in / 12)
    p(f"  Wind 20 mph on {area:.1f} ft^2 side area: {q_psf*area*1.2:.1f} lbf total "
      f"(~{q_psf*area*1.2/len(stations):.1f} lbf per station)")
    p(f"  Head roller bearing radial load ~{2*PRETENSION_N:.0f} N shared by 2 x 608 (rated in kN) -> trivial")

    report = "\n".join(out)
    print(report)

    # ---------------------------------------------------------------- SVG profile
    VX = 4.2      # px per inch horizontal
    VY = 8.4      # px per inch vertical (2x exaggeration)
    x0, x1 = -20, x_head + 25
    ymax = y_head + 45
    W, H = (x1 - x0) * VX + 40, ymax * VY + 70

    def P(x, y):
        return f"{(x - x0) * VX + 20:.1f},{H - 40 - y * VY:.1f}"

    pts = [P(x0, 0)]
    for xx in [x0, 0, LAWN_RUN - 0.001] + sum(([xr - 0.001, xr] for xr in riser_xs()), []) + [x1]:
        pts.append(P(xx, ground(xx) if xx > 0 else 0))
    pts += [P(x1, -3), P(x0, -3)]
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" font-family="sans-serif" font-size="13">',
           '<rect width="100%" height="100%" fill="#fff"/>',
           f'<polygon points="{" ".join(pts)}" fill="#cfe3c2" stroke="#4a6b3a"/>',
           f'<text x="20" y="22" font-size="15" font-weight="bold">Side profile (vertical scale x2) - provisional site data</text>']
    # rails
    svg.append(f'<polygon points="{P(x_tail, belt_top(x_tail)+RAIL_ABOVE_BELT/IN)} {P(x_head, belt_top(x_head)+RAIL_ABOVE_BELT/IN)} '
               f'{P(x_head, rail_bottom(x_head))} {P(x_tail, rail_bottom(x_tail))}" fill="#d9b98a" opacity="0.7"/>')
    # belt runs
    svg.append(f'<polyline points="{P(x_tail, belt_top(x_tail))} {P(x_head, belt_top(x_head))}" stroke="#111" stroke-width="3" fill="none"/>')
    svg.append(f'<polyline points="{P(x_tail, return_run(x_tail))} {P(x_head, return_run(x_head))}" stroke="#111" stroke-width="2" stroke-dasharray="8 4" fill="none"/>')
    for xr, d_mm, lab in ((x_tail, D_TAIL, "tail Ø50 + take-up"), (x_head, D_HEAD, "drive Ø80")):
        r = d_mm / IN / 2
        cy = belt_top(xr) - r - BELT_T / IN
        cx_, cy_ = P(xr, cy).split(",")
        svg.append(f'<ellipse cx="{cx_}" cy="{cy_}" rx="{r*VX:.1f}" ry="{r*VY:.1f}" fill="#888" stroke="#000"/>')
        svg.append(f'<text x="{float(cx_)-40:.0f}" y="{float(cy_)+r*VY+18:.0f}">{lab}</text>')
    # stations
    for xs_ in stations:
        a = P(xs_, ground(xs_) - STAKE_EMBED * 0.25)
        b = P(xs_, rail_bottom(xs_) + 2.5)
        svg.append(f'<polyline points="{a} {b}" stroke="#7a5a2a" stroke-width="4"/>')
    # head stand + crank tower
    hb = belt_top(x_head) - D_HEAD / IN / 2
    svg.append(f'<polyline points="{P(x_head-6, porch_y)} {P(x_head-6, rail_bottom(x_head-6))}" stroke="#7a5a2a" stroke-width="4"/>')
    svg.append(f'<polyline points="{P(x_head, hb)} {P(x_head, hb + CHAIN_CENTER)}" stroke="#555" stroke-width="2" stroke-dasharray="3 3"/>')
    cx_, cy_ = P(x_head, hb + CHAIN_CENTER).split(",")
    svg.append(f'<circle cx="{cx_}" cy="{cy_}" r="9" fill="#c60"/>')
    svg.append(f'<text x="{float(cx_)-150:.0f}" y="{float(cy_)-6:.0f}">crank (chain 1:1.5)</text>')
    # basket
    bx = x_tail - 1
    svg.append(f'<rect x="{(bx - 6 - x0)*VX + 20:.0f}" y="{H-40-(TAIL_BELT_TOP-1.5)*VY:.0f}" width="{12*VX:.0f}" '
               f'height="{(TAIL_BELT_TOP-1.5)*VY:.0f}" fill="none" stroke="#e67e22" stroke-width="2"/>')
    svg.append(f'<text x="{(bx-6-x0)*VX+20:.0f}" y="{H-12:.0f}">basket</text>')
    svg.append(f'<text x="{(120-x0)*VX:.0f}" y="{H-12:.0f}">lawn 250 in @ 5°  —  belt line {ang:.1f}°, centres {C_in/12:.1f} ft</text>')
    svg.append(f'<text x="{(LAWN_RUN-60-x0)*VX:.0f}" y="{H-40-(porch_y+28)*VY:.0f}">{STEP_RISERS} risers (belt bridges over)</text>')
    svg.append("</svg>")
    out_svg = Path(__file__).resolve().parent.parent / "docs" / args.svg
    out_svg.write_text("\n".join(svg))
    (Path(__file__).resolve().parent / f"report-{STEP_RISERS}-risers.txt").write_text(report + "\n")


if __name__ == "__main__":
    main()

# Hand-cranked Halloween candy conveyor

A manually powered, continuous-belt conveyor that carries candy about 24 ft from the porch,
over the steps and down a 5° lawn, into a basket at the sidewalk.

| Stage | Status |
|---|---|
| 1. Analysis | ✅ [docs/01-analysis-and-architecture.md](docs/01-analysis-and-architecture.md) |
| 2. Architecture | ✅ single straight belt, webbing loop, wooden rails on stakes, chain-driven crank |
| 3. Mechanism detail | ⏳ waiting for site measurements |
| 4–7. CAD, validation, test prints, assembly guide | not started |

Nothing has been built or tested yet.

## Calculator

```
python3 calc/conveyor_calc.py --risers 2 --head 9 --svg side-profile-2-risers.svg
```

Edit the `ASSUMED` values at the top of `calc/conveyor_calc.py` once the site is measured.
The script prints clearances, stake lengths, belt length, sag, drive grip, crank effort and
chain length, and redraws the side profile in `docs/`.

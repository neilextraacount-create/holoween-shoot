# Shopping list

Everything is printed except the belt. You only buy the belt (and filament if you need more).

Prices: Amazon pages could not be opened from the environment where this was written. Prices
are from search-result snapshots or marked **est.** Check the live listing before buying.

## 1. The belt ("the black thing the candy rides on")

| | |
|---|---|
| **Buy** | **Country Brook Design 3 in Black Heavy Polypropylene Webbing, 50 yd**: <https://www.amazon.com/dp/B0BJ7X4THD> |
| Specs (from the listing) | 3 in (76 mm) wide, about 1.7 mm (0.067 in) thick, 2,100 lb break strength, black |
| Price | about $35-45 (the same roll was seen at $34.50 on Country Brook's own site and $38.50 on eBay; not visible on Amazon in search) |
| How much you use | one loop of **41 ft**. Cut 43 ft and sew it in place (build guide, section 7). |
| Why the 50 yd roll | Country Brook says its rolls *may contain factory splices*. You need one unbroken 43 ft piece, and 150 ft guarantees that. The rest is a spare belt. Before ordering, message the seller through Amazon and ask for a roll with no splices. |
| Does it fit the printed parts? | Yes. Every belt-dependent part is sized from `belt_w = 76.2` and `belt_t = 1.7` in `cad/params.scad`. When the belt arrives, measure its width in 3 places and its thickness. If either is off by more than 0.5 mm, change the number and run `python3 cad/check_parts.py` to regenerate and re-check every part. |

**Backup:** MECCANIXITY 3 in black polypropylene webbing, 25 yd
(<https://www.amazon.com/dp/B0CSDKQ2Y6>, about $23 seen). It is thinner (1.1 mm), so set
`belt_t = 1.1`. 25 yd = 75 ft, enough for one loop if there's no splice in the middle.

**Do not buy:**
- rubber or neoprene strip (stretches)
- nylon webbing (stretches when wet)
- 4 in PVC conveyor belting (every part would need resizing, and it needs metal lacing)
- 1 in or 2 in webbing (too narrow for the rollers)

## 2. Filament

| Item | Amount |
|---|---|
| PLA, any brand, 1.75 mm | about **2.5 kg** for the machine (the checker's estimate, see `cad/parts-table.md`) plus about 0.3 kg for the test coupon, test prints and mistakes: **buy 3 x 1 kg spools if you have none** (a 4th gives room for reprints). Bambu PLA Basic or eSUN PLA+ are fine (eSUN 1 kg was seen at $11.99). Black or orange looks good for Halloween; the belt is black, so a lighter colour makes the frames easier to see in the dark. |

## 3. Things you probably already have (not bought for this)

| Item | Used for |
|---|---|
| A large sewing needle and strong thread (upholstery or button thread, braided fishing line, or waxed dental floss) | sewing the belt loop: a 75 mm lap, box-and-X stitch. A hot nail or soldering iron to pierce the webbing makes it much easier (mark the holes through the template first; never push a hot tool through the PLA template). |
| Lighter or candle | sealing the cut ends of the webbing so they don't fray |
| A candle (wax) | rub on the print-in-place bearings before first use: cuts the crank effort about 25 % |
| Tape measure, string, marker | laying out the line on the lawn |
| Screwdriver or a long nail | making pilot holes for the stakes and ground screws in hard soil |
| A strap, rope or 2 long zip ties | ties the porch stand post to a railing or column, so cranking can't tip it |
| 2 full 1-gallon water jugs (about 8 kg) | ballast on the stand's foot if there is nothing to tie it to |
| Candy bowl | sits on the stand's foot, right by the funnel |
| Optional: water jugs or bricks | extra weight if your soil is too soft or too hard for the ground screws (about 5 kg at the tail, 3 kg at the head). It only stops lifting: the screws or spikes still go in as pegs (build guide, section 5). |

## 4. Totals

| | |
|---|---|
| Belt | about $35-45 |
| Filament (if you have none) | about $36-60 for 3 spools |
| **Total** | **about $35-45 if you already have filament; $70-105 if not** |

The previous version needed $180-230 of wood, bearings, chain and bolts. All of that is now
printed.

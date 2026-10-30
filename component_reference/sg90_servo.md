# SG90 micro servo — component reference

Mechanical analog of `hardware_reference/*.md`: this is what a future
design/3D agent would be fed as grounding context before generating a
mounting bracket for this part, the same way `hardware_reference/
arduino_uno.md` grounds the coder agent's pin/voltage claims. Keep it
factual and sourced — this is what prevents dimension hallucination
for mechanical parts, same principle as the electronics side.

## Status: GROUNDED FOR A FIRST DRAFT — tab thickness still open
Envelope, hole spacing, and now hole diameter are sourced (product
diagram + user confirmation). Remaining gap is tab thickness, which
affects screw length but not hole layout. **A design agent can draft
a full bracket (footprint + hole positions + hole diameter) from this
file now.** See "What's still missing" for the one item worth
confirming before finalizing for print.

## Target part
Specific product in hand/ordered: "Beffkkip 10Pcs SG90 9g Micro Servos"
(Amazon ASIN B08KY49SFX). The dimensions below come from this
product's own listing diagram (Beffkkip-branded, matches the ordered
part), not a generic "SG90" aggregate — more trustworthy than the
cross-manufacturer sources in "Other public sources (superseded)"
below, which disagreed with each other by up to ~4mm. Still a stock
product-page diagram, not a hand-measured caliper reading of the
physical part — treat as good but not gold-standard until confirmed.

## Confirmed dimensions (from product dimension diagram, 2026-10-30)
- **Overall case height:** 32mm (0.98in label in source rounds
  oddly — read as 32mm / 1.26in per the diagram's own left-side
  figure)
- **Case width** (side view, consistent across two panels of the
  diagram): 12.5mm
- **Mounting tab hole-to-hole spacing** (center-to-center, long
  axis): **22.4mm** — this is the number that blocked bracket design;
  not available from any public source checked earlier.
- **Overall footprint length** (tab tip to tab tip, long axis):
  31.8mm
- Two sub-height figures on the diagram (18mm and 25mm) split the
  32mm total between the narrow upper gearbox housing and the main
  body, but which label belongs to which section isn't fully certain
  from the image alone. Doesn't block the bracket (footprint + hole
  spacing are what matter for mounting); worth a 10-second caliper
  check if the servo is in hand anyway.

## Mounting tab hole diameter: M3 (user-confirmed, 2026-10-30)
The included mounting screw is M3. Checked public sources first
before accepting this (an
[Arduino forum thread](https://forum.arduino.cc/t/servo-arm-screw-mount-size/696481)
on this exact question had posters disagreeing from "just under 2mm"
to "M3," and conflated horn screws with tab screws — not usable on
its own) — the user directly confirmed M3 for this part, which is a
better source than scattered forum guesses about a different/unknown
clone. Derived clearance-hole sizing for the bracket's own mating
holes (standard practice, not a measurement): a through-hole sized
for M3 clearance is typically ~3.2-3.4mm; confirm against the actual
screw if a snug/self-tapping fit is wanted instead of a clearance fit.
The servo's own tab hole diameter itself (as opposed to the bracket's
mating hole) hasn't been separately measured, but M3 is now the
working assumption for sizing both sides of the joint.

## What's still missing
- **Tab thickness** — not on the diagram, not yet measured. Affects
  screw length selection, not hole layout — doesn't block a first
  draft.

## How to fill in what's left
1. Tab thickness (quick caliper reading once the part is in hand)
2. (Optional, not blocking) confirm which of 18mm/25mm is which
   sub-height, and the output shaft/horn height from the base

## Other public sources (superseded by the diagram above for L/W/H
and now superseded entirely for hole spacing — kept for the
clone-variance context, not as the active reference)
| Source | L | W | H | Weight |
|---|---|---|---|---|
| [TAMS Uni-Hamburg SG90 datasheet](https://tams.informatik.uni-hamburg.de/lehre/2023ss/vorlesung/es/doc/sg90.pdf) | 22.2mm | 11.8mm | 31mm | 9g |
| [TowerPro SG90 listing](https://skycraftsurplus.com/products/towerpro-sg90-micro-servo-arduino-compatible.html) | 23.1mm | 12.2mm | 29.0mm | 9.0g |
| T-Pro Mini SG-90 listing | 22.0mm | 11.5mm | 27mm | 9g (10.6g w/ wire+connector) |

Up to ~4mm disagreement between these on height — real clone-to-clone
variance, part of why the diagram above (specific to the ordered
part) is now the preferred source instead.

## Provenance
- Confirmed dimensions: product's own dimension diagram, supplied by
  the user, 2026-10-30. Specific to the Beffkkip-branded SG90 listing
  (Amazon ASIN B08KY49SFX). Source image saved at
  `component_reference/images/sg90_beffkkip_dimensions.png`.
- Mounting screw size (M3): confirmed directly by the user, 2026-10-30.
- Other sources consulted (superseded): see links above (2026-10-30).
- No CAD model, STEP, or STL file of this part exists anywhere in
  this project yet.
- No license/attribution concerns apply to taking your own physical
  measurements of a part you own, or to reading dimensions off its
  own product listing.

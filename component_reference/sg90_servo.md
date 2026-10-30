# SG90 micro servo — component reference

Mechanical analog of `hardware_reference/*.md`: this is what a future
design/3D agent would be fed as grounding context before generating a
mounting bracket for this part, the same way `hardware_reference/
arduino_uno.md` grounds the coder agent's pin/voltage claims. Keep it
factual and sourced — this is what prevents dimension hallucination
for mechanical parts, same principle as the electronics side.

## Status: INCOMPLETE — do not use to ground a design agent yet
The one measurement a bracket design actually needs most — the
mounting tab hole diameter and hole-to-hole spacing — is not reliably
available from any public source checked so far (2026-10-30). See
"What's missing" below. **A design agent must not generate a bracket
against this file until that section is filled in from a real
measurement.**

## Target part
Specific product in hand/ordered: "Beffkkip 10Pcs SG90 9g Micro Servos"
(Amazon ASIN B08KY49SFX) — a generic SG90-labeled clone, not a single
standardized manufacturer part. "SG90" is used across many
manufacturers' clones with measurable differences between them (see
below), so treat any number here as specific to this batch, not a
universal SG90 constant, until re-confirmed against the actual part.

## Overall body envelope (approximate, source-inconsistent)
| Source | L | W | H | Weight |
|---|---|---|---|---|
| [TAMS Uni-Hamburg SG90 datasheet](https://tams.informatik.uni-hamburg.de/lehre/2023ss/vorlesung/es/doc/sg90.pdf) | 22.2mm | 11.8mm | 31mm | 9g |
| [TowerPro SG90 listing](https://skycraftsurplus.com/products/towerpro-sg90-micro-servo-arduino-compatible.html) | 23.1mm | 12.2mm | 29.0mm | 9.0g |
| T-Pro Mini SG-90 listing | 22.0mm | 11.5mm | 27mm | 9g (10.6g w/ wire+connector) |

Up to ~4mm disagreement on height between sources labeled identically
— this is real clone-to-clone variance, not reading error. **Do not
treat any single row above as ground truth for the actual part in
hand.** A bracket design should either use the real measured part
(preferred) or build in enough clearance/tolerance to absorb this
spread if forced to rely on a published figure.

## What's missing (the actual blocker)
- **Mounting tab hole diameter** — not found in any source checked.
- **Mounting tab hole-to-hole spacing** (center-to-center, same side)
  — not found. This is the single most important number for a
  bracket; without it, hole positions in a design would be guessed,
  which is exactly what this project's grounding rule exists to
  prevent.
- **Tab thickness** — not found.
- **Output shaft/horn height from the case base** — not found.
  [One datasheet PDF](https://www.kjell.com/globalassets/mediaassets/701916_87897_datasheet_en.pdf)
  has a real dimensioned drawing with unlabeled numbers (22.8, 32.0,
  26.7, 15.6, 12.4, 15.8, 14.2, 7.7, 2.54mm) that likely include this,
  but the labels didn't survive text extraction and the file couldn't
  be downloaded to inspect visually from this environment (host not
  reachable). Don't assign these numbers to features by guessing which
  is which.

## How to fill this in (next action, blocks any design-agent work)
Measure the actual physical part (the Beffkkip-batch servo once it's
in hand) with calipers:
1. Body L x W x H (case only, excluding horn/wire)
2. Mounting tab hole diameter
3. Hole-to-hole spacing (center-to-center, same side)
4. Tab thickness
5. Output shaft height from the case base, to where the horn spline
   sits

Record each with the tool used (calipers vs. estimated) and date
measured. Once filled in, this file becomes the actual grounding
source for the design agent's first bracket spec — same role
`hardware_reference/*.md` plays for the coder agent.

## Provenance
- Sources consulted: see links above (2026-10-30).
- No CAD model, STEP, or STL file of this part exists anywhere in
  this project yet.
- No license/attribution concerns apply to taking your own physical
  measurements of a part you own.

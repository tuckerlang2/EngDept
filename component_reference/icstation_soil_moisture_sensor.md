# Icstation resistive soil moisture sensor — component reference

Mechanical/electronics analog of `hardware_reference/*.md` and
`component_reference/sg90_servo.md`. Target part: "Icstation Soil
Hygrometer Sensor Test Kit with Corrosion Resistant Probe, Digital
Analog Signal Output" (resistive 2-probe type, sold for
Arduino/automatic-watering use) — named in
`design_specs/moistureSensorDroneMount`.

## Status: INCOMPLETE — do not use to ground a bracket's clip/channel
yet
Electrical specs and probe geometry are confirmed from the product's
own listing. The one dimension that actually blocks this specific
design task — **the black sensor housing's own width/diameter and
cross-section shape** — is not shown anywhere in the two reference
images supplied and is not stated in the design request. This is the
same shape of gap that blocked the SG90 bracket until a dimensioned
diagram was supplied.

## Confirmed specs (from the product's own Amazon listing screenshots,
supplied with the design request, 2026-11-01)
- Working voltage: DC 3.3–12V
- Working current: <20mA; output current: <30mA
- Driver/comparator board size: 36 x 15 x 6mm (L*W*H) — this is the
  small HD-38 potentiometer board, NOT the sensor probe housing
- Sensor probe length: 8.8cm / 3.46in
- Sensor pin pitch (distance between the two probes): 5mm
- Sensor cable length: 1.2m
- Sensor connector: XH2.54 2P
- Outputs: DO (digital threshold) and AO (analog value)
- Driver board footprint detail (from the second screenshot): roughly
  3cm wide, with a 1.5cm cable-connector tab and a 0.7cm notch —
  useful only if the driver board itself ever needs mounting; not
  relevant to the probe-housing bracket.

## What's actually missing (the real blocker for this task)
- **Sensor housing (the black cap the two probes extend from) width/
  diameter and cross-section shape.** Neither screenshot shows this —
  one is a specs table, the other is a close-up of the driver board,
  not the probe housing. The design request's own `dimensions` field
  gives "bracket width 13mm, bracket length 50mm," but these describe
  the *bracket*, not a measured housing dimension, so there's no way
  to confirm whether 13mm actually matches/clears the real housing —
  treat 13mm as the requester's working guess, not a grounded fact,
  until it's confirmed against the actual part.
- Housing length (how much of the handle needs to sit inside the
  channel) is also unstated.
- Whether the housing cross-section is round, has a flat/keyed face,
  or tapers — matters directly for whether a "slide-in channel" vs. a
  "clip" is even the right mechanism.

## How to fill in what's left
Same resolution path that worked for the SG90 bracket: either (a) a
caliper measurement of the housing's width and length once the part
is in hand, or (b) a clear top-down/end-on photo of the housing with
a ruler or known-size reference object next to it. A rotated/angled
product photo (like the two already supplied) isn't enough on its own
for a clip/channel fit — this is exactly the kind of mechanical
dimension this project's rules require grounding, not guessing.

## Provenance
- Electrical specs, probe pitch/length, driver board size: read
  directly off the product listing screenshots supplied with
  `design_specs/moistureSensorDroneMount`, 2026-11-01.
- No CAD model, STEP, or STL of this part exists anywhere in this
  project yet.
- No physical measurement of the probe housing has been taken.

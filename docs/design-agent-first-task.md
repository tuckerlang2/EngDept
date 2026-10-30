# Design/3D agent — first task scoping (not yet a spec)

Step 3 of the original plan: before writing the design/3D agent's
code or system prompt, figure out its first real task and what data
it needs. This doc is that scoping work. It is explicitly NOT yet a
buildable spec — see "Status" below. Compare
`docs/primary-coder-agent-spec.md` for what a completed spec for this
agent should eventually look like once this doc's blocker clears.

## Status: dimensionally grounded for a first draft; two design
questions still open
`component_reference/sg90_servo.md` now has what a first bracket
draft needs — footprint, hole spacing, and hole diameter — sourced
from the product's own dimension diagram plus direct user
confirmation on screw size, not from the inconsistent public sources
checked earlier. The one still-open physical item (tab thickness)
affects screw-length selection, not the bracket's hole layout, so it
doesn't block drafting. **What still blocks writing
`agent/design_agent.py` or a design-equivalent of `system_prompt.md`
is not physical data anymore — it's the two open architecture
questions below** (output format, verification-gate equivalent).

## Chosen first task
A mounting bracket for an SG90 micro servo (the specific part in
`component_reference/sg90_servo.md` — "Beffkkip 10Pcs SG90", Amazon
ASIN B08KY49SFX). Chosen because:
- It's cheap, common, and the kind of part this project's eventual
  drone/robotics work will use repeatedly — a reasonable first case,
  not a one-off.
- It's small and simple enough to prove the architecture
  (grounded-design + some verification step, mirroring the coder
  agent's grounded-codegen + compile-check) without also requiring
  solving a hard mechanical problem.
- Unlike a drone frame or a multi-component assembly, it has exactly
  one part to ground against, which keeps the first test case as
  simple as the coder agent's PIR+LED case was.

## Decisions made so far (defaults chosen when the user had no
preference — stated as defaults, not requirements; revisit if that
turns out wrong)
- **Manufacturing method: 3D printed (FDM).** Determines the design
  agent's output format (STL or STEP, not a 2D cut file) and its
  tolerance/wall-thickness rules (FDM needs different minimums than
  laser-cut acrylic).
- **Mount target: generic flat panel.** The bracket's servo-side
  (holes/clearance matching the servo) is the part that needs real
  measurement; the panel-side (how the bracket itself attaches —
  screw holes, a slot, etc.) can be a simple, generic flat-panel
  mount for this first case, since no specific frame/chassis exists
  yet to mount to instead.

## What this task needs before a spec can be written (the actual
scoping output of this doc)
1. **The servo's measured mounting envelope** —
   `component_reference/sg90_servo.md`'s missing fields (tab hole
   diameter, hole spacing, tab thickness, horn height). This is the
   hard blocker; nothing else below matters until this exists.
2. **An output format decision for the design agent's generated
   file** — likely an OpenSCAD or CadQuery parametric script (text,
   diffable, matches this project's "code, not binary blobs"
   instinct from the coder agent) that generates an STL, rather than
   a hand-drawn STEP file. Not yet decided for certain — needs a
   short investigation into what's actually scriptable headlessly
   (mirrors the coder agent's own "verify the current API against
   real docs, not memory" discipline from Session 1).
3. **A verification-gate equivalent to `compile_check`** — the
   non-negotiable "no agent self-certifies" rule applies here too.
   For code, compile-check is unambiguous (it compiles or it
   doesn't). For a mechanical design, the equivalent check is less
   obvious — candidates: a dimension-conformance check (does the
   generated model's hole spacing actually match the component
   reference file, programmatically, not just by the agent's say-so),
   a mesh-validity check (watertight/manifold, so it's actually
   printable), and possibly a basic interference/clearance check.
   Needs its own short design pass once (1) is unblocked — don't
   invent this in the abstract before there's a real model to check.
4. **Tolerance policy for FDM printing** — hole diameters typically
   need to be printed slightly larger than the nominal screw/pin size
   to actually fit (a well-known FDM-specific issue, not something to
   solve by precision alone). Needs a stated tolerance value (e.g.
   "+0.2mm on hole diameters") once a specific printer/filament isn't
   yet known — can start with a commonly-cited conservative default
   and flag it as adjustable, rather than blocking on this alone.

## Explicitly not decided yet
- Whether the design agent is Agent-SDK-based like the coder agent,
  or a simpler script-based tool (a design task may not need an LLM
  in the loop for a first simple bracket at all — worth asking
  "does this need to be an agent, or just a parametric script," the
  same kind of scope question the coder agent spec asked and answered
  for code generation).
- The actual verification tool/library (OpenSCAD's own render,
  a Python CAD library's validity checks, etc.) — needs research once
  the output-format decision above is made.

## Next action
Resolve the two open design questions above (output format; a
compile-check equivalent for mechanical designs) and the "does this
need to be an LLM agent at all" question — these, not physical
measurement, are now what's between this doc and a real spec. Tab
thickness (the one remaining physical gap, see
`component_reference/sg90_servo.md`) can be measured in parallel; it
doesn't block this.

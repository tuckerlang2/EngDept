# Design/3D agent — first task scoping (not yet a spec)

Step 3 of the original plan: before writing the design/3D agent's
code or system prompt, figure out its first real task and what data
it needs. This doc is that scoping work. It is explicitly NOT yet a
buildable spec — see "Status" below. Compare
`docs/primary-coder-agent-spec.md` for what a completed spec for this
agent should eventually look like once this doc's blocker clears.

## Status: first draft actually built live in Fusion (2026-10-31,
session 7) — output format resolved, verification gate still open
A first bracket (44x24x3mm plate, 2 servo holes at 22.4mm spacing + 4
corner panel-mount holes, all M3-clearance) was built live and
exported as `.f3d` — now organized at
`library/projects/sg90-servo-bracket/` (see `docs/library-spec.md`),
containing the output file, `PROVENANCE.md` (full detail, dimensions,
what was/wasn't verified) and `metadata.yaml`. This resolves the output-format
question (below) but this is **one interactive build, not a
repeatable agent** — see "Architecture conclusion" and "Still open"
below before treating step 3 as proven the way steps 1-2 are.

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
2. **Output format — RESOLVED (session 7), with a structural caveat.**
   The user does Fusion 360 CAD work and explicitly wanted a `.f3d`
   file, not a parametric script requiring manual execution. Confirmed
   Fusion 360 has no headless/batch mode (checked, not assumed) — the
   only true-headless Autodesk option is the separate, billed
   Forge/APS Design Automation cloud API. So `.f3d` output means the
   design agent (whatever it ends up being) must run as a **live
   session with Fusion open and its MCP connector connected**, driving
   the real Fusion Python API via `fusion_mcp_execute` — never a
   cloud-headless component like the coder agent. This is now a fixed
   architectural fact for this whole department, not an open question.
3. **A verification-gate equivalent to `compile_check` — STILL OPEN,
   and now a known real gap, not a hypothetical one.** Session 7's
   build script wrote a numeric self-check (expected vs. actual
   bounding box, read back via `boundingBox` on the created body) into
   a `global result` variable, the same capture convention used
   earlier for text output — but the MCP tool's response message came
   back empty both times this was tried (once on the original build,
   once on the cleanup/export run). The bracket's dimensions are only
   confirmed **visually** (an isometric screenshot showing the right
   shape and hole count) and by **file existence/size** (the exported
   `.f3d` is non-zero), not by an actual re-read numeric check. See
   `design/sg90_bracket_v1_PROVENANCE.md` for full detail. This is
   exactly the "no agent self-certifies" rule being violated in
   practice right now, not just unaddressed in theory — fixing the
   result-capture path (or finding a different way to read dimensions
   back out, e.g. a separate read-only script/query rather than
   trusting the same execute call's message field) is the concrete
   next step for this item, not abstract design work.
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

## Intake side — RESOLVED in a separate doc (session 7, same day)
How a design request even gets specified (required fields, optional
reference image, JSON output) is now its own doc:
`docs/design-intake-form-spec.md`, with a working form artifact and a
worked example (`design_specs/sg90_bracket_request.json`, back-filled
from this bracket). That doc also defines a two-phase workflow —
a cheap, no-Fusion-connector "confirmation sketch" step before any
live CAD session — which is the right place for the self-check idea
below to eventually live, once it's real.

## Next action
Output format is resolved (session 7). What's left before a real spec:
1. Close the verification-gate gap above — get a real numeric
   dimension self-check working, not just visual/file-existence
   confirmation.
2. Decide the FDM hole-tolerance policy (item 4 above).
3. Decide whether this is an LLM-based agent or a plain repeatable
   script — session 7's build was neither: it was ad-hoc interactive
   scripting against the live Fusion MCP connector, iterating through
   3 real API errors by hand. Turning that into either a saved,
   re-runnable script or an actual `agent/design_agent.py` (with a
   system prompt analogous to the coder agent's) is unstarted.
4. Build the actual Phase-0 "confirmation sketch" step described in
   `docs/design-intake-form-spec.md` — demonstrated manually once this
   session (the SVG sent to the user for this same bracket), not yet
   a scripted, repeatable step with its own output format.
Tab thickness (the one remaining physical gap, see
`component_reference/sg90_servo.md`) still doesn't block any of this.

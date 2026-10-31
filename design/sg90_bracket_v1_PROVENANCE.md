# SG90 servo mounting bracket v1 — provenance

## What this is
First design-agent-equivalent output for the Engineering Department
project. Built **live, interactively, inside the user's own Fusion
360 session** via the Fusion 360 MCP connector — not by a headless
agent. See "Architecture conclusion" below for why that's permanent,
not a current limitation.

## Grounding
All dimensions sourced from `component_reference/sg90_servo.md`
("GROUNDED FOR A FIRST DRAFT" status), itself sourced from the
Beffkkip SG90 product's own dimension diagram plus user-confirmed M3
mounting screw. No dimension in this part was invented from model
memory.

## Design
- Flat plate, 44mm x 24mm x 3mm (FDM-printable default thickness).
- Two servo mounting holes at 22.4mm center-to-center spacing
  (matches the servo's confirmed tab hole spacing), 3.4mm diameter
  (M3 clearance, standard-practice sizing per the component reference
  — not yet adjusted for FDM print tolerance, see "Open items").
- Four corner panel-mount holes, 3.4mm diameter, inset 4mm from each
  edge — generic flat-panel mount per the default chosen in
  `docs/design-agent-first-task.md` (no specific target frame existed
  to mount to instead).

## Verification performed
- **Visual:** isometric screenshot of the built body, taken via
  `fusion_mcp_read` (queryType: screenshot) immediately after the
  extrude feature completed. Shows a flat plate with exactly 6 round
  holes (2 center + 4 corner), consistent with the intended design.
- **File existence/size:** confirmed via direct filesystem check after
  export — `sg90_bracket_v1.f3d`, 75,584 bytes, written
  2026-10-31 12:17 — not a zero-byte or failed export.
- **NOT confirmed:** a numeric bounding-box self-check (expected
  44.00 x 24.00 x 3.00mm) was written into the build script (reading
  `rootComponent.bRepBodies.item(0).boundingBox` and converting from
  Fusion's internal cm units) but the script's result-capture
  mechanism (`global result = "..."`) did not surface in the MCP
  tool's response message on either the build or the cleanup/export
  run — tried twice, same empty-message behavior both times. This is
  an unresolved tooling gap, not a design uncertainty: treat the
  44x24x3mm dimensions as "what the script was told to build," backed
  by the visual check, but not independently re-measured and
  confirmed by a second read. A real dimension-conformance
  self-check (the "compile-check equivalent" question in
  `docs/design-agent-first-task.md`) needs this gap closed first —
  e.g. a follow-up read-only script that reads the bounding box back
  out via a different path (`fusion_mcp_read`, not relying on the
  execute call's own message field) rather than trusting the same
  mechanism that already failed to surface once.

## Open items (do not treat this as a finished part)
- **Tab thickness unmeasured** (see `component_reference/sg90_servo.md`)
  — doesn't affect this bracket's hole layout, but does matter for
  screw length selection before anything is actually printed and
  assembled.
- **No FDM hole tolerance applied.** Hole diameters (3.4mm) are
  standard M3-clearance sizing, not adjusted for the fact that FDM
  prints typically come out slightly undersized on hole diameter —
  `docs/design-agent-first-task.md` flagged this as an open "tolerance
  policy" item and it's still open. Expect the as-printed holes to
  need slight reaming/drilling, or re-export with a larger diameter
  (e.g. +0.2mm) once an actual printer/filament is known.
- **No interference/clearance check performed** against anything the
  bracket would actually mount next to (motor horn rotation sweep,
  wiring, etc.) — there is no target assembly yet for this to check
  against; flagged as a gap, not resolved.
- Plate thickness (3mm) and corner-hole inset (4mm) are my own
  reasonable defaults for a generic flat-panel FDM mount, not sourced
  from any requirement the user stated — worth confirming before
  this becomes a print-ready file.

## Architecture conclusion (for `docs/design-agent-first-task.md`)
Fusion 360 has no headless/batch mode for the desktop app (confirmed
via research this session, not assumed) — the only true-headless
Autodesk option is the separate, billed Forge/APS Design Automation
cloud API, a different product. This means a `.f3d`-producing design
agent can never be a cloud-headless, orchestrator-callable component
the way the coder agent is. It must run as a live session with the
user's Fusion 360 open and the MCP connector connected — a structural
constraint on this whole department's architecture, not a gap to
close later.

## How this was actually built (for repeatability)
Interactively, through iterative script execution against the live
Fusion MCP connector (`fusion_mcp_execute`, featureType "script"),
not from a saved/repeatable script file. Real API facts used (learned
via `fusion_mcp_read` queryType "apiDocumentation", not from model
memory):
- Script entry point must be `def run(context):` — a bare top-level
  script fails (`NameError: name 'run' is not defined`).
- `context` passed to `run()` is `None`, not a dict.
- `Document.name` is settable; `Component.name` on the *root*
  component is not (`RuntimeError: 3 : root component name cannot be
  changed`) — rename the document, not the root component.
- `Point3D.create()` coordinates are in **centimeters** (Fusion's
  internal model-space unit), not mm — `ValueInput.createByString('3
  mm')` is the safer way to pass a dimensional value with explicit
  units.
- Fusion auto-generates a `Profile` object for every closed region in
  a sketch; for a rectangle containing N circles this yields N+1
  profiles (1 "rectangle minus all holes" compound profile, found via
  `profile.profileLoops.count == N+1`, plus N separate tiny
  circle-interior profiles) — select the compound one for extrusion.
- `ExportManager.createFusionArchiveExportOptions(path)` +
  `ExportManager.execute(options)` is the real API for producing a
  `.f3d` file, accessed via
  `adsk.fusion.Design.cast(app.activeProduct).exportManager`.
- Closing a `Document` via `doc.close(False)` invalidates that Python
  object immediately — reading any property of it afterward (even
  `.name`) raises `RuntimeError: 4 : An API Object refers to a deleted
  Object`. Capture anything needed from a document before closing it.

This was not yet turned into a saved, reusable script file or a
repeatable `design_agent.py` workflow — doing so, and designing the
actual verification-gate equivalent, is the next real step (see
`docs/design-agent-first-task.md`).

## Cleanup performed
Three empty "Untitled" Fusion documents, left over from earlier failed
script attempts in this same session (each one's `app.documents.add()`
call succeeded before the script errored later), were closed without
saving via the same MCP connector, so they don't clutter the user's
live Fusion session.

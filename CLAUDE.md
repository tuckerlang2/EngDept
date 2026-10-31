# CLAUDE.md — context for every session

Read automatically at the start of a session. Keep it current — update
"Current state" at the end of every work session, before you stop.

## What this project is
The primary coder agent: the first node in an eventual multi-agent
engineering department (coder → design → manufacturing engineering),
itself the first department in a multi-agent company whose 2-3 year
goal is a manufacturable flying/ground/water drone product line. See
`docs/engineering-department-notes.md` for the full context and
`docs/primary-coder-agent-spec.md` for this agent's specific contract.

Rebuilt from a sibling project, `embedded-code-gen-agent`, whose
`src/` pipeline proved the core idea once (grounded codegen +
compile-check) but was never re-verified and couldn't represent
multi-board specs. Several files are ported unchanged from there
(`hardware_lookup.py`, `spec_schema.py`, `compile_check.py`,
`config/boards.yaml`, `hardware_reference/*.md`) because they already
worked and the rebuild is about the agent architecture (headless,
SDK-based, structured output), not about redoing data entry that was
already correct.

## Non-negotiable design rules
(Same rules as the sibling project, carried forward deliberately —
these aren't being relaxed because the architecture changed.)
- Never let the agent invent pin numbers/voltage specs from memory
  alone — always ground generation in `hardware_reference/*.md` for
  the specific board in use. This is the #1 reliability lever.
- The agent must run its own compile-check (via the `compile_check`
  tool) before reporting success — it cannot self-certify.
- The agent never flashes/uploads to physical hardware, and never
  claims to. A human reviews and flashes separately, always.
- Voltage/logic-level mismatches are the main physical risk —
  hardware_reference entries must state logic level.
- The agent's final output must end with a structured STATUS line
  (PASS / ESCALATE / FAIL_RETRY_EXCEEDED) so a calling orchestrator
  can branch on it without parsing prose. See `agent/system_prompt.md`.
- **Prefer adapting existing, proven public designs and code over
  building from scratch**, when a reasonable fit exists. Applies
  especially to flight-control/stabilization firmware (prefer
  established, flight-proven projects like ArduPilot/PX4/Betaflight
  over a custom-written control loop — this is a safety argument, not
  just an efficiency one) and to mechanical frame/structural starting
  points (use an existing design's geometry as a baseline, modify to
  fit actual components/budget/payload — not a finished product to
  ship unmodified).
- **Mandatory before incorporating anything external: check and record
  its license.** Escalate (don't silently proceed) if a design or
  codebase is non-commercial-licensed (e.g. CC BY-NC) or copyleft in a
  way that could force disclosure of derivative work (e.g. GPL) when
  the end use is a commercial product. This is a real legal/IP risk,
  equivalent in severity to the physical/spend/cost escalation
  triggers elsewhere in this list, not a formality.
- Document provenance for anything adapted: source, license, and what
  was modified. Part of the project's "professionally documented"
  goal, and needed for any future legal/IP review.

## Project structure
See README.md's "Layout" section — kept there instead of duplicated
here to avoid the two going out of sync.

## Current state
(Update this every session)
- Status: **Steps 1 and 2 of the 3-step plan (coder agent alone) are
  cleared.** Two independent `STATUS: PASS` results, on genuinely
  different board/component combinations: PIR+LED/Arduino Uno
  (2026-10-30, session 3) and DHT22/ESP32 DevKitC (2026-10-30, session
  4). That's a real second data point, not just a replay — see below
  for a gap the second run surfaced that still needs closing before
  step 3 starts.
- Last worked on (2026-10-30, session 4): ran
  `python3 agent/coder_agent.py specs/example_dht22_esp32.yaml` —
  different board (ESP32 vs Arduino Uno), different component class
  (DHT22's timed one-wire protocol vs PIR's simple digital read),
  different arduino-cli core (`esp32:esp32`, not preinstalled, unlike
  `arduino:avr`). Real `STATUS: PASS`: compiled for
  `esp32:esp32:esp32`, 273,996 bytes flash (20%), 22,140 bytes RAM
  (6%). Full detail, including disclosed assumptions (GPIO4 data pin,
  external pull-up, 2s power-up delay, output format), in PROGRESS.md.
  **Real gap found:** the agent used the Adafruit DHT sensor library
  and Adafruit Unified Sensor library (correctly preferring an
  established library per rule 6 in `agent/system_prompt.md`) but
  explicitly disclosed it did not check their licenses — it has no
  tool capable of doing so, and `system_prompt.md`'s rule 6 only says
  to prefer known libraries, not to verify or escalate on license.
  The newer CLAUDE.md rule ("mandatory before incorporating anything
  external: check and record its license... escalate, don't silently
  proceed") was never folded into `system_prompt.md` as an actual
  instruction the agent can act on, and the agent has no web-fetch
  tool to do the lookup itself even if instructed. This time it's
  moot — checked manually, both libraries are MIT/Apache-2.0,
  commercial-safe, no escalation needed — but the agent correctly
  disclosing "I couldn't check this" rather than silently passing is
  the one thing that worked; the rule itself is still unenforced by
  the running system. Treat this as real coverage, not resolved.
  **Fixed same session:** added rule 7 to `agent/system_prompt.md` —
  an external library whose license the agent cannot state from what
  it actually knows is now itself a required `STATUS: ESCALATE`,
  never a disclosed-but-passed caveat under `STATUS: PASS`. Not yet
  re-tested against a live run (no spec has been re-run since the
  prompt change) — treat as a design fix made, not a verified
  behavior change, until it's actually exercised.
- **Step 3 scoping in progress (2026-10-30, sessions 5-6) —
  dimensional blocker cleared, two architecture questions remain.**
  Chose the design/3D agent's first task: a mounting bracket for an
  SG90 micro servo (specific part: "Beffkkip 10Pcs SG90", Amazon ASIN
  B08KY49SFX). Wrote `component_reference/sg90_servo.md` (mechanical
  analog of `hardware_reference/*.md`) and
  `docs/design-agent-first-task.md` (scoping notes, not yet a spec).
  Session 5 confirmed the dimensional gap was real (checked multiple
  public SG90 sources — up to ~4mm disagreement on body height, no
  reliable mounting-tab hole spec anywhere). Session 6 closed it: the
  user supplied the exact ordered part's own dimension diagram
  (footprint 31.8x12.5mm, hole-to-hole spacing 22.4mm) and confirmed
  the mounting screw is M3. `component_reference/sg90_servo.md` is now
  "GROUNDED FOR A FIRST DRAFT" — a design agent could draft a
  bracket's footprint and hole layout from it. Only tab thickness
  (affects screw length, not hole layout) is still unmeasured, and it
  doesn't block drafting. Defaults picked earlier, still in force
  (stated as defaults, not firm requirements): FDM 3D-printed output,
  generic flat-panel mount target.
- **Step 3, first real output (2026-10-31, session 7): a first-draft
  SG90 bracket was built live in Fusion 360 and exported.** The user
  wanted native `.f3d` output, which ruled out a headless
  parametric-script approach — confirmed (not assumed) Fusion 360 has
  no headless/batch mode; the only true-headless Autodesk path is the
  separate, billed Forge/APS cloud API. So this had to run as a live
  session with the user's Fusion 360 open, via the Fusion 360 MCP
  connector (account Settings → Connectors → "Autodesk Fusion",
  Desktop type, local port 27182) — a structural fact for this whole
  department's design agent, not a workaround. Getting that connector
  actually connected took real troubleshooting this session (root
  cause never fully pinned down — it started working after the user
  interacted with its Settings page while Fusion was already open;
  see PROGRESS.md for the full sequence). Once connected, built a
  44x24x3mm plate (2 servo holes at 22.4mm spacing + 4 corner
  panel-mount holes, all M3-clearance) via real, doc-verified Fusion
  Python API calls (not memory) and exported it as
  `design/sg90_bracket_v1.f3d`. Full build detail, what was and
  wasn't verified, and the real API facts learned, are in
  `design/sg90_bracket_v1_PROVENANCE.md` and
  `docs/design-agent-first-task.md`.
  **Real gap, same shape as the license-check gap above: the
  numeric self-check didn't actually work.** The build script wrote
  an expected-vs-actual bounding-box check to a `result` variable, but
  the tool never surfaced it — confirmation is visual (a screenshot)
  and file-existence only, not a re-read numeric check. That's the
  "no agent self-certifies" rule not actually being met yet for this
  agent, not a cosmetic issue — see `design-agent-first-task.md` item
  3. **Also unresolved:** this was one ad-hoc interactive build, not
  a repeatable script or an actual `agent/design_agent.py` — turning
  it into either is still unstarted, so step 3 is not yet "proven"
  the way steps 1-2 are (one build, not re-verified, same caveat this
  project applies everywhere else).
- **Design intake form built (2026-10-31, session 7, same day).** The
  user's own concrete problem: translating human measurements/intent
  into something a design agent won't misread is hard, and opening the
  live Fusion MCP connector is expensive, so speculative live sessions
  should be avoided. Built a structured intake form (fillable artifact
  https://claude.ai/artifact/AT84wE1oMH41rXExXD9UBj, exports JSON) —
  required fields (name, description, application, dimensions,
  manufacturing method, budget), optional ones (tolerances, electronics
  components, reference image — explicitly never blocking). Documented
  in `docs/design-intake-form-spec.md`, with a worked example
  (`design_specs/sg90_bracket_request.json`, back-filled from the real
  bracket). That doc defines a two-phase workflow: Phase 0 is a cheap,
  no-Fusion-connector confirmation sketch (demonstrated once this
  session, informally, as the SVG sent to the user) so a
  misunderstood request gets caught before any live CAD session;
  Phase 1 is the live build, only after the user confirms Phase 0.
  Phase 0 is not yet a scripted/repeatable step.
- Next step: close the self-check gap (get a real numeric dimension
  check working, not just visual), decide the FDM hole-tolerance
  policy (still open), build the actual Phase-0 confirmation-sketch
  step (currently manual/informal), and decide whether the design
  agent should be LLM-based or a plain repeatable script before
  writing `agent/design_agent.py` or its system prompt. Separately,
  opportunistically confirm the license-escalation fix (rule 7 in
  `agent/system_prompt.md`) actually fires correctly the next time any
  coder-agent spec exercises an external library.
- Open decisions: see `docs/engineering-department-notes.md`'s "Open
  questions" section (operations department placement, per-department
  spend thresholds, when to build a literal orchestrator agent).

## Environment notes
- Requires `claude-agent-sdk` (pip) and the Claude Code CLI it shells
  out to — confirm `claude --version` works before running the agent.
- Requires `arduino-cli` on PATH for Arduino-target specs, with the
  relevant core installed (see `config/boards.yaml` per-board notes).
- Python 3.10+ (Agent SDK requirement).

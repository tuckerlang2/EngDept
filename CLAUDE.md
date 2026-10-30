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
- **Step 3 scoping started (2026-10-30, session 5), still blocked.**
  Chose the design/3D agent's first task: a mounting bracket for an
  SG90 micro servo (specific part: "Beffkkip 10Pcs SG90", Amazon ASIN
  B08KY49SFX). Wrote `component_reference/sg90_servo.md` (mechanical
  analog of `hardware_reference/*.md`) and
  `docs/design-agent-first-task.md` (scoping notes, not yet a spec).
  **Confirmed the blocker is real, not assumed:** checked multiple
  public sources for SG90 dimensions — they disagree with each other
  by up to ~4mm on overall body height, and none of them give the one
  number a bracket actually needs most (mounting-tab hole diameter
  and hole-to-hole spacing). One datasheet PDF has a real dimensioned
  drawing with the right numbers, but they're unlabeled after text
  extraction and the file isn't downloadable from this environment —
  so rather than guess which unlabeled number is which, the correct
  move was to stop and require a real caliper measurement of the
  actual physical part, same discipline as the coder agent's
  hardware-grounding rule, one level up. Defaults picked for now
  (stated as defaults, not firm requirements — user had no
  preference): FDM 3D-printed output, generic flat-panel mount target.
- Next step: get caliper measurements of the physical servo (see
  `component_reference/sg90_servo.md`'s 5-item measurement list) —
  this is the actual blocker on everything else in step 3. Once that
  file is filled in, resolve the two remaining open design questions
  in `docs/design-agent-first-task.md` (output format — likely an
  OpenSCAD/CadQuery parametric script over a hand-drawn file; and a
  compile-check equivalent for mechanical designs) before writing the
  design agent's actual spec/system prompt. Separately, opportunistically
  confirm the license-escalation fix (rule 7 in `system_prompt.md`)
  actually fires correctly the next time any coder-agent spec
  exercises an external library.
- Open decisions: see `docs/engineering-department-notes.md`'s "Open
  questions" section (operations department placement, per-department
  spend thresholds, when to build a literal orchestrator agent).

## Environment notes
- Requires `claude-agent-sdk` (pip) and the Claude Code CLI it shells
  out to — confirm `claude --version` works before running the agent.
- Requires `arduino-cli` on PATH for Arduino-target specs, with the
  relevant core installed (see `config/boards.yaml` per-board notes).
- Python 3.10+ (Agent SDK requirement).

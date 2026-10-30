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
- Status: **Step 1 of the 3-step plan (coder agent alone) is cleared.**
  Real `STATUS: PASS` achieved 2026-10-30 — `compile_check` actually
  invoked `arduino-cli compile --fqbn arduino:avr:uno` and it
  succeeded (1008 bytes flash, 14 bytes RAM) on the PIR+LED spec, the
  old repo's one historical success, now re-verified in this rebuild.
  One fixed bug stands between this and the prior session: see below.
- Last worked on (2026-10-30, session 3): ran
  `python3 agent/coder_agent.py specs/example_pir_led.yaml` on a real
  Windows machine with `arduino-cli` + `arduino:avr` core installed.
  First run crashed with `UnicodeEncodeError` — `print(text)` in
  `coder_agent.py`'s response loop choked on a non-ASCII character
  (an arrow glyph) because Windows consoles default to cp1252. Fixed
  by adding `sys.stdout.reconfigure(encoding="utf-8")` at the top of
  `main()`. Second run passed cleanly end to end. Full detail,
  including the agent's disclosed assumptions (pin choices, 2Hz blink
  rate, PIR voltage) in PROGRESS.md's 2026-10-30 Session 3 entry.
- Next step: **Step 2 of the 3-step plan** — write and run a second
  spec that is genuinely new (a different board or component than
  PIR+LED), to get a real second data point. One pass on one spec is
  a regression check, not evidence the agent generalizes across
  boards/components. Do not start on the design/3D agent (step 3)
  before this.
- Open decisions: see `docs/engineering-department-notes.md`'s "Open
  questions" section (operations department placement, per-department
  spend thresholds, when to build a literal orchestrator agent).

## Environment notes
- Requires `claude-agent-sdk` (pip) and the Claude Code CLI it shells
  out to — confirm `claude --version` works before running the agent.
- Requires `arduino-cli` on PATH for Arduino-target specs, with the
  relevant core installed (see `config/boards.yaml` per-board notes).
- Python 3.10+ (Agent SDK requirement).

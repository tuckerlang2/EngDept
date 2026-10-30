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
- Status: SDK plumbing verified working (first real run completed
  2026-10-29). Full pipeline still NOT YET VERIFIED — the one run so
  far escalated before reaching `compile_check`'s actual PASS/FAIL,
  because `arduino-cli` wasn't installed in that run environment. The
  old repo's one confirmed-working case (a clean compile) has still
  never been re-verified in this rebuild.
- Last worked on (2026-10-29, session 2): ran
  `python3 agent/coder_agent.py specs/example_pir_led.yaml` for the
  first time. The SDK message-handling code (the thing expected to
  break first) worked correctly end to end — client connected, agent
  called `write_code` then `compile_check` in order, got a real tool
  error, escalated honestly instead of self-certifying. The run
  environment was missing `arduino-cli`, so `compile_check` never
  actually compiled anything; `generated/pir_led.ino` was written but
  is unverified. See PROGRESS.md's 2026-10-29 Session 2 entry for
  full detail, including why `arduino-cli` couldn't be installed in
  that particular sandboxed session (network allowlist, not a project
  issue) — don't let that environment-specific note get mistaken for
  a project blocker in general.
- Next step: in an environment with normal internet access, install
  `arduino-cli` + the `arduino:avr` core, confirm `arduino-cli
  version` and `arduino-cli compile --fqbn arduino:avr:uno <dir>`
  work standalone, then re-run
  `python3 agent/coder_agent.py specs/example_pir_led.yaml` and
  require a real `STATUS: PASS` (meaning `compile_check` itself
  returned PASS, not just that the agent didn't crash). That's the
  actual bar for "the rebuild works," not the code existing or the
  SDK layer behaving — both of those are now true but are not
  sufficient on their own.
- Open decisions: see `docs/engineering-department-notes.md`'s "Open
  questions" section (operations department placement, per-department
  spend thresholds, when to build a literal orchestrator agent).

## Environment notes
- Requires `claude-agent-sdk` (pip) and the Claude Code CLI it shells
  out to — confirm `claude --version` works before running the agent.
- Requires `arduino-cli` on PATH for Arduino-target specs, with the
  relevant core installed (see `config/boards.yaml` per-board notes).
- Python 3.10+ (Agent SDK requirement).

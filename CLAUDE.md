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

## Project structure
See README.md's "Layout" section — kept there instead of duplicated
here to avoid the two going out of sync.

## Current state
(Update this every session)
- Status: scaffold written, NOT YET RUN against the real SDK. This is
  the single most important fact about the project right now — nothing
  below should be read as "working," only as "exists."
- Last worked on: initial build — ported `hardware_lookup.py`,
  `spec_schema.py`, `compile_check.py`, `config/boards.yaml`, and
  `hardware_reference/*.md` unchanged from `embedded-code-gen-agent`;
  wrote `agent/coder_agent.py`, `agent/system_prompt.md`,
  `agent/tools.py` fresh, using the Claude Agent SDK (verified current
  API against the SDK's own README at build time, not from memory).
- Next step: run `python3 agent/coder_agent.py specs/example_pir_led.yaml`
  for the first time. This spec deliberately re-runs the old repo's one
  confirmed-working case (PIR+LED, Arduino Uno) — a pass here is a real
  regression check, not a new unverified claim; a fail tells you
  specifically what the rebuild broke relative to what already worked.
  Expect to need to fix something on first run — the SDK
  message-handling code was written from current docs, not validated
  against a live run.
- Open decisions: see `docs/engineering-department-notes.md`'s "Open
  questions" section (operations department placement, per-department
  spend thresholds, when to build a literal orchestrator agent).

## Environment notes
- Requires `claude-agent-sdk` (pip) and the Claude Code CLI it shells
  out to — confirm `claude --version` works before running the agent.
- Requires `arduino-cli` on PATH for Arduino-target specs, with the
  relevant core installed (see `config/boards.yaml` per-board notes).
- Python 3.10+ (Agent SDK requirement).

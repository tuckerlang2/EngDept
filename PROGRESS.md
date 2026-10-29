# Progress log

Append a new entry every session. Don't delete old entries.

---

## 2026-10-28 — Session 1: rebuild from embedded-code-gen-agent, initial scaffold
- Decision: rebuild rather than extend `embedded-code-gen-agent`'s
  `src/` pipeline. That repo's one real success (Session 2 there: PIR+
  LED on an Arduino Uno, compiled clean) was never re-verified, and its
  one-spec-one-board-one-file architecture couldn't represent the
  rover's two-board shared-protocol case, which is why the rover ended
  up hand-written instead of agent-generated. Rather than keep bending
  that architecture after the fact, started fresh with the eventual
  multi-agent system's needs in mind from the start: headless
  operation, a structured pass/fail/escalate contract an orchestrator
  can consume, and the Claude Agent SDK instead of hand-rolled API
  calls.
- Ported unchanged (already worked, no reason to redo): `hardware_lookup.py`,
  `spec_schema.py`, `compile_check.py`, `config/boards.yaml`,
  `hardware_reference/*.md` (arduino_uno, esp32_devkitc_v4,
  raspberry_pi_4, raspberry_pi_zero_2w).
- Wrote fresh: `agent/coder_agent.py` (headless entry point),
  `agent/system_prompt.md` (the non-negotiable rules + required
  STATUS output format), `agent/tools.py` (the only two actions the
  agent can take: write_code, compile_check). Verified the Claude
  Agent SDK's actual current API (package name, ClaudeSDKClient,
  @tool/create_sdk_mcp_server pattern, message/block class names) from
  the SDK's own README before writing code against it, rather than
  from training-data memory — this project's own non-negotiable rule
  about not inventing hardware facts from memory applied here too, one
  level up (don't invent SDK facts from memory either).
- Wrote `specs/example_pir_led.yaml` as the first test case,
  deliberately matching the old repo's one historical success so a
  result here is a real re-verification, not a new unvalidated claim.
- Wrote `docs/engineering-department-notes.md` capturing the
  architecture discussion (sequencing: coder alone first, then design
  + manufacturing engineering, then business/finance; hub-and-spoke
  coordination through an orchestrator for anything spend/risk-
  relevant; the worked actuator-mechanism example and its real
  dependency chain + missing-prerequisite gap).
- **NOT YET RUN against the real SDK.** This is a first-pass scaffold.
  The SDK message-handling code in `coder_agent.py` was written against
  current documentation but has not been exercised against a live
  Claude Code CLI run — expect to find and fix at least one real issue
  on first execution.
- Next step: `pip install -r requirements.txt`, confirm `claude
  --version` and `arduino-cli` are both available, then run
  `python3 agent/coder_agent.py specs/example_pir_led.yaml` and fix
  whatever breaks. Treat a clean STATUS: PASS on that one spec as the
  actual bar for "the rebuild works" — not the code existing.

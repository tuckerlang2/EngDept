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

---

## 2026-10-29 — Session 2: first real run — SDK plumbing works, run blocked on missing arduino-cli
- Ran `python3 agent/coder_agent.py specs/example_pir_led.yaml` for the
  first time against the real SDK and CLI. `claude-agent-sdk` and
  `pyyaml` were already present; `claude --version` responded (2.1.312)
  and was authenticated.
- **Result: no SDK bug.** Contrary to the stated expectation that the
  first real issue would be in the SDK message-handling code in
  `coder_agent.py`, that code worked correctly end to end on the first
  try: all imports (`AssistantMessage`, `ClaudeAgentOptions`,
  `ClaudeSDKClient`, `ClaudeSDKError`, `TextBlock`,
  `create_sdk_mcp_server`) resolved against the installed SDK, the
  client connected, the agent read the hardware reference grounding,
  called `write_code`, called `compile_check`, received a real tool
  error, and correctly escalated instead of reporting a false PASS.
  This is a genuine (if negative) data point for the rebuild's SDK
  integration — don't re-flag "SDK message handling" as the expected
  first failure point in future sessions; it's been exercised and
  held up.
- **Actual blocker: `arduino-cli` is not installed in the run
  environment.** `compile_check` failed immediately with
  `[Errno 2] No such file or directory: 'arduino-cli'`. This is
  exactly the missing-prerequisite case CLAUDE.md's "Environment
  notes" already called out — it just hadn't been hit yet. Per the
  project's non-negotiable rules, the agent did not self-certify: it
  wrote `generated/pir_led.ino` (gitignored, not committed), reported
  that result as unverified, and ended with `STATUS: ESCALATE` naming
  the specific missing tool — the system worked as designed when it
  hit a real gap.
- Environment note from this session: in the sandboxed agent
  environment this was run in, `arduino-cli` could not be installed —
  its official install script and GitHub-release binaries are both
  outside the environment's network allowlist, and an npm wrapper
  package (`arduino-cli` on npm, which shells out to a downloaded
  binary) was also blocked. `go install
  github.com/arduino/arduino-cli@latest` reached `proxy.golang.org`
  but got an HTTP 403 (policy denial, not a missing-host issue).
  Installing `arduino-cli` from a normal shell with internet access
  (a dev machine, CI runner, or a less restricted container) should
  not hit this; it's specific to that run environment, not a flaw in
  the project.
- Generated sketch (`generated/pir_led.ino`, not committed —
  regenerate by re-running the spec) is plausible on inspection: PIR
  on D2, LED on D13 per the reference doc, non-blocking blink using
  `millis()`, correct rollover-safe subtraction, LED forced off and
  blink timer reset on motion-stop. **Not yet actually compiled or
  verified — this is a read, not a check.** Do not treat this as the
  regression check passing; it hasn't run through `compile_check` at
  all yet.
- Next step (unchanged in substance, now more specific): get
  `arduino-cli` on PATH with the `arduino:avr` core installed in an
  environment with normal internet access, then re-run
  `python3 agent/coder_agent.py specs/example_pir_led.yaml` and
  require an actual `STATUS: PASS` from `compile_check` before this
  counts as a regression check passed. Until then, the rebuild's SDK
  layer is validated but the full pipeline (including the one thing
  the old repo actually proved — a clean compile) is still unverified.

---

## 2026-10-30 — Session 3: real STATUS: PASS on Windows, found and fixed a genuine bug
- Ran on the user's own Windows machine (Python 3.13, `arduino-cli`
  1.5.1, `arduino:avr` core already installed). First end-to-end
  attempt at an actual compile verdict for this rebuild.
- **Bug found (first run): `UnicodeEncodeError` crash — not a hardware
  or SDK-protocol bug.** `coder_agent.py`'s `print(text)` in the
  streaming-response loop crashed the moment the model's reply
  contained a non-ASCII character (an arrow glyph, "→") — a Windows
  console defaults to the cp1252 encoding, which can't encode it.
  This is a more specific version of the bug flagged as most likely
  up front ("SDK message-handling code," not the hardware-grounding
  logic): it's an *output-encoding* bug, not a protocol bug, and it
  happens routinely — any ordinary reply with an em dash, curly quote,
  or arrow triggers it, not just edge-case input. In a headless/
  orchestrator context this crash is indistinguishable from a genuine
  agent failure, so it had to be fixed at the source, not worked
  around per-call.
- **Fix applied and committed:** `sys.stdout.reconfigure(encoding=
  "utf-8")` at the top of `main()` in `agent/coder_agent.py`, forcing
  UTF-8 stdout regardless of the host console's default codepage.
- **Second run, with the fix: a real `STATUS: PASS`.** Exit code 0.
  `compile_check` actually invoked `arduino-cli compile --fqbn
  arduino:avr:uno` and it succeeded: 1008 bytes flash, 14 bytes RAM.
  This is the bar Sessions 1–2 couldn't clear — not "the agent ran
  without crashing" but a genuine compiler PASS. **First time this
  rebuild has cleared that bar.** It reproduces the old
  `embedded-code-gen-agent` repo's one historical success (PIR+LED on
  Uno), so this is a real regression check passed, not a new
  unverified claim.
- Generated sketch used D2 for the PIR input and the Uno's built-in
  LED (D13) for output rather than an external LED — reasonable since
  the spec didn't pin an LED pin, but worth noting for anyone
  physically wiring this up: an external LED on D13 would be
  redundant with the onboard one, not required to see the behavior.
  Agent-disclosed assumptions, not independently re-verified here:
  motion → 2 Hz blink while detected, solid off when motion stops;
  PIR assumed 5V-compatible since the spec didn't name the part.
- Nothing flashed to physical hardware — compile-only, as required.
- **The primary coder agent has now cleared step 1 of the 3-step
  plan.** Per the project's sequencing discipline, next is step 2 — a
  second, genuinely different spec (different board or component) —
  before this counts as "generalizes," not just "this one case still
  works."

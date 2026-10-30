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

---

## 2026-10-30 — Session 4: second data point (ESP32+DHT22) — real PASS, real gap found
- Wrote `specs/example_dht22_esp32.yaml`: ESP32 DevKitC V4 + DHT22,
  deliberately different from Session 3's case on every axis that
  matters — different board, different component class (DHT22's timed
  one-wire digital protocol vs PIR's simple active-high digital
  input), different arduino-cli core (`esp32:esp32`, which
  `config/boards.yaml` already notes is not installed by default,
  unlike `arduino:avr`).
- Ran on the same Windows machine, after installing the `esp32:esp32`
  core and the `DHT sensor library` + `Adafruit Unified Sensor`
  Arduino libraries. Clean run, no retries needed.
- **Result: real `STATUS: PASS`.** `compile_check` invoked
  `arduino-cli compile --fqbn esp32:esp32:esp32` and it succeeded:
  273,996 bytes flash (20%), 22,140 bytes RAM (6%). Generated sketch
  `esp32_dht22_serial.ino` reads the DHT22 on GPIO4 every 5s and
  prints over serial at 115200 baud. Nothing flashed to hardware.
- **This is the real second data point step 2 called for.** Two
  independent passes on genuinely different board/component
  combinations — not a second run of the same case — is actual
  evidence the rebuild's grounded-codegen + compile-check loop
  generalizes, not just that it memorized one known-good case.
- Agent-disclosed assumptions (not independently re-verified here):
  GPIO4 for the DHT22 data pin (reference lists it as safe
  general-purpose, not strapping/flash/input-only); DHT22 powered
  from 3.3V per the board's logic-level note; an external 4.7k-10k
  pull-up on the data line (not in the hardware reference — agent
  sourced this from "typical datasheets" per the spec's own note, a
  reasonable but unverified-by-us assumption); 2s power-up delay
  before first read; "Temperature: X.X C, Humidity: Y.Y %" serial
  output format.
- **Real gap found, worth tracking as its own item, not just a
  footnote:** the agent correctly preferred an established library
  (Adafruit DHT sensor library, which depends on Adafruit Unified
  Sensor) over hand-rolling the one-wire timing protocol itself — that
  part of `agent/system_prompt.md` rule 6 worked as intended. But the
  agent explicitly disclosed it did **not** check either library's
  license, and said so plainly rather than silently proceeding or
  fabricating a license claim — that disclosure is good behavior. The
  underlying problem: CLAUDE.md's newer non-negotiable rule
  ("mandatory before incorporating anything external: check and
  record its license... escalate, don't silently proceed") was never
  folded into `agent/system_prompt.md` as an instruction the agent
  can actually act on, and the agent has no web-fetch or license-
  lookup tool even if it were instructed to check. So the rule exists
  in the project's docs but isn't enforced by the running system yet.
  Checked the two licenses manually for this session: DHT sensor
  library (adafruit/DHT-sensor-library) is MIT; Adafruit Unified
  Sensor (adafruit/Adafruit_Sensor) is Apache-2.0. Both permissive,
  no commercial-use or copyleft conflict — so no escalation was
  actually warranted here, but that was luck/manual follow-up, not
  something the system itself verified or would have caught if the
  license had been GPL or CC BY-NC instead.
- **Fixed same session:** added rule 7 to `agent/system_prompt.md`:
  "Any time you use an external library (rule 6), you must state its
  license... if you cannot state it from what you actually know, that
  is itself a STATUS: ESCALATE condition... Do not report STATUS:
  PASS with an unverified license disclosed as a caveat." This closes
  the gap this session found — the agent has no license-lookup tool,
  so the fix can't make it verify a license itself, but it does make
  "I can't verify this" a hard stop instead of a footnote.
  **Not yet re-verified against a live run** — no spec has been
  re-run since this prompt edit. Don't treat this as a confirmed
  behavior change until the next run that actually uses an external
  library exercises it (either a correct disclosure or a correct
  escalation).
- Next step: move to **step 3** — start scoping the design/3D agent
  (first blocker per the original plan: no existing CAD model or
  measured physical envelope of anything it would design against yet
  — figure out the first real design task and what data it needs
  before writing that agent's spec). Opportunistically confirm rule 7
  fires correctly the next time any spec pulls in an external
  library, rather than assuming the prompt edit alone is proof.

---

## 2026-10-30 — Session 5: design/3D agent — chose first task, confirmed real blocker
- Chose the design/3D agent's first task: a mounting bracket for an
  SG90 micro servo, the specific part in a 10-pack the user has/is
  getting ("Beffkkip 10Pcs SG90 9g Micro Servos", Amazon ASIN
  B08KY49SFX). Reasoning: cheap, common, will recur in this project's
  eventual drone/robotics work, and simple enough (one part, one
  mounting interface) to prove the architecture the same way PIR+LED
  was a deliberately simple first case for the coder agent.
- **Did not take the "no existing CAD model/measured envelope"
  blocker on faith — checked it.** Searched for and read multiple
  public SG90 sources:
  - [TAMS Uni-Hamburg SG90 datasheet](https://tams.informatik.uni-hamburg.de/lehre/2023ss/vorlesung/es/doc/sg90.pdf): 22.2 x 11.8 x 31mm, 9g
  - [TowerPro SG90 listing](https://skycraftsurplus.com/products/towerpro-sg90-micro-servo-arduino-compatible.html): 23.1 x 12.2 x 29.0mm, 9.0g
  - A T-Pro Mini SG-90 listing: 22.0 x 11.5 x 27mm, 9g
  - [ProtoSupplies SG90/MG90 bracket listing](https://protosupplies.com/product/sg90-mg90-servo-bracket/): gives their own bracket's cutout size, not the servo's own tab dimensions
  - A [kjell.com datasheet PDF](https://www.kjell.com/globalassets/mediaassets/701916_87897_datasheet_en.pdf) that does have a real dimensioned drawing (confirmed: "Dimensions are in millimeters," with numbers 22.8, 32.0, 26.7, 15.6, 12.4, 15.8, 14.2, 7.7, 2.54 present) -- but the labels didn't survive PDF text extraction, and the file couldn't be downloaded from this sandboxed environment to inspect visually (host not reachable through the egress proxy).
  - Result: **confirmed real disagreement between sources** (up to
    ~4mm on overall height) and **confirmed the mounting-tab hole
    diameter/spacing — the number a bracket design needs most — isn't
    reliably available from any source checked.** This is not a
    theoretical gap; it's a verified one.
  - Correct call given that: don't guess which unlabeled drawing
    number is the hole spacing. Require an actual caliper measurement
    of the physical part instead. Same principle as the coder agent's
    hardware-grounding rule (never invent a pin/voltage from memory),
    one level up, applied to a mechanical fact instead of an
    electrical one.
- Wrote `component_reference/sg90_servo.md` — mechanical analog of
  `hardware_reference/*.md`. Holds the body-envelope source table,
  flags the missing tab/hole/horn numbers explicitly, and lists the
  exact 5 measurements needed (body L/W/H, tab hole diameter,
  hole-to-hole spacing, tab thickness, horn height from base) with
  the instruction not to use this file to ground a design agent until
  those are filled in.
- Wrote `docs/design-agent-first-task.md` — scoping notes (explicitly
  not yet a spec, mirroring but distinct from
  `docs/primary-coder-agent-spec.md`'s format). Records: the chosen
  task and why; two defaults picked since the user had no preference
  (FDM 3D-printed output; generic flat-panel mount target for this
  first case, since no specific frame/chassis exists yet); three
  things still undecided even after the measurement blocker clears
  (output file format -- likely an OpenSCAD/CadQuery parametric
  script, not a hand-drawn file, to keep with this project's
  code-not-binary instinct, but not yet confirmed as scriptable
  headlessly; a compile-check equivalent for mechanical designs --
  likely dimension-conformance + mesh-validity checks, not yet
  designed; an FDM hole-tolerance policy, since printed holes need to
  be oversized slightly to actually fit screws).
- Also flagged but not resolved: whether this task even needs an
  LLM-based agent at all, or whether a simple parametric script
  suffices for a first bracket -- worth asking explicitly before
  building an Agent-SDK-based design agent by default just because
  that's the pattern the coder agent used.
- Next step: measure the physical servo once it's in hand (see the
  5-item list in `component_reference/sg90_servo.md`) and fill that
  file in. That's the actual blocker on everything else in step 3 --
  the output-format and verification-gate questions in
  `docs/design-agent-first-task.md` are real but secondary; don't
  spend more time on them until the measurement exists.

---

## 2026-10-30 — Session 6: dimensional blocker on SG90 bracket cleared
- User supplied the exact ordered part's own dimension diagram
  (Beffkkip-branded, same ASIN as the part recorded in Session 5) --
  a real source specific to the actual servo, not a cross-manufacturer
  aggregate. Read off it: overall case height 32mm, case width 12.5mm,
  **mounting tab hole-to-hole spacing 22.4mm** (the number that was
  missing from every public source checked in Session 5), overall
  footprint 31.8mm long. Two sub-height figures (18mm/25mm) split the
  32mm total between the upper gearbox housing and main body, but
  which label is which isn't fully certain from the image -- doesn't
  block the bracket, since footprint + hole spacing are what matter
  for mounting.
- Mounting tab hole diameter was still missing after the diagram (it
  doesn't show hole size). Checked whether a public source could fill
  this in before accepting anything from the user without a check --
  an Arduino forum thread on this exact question had posters
  disagreeing from "just under 2mm" to "M3," and conflated horn screws
  with tab screws. Not usable. **User then directly confirmed the
  mounting screw is M3.** Recorded that as the working value, with a
  derived (not measured) clearance-hole sizing note (~3.2-3.4mm is
  standard practice for an M3 clearance fit) for the bracket's own
  mating holes.
- `component_reference/sg90_servo.md` status upgraded from
  "INCOMPLETE -- do not use to ground a design agent yet" to "GROUNDED
  FOR A FIRST DRAFT." Only remaining physical gap: tab thickness
  (affects screw length, not hole layout -- doesn't block drafting a
  bracket design).
- Updated `docs/design-agent-first-task.md`'s status accordingly: the
  blocker on writing an actual design-agent spec is no longer physical
  data, it's the two architecture questions already identified in
  Session 5 (output file format; a compile-check equivalent for
  mechanical designs) plus whether this first task even needs an
  LLM-based agent versus a plain parametric script.
- Next step: resolve those two (three, counting the LLM-vs-script
  question) open design questions. Tab thickness can be measured in
  parallel whenever the physical part is in hand; it's not on the
  critical path anymore.

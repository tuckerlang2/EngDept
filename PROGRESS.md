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

## Session 7 (2026-10-31) — Fusion 360 MCP connector working; first
SG90 bracket built and exported live

### Fusion 360 MCP connector troubleshooting
User asked to just keep Fusion 360 open so its MCP connector would
work. That alone didn't fix it — the connector (`fusion_mcp_*` tools,
proxied through the device bridge) stayed in a "failed"/"Connection
closed" state with Fusion open. Ruled out: `RefreshMcpTools` (only
manages top-level session MCP servers, not device-bridge-proxied
local ones); an account-level connector (another Claude session's
`ListConnectors`/`SearchMcpRegistry` found nothing, consistent with
this being a Desktop-type connector, not Web-type — confirmed via two
screenshots of Settings -> Connectors: "Autodesk Fusion," Desktop
type, enabled, port 27182, 4 tools always-allowed). Root cause never
definitively pinned down — the connector spontaneously started
working (state "announced," 4 tools available) right after the user
viewed/interacted with its Settings detail page while Fusion was
already open. Treat "keep Fusion open + the connector shows enabled
in Settings" as necessary but not confirmed sufficient on its own.

### Fusion Python API facts learned (via `fusion_mcp_read`
queryType "apiDocumentation" -- real doc queries, not memory, same
grounding discipline as `hardware_reference/*.md` on the electronics
side)
- Script entry point must be `def run(context):`; a bare top-level
  script fails with `NameError: name 'run' is not defined`.
- `context` passed into `run()` is `None`, not a dict -- can't do
  `context['result'] = ...`.
- `Document.name` is settable; the *root component's* `.name` is not
  (`RuntimeError: 3 : root component name cannot be changed`).
- `Point3D.create(x, y, z)` coordinates are centimeters (Fusion's
  internal model-space unit), not mm -- `ValueInput.createByString('3
  mm')` is the safer way to pass a dimensioned value.
- A sketch's auto-generated `profiles` collection gives one profile
  per closed region; a rectangle containing N circles yields N+1
  profiles (the "rectangle minus all holes" compound one, identified
  via `profile.profileLoops.count == N+1`, plus N tiny circle-interior
  ones) -- select the compound one to extrude.
- `ExportManager.createFusionArchiveExportOptions(path)` +
  `ExportManager.execute(options)`, off
  `adsk.fusion.Design.cast(app.activeProduct).exportManager`, is the
  real API for writing a `.f3d` file to disk.
- Closing a `Document` via `doc.close(False)` invalidates that Python
  object immediately -- reading `.name` or any other property on it
  afterward raises `RuntimeError: 4 : An API Object refers to a
  deleted Object`. Capture anything needed before closing.

### What was built
A first-draft SG90 servo mounting bracket, grounded entirely in
`component_reference/sg90_servo.md`: 44x24x3mm flat plate, two servo
mounting holes at the confirmed 22.4mm center spacing (3.4mm
diameter, M3 clearance), four corner panel-mount holes inset 4mm from
each edge (3.4mm diameter, M3 clearance). Built via 3 rounds of real,
live script execution against the Fusion MCP connector -- first two
attempts failed on real errors (missing `run()` wrapper; then the
root-component-rename error, which cascaded into a second error from
assuming `context` was a dict), third attempt succeeded. Verified
visually via an isometric screenshot (plate with exactly 6 holes,
matching the design) and exported to
`design/sg90_bracket_v1.f3d` (75,584 bytes, confirmed via direct
filesystem check -- not zero-byte, not a failed write). Three empty
"Untitled" documents left behind by the two failed attempts (each
one's `app.documents.add()` succeeded before the later error) were
closed without saving as part of the same cleanup script, so they
don't clutter the user's live Fusion session. Full design detail and
provenance in `design/sg90_bracket_v1_PROVENANCE.md`.

### Real gap found (same shape as Session 4's license-check gap):
the self-check didn't actually surface
The build script wrote an expected-vs-actual bounding-box check
(converting Fusion's internal cm units to mm) into a `global result`
string, mirroring the text-output capture convention used earlier
this project -- but the MCP tool's response `message` field came back
empty both times this was tried (the original build, and the
separate cleanup/export run). So the 44x24x3mm dimensions are
confirmed by screenshot and by the exported file's non-zero size, but
**not by an actual re-read numeric check**. This is a real instance
of the "no agent self-certifies" rule not being met in practice for
this task, not a hypothetical concern -- flagged as item 3 in
`docs/design-agent-first-task.md`, needs a genuinely different
verification path (e.g. a separate read-only script/query) before
step 3 can claim the same rigor steps 1-2 have.

### Architecture conclusion
Fusion 360 has no headless/batch mode (confirmed via research this
session -- the only true-headless Autodesk option is the separate,
billed Forge/APS Design Automation cloud API, a different product).
A `.f3d`-producing design agent can therefore never be a
cloud-headless, orchestrator-callable component the way the coder
agent is -- it must always run as a live session with the user's
Fusion 360 open and its MCP connector connected. This is now a fixed
structural fact for this department, recorded in
`docs/design-agent-first-task.md`, not an open question.

### What's still not done
This was one ad-hoc interactive build -- iterating by hand through
real API errors against a live connector -- not a saved, re-runnable
script, and not an actual `agent/design_agent.py` with its own system
prompt analogous to the coder agent's. Treat step 3 as "a first real
output exists," not "proven" -- same standard this project has
applied to the coder agent itself (one undocumented past success
isn't an ongoing guarantee). Next step: close the self-check gap,
decide the FDM hole-tolerance policy (still open from Session 5-6),
then decide LLM-agent-vs-plain-script before writing
`agent/design_agent.py`.

## Session 7 continued (2026-10-31) — design intake form + two-phase
workflow (motivated by the user's own token-efficiency concern)

User's real problem, stated directly: translating human
measurements/intent into something an LLM design agent won't
misread is hard, they're not confident in their own ability to
explain designs precisely, and opening the live Fusion MCP connector
is assumed to be token/attention-expensive, so they want to avoid
doing that speculatively.

Built a structured intake form as a fillable artifact
(https://claude.ai/artifact/AT84wE1oMH41rXExXD9UBj) that exports a
JSON `design_request` document -- the same role `specs/*.yaml` plays
for the coder agent. Required fields: project name, general
description, application/context, at least one hard dimension,
manufacturing method, budget. Explicitly optional and non-blocking,
per direct instruction: a reference photo/drawing field -- encouraged
in the form's own copy (this session's own SG90 bracket work is the
proof: the product dimension diagram, not prose, is what actually
closed that dimensional blocker) but never required.

Documented the form and, more importantly, the workflow it enables in
`docs/design-intake-form-spec.md`:
- **Phase 0 (cheap, no live Fusion connector):** design agent reads
  the filled JSON, grounds components against
  `component_reference/*.md`, and sketches back what it understood
  (a dimensioned diagram plus a short restatement) for the user to
  confirm or correct -- exactly the kind of SVG sketch sent to the
  user earlier this session for the already-built SG90 bracket,
  generated from reasoning alone with zero live CAD tool calls.
- **Phase 1 (live build):** only happens after the user confirms
  Phase 0. This is the actual fix for the stated concern -- a
  misunderstood request gets caught before any live, presumably
  expensive Fusion session, not after.

Back-filled a worked example, `design_specs/sg90_bracket_request.json`,
from the real SG90 bracket data (dimensions, M3 confirmation, output
file) -- explicitly marked as retroactive, since the form didn't
exist when that bracket was actually built. Doing this surfaced a
real gap: the bracket build never had a stated budget, which the new
form would now require -- noted directly in that file's `notes`
field rather than silently backfilling a number.

### What's still not real yet
- Nothing in the repo consumes `design_specs/*.json` automatically --
  no `design_agent.py`, no schema validator analogous to
  `agent/spec_schema.py`.
- Phase 0 ("confirmation sketch before live Fusion") is a described
  workflow and one informal demonstration, not a scripted, repeatable
  step with a defined output format or an escalation rule for when
  the user's correction and the agent's understanding still don't
  converge.
- The form's own required-field enforcement is JS-only, not backed by
  anything a design agent could re-validate.

Updated `CLAUDE.md` current state and `docs/design-agent-first-task.md`
accordingly.

## Session 7 continued again (2026-10-31) — local project library

User wants a durable local library: one folder per completed/in-
progress project (so a project can actually be referenced, rebuilt,
or improved later instead of its files being scattered), plus a
separate place to cache externally-sourced electronics/mechanical
designs the agent is asked to go find -- with a hard requirement that
even when the actual file can't legally be cached, a link or the
search query that found it gets saved so it's findable again.

Designed and documented in `docs/library-spec.md`:
- `library/projects/<slug>/` -- one folder per project:
  `design_request.json`, the output file(s), `PROVENANCE.md`, and a
  `metadata.yaml` (slug, status, tags, summary, outputs,
  related_components, open_items) for lightweight findability without
  building a database ahead of what's proven.
- `library/reference/<slug>/` -- externally-sourced designs, each
  with `source_url`, `search_terms_used` (the actual query, so it's
  findable even if the link dies), `license` + `license_confirmed`
  (mandatory -- reuses the existing non-commercial/copyleft escalation
  rule directly), and `local_file` (the cached design, or null +
  reason when the license doesn't permit caching it). No entries yet
  -- this is a documented convention, not yet exercised.
- `design_specs/` is now explicitly the inbox (freshly generated
  intake-form JSON, not yet a real project); a project gets promoted
  out of the inbox into `library/projects/` once there's real output
  worth keeping. No automated promotion tool -- manual `git mv` each
  time, same as everything else here until it's proven.

Promoted the SG90 bracket as the first (retroactive) example:
`git mv`'d `design/sg90_bracket_v1.f3d`,
`design/sg90_bracket_v1_PROVENANCE.md` (-> `PROVENANCE.md`), and
`design_specs/sg90_bracket_request.json` (-> `design_request.json`)
into `library/projects/sg90-servo-bracket/`, added its
`metadata.yaml`. Updated path references in `CLAUDE.md`,
`docs/design-agent-first-task.md`, and
`docs/design-intake-form-spec.md` accordingly. Left PROGRESS.md's own
earlier entries pointing at the old paths unchanged -- this is an
append-only log of what happened at the time, not something to
rewrite when a layout changes later.

### What's still not real
`library/reference/` has zero entries -- the actual test of that
half of this design is the next time the agent is asked to go find
an existing drone-frame or electronics design, not before. No search/
catalog tool beyond `ls`/`grep` across `library/`.

## Session 8 (2026-11-01) — real second design request: moisture sensor
bracket, grounding gap found and escalated (not built)

User saved a real new design request to `design_specs/moistureSensorDroneMount`
via the intake form workflow -- the actual second data point step 3
needed (not a backfill like the SG90 bracket). Project: a bracket
holding an Icstation resistive soil moisture sensor (2-probe,
"Resistive Soil Moisture Meter... Corrosion Resistant Probe") so it
clips/slides into a channel, eventually mounted to a linear actuator
on a ground drone to push probes into soil -- explicitly scoped by
the user to "only building the first bracket now" (not the
actuator-mount interface yet).

Read the two attached reference images (real Amazon listing
screenshots for this exact part, not generic photos) by extracting
them from the request's embedded base64 and viewing them via the
device bridge. They confirmed real electrical/probe specs (DC
3.3-12V, probe length 8.8cm, ~5mm probe pitch, driver board
36x15x6mm) but -- critically -- neither image shows the black sensor
housing's own width/diameter/cross-section, which is the one
dimension that actually matters for a slide-in channel or clip. The
request's own `dimensions` field (bracket width 13mm, length 50mm)
describes the requester's guess at the bracket, not a measured
housing fact.

**This is the same shape of gap the SG90 bracket had, and it was
handled the same way: documented, not guessed past.** Wrote
`component_reference/icstation_soil_moisture_sensor.md` (status:
INCOMPLETE, same template as `sg90_servo.md`) recording what's
confirmed vs. missing, with real provenance (the two screenshots).
Sent the user a diagram showing exactly what's grounded (probe pitch,
mounting-hole spec) vs. what isn't (the channel geometry), instead of
proceeding to a live Fusion build on an ungrounded guess.

### Why this matters for the project, not just this part
This is a real, unprompted exercise of the project's core rule --
never invent a mechanical dimension from a guess or an unclear
photo -- on a genuinely new request, not a revisit of the SG90 case.
Also the first real test of the intake-form -> design_specs/ ->
session pipeline end to end: it worked. The form's required fields
(dimensions, application, budget) were all present and usable; the
gap was in what the fields *contained* (requester's own estimate
vs. measured fact), which is exactly the kind of thing Phase 0 is
for catching before Phase 1.

### What's still open
- Waiting on either a caliper measurement of the housing or a clear
  end-on photo with a size reference, same resolution path that
  worked for the SG90 bracket.
- No build has happened for this part. `design_specs/moistureSensorDroneMount`
  is unchanged -- nothing promoted to `library/` yet, correctly, since
  there's nothing real to promote.
- The file itself has no extension and isn't named per the
  `<slug>_request.json` convention used elsewhere -- cosmetic, not
  blocking, worth tidying whenever it's touched next.

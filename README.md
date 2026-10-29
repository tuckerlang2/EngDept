# Primary coder agent

The first agent in an eventual multi-agent "engineering department"
(coder → design → manufacturing engineering, later test/review agents),
itself the first department in an eventual multi-agent company. See
`docs/engineering-department-notes.md` for how this fits the larger plan.

## What this is, and isn't

A **headless** coding agent: given a structured hardware spec, it
generates Arduino/Raspberry Pi code grounded in real hardware reference
data, verifies it compiles, and returns a machine-parsable result --
callable by an orchestrator (or by hand, for now) with no human in the
loop during the run itself.

It is a rebuild, not a copy, of `embedded-code-gen-agent`'s `src/`
pipeline from a sibling project. That repo's agent code was written but
only run once (a single Arduino Uno PIR+LED example) and never
re-verified; everything in `rover/` there was hand-written specifically
*because* that pipeline couldn't represent a multi-board spec. This repo
starts over with: the Claude Agent SDK instead of hand-rolled API calls,
a structured pass/fail/escalate contract an orchestrator can consume
without parsing prose, and the same non-negotiable safety rules ported
forward rather than re-derived from scratch.

**This agent does not decide what to build, test its own work beyond a
compile check, or touch physical hardware.** Those stay separate --
see `docs/primary-coder-agent-spec.md` for the full scope contract.

## Layout
```
agent/
  coder_agent.py      - headless entry point (python3 coder_agent.py specs/some_spec.yaml)
  system_prompt.md     - the agent's non-negotiable rules + output contract
  tools.py              - the only two things the agent can do: write_code, compile_check
  hardware_lookup.py    - loads hardware_reference/*.md for a board (ported, unchanged)
  spec_schema.py         - structured spec format (ported, unchanged)
  compile_check.py        - arduino-cli / python syntax checking (ported, unchanged)
config/
  boards.yaml          - board registry (ported, unchanged)
hardware_reference/*.md - pinouts/logic levels/notes per board (ported, unchanged)
specs/
  example_pir_led.yaml - first test case, deliberately re-running the old
                          repo's one confirmed-working example as a real
                          regression check, not a new unverified claim
docs/
  primary-coder-agent-spec.md     - the full scope/contract spec
  engineering-department-notes.md - how this fits the larger department/company plan
generated/             - agent output lands here (gitignore this)
PROGRESS.md             - session log, same discipline as the sibling repo
```

## Setup
```bash
pip install -r requirements.txt
```
The Claude Agent SDK shells out to the Claude Code CLI under the hood --
confirm it's installed and authenticated (`claude --version`) before
running the agent, or you'll hit `CLINotFoundError`.

For Arduino-target specs, `arduino-cli` must also be installed and on
PATH, with the relevant core installed (see `config/boards.yaml` for
per-board notes, e.g. the ESP32 core isn't bundled by default).

## Running it
```bash
cd agent
python3 coder_agent.py ../specs/example_pir_led.yaml
```
Exit code 0 = `STATUS: PASS`. Nonzero = `STATUS: ESCALATE` or
`STATUS: FAIL_RETRY_EXCEEDED` -- read the printed status block for the
specific question or error; an orchestrator should do the same rather
than treating "nonzero" as a single undifferentiated failure mode.

**NOT YET RUN against the real SDK** -- this is a freshly-written
scaffold. First real task: run the command above, fix whatever the
first real execution surfaces (SDK message-handling details were
written from current docs, not from a live test), and treat a clean
PASS on `example_pir_led.yaml` as the actual bar for "the rebuild
works," not just "the code was written."

## Adding a new board
1. Add an entry to `config/boards.yaml`.
2. Write `hardware_reference/<board>.md` -- pinouts, logic level, any
   peripheral-specific notes. This is the single highest-leverage file
   for reliability; don't skip it or let the agent fall back to
   generating without it.

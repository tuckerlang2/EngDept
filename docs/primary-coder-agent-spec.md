# Primary Coder Agent — Spec v1

Template for the first agent in the multi-agent company (coders → 3D
design → finance/marketing/ops/manufacturing). Prove this one works
solo before building the teacher/editor or test/simulation agents
around it — don't build the ensemble before one member is proven.

## Role (one line)
Generates embedded/software code from a structured spec, grounded in
real hardware reference data. Nothing else.

## Scope — hard boundaries
**In scope:**
- Generate code from a structured spec (board, sensors/actuators, IO
  requirements, goal) — this repo's `spec_schema.py`, extended for
  multi-board/shared-protocol specs when that work gets prioritized.
- Ground every pin/voltage/protocol claim in `hardware_reference/*.md`
  — never from model memory. This is the #1 reliability lever; it
  doesn't get relaxed as scope grows.
- Iterate against compiler/test errors handed back by the test/
  simulation agent.

**Explicitly out of scope** (so scope doesn't silently creep):
- Deciding *what* to build — that's upstream of this agent (you, or a
  future product/ops role).
- Flashing to real hardware — human-gated, non-negotiable, same rule
  this repo already enforces.
- Mechanical/3D design — separate agent.
- Writing or grading its own tests — the test/simulation agent's job.
  A coder that verifies its own work is a coder grading its own
  homework; keep this a hard separation of duties.
- Talking directly to finance/marketing/ops/manufacturing agents —
  routed through the orchestrator, not peer-to-peer.

## Inputs (contract)
- A structured spec in the existing schema format.
- The specific `hardware_reference/*.md` doc(s) `hardware_lookup.py`
  selects for the target board(s). The agent is not permitted to
  answer a pin/voltage question from general knowledge if the doc
  doesn't cover it — see escalation triggers below.

## Outputs (contract)
- Generated code file(s).
- A short manifest alongside it: which hardware_reference docs were
  used, and an explicit line for every place the spec was ambiguous
  and the agent had to assume something ("assumed X because spec
  didn't specify Y") — same discipline this repo's own PROGRESS.md
  already uses, applied automatically instead of relying on a human
  session to think to write it down.

## Verification gate (mandatory)
- Every output goes through the test/simulation agent (compile-check
  / simulated-run loop) before being marked ready for human review.
  Primary coder cannot self-certify.
- On failure: loop with the returned error, same pattern as
  `compile_check.py`'s existing loop. Cap retries (e.g. 3) — past
  that, escalate to a human/teacher-agent rather than looping
  silently and burning calls on a problem it can't solve alone.

## Escalation triggers — stop and ask, don't guess
- Spec is ambiguous or contradictory on anything safety- or
  cost-relevant (mirrors the existing rule: ambiguous + expensive to
  redo = ask first, don't proceed on a guess).
- A pin/voltage/logic-level the spec needs isn't covered in
  `hardware_reference` for the target board — flag the doc gap, don't
  fall back to parametric knowledge. A missing reference doc is a
  data problem to fix, not a prompt to improvise around.
- Anything touching physical actuation or flashing — always hands off
  to a human, no exceptions, same as this repo's existing rule.

## Relationship to other agents (once built — not yet)
- **Teacher/editor coder(s):** review for maintainability/style — a
  different lens than "does it compile," not a duplicate of the
  verification gate.
- **Test/simulation coder:** owns pass/fail. Primary coder's output is
  not "done" until this agent says so.
- **Orchestrator:** assigns specs, routes escalations and failures,
  tracks status. Primary coder doesn't talk to any other role agent
  directly.

## Success criteria — how to know this is actually working
Not vibes. Concretely: given a new, previously-unseen single-board
spec, the agent produces code that compiles clean within the retry
cap, citing the correct hardware_reference doc, with zero human
pin/voltage corrections needed. Re-run this test periodically — the
gap already identified in this project is that the one past success
(Session 2, PIR+LED on an Arduino Uno) was never re-verified, so
there's exactly one data point for "does this actually work,"
collected months ago.

## Sequencing note
Build and prove this agent alone first. Don't stand up teacher/editor
or test/simulation agents, let alone 3D design, finance, marketing,
ops, or manufacturing agents, until this one has a real track record
(multiple specs, multiple boards, re-verified — not one historical
run). An ensemble built on top of one unproven component just moves
the debugging cost from "cables and USB hubs" to "agent handoffs,"
with less visibility into what actually broke.

## Implementation status (this repo)
A first-pass implementation of this contract exists in `agent/` --
`coder_agent.py` (headless entry point), `system_prompt.md` (rules 1-5
above encoded as the agent's instructions), `tools.py` (write_code +
compile_check, the only two actions available). NOT YET RUN against
the real SDK -- see the repo README for the first real test to run.

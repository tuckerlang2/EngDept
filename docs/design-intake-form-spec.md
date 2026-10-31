# Design intake form — spec (2026-10-31, session 7)

Plays the same role for the design agent that `specs/*.yaml` plays for
the coder agent: a structured input the orchestrator and design agent
can actually act on, instead of free-form prose. Built in response to
a real problem this session surfaced directly — translating human
intent/measurements into something an LLM-driven design agent won't
misread or invent dimensions around is genuinely hard, and the one
thing that actually worked (the SG90 bracket) worked because the user
supplied an explicit dimensioned diagram, not a verbal description.

The form itself (fillable page, not yet wired to anything
executable): https://claude.ai/artifact/AT84wE1oMH41rXExXD9UBj

## Why a form instead of a YAML file by hand
The coder agent's spec format (YAML) works because board/sensor specs
are inherently structured. A design request mixes hard numbers (must
be exact), prose (intent, application, constraints), and an optional
image — awkward to hand-author as YAML, natural as a form with
labeled fields. The form exports the same kind of structured document
(JSON) that a design agent would actually consume; the form is the
authoring UI, the JSON is the artifact that matters.

## Fields (required vs. optional, and why)
- **Project/part name, general description, application &
  context — required.** The orchestrator needs these to make
  scope/routing decisions; a design request with no stated
  application can't be evaluated for reasonableness or escalated
  correctly.
- **Hard dimensions — required, at least one.** This is the
  non-negotiable grounding data — same principle as
  `hardware_reference/*.md` for the coder agent. A design request
  with zero stated dimensions is exactly the "agent invents facts
  from memory" failure mode this project exists to prevent.
- **Tolerances — optional but recommended.** If left blank, the
  design agent must pick a default and flag it explicitly (mirrors
  the existing "disclose every assumption" discipline), not silently
  assume precision-fit.
- **Manufacturing method & budget — required.** Both materially
  change the design (wall thickness minimums, hole tolerance,
  achievable geometry) — same reasoning as
  `docs/design-agent-first-task.md`'s existing manufacturing-method
  default discussion, now made a required input instead of a
  standing default picked for the user.
- **Electronics/components involved — optional.** Not every design
  has them (a pure structural bracket might not need anything beyond
  dimensions), but when present this is exactly the list the agent
  should ground against `hardware_reference/*.md` /
  `component_reference/*.md` rather than guessing.
- **Reference photo/drawing — optional, explicitly never blocking.**
  Deliberately not required, per direct instruction: don't make
  people who can't draw well stall here. But the form actively
  encourages it, because this session's own experience is the proof
  of why — a dimensioned product diagram is what actually closed the
  SG90 bracket's dimensional blocker, after multiple rounds of
  inconsistent public sources failed to.
- **Anything else — optional free-text catch-all.**

## Output format
A single JSON object (`design_specs/*.json` in this repo), schema
fields: `project_name`, `description`, `application`, `dimensions`
(array of `{label, value, unit, tolerance}`), `tolerance_policy`,
`manufacturing_method`, `budget`, `electronics_components` (array of
`{name, note}`), `reference_image_data` (base64 data URL or null),
`notes`, `status`. `status` starts as `"awaiting_confirmation_sketch"`
— see workflow below. See `design_specs/sg90_bracket_request.json`
for a real worked example, back-filled from this session's actual
SG90 bracket build (the data was real; the form didn't exist yet when
that bracket was built, so this is a retroactive example, not a
replay of an actual form submission). That example now lives at
`library/projects/sg90-servo-bracket/design_request.json` — see
`docs/library-spec.md` for why: once a design request produces a real
project, it's promoted out of the `design_specs/` inbox into its own
library folder alongside the project's output and provenance.

## The workflow this form is part of (the actual point of this doc)
This directly answers the token-efficiency concern that motivated the
idea: the Fusion MCP connector is only reachable through a live,
human-present session — expensive in attention and probably tokens
both, not something to open speculatively. So the workflow has two
phases with a human checkpoint between them:

**Phase 0 — cheap confirmation, no Fusion connector involved.**
Design agent reads the filled-in JSON, grounds any named components
against `component_reference/*.md` (escalating if a referenced
component has no reference doc yet — same "missing reference is a
data problem, not an improvise opportunity" rule as the coder agent),
and produces a rough sketch of what it understood it's being asked to
build. This is exactly the kind of diagram sent earlier this session
(a dimensioned SVG plan-view sketch, generated from reasoning alone —
no live CAD tool calls), plus a short written restatement of the
request. The user reviews this and either confirms or corrects it.
This is also where the "verification gate" question from
`docs/design-agent-first-task.md` partially resolves for the *intent*
side of the design (confirming the agent understood the ask) — it
does not replace the still-open *geometry* self-check gap from the
SG90 build (whether the actually-built model's real dimensions match
what was intended; see that doc's item 3).

**Phase 1 — live build, only after Phase 0 is confirmed.** Only once
the user confirms the Phase 0 sketch does the design agent (or the
user, today, since no automated `design_agent.py` exists yet) open
the live Fusion MCP connector and actually build. This means a
misunderstood request gets caught before any live Fusion session,
which is the actual cost most worth avoiding.

## Future direction — noted, not scheduled
User wants to eventually run this form as a local app on their own
PC instead of a claude.ai artifact — once the form/workflow is
stable, not now. Reasoning not yet captured in detail (likely:
persistence across sessions, not re-generating/re-publishing the
artifact each time, maybe wiring it directly to `design_specs/` on
disk instead of copy-paste). Explicitly deferred — don't start this
until the intake form and the Phase 0/Phase 1 workflow it feeds have
actually been used and honed, per direct instruction. Revisit this
section when that happens instead of treating it as a live task.

## What this doc does not yet resolve
- The form is a standalone artifact right now — nothing in this repo
  reads its JSON output automatically. There is no `design_agent.py`
  to consume `design_specs/*.json` yet (same gap
  `docs/design-agent-first-task.md` already names).
- Phase 0's "rough sketch" step has been demonstrated manually once
  (this session, for the SG90 bracket, informally) but isn't yet a
  scripted/repeatable step with its own defined output format or
  escalation rule for when the user's correction and the agent's
  understanding still don't converge after a round or two.
- The form's "required" fields are enforced by the form's own JS, not
  by anything a design agent could re-validate programmatically yet —
  `design_specs/*.json` has no schema validator the way
  `agent/spec_schema.py` does for the coder agent.

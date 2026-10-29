# Engineering department — working notes

Captures the architecture discussion this repo grew out of, so the
reasoning isn't lost once the chat that produced it scrolls away.
Update as real decisions get made; this isn't a spec to follow
rigidly, it's the current best thinking.

## Context / goal
2-3 year goal: a working, refined, manufacturable flying/ground/water
drone product line, professionally engineered and documented, built by
a multi-agent company (engineering, business/finance, marketing, ops,
manufacturing) coordinated by an orchestrator -- with the explicit
caveat that "autonomous" means *less human input, at a higher level*,
not *zero* human input. Someone always defines intent, approves spend,
and bears legal/physical responsibility; no department (least of all
manufacturing or finance) should be designed as if that disappears.

## Why this repo exists instead of extending embedded-code-gen-agent
That repo proved the core idea once (grounded codegen + compile-check,
Session 2) but never re-verified it, and its architecture (one spec ->
one board -> one file) couldn't represent the two-board rover, which is
why the rover was hand-written instead. This repo is a fresh build
using the Claude Agent SDK, scoped as one node in a larger system from
the start rather than retrofitted into one later.

## Sequencing (don't skip steps)
1. **Prove the primary coder agent alone.** Multiple specs, multiple
   boards, re-verified -- not one historical success treated as
   ongoing proof.
2. **Build the rest of engineering around it**: a design agent (3D/
   mechanical) and a manufacturing engineering agent (translates design
   into a manufacturable process/tolerances), since these three have a
   real dependency chain (design decisions determine what the coder
   needs to build, e.g. an actuator's control signal type determines
   firmware requirements; manufacturing engineering determines whether
   a design is actually buildable at the tolerances/cost the business
   needs).
3. **Only then** stand up business/finance -- a finance agent with
   nothing real to account for yet is premature infrastructure.
4. 3D design, teacher/editor coder(s), and test/simulation agents are
   each separate builds, added once the primary coder has a track
   record, not alongside it.

## Department-to-department coordination
- Default: route decisions and requests that trigger spend or action
  through the orchestrator (hub-and-spoke), not free-form agent-to-
  agent chat -- this is the one place that can enforce spend/risk
  thresholds and the one place a human can see what's actually
  happening across departments. Matters doubly here since "auditable
  decision trail" is part of the stated 2-3 year goal
  (professionally documented), not separate from it.
- Carve-out: shared reference data (specs, BOM, docs, the repo itself)
  lives in common storage any department can read directly, rather
  than being requested department-to-department.
- Not yet decided, revisit once a second department actually exists:
  exact spend/authority thresholds per department and per product
  line, and what counts as "major enough to run by [the human]
  regardless of threshold."

## A worked example (illustrates the dependency chain, not yet built)
"Design a linear actuator mechanism for the rover's probe, integrated
so the gamepad can control it" is not a parallel fan-out to
design+coder+BOM agents simultaneously. Real sequence:
1. Design needs the rover's actual physical envelope/mounting points
   first -- a real prerequisite, not assumed. No existing CAD model of
   the rover chassis exists yet as of this writing.
2. Design agent picks an actuation method (leadscrew+stepper? linear
   DC actuator? servo-driven?) -- this determines the control signal
   type, voltage, and current draw.
3. That spec feeds the coder agent (firmware + control mapping), which
   checks it against the target board's actual pin/power budget
   (hardware_reference data) -- may loop back to design if it doesn't
   fit.
4. BOM/cost agent prices the parts list design produced.
5. 3D printing and physical mounting stay human/physical steps
   regardless of how good the agents get -- same category as the
   existing human-review-before-flash rule, applied to the
   manufacturing endpoint instead of the flashing endpoint.

## Open questions, not yet resolved
- What does "operations" mean in the original department list --
  business ops (logistics/admin/scheduling) or production ops (running
  the build line)? Decides whether it sits under engineering or
  business once that department gets built.
- Exact per-department, per-product-line spend thresholds.
- Whether/when to build a literal orchestrator agent vs. continuing to
  coordinate manually (you, directly) until there's a second proven
  department to actually coordinate.

# Local library — spec (2026-10-31, session 7 continued)

Implements the project instructions' "shared reference data (specs,
BOM, docs) lives in common storage any agent/department reads
directly, rather than being requested peer-to-peer" principle,
concretely, for the first time. Two distinct things live here, kept
separate on purpose:

## 1. `library/projects/<slug>/` — this project's own completed work
One folder per design project (a bracket, a frame, eventually a full
drone), so finishing a project means it's actually *organized and
re-findable*, not scattered across `design/`, `design_specs/`,
`component_reference/images/` with no single entry point.

Each project folder contains:
- `design_request.json` — the intake form's output for this project
  (moved here from `design_specs/` once the project is real, not
  speculative — see "Lifecycle" below).
- The actual output file(s) (`.f3d`, eventually `.stl`/`.step`/code).
- `PROVENANCE.md` — what was built, what's confirmed vs. not, real
  API/grounding facts learned (same pattern already used for the
  SG90 bracket).
- `metadata.yaml` — machine-readable summary: `slug`, `project_name`,
  `status` (`draft` / `in_progress` / `built` / `archived`),
  `created`, `last_updated`, `tags`, `summary`, `design_request`
  (path), `outputs` (list of paths), `related_components` (paths
  under `component_reference/` this project depends on). This is
  what lets a future search/catalog step (or a human) find a project
  by tag or component without opening every folder — intentionally
  just a flat file per project, not a database, consistent with not
  building infrastructure ahead of what's proven.

`component_reference/*.md` stays where it is and is NOT duplicated
into project folders — it's reusable grounding data any project with
that part can reference, the mechanical equivalent of
`hardware_reference/*.md`. A project folder's `metadata.yaml` points
to the component docs it used instead of copying them.

## 2. `library/reference/<slug>/` — externally-sourced designs
Where the agent caches designs/parts it goes and finds on the
public internet when asked to seek out existing electronics or
mechanical designs (a drone frame, a flight-controller board
layout, etc.) — directly implementing the existing non-negotiable
rule to prefer adapting proven existing designs over building from
scratch, and to check and record licenses before incorporating
anything.

Each entry is a folder with a `metadata.yaml`:
- `source_url` — where it was found.
- `search_terms_used` — the actual query that found it, so it's
  **findable again even if the link dies** (this was explicitly
  asked for: "if not the physical file at least a link or a prompt
  so it can be found again").
- `retrieved_date`.
- `license` and `license_confirmed` (bool) — mandatory, not optional.
  If the license is non-commercial (e.g. CC BY-NC), copyleft in a way
  that could force disclosure of a derivative commercial work (e.g.
  GPL), or simply not confirmable from what's actually known, that's
  itself an escalation per the existing rule (same shape as
  `agent/system_prompt.md` rule 7 for the coder agent) — it does not
  get silently cached and used.
- `what_it_is` — one or two sentences.
- `local_file` — path to the actually-cached design file (STL/STEP/
  source), **only when the license permits local redistribution**;
  otherwise `null` with a `why_not_cached` note (e.g. "license
  unconfirmed" or "redistribution not permitted — link only").

This means a restrictive-license design still gets a `metadata.yaml`
entry (link + search terms + license status) even when its actual
file is never downloaded — the point is "findable again," not
"always cached."

## Lifecycle (how a project actually ends up in `library/projects/`)
1. Intake form → `design_specs/<something>.json` (the inbox — see
   `docs/design-intake-form-spec.md`). Nothing here is "a project"
   yet, just a request.
2. Phase 0 (confirmation sketch) → Phase 1 (live build, per the
   existing two-phase workflow) happens using that request.
3. Once there's a real output worth keeping — not necessarily
   "finished" forever, just real enough to reference later — promote
   it: `git mv` the request JSON and the output file(s) into a new
   `library/projects/<slug>/`, write `PROVENANCE.md` and
   `metadata.yaml`. There is no automated promotion tool yet; this is
   a manual step every time, same as everything else in this project
   until it's proven enough to automate.

## First (retroactive) example
`library/projects/sg90-servo-bracket/` — the SG90 bracket built in
this same session, promoted from the old flat `design/` +
`design_specs/` layout that existed before this doc. `design/` and
the entry in `design_specs/` for this bracket no longer exist;
`design_specs/` remains as the live inbox for the *next* request.

## What this doesn't resolve yet
- No automated promotion step, no schema validator for
  `metadata.yaml`, no actual search/catalog tool — listing/finding a
  project or reference entry today means `ls`/`grep` across
  `library/`, same as everything else in this project right now.
- `library/reference/` has no entries yet — it exists as a convention,
  not as a demonstrated workflow. The first real test is the next time
  the agent is actually asked to go find an existing drone-frame or
  electronics design, not before.
- No retention/cleanup policy for `library/reference/` if it grows
  large (many cached STL/STEP files) — not a real problem yet at zero
  entries.

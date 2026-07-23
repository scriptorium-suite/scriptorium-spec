# Changelog

## Unreleased

Release candidate for **v2.3.0**.

- Adds `experiment-run/1.0`, a minimal observation record for one external
  research-compute attempt: stable run/project identity, objective, executor/code
  and environment references, effective parameters, named random seeds, lifecycle
  status, artifacts, metrics, and producer identity. The file is explicitly data,
  never an execution instruction or authorization.
- Adds `claim-evidence/1.0`, a reviewable claim with precise evidence links and
  independent `epistemic_status` and `review_state` axes. Every explicit review
  decision records `reviewed_at`; accepted claims require evidence and cannot remain
  speculative; superseded claims retain history and identify their replacement.
- Adds synthetic XQ-17 examples, negative fixtures, stdlib validator dispatch, and
  JSON Schema conformance coverage for both formats.
- Adds `specs/research-execution-and-evidence.md` and updates ownership/product
  direction. External executors own run records; explicit human review owns claim
  decisions; the thin entry neither executes code references nor approves claims.
- This is not a restoration of the broad `experiment-log/1.0` removed in v2.0.0.
  `project/1.x` remains unchanged and has no `experiments` field.
- Records the implemented local Provenance ingestion of `parsed-paper/1.0`,
  `reading-note/1.0`, `review/1.0`, and `lineage-graph/1.0`. Provenance ingestion
  of the two new contracts remains a release gap.

## v2.2.0 — 2026-07-20

- Replaces all public worked examples and domain-bearing invalid fixtures with a
  coherent, explicitly fictional XQ-17 dataset; no schema or contract version changes.
- `library-kb/1.1` formally adds the optional Better BibTeX `citekey` field. The
  field was added to the v1 schema after v2.1.0, but first-party examples and
  Steward output still identified those payloads as `library-kb/1.0`.
- `library-kb/1.0` remains supported. Consumers continue to accept historical
  1.0 payloads that already contain `citekey`; new first-party payloads carrying
  the field must identify themselves as 1.1.
- Adds explicit 1.0 and 1.1 examples, producer-honesty policy tests, release-fact
  consistency checks, Windows + Ubuntu CI, and a tag preflight workflow.
- The coordinated Steward compatibility target is `steward 0.2.0`.
- Clarifies the existing `session-summary/1.0` contract without changing its version:
  an unresolved event remains inflight and requires explicit project resolution; producers
  must not emit a summary with `project: null`. The convention now also records the
  read-only unresolved inspector and component-owned, link-safe pending scaffold/fill seam;
  candidate fill submission and authoritative pull remain separately authorized.
- Records the local umbrella candidate's preview-first `init`, strict suite config,
  canonical host installers, public pull entry, and Windows CI as implemented entry
  surfaces. This is an implementation-status clarification, not a schema change or
  a claim that a package or external beta has been published.
- Records the umbrella's content-free `status` aggregation over trusted
  doctor and pull-preview reports. Status exposes only allowlisted readiness,
  freshness, aggregate counts, and fixed review cues; it never authorizes
  `pull --run` or other suite project/data writes, and it does not forward local
  paths, identifiers, research content, or stderr. External readiness probes are
  disclosed rather than claimed to be OS-sandboxed.
- Records the umbrella's `inventory` boundary for explicitly selected local
  Markdown/PDF sources, AI conversation exports, and Zotero exports. The preview
  classifies suffix candidates without opening payloads, suppresses paths and
  filenames, performs no write or egress, and does not persist or apply a migration.
  Adapter-specific reviewed migration execution remains a release gap; no exchange
  schema is added by this convention clarification.
- Clarifies the existing optional `project/1.x` `linked_repo` field without changing
  its type or version: it is the local session-resolution root, normally the code
  repository and otherwise the Markdown workspace selected by the thin entry.

## v2.1.0 — 2026-06-22

Adds the **literature-reading expansion** (additive minor bump): staged per-paper
reading + research-direction synthesis, local-first and agent-driven on the suite's
file contracts. Four new contracts, two new Steward commands, two new skills;
existing contracts unchanged. See specs/literature-reading.md.

- `reading-note/1.0` — per-paper staged interpretation (glance / close / deep /
  situate, each optional, filled on demand), keyed by Better BibTeX citekey. Produced
  by the `read-paper` skill (agent, in-session); consumed by Provenance + Obsidian.
- `parsed-paper/1.0` — normalized local parse of a paper PDF (sections + references +
  figures/tables). Produced by `steward parse` (GROBID, local — no cloud egress).
- `lineage-graph/1.0` — a research direction's citation 脉络: deterministic `cites`
  edges (Steward `lineage`, own-library reference matching) enriched by the agent with
  typed relations (extends / supersedes / method-of / contrasts). Render targets:
  Breadcrumbs-compatible frontmatter + ExcaliBrain / Dataview.
- `review/1.0` — direction synthesis (narrative `sections` + `comparison_table` +
  `gaps` + `priority_reads`). Produced by the `synthesize-direction` skill.
  Anti-fabrication: the table + citations are built from parsed-paper / library-kb,
  never invented.
- specs/literature-reading.md — the expansion design + the relationship-field
  convention (the five edge relations double as Breadcrumbs-compatible frontmatter keys).
- tools/validate.py dispatches all four new formats (stdlib-only); examples + negative
  fixtures added. Format count 6 → 10.

Also landed since v2.0.0 (no contract change): specs/trust-model.md (suite
safety/privacy guarantees + honest limits); a jsonschema conformance test suite + CI
for tools/validate.py (dev-only — the stdlib validator stays dependency-free).

## v2.0.0 — 2026-06-21

Breaking: removed `experiment-log/1.0` — experiment tracking dropped. The suite no
longer models per-experiment/run/sample records; projects, portfolio, library,
handoff, notes, and session-summaries are unchanged.

- Removed `schemas/experiment-log/v1.json` and `examples/experiment-log.v1.example.json`.
- `tools/validate.py` no longer dispatches `experiment-log` (a file carrying
  `schema_version: experiment-log/1.x` is now rejected as an unknown format) and
  drops the experiment-log validator + its `type`/`status` enums.
- `schemas/project/v1.json` drops the optional `experiments` field (its only role
  was to reference experiment-log exp_ids); `examples/project.v1.example.json`
  updated to match.
- specs/project-portfolio.md and specs/vault-layout.md drop the `Experiments/`
  folder layout and experiment-log references (project/portfolio content kept).
- README.md / README.zh.md / CLAUDE.md: schema count 7 → 6; experiment-log removed
  from the format table and producer/consumer map.
- Major version bump per specs/versioning.md (removing a contract is breaking).

**Doc clarifications** (no contract change, no version bump):
- specs/sync-layer.md: the worker runs **on-demand** (`sync-run -Mode once`) — the
  scheduled drain + resident watchers were retired (the Provenance daemon scripts +
  the headless summarizer were **removed entirely 2026-06-22**; the per-session summary
  fill is now interactive in-session). Capture front doors stay always-on (enqueue-only).
- specs/literature-automation.md: cadence is **on-demand** (`steward review --since-days N`);
  the weekly `harden/` Register-ScheduledTask automation was **removed entirely in steward 0.1.1**
  (no scheduled job; the digest fill is interactive in-session).
- For the record, the session-summary/1.0 gated high-value set is
  `status`/`stage`/`next_actions`/`conclusion`/`blocked_by`; the v1.3.0 entry below
  predates `stage` (added 2026-06-21) and omitted it — specs/sync-layer.md is authoritative.

## v1.3.0 — 2026-06-20

Adds the event/sync-layer contracts (additive minor bump) so the suite can
auto-update the memory hub + project notes with zero manual steps. See
specs/sync-layer.md (+ specs/vault-layout.md for the lean vault).

- `note/1.0` — a free-text note/idea/openclaw-drop ingested into Provenance
  memory (M3). Carries `private` so personal-zone notes (Inbox/, _planning/) are
  usable as project context + local search but excluded from the profile pipeline
  and kept in the protected layer.
- `session-summary/1.0` — a CC session's writeback: auto `timeline` (applied
  without approval) + gated high-value claims (`status`/`next_actions`/
  `conclusion`/`blocked_by`) behind `approval_state` (draft→approved→applied).
  `summary_id` is the idempotency key. High-value fields map 1:1 to project/1.0.
- specs/sync-layer.md — the event/sync-layer convention: single serializing
  worker, the frozen progress-log marker + append-only primitive, the approval
  surface (Obsidian queue + CLI), privacy classification, openclaw routing,
  abuse limits.
- tools/validate.py extended to both new formats; examples added.
- Produced/consumed by the host sync layer; Provenance consumes both.
  Steward / Lectern contracts untouched.

## v1.2.0 — 2026-06-17

Handoff gains a multi-paper / report-kind form (additive minor bump; the file
`schemas/handoff/v1.json` now describes **handoff/1.1**). A 1.0 single-paper
package validates unchanged.

- `handoff/1.1`: adds optional `report_type` (enum `literature` | `experiment`,
  default `literature`) and `papers` (array of per-paper objects with the same
  fields as the top-level paper). When `papers` is present the top-level `title`
  is the report title; when absent the top-level fields ARE the single paper.
- Ratifies what Lectern's `add-handoff-ingestion` change already reads. Producer
  side (Steward `pick`) still emits `handoff/1.0`; teaching it to emit
  `report_type`/`papers` is a separate Steward-side change.
- Added `examples/handoff.v1.1.multi.example.json`.

## v1.1.0 — 2026-06-11

Adds the project-portfolio layer (workflow capability ③ = project management;
experiment records are supplementary detail under a project):

- `project/1.0` — a research project record (Obsidian `Projects/<id>.md`
  frontmatter): status/stage/priority/next_actions/blocked_by/linked_literature/
  linked_repo/linked_conversations/experiments.
- `experiment-log/1.0` — one experiment/run/sample under a project
  (`Experiments/<exp_id>.md` frontmatter); unifies ml_run / wet_lab /
  field_sample / analysis.
- specs/project-portfolio.md — vault layout (Projects/ + Experiments/), the
  总纲 dashboard, and per-project-session + cross-project-overview working pattern.
- tools/validate.py extended to both new formats; examples added.

## v1.0.0 — 2026-06-11

Initial release. Formalizes the first suite exchange formats:

- `library-kb/1.0` — canonical library snapshot (was: bare-array library.json, now enveloped with `schema_version`)
- `proposal/1.0` — offline, human-reviewable reorganization plan (terraform plan/apply pattern)
- `handoff/1.0` — single-paper PDF + metadata staging for slide generation
- specs: versioning rules, Obsidian export convention (incl. Zotero extra-field
  conventions for TLDR / Read_Status), config-root convention
- tools/validate.py — minimal stdlib structural validator

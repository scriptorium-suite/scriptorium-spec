# Literature Automation (R16 ③)

> **Status:** v1 · 2026-06-22 · **implemented in steward** (review what's-new
> selection; on-demand, interactive in-session fill). The headless fill driver + the
> weekly `harden/` task were **retired in steward 0.1.1** — literature is on-demand only.
> Decisions marked `[decided]` are
> ratified; the former `[open]` items are resolved below under `[decided: build]`.
> Related: [product-direction.md](product-direction.md) R13; [sync-layer.md](sync-layer.md)
> (worker/pull shape); [obsidian-export.md](obsidian-export.md) (Reviews/ + Literature note format).

## Purpose

Auto-refresh the literature flow **Zotero → Steward `library-kb` → Provenance**, plus a
**"库内新进展" (what's-new) digest**, so the memory hub's literature view
(`get_portfolio` / `get_current_context` / search / a project's `linked_literature`)
stays current — refreshed **on demand** (`steward review --since-days N`), the literature
analogue of the event/sync layer for sessions/notes.

## Cadence — on-demand by default `[decided]`

Refreshed **on demand** by default (`steward review --since-days N`, run when you want to
archive new arrivals). Literature is low-frequency; the enemy is "forgotten", not latency —
no watcher or high-frequency drain needed. *Decision history:* 2026-06-21 initially decided
weekly, superseded the same day by on-demand; the weekly `harden/` Task Scheduler automation
was then **removed entirely in steward 0.1.1** — there is no scheduled job at all; literature
is archived on demand when you run `steward review`.

## Mechanism

An on-demand run executes decoupled CLIs that exchange data via the `kb/library.json`
file (no tool calls another's internals — suite rule):

1. `steward export --kb $PROVENANCE_HOME/kb/library.json` — refresh the KB from Zotero
   (**read-only**, see Credentials).
2. `prov-ingest-library` — ingest the KB into Provenance memory.
3. **R13 digest** — generate the "库内新进展" review into vault `Reviews/` (see below).

Optional Phase-2 (not now): a Zotero local-DB (`zotero.sqlite` mtime) change hint for
"refresh on actual change" — a future convenience that would prompt an on-demand refresh.

## R13 「库内新进展」digest — included `[decided]`

After the refresh, produce a digest of **recent additions + unread** library items into
vault `Reviews/`, by extending `steward review` (scaffold → interactive in-session fill →
assemble shape, with the same anti-fabrication guarantee: the literature table / DOIs /
reading-path are built from the KB, never the LLM; the LLM only writes prose).

`[decided: build]` **digest scope = recent-additions AND still-unread**
(`steward review scaffold --since-days 7 --unread`); the filters compose with the
existing `--topic` (all AND; ≥1 required). Rationale: "库内新进展" is the week's
*new and not-yet-read* arrivals, not the whole unread backlog.
`[decided: build]` **landing = dated snapshot** `Reviews/库内新进展-<date>.md`
(one note per run), not a single rolling note — preserves history, never clobbers
a prior week. An empty week is a clean no-op (no note written).

## Credentials — read-only, least-privilege `[decided: read-only]`

`steward export` only READS the library, so a **read-only** Zotero Web API key is
sufficient (no write key needed). Use a **project-specific** key (so it
can be revoked independently). `[decided: build]` stored in steward `config.toml`
(`~/.config/scriptorium/steward/config.toml`, gitignored + ACL-locked to the
user); steward self-reads it, so an on-demand run needs no `ZOTERO_*` env. (Windows
Credential Manager deferred — config.toml ACL is sufficient for a read-only key.)

## Build

- R13: extend `steward review` for the what's-new digest (Steward-repo change). *Done.*
- Repo ownership: `steward export` + `review` = Steward; `prov-ingest-library` =
  Provenance. **No scheduling** — the user runs `steward review --since-days N` on demand;
  the weekly `harden/` task was removed in steward 0.1.1.
- **Verify live:** a newly-added Zotero item appears in a project's
  `get_current_context` `linked_literature`, and a `Reviews/` digest is produced, after
  an on-demand run.

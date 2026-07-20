# Markdown Workspace Layout & Ownership Convention (v2)

The Scriptorium Markdown workspace is the **human-readable research workbench**.
Obsidian is a supported example client, not a runtime dependency: the same files MAY
be edited with any Markdown-capable application. This spec defines which folders are
human-authored vs tool-derived, who *owns* (may overwrite) each, and the
**lean-workspace** policy. It is the structural half of the Public Alpha decisions in
[product-direction.md](product-direction.md) and the ownership ADR in
[suite-entry-and-ownership.md](suite-entry-and-ownership.md).

## Principle

- **There is no universal source of truth.** Each durable artifact has one domain
  master: human-authored Markdown stays authoritative in the workspace; PDFs and code
  stay authoritative at their original paths; Zotero stays authoritative for Zotero
  records when used; contract schemas are governed by `scriptorium-spec` while each
  produced contract instance remains its own authoritative artifact; Provenance is
  authoritative only for approved cross-session memory, its index, and protected sync
  state.
- **The workspace is not a mirror.** It contains human-input zones plus a small set of
  curated, rebuildable views. It is **NOT a 1:1 mirror** of Provenance, Zotero, agent
  logs, attachments, or source repositories.
- **Every path has exactly one master.** A tool only creates/overwrites files in paths
  it owns. Derived views are regenerated from their named producer and users do not
  hand-edit them by default. Human-input zones are authored by the user (by hand or via
  an agent) and may be indexed by Provenance without transferring ownership.

## Zones

| Zone | Folders | Master | Who writes |
|---|---|---|---|
| **Human-input** | `Projects/`, `Inbox/`, `_planning/` | user / Markdown workspace | user (hand or agent); indexed by Provenance only after the applicable review policy |
| **Optional capture quarantine** | connector-declared staging folder outside authoritative zones | the producing adapter until accepted | adapter writes only within its declared boundary; host validates and stages; never a direct authoritative write |
| **Authoritative contract artifacts** | `reading-notes/*.json` and any `review` / `lineage-graph` JSON materialized in `Reviews/` | the contract instance produced by the agent workflow or Steward | producer writes or explicitly updates; view regeneration MUST NOT delete or overwrite it |
| **Curated derived view** | `总纲`/`Dashboard`, `Reviews/*.md`, `reading-notes/*.md`, `reading-notes/_index.md`, `Home.md` | the named renderer | deterministic, rebuildable projections; small enough to browse |
| **Hybrid approval queue** | `Approvals.md` | host sync layer owns queue structure; user owns edits and approval decisions | regeneration merges pending/edited items; only explicit user approval commits claims |
| **Provenance-protected** (not in workspace) | approved memory, search index, raw-ingest staging, profile, sync-state | Provenance | never mirrored wholesale into the workspace |
| **External source material** (not owned by workspace) | PDFs, code repositories, agent logs/exports, optional Zotero data | original application or filesystem path | read or imported through explicit adapters; source remains outside the workspace |

## Lean-workspace policy (eviction)

- `Conversations/`, `Literature/`, `Attachments/`, `Profile/`, and the auto-generated
  `MOC/` are **NOT full-mirrored** into the workspace. Conversation originals remain
  with their agent host/export; Zotero records remain in Zotero when used; PDFs and
  attachments remain at their source paths; approved memory and indexes remain in
  Provenance. They are reached **on demand** or materialized **one note at a time**.
  At most 1–2 hand-maintained overview maps may remain.
- **Literature understanding**, when the optional literature profile is installed, is
  served by `Reviews/` artifacts + on-demand materialization + optional Zotero/Steward —
  not by a full-library mirror. Ownership is file-level: a `review/1.0` or
  `lineage-graph/1.0` JSON placed there is authoritative; `*.md` renders are tool-owned,
  rebuildable projections. A renderer or cleanup routine MUST target only its marked
  projection files and leave contract JSON untouched. Steward's `*.lineage.md` render
  contains Mermaid + timeline + edge table; see
  [literature-reading.md](literature-reading.md) §3 "Lineage render".
- **`reading-notes/` has mixed file-level ownership**, with two files per paper keyed
  by citekey: the `read-paper` agent workflow writes authoritative `<citekey>.json`
  (`reading-note/1.0`), while Steward
  `read-render` projects it to a browsable `<citekey>.md` (frontmatter + a section per
  filled stage + `[[wikilinks]]` + an annotations section; deterministic, idempotently
  re-rendered — the `.json` stays the source of truth). Steward `read-index` also
  projects the whole directory into a single `_index.md` overview (the reading status
  dashboard — status-grouped wikilink sections + a table + a Dataview block), likewise
  idempotent. The per-paper `[[citekey]]` **library-note** link resolves because Steward
  `export` stamps a Better BibTeX `citekey` alias onto each `Literature/` note (from the
  item's `Citation Key:` extra-field line). Unlike the lean-vault-evicted `Literature/`,
  this is a small, **persistent** set of papers you actually read. Regeneration may
  replace only the `.md` projections and `_index.md`, never the JSON contract artifacts;
  see [literature-reading.md](literature-reading.md) §3–4.
- **Eviction is non-destructive:** back up first; verify the domain master still exists;
  never hard-delete the only copy. Provenance is not assumed to be the master for PDFs,
  code, Zotero records, or human-authored Markdown.

## Ownership rules

- A tool MUST only create/overwrite the paths or file patterns it owns. A mixed
  directory does not grant ownership of every file beneath it.
- **Human-input zones:** tools MUST NOT overwrite user content. They may *read* (for
  ingest) and, for the project progress-log section only, *append* (append-only; see
  "Project note"). An approved sync operation MAY update only the frozen set of
  project frontmatter keys defined by [sync-layer.md](sync-layer.md); it MUST journal
  and remain reversible.
- **External capture staging** is a quarantine, not a workspace master. Each optional
  adapter MUST declare its own staging boundary and write nowhere else; the host sync
  layer validates and stages accepted input. Cleanup follows an explicit retention
  policy and MUST NOT hard-delete the only copy of user content.

## Project note (M2)

A project note holds two sections with different masters in one file:

1. **Hand-authored** — plan / ideas / next actions. Master = user.
2. **Auto progress-log** — append-only, written by the sync layer from session
   summaries (M1: low-risk facts auto, high-value claims after one-click approval).
   Delimited by the frozen `<!-- scriptorium:progress-log:begin -->` /
   `:end` marker pair; the sync layer only inserts dated blocks inside that region and
   never edits the hand-authored content outside it. Mechanism + the append-only
   primitive: see [sync-layer.md](sync-layer.md) §3.

## Optional external proposal boundary

Mobile capture, messaging front doors, and other external proposal sources are not
Public Alpha core dependencies. If enabled, they remain outside the authoritative
workspace and use the same minimum-trust boundary:

- **Write surface:** one connector-declared quarantine or the public proposal command;
  never `Projects/`, source repositories, Provenance memory, or protected sync state.
- **Read surface:** no access to raw research, personal profiles, credentials, or
  protected paths is required by the core flow. Any additional read scope is explicit,
  user-selected, and documented by the connector.
- **Host acceptance:** the sync layer normalizes and limits input, mints trusted
  identifiers, and resolves a registered project before creating any summary. An
  unresolved project remains in protected inflight state and MUST NOT produce a
  `session-summary/1.0`, timeline, draft, or new project.
- **Windows boundary:** component-owned commands reject traversal and
  link/junction/reparse escapes, then serialize state changes under the worker lock.
  Host permissions, transport isolation, connector credentials, and egress hardening
  remain deployment responsibilities rather than suite guarantees.

## Cross-reference

- Literature note *format*, when a note is materialized on demand: see
  [obsidian-export.md](obsidian-export.md).
- Versioning / consumer tolerance: see [versioning.md](versioning.md).
- Config root + env conventions: see [config-root.md](config-root.md).
- Suite entry, component ownership, optional integrations, and egress classes: see
  [suite-entry-and-ownership.md](suite-entry-and-ownership.md).

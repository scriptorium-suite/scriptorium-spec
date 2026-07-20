# ADR-001: Thin Suite Entry and Component Ownership

> Status: **Accepted**
> Date: 2026-07-15
> Scope: Scriptorium Public Alpha and later compatible releases

## Context

Scriptorium is a suite of independently useful tools joined by versioned files.
Publishing it for external technical researchers requires one coherent entry
experience without turning the tools into a monolith or creating a second source
of truth. It also requires an explicit boundary between the suite, the agent host,
optional desktop applications, and networked services.

This decision supersedes the earlier assumptions that Scriptorium is only for its
author, that Obsidian is a required runtime, and that Provenance is the universal
source of truth for every kind of data. Provenance remains the authoritative
cross-session **memory and retrieval layer**; source records keep their own domain
masters.

## Decision

### 1. The suite entry is a thin control plane

The umbrella repository (`scriptorium-suite/scriptorium`) owns the public
entry experience. Its entry command MUST provide the equivalent of:

- `scriptorium init` — create suite configuration and a Markdown workspace;
- `scriptorium doctor` — verify component versions, paths, local services, and
  optional integrations without exposing secrets;
- `scriptorium status` — aggregate content-free readiness and freshness information
  without authorizing suite project/data writes;
- `scriptorium inventory` — classify explicitly selected local source roots and
  preview their review routes without reading file content or writing a plan;
- `scriptorium pull` — invoke the on-demand capture/ingest/sync sequence;
- `scriptorium demo` — run a synthetic-data, credential-free product walkthrough;
- `scriptorium host install codex|claude-code` — explicitly install a host adapter.

The entry MAY open an installed editor or local UI after an explicit user action.
It MUST invoke components through their public CLI, MCP, or contract files. It MUST
NOT import their internal Python modules.

The entry MUST NOT:

- own or duplicate schemas, library records, memory records, project notes, or
  presentation outputs;
- write Zotero or Provenance databases directly;
- embed an LLM provider or copy component business logic;
- auto-approve high-value claims;
- install a daemon, scheduled task, component, or credential silently;
- make an undeclared network request or emit telemetry.

The entry owns only suite-selection/configuration data, a compatibility manifest,
and disposable readiness caches. These are not business-data sources of truth.
A complete Public Alpha setup MUST select at least one supported agent host. A
host-less setup MAY run deterministic import, validation, search, and diagnostics,
but MUST be reported as incomplete rather than as a fully operational Scriptorium.

#### Status aggregation boundary

`scriptorium status` is a content-free control-plane report, not a new business
artifact or source of truth. It authorizes no suite project/data writes, but it
does invoke external readiness probes; OS-level subprocess side effects are not
observed or claimed to be sandboxed. It MUST:

1. evaluate the Public Alpha `doctor` boundary;
2. run only a non-authorizing `pull` preview, and only after that readiness boundary
   is trustworthy enough to invoke the public pull entry;
3. rebuild its output from an explicit allowlist of readiness states, aggregate
   workflow counts, fixed action types, egress guarantees, and static limitations;
4. suppress local paths, project/session identifiers, research content, component
   stderr, raw diagnostic details, and unknown producer fields;
5. never invoke, imply, or treat the report as authorization for `pull --run`.

The stable status classes and process exits are:

| Status | Exit | Meaning |
|---|---:|---|
| `ready` | 0 | required capabilities are ready and the preview has no pending work |
| `attention` | 0 | normal reviewable backlog exists; this is not infrastructure failure |
| `incomplete` / `blocked` | 1 | a required capability is missing or the preview stopped safely |
| `error` | 2 | a trusted pull preview reported an error, or the entry could not form a trustworthy content-free report |

A suggested `review-pull-plan` or `pull-diagnostics` action MUST point to plain
`scriptorium pull`; the user reviews that separate preview before explicitly
authorizing `--run`. Project resolution, agent fill, human approval, and workspace
review are fixed cues and MUST NOT claim that plain `pull` completes those actions.
Freshness MUST be derived from current preview evidence rather than an invented age
threshold. Until a stable component field exists, the last successful pull time is
reported as `not-reported`; the entry MUST NOT scrape legacy human-readable status
output to manufacture it.

#### Source inventory boundary

`scriptorium inventory` is a classification-only intake preview, not a migration
artifact or authorization to ingest. It MUST:

1. scan only roots explicitly supplied by the user as ordinary Markdown/PDF
   sources, AI conversation exports, or Zotero exports; it MUST NOT discover the
   current directory, home directory, agent profiles, browser data, or a live Zotero
   database;
2. inspect filesystem metadata and filename suffixes only; it MUST NOT open file
   payloads, archives, JSON, PDFs, or bibliography exports;
3. make no file or configuration write, persist no manifest or cache, invoke no
   component, model, credential, network path, or optional connector;
4. suppress absolute and relative paths, filenames, titles, sizes, timestamps,
   hashes, file content, and raw operating-system errors from both human and JSON
   reports;
5. report only aggregate candidate counts and the fixed review routes
   `workspace-review`, `literature-reference`, `provenance-import-review`, and
   `steward-review`;
6. leave every source at its existing domain master. A generic command output remains
   an external source; inventory does not turn it into a project note, evidence,
   memory, literature record, or session summary.

Explicit roots and every ancestor MUST be checked before resolution or traversal.
UNC and mapped-remote roots, duplicate or overlapping roots, missing or special roots,
and roots crossing a symbolic-link, junction, or other reparse point make the preview
incomplete and MUST fail closed. Nested reparse entries MUST never be followed.
Directory identity MUST be checked again after traversal; an access failure, scan
limit, or detected change invalidates candidate counts rather than presenting a
partial count as complete.

On Windows, the implementation MAY keep metadata-only handles without write or delete
sharing open for the preview lifetime so checked ancestors and selected objects cannot be
renamed, deleted, or opened for data write during path-based enumeration. This temporary
operating-system constraint MUST be disclosed as a limitation and MUST NOT be
described as content access.

The normal report classes are `planned` (candidates exist), `noop` (a complete scan
found none), and `partial` (safe completion was not possible). `planned` and `noop`
exit 0; `partial` exits 1. Invocation or internal boundary failures use the fixed,
content-free `error` envelope and exit 2. The preview deliberately does not validate
file signatures, deduplicate or hash sources, or provide an apply mode.
When an arbitrary root iterable exceeds the bounded root budget, `roots_requested`
MAY report the first over-limit count as a lower-bound sentinel rather than consuming
the remaining iterable to calculate an exact total.

### 2. Persistent data has domain-specific masters

| Data or artifact | Master / owner | Other components |
|---|---|---|
| JSON Schemas and suite conventions | `scriptorium-spec` | consume only |
| Enabled components, paths, compatibility selection | thin suite entry | non-authoritative orchestration config |
| Literature metadata, attachments, and reading status | Zotero, when the Literature profile is enabled | Steward governs through backup/proposal/review/apply; others consume files |
| `library-kb/1.x` | Steward-produced contract file | Provenance indexes it; agents and other consumers read it |
| Human-authored project prose, plans, and inbox notes | Markdown workspace | Provenance ingests them |
| `project/1.x` frontmatter | the corresponding Markdown project file | approved sync operations MAY update only the contract fields they own |
| Tool-owned progress-log marker region | host sync layer | append-only; human-authored regions are immutable to tools |
| `parsed-paper/1.x` and deterministic `lineage-graph/1.x` | Steward-produced contract files | current Steward/agent file workflows consume them; direct Provenance ingestion is a release gap |
| Reviewed `reading-note/1.x` and `review/1.x` | contract files produced by the agent workflow | Steward renders supported projections and agents read the files; direct Provenance ingestion is a release gap |
| Agent-generated scaffold/fill or high-value claims before approval | draft owned by the host workflow | no authoritative consumer until approved |
| Cross-session memory/index and protected sync state | Provenance | exposed through read-only MCP and derived views |
| Raw browser/platform export | source-platform or local capture artifact | Provenance ingests and sanitizes it |
| `handoff/1.x` | Steward-produced contract file | Lectern consumes it |
| Generated `.pptx` | Lectern until delivery; the user after delivery/editing | no automatic round-trip into the memory hub |
| Rendered Markdown dashboards, review notes, and indexes | their declared generating tool | disposable, reproducible views |

"Provenance is the memory SSoT" therefore means that it is authoritative for the
suite's normalized cross-session memory and retrieval state. It does not replace
Zotero, human-authored Markdown, or versioned contract artifacts as their masters.

### 3. Markdown is the workspace contract; Obsidian is optional

The project workspace is a directory of plain Markdown and JSON files. Core flows
MUST remain usable with a text editor and MUST NOT require an Obsidian plugin.
Obsidian MAY provide editing, navigation, Dataview, PDF++, or other enhanced views,
but it is an optional client and never the architectural master by itself.

The workspace keeps the ownership zones defined in `vault-layout.md`: human-input
zones, small tool-owned derived views, and protected/full-history data held outside
the workspace by Provenance.

### 4. Codex and Claude Code are first-class agent hosts

The suite code does not contain an LLM. Codex and Claude Code are host adapters for
the same file/MCP workflows. Both MUST be able to:

1. read the relevant contract files and Markdown workspace;
2. call public local CLI or read-only MCP tools;
3. produce the same versioned scaffold/fill or exchange artifacts;
4. stage high-value claims for human approval;
5. complete an on-demand `scriptorium pull` without requiring identical event APIs.

Host triggers MAY differ. Claude Code MAY use an enqueue-only `SessionEnd` hook.
Codex MAY use an on-demand local-log scanner when no equivalent stable hook exists.
Public documentation MUST describe this difference and MUST NOT claim identical
automatic capture.

Canonical skill content and host installers belong in the umbrella repo.
Host-specific directories such as `.claude/skills/` are adapters or installation
targets, not the suite-wide skill source of truth. The stable interoperability
surface remains the files and schemas in this repository.

### 5. Integrations are capability profiles, not hidden requirements

- **Public Alpha core:** thin entry + Provenance + Markdown workspace + at least
  one supported agent host. The user MUST select Codex, Claude Code, or both;
  neither host is preferred or treated as a second-class fallback.
- **Literature profile:** Steward; Zotero is optional and becomes the literature
  master only when this profile is enabled.
- **Slides profile:** Lectern as an optional `handoff/1.x` consumer.
- **Obsidian:** optional Markdown client.
- **Browser extension:** optional capture front door; local agent logs and explicit
  imports remain supported without it.
- **GROBID, Better BibTeX, PDF++, Dataview, and similar tools:** optional capability
  enhancers with documented degradation when absent.

Future OpenAlex, RSS, or other discovery connectors MUST produce candidates or
reviewable proposal files. They MUST NOT bypass Steward to mutate Zotero or write
authoritative Provenance state directly.

### 6. Network access is explicit and attributable

The entry, `scriptorium-spec`, and Provenance make no runtime network requests by
default and emit no telemetry. The following are separate, explicit egress classes:

| Egress owner | Permitted use |
|---|---|
| User-invoked bootstrap | download declared runtimes/dependencies after showing the purpose |
| Steward | Zotero Web API only when configured; writes retain backup, dry-run, review, and explicit-run gates |
| Agent host | the provider selected by the user; this is host-managed egress, not a hidden suite call |
| Lectern | configured LLM provider and optional parser service; unpublished inputs require a clear warning and local alternatives |
| Future discovery connector | its documented metadata/search request only; no private memory payload by default |
| Browser extension | read the user's signed-in page and create a local export; no third-party telemetry |

`doctor`, `status`, and dry-run plans MUST identify expected egress without printing
secret values. No component may market the whole suite as absolutely "offline" when
an enabled host or integration is configured to use a remote service.

### 7. Engram is not an official Public Alpha component

Provenance remains the official Scriptorium memory hub. Engram is a standalone
product/UX experiment derived from the memory pipeline and MAY be referenced under
`Labs`, but it MUST NOT appear in the official runtime component registry or be
presented as a second memory master.

Reusable Engram UI or branding assets MAY later be reviewed and moved into the thin
entry. Replacing Provenance with Engram would require a separate accepted migration
ADR covering package/CLI names, data roots, MCP tools, contract consumers, and repo
history. Long-lived dual memory hubs are not allowed.

### 8. Public Alpha boundary

Public Alpha targets external, technically capable individual researchers. It MUST
provide a reproducible synthetic demo, documented source installation, a Markdown
workspace, Provenance memory/search/MCP, Steward's contract-driven literature path,
at least one installed Codex or Claude Code adapter (with both documented and
equally supported), and one verified optional Steward-to-Lectern handoff.

Public Alpha does not include a desktop shell, cloud/team sync, OpenAlex/RSS
discovery, local vector embeddings, remote-control or third-party automation
connectors, or a consumer-grade installer. Those
capabilities require later decisions and must not be implied by the release surface.

## Repository boundary

This repository owns the normative responsibilities, masters, file contracts, and
trust boundaries above. The umbrella repository owns executable entry code,
component manifests, workspace templates, demo fixtures, host installers, product
documentation, screenshots, and cross-repository end-to-end CI.

No new exchange schema is introduced by this ADR.

## Consequences

- Each component remains independently installable and testable.
- A missing optional integration degrades one capability rather than invalidating
  the suite.
- Cross-repository tests can assert contracts without importing private internals.
- Product claims must distinguish local suite code from host- or connector-managed
  network calls.
- The previous author-only, Obsidian-required, Claude-only, and dual-memory-hub
  interpretations are superseded.

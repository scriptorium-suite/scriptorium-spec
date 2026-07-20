# Event / Sync Layer Convention (v2)

The host-side connective tissue that turns supported agent sessions, Markdown changes,
and optional imports into reviewable research memory. Capture mechanisms differ by
host, but every supported path converges on the same contracts and serializing worker.
The reference flow is **on demand**: the user or agent runs one pull, then separately
approves high-value claims. This document defines the invariants, frozen markers,
contracts, and safety model that every adapter MUST follow. Product and ownership
boundaries live in [product-direction.md](product-direction.md) and
[suite-entry-and-ownership.md](suite-entry-and-ownership.md).

> **Status:** the Provenance worker, approval flow, append-only writeback, Claude Code
> enqueue adapter, and Codex on-demand log scanner are implemented and tested. Trigger
> parity is not claimed: Claude Code can enqueue from `SessionEnd`; Codex is discovered
> by an explicit local scan. Browser history and other external imports are optional
> adapters, not Public Alpha core dependencies. Scheduled drains, resident watchers,
> and unattended summarizers are not part of the reference deployment.

## 1. Shape

Host-specific capture adapters feed **one normalized queue and one serializing worker**,
which writes to two destinations:

```
Claude Code SessionEnd ─┐
Codex local-log scan    ├─► sync-state/queue.jsonl ─► single worker (lockfile) ─► ① approved Provenance memory/index
manual / optional import┘                                                           └► ② project-note progress-log (append-only)
```

- The worker is **on-demand and short-lived** (invoked by Provenance's
  `sync-run -Mode once` and exposed by the thin suite entry as `scriptorium pull`).
  The reference deployment has **no daemon, scheduled task, resident watcher, or
  unattended summarizer**.
- **All authoritative writes funnel through the one worker** under a lockfile. A hook,
  scanner, or import adapter only stages/enqueues; it never writes memory or project
  notes directly. This prevents dueling writers.
- Functional parity is measured after normalization: the same fixture from Codex and
  Claude Code MUST be consumable by the same worker and assemble to the same contract
  shape. Capture timing is allowed to differ.

## 2. Hard invariants (R9/R10)

1. **Append-only.** Two write modes only: (a) CREATE a new file in a tool-owned /
   protected location; (b) APPEND a dated block inside the project-note progress-log
   marker region. No code path opens a human file to rewrite its hand-authored content.
2. **Never overwrite human content.** The hand-authored section of a note (everything
   OUTSIDE the marker region) is read but never written.
3. **Journal before write, dry-run default.** Every write journals the touched file's
   pre-state to `sync-state/journal/<stamp>.json` and is reversible; `--run` is explicit
   (borrow Steward `apply.py`'s *shape* — its code is Zotero-REST-specific, not reused).
4. **Atomic + encoding-safe.** Read `utf-8-sig` (BOM-tolerant), preserve the file's
   existing newline style, write via temp-file + rename. Treat a file as ready only when
   its `(size, mtime)` signature is stable across two scans AND it fully parses (reuse
   `provenance/ingest/watch.py` debounce/readiness) — guards Obsidian half-saves.
5. **Idempotent.** Every applied entry carries a stable key; re-running with the same key
   is a no-op (no double-logging on hook re-fire / worker resume).
6. **Privacy.** See §6.

## 3. Frozen marker (M2 progress-log)

The auto progress-log lives between this exact, frozen BEGIN/END pair inside a project
note; everything outside the pair is hand-authored and never touched:

```
<!-- scriptorium:progress-log:begin -->
<!-- scriptorium:progress-log:end -->
```

- New dated blocks are inserted **immediately after `:begin`** (newest-first), each block
  prefixed by an HTML comment carrying its idempotency key:
  `<!-- entry:<summary_id> -->`.
- The **append-only primitive** (new, separately unit-tested — this is NOT
  `portfolio.apply_snapshot`, which is splice-REPLACE): parse the begin/end region,
  preserve all existing entry blocks, skip if `<!-- entry:<key> -->` already present,
  else insert the new block after `:begin`. **Refuse** to write a note that lacks the
  marker pair (route the content to a draft instead); never silently grow an unmarked
  human file. A tool MAY create the empty marker pair when it first creates a project
  note, but never injects markers into a pre-existing hand-authored note.

## 4. Contracts (additive, scriptorium-spec v1.3.0)

### `note/1.0` — free-text ingest
Envelope for supported free-text note/idea/import capture ingested into Provenance (M3).
Required: `schema_version`, `note_id`, `source`, `created`, `body`. Optional: `project`,
`title`, `tags`, `generated_by`, `origin_path`, `private` (bool). `note_id` is minted by
the producer or host-stamped on first ingest (collision-safe). `source` uses the
versioned enum defined by the schema; those values are compatibility identifiers and
do not make any optional integration a core dependency. `private:true` (default for
the `_planning/`,`Inbox/` zones) gates the profile-exclusion rule (§6).

### `session-summary/1.0` — session writeback (single staging contract)
**One** shape, **one** name, **one** location, **one** idempotency key (resolves the
3-way divergence the review found). Flat object mapping 1:1 to `project/1.0` fields:

Required: `schema_version`, `summary_id`, `project`, `created`, `approval_state`.
Auto (low-risk, applied without approval): `timeline` (files-touched / commits /
session bullets). High-value (gated — applied only after approval): `status`,
`stage` (FREE-TEXT project phase, no enum — unlike `status`), `next_actions[]`,
`conclusion`, `blocked_by`, each with optional `confidence`.
`approval_state` ∈ {`draft`,`approved`,`applied`}; `idempotency_key` = `summary_id`.
**Location:** `$PROVENANCE_HOME/sync-state/drafts/<summary_id>.json` (protected, NOT in
the vault — keeps distilled personal claims outside optional connector reach). The vault only ever
gets the human-facing Approvals queue note (§5) and, on approval, the appended
progress-log block.

Producer/consumer: the **host sync layer** produces & consumes both; **Provenance**
consumes `note/1.0` (memory) and the applied `session-summary` (memory + project note);
**Steward is untouched**.

### Protected pending-fill seam

An in-session agent MAY draft `summary-fill/1.0` content, but it MUST use component-owned
public commands rather than construct paths under `sync-state/`:

- Pending listing returns only safe summary IDs. Reading one item returns a schema-scoped
  scaffold containing identity, title, and already-sanitized turns; it never returns a
  protected filesystem path or unknown scaffold fields.
- Fill submission accepts one summary ID plus JSON on standard input. The component MUST
  reject unresolved or forged scaffold identity, unknown/identity fields in the fill,
  duplicate targets, traversal, and link/junction/reparse paths; it MUST recheck under the
  worker lock and atomically create the sibling fill without exposing its absolute path.
- A preview/status request grants no write authority. The user approves the listed
  candidate fills before submission and separately approves the later authoritative pull.
  A fill never implies approval of high-value claims or permission to tick `Approvals.md`.

## 5. Approval surface (M1 hybrid)

- **Primary:** a plain-Markdown queue note `Approvals.md` (plugin-free
  `- [ ]`/`- [x]` checkboxes; supports edit-before-approve and a top-of-note
  `APPROVE ALL`). Obsidian MAY be used to edit it but is not required. It is a
  documented single exception: a derived view that is also user-editable. Regeneration
  preserves still-pending items and never discards an edited-but-unapproved claim.
- **Fallback / committer:** a CLI `approve` verb (headless/scriptable) — and it is the
  actual committer the Obsidian flow shells out to.
- An optional notification connector MAY report only the aggregate pending count, but
  MUST NOT expose draft contents or commit an approval.
- On approve: the append-only primitive (§3) writes the approved high-value claims into
  the project-note progress-log and updates Provenance memory; `approval_state →
  applied`; the draft file is the audit trail. **It also writes the approved
  `status`/`stage`/`next_actions`/`blocked_by` back into the project-note YAML
  frontmatter** — a surgical, journaled, reversible update touching ONLY those named keys,
  never the prose, the progress-log region, or any other frontmatter key — so the Dataview
  portfolio board reflects the change. `conclusion` has no frontmatter field (log-only); a
  note without a frontmatter block is skipped (the memory overlay + progress-log still apply).

### 5.1 Optional external proposal route (input → approvable draft)

This compatibility route is not a Public Alpha core dependency. An adapter may
normalize free text to a private `note/1.0` (§4) only when it can use a source value
supported by that versioned contract; a new source requires an additive contract
revision. A **structured `kind: proposal` input** instead STAGES an approvable draft,
so an idea captured outside the suite can surface in the local Approvals queue without
bypassing the same review and writeback rules used by agent sessions.

**Envelope.** A markdown file with leading YAML frontmatter (or the equivalent JSON
object). All fields except `kind`/`project` are optional:

```
---
kind: proposal
project: <project_id>            # MUST exist in memory/projects.json
status: <planned|active|paused|done|archived>   # optional; invalid -> omitted
stage: <free text>               # optional; FREE-TEXT project phase (no enum)
next_actions: [a, b]             # optional
conclusion: <text>               # optional
blocked_by: <text>               # optional
confidence: high|medium|low      # optional (default medium)
---
<optional free-text rationale>
```

**Flow.** input → resolve → DRAFT → Approvals → apply:

1. The host proposal adapter detects `kind: proposal`. `status` (if given) must be
   in the project/1.0 enum, else it is omitted; there must be ≥1 high-value field
   (`status`/`stage`/`next_actions`/`conclusion`/`blocked_by`), else it falls back to
   the note route. `stage` is free-text (no enum check). All text is sanitized (§6),
   and the size/count caps (§9) apply.
2. The `project` must resolve against the registered portfolio before any summary
   object is instantiated. Unresolved input remains in protected inflight state and
   exposes only an opaque resolution action; invalid input is rejected with a reason.
   Neither case may create a `session-summary/1.0`, append a timeline, or invent a
   project.
3. A resolved proposal is written as a minimal `session-summary/1.0` DRAFT
   (`approval_state=draft`, **no `timeline`**) through component-owned protected
   storage. Its `summary_id` is a deterministic host-minted digest of the received
   payload bytes; a connector-declared identifier is never trusted, and repeated submission
   is idempotent.
4. The M3 approval surface (§5) picks the draft up: `generate` lists it in `Approvals.md`;
   on the human tick `approve` applies it via the existing M1 path (progress-log append +
   memory overlay).

**Least-trust note (critical).** A proposal only STAGES a draft for human approval — it
NEVER auto-applies, never creates a project, never runs code. The human Approvals tick
(§5) is the only path into notes/memory; the least-trust boundary (§1) is unchanged.

## 6. Privacy (R10)

- **Personal-zone free-text** (`Inbox/`, `_planning/`, `note/1.0` with `private:true`):
  ingested into Provenance memory and usable by MCP `get_current_context` / local search,
  but **EXCLUDED from the profile/persona pipeline**, and stored in the **protected
  layer**.
- **Protected state is not a connector share.** Optional external adapters receive
  only the public input/result surface and MUST NOT be given the protected drafts,
  journals, raw inbox, profile, or re-identification data. On Windows, component-owned
  commands must reject link/junction/reparse escapes and serialize state changes under
  the worker lock. Host account permissions, transport isolation, and credential
  hardening remain deployment responsibilities rather than suite guarantees.
- The suite-owned summary scaffold contains ONLY the current session's sanitized turns
  and strips the absolute-path `cwd`. The sync layer itself performs no model call.
  A Codex/Claude Code model call is host-managed egress and follows that host's privacy
  settings; the suite MUST NOT describe it as offline merely because the worker is local.

## 7. cwd → project_id resolver

Build a reverse index from the current project portfolio keyed by `linked_repo` (absolute
path, normalized) AND `project_id`. On a session/import event, resolve the `project` from
the event's `cwd`/hint. **Fallback when no match:** keep the event in protected inflight
state and surface only an aggregate `project-resolution` action. Do not build a summary
scaffold, instantiate `session-summary/1.0`, append a timeline, or stage a draft until a
non-empty registered `project_id` resolves. Never auto-author a project spine file in a
human-input zone. Once the user approves and ingests the mapping, a later on-demand pull
resumes the same event. A local read-only inspector MAY expose stable opaque resolution
IDs and repository labels by default; full local `cwd` values require an explicit
show-paths option. It MUST never expose session IDs or transcript paths and MUST never
modify queue, inflight, claim, project, or summary state.

## 8. Agent-host adapters

The first supported hosts are **Claude Code** and **Codex**. They share the normalized
capture contract, not necessarily the same trigger.

### Claude Code

Register **`SessionEnd`** only (enqueue-only, fast, fire-and-forget; it cannot block
teardown). **Do NOT use `Stop` as a fallback** — it fires after every assistant response
and would run the summarizer mid-session. ⚠️ The live `SessionEnd` STDIN payload
(`session_id`, `transcript_path`, `cwd`, `hook_event_name`) MUST be verified on the
actual installed client before wiring.

### Codex

The current adapter is an explicit, on-demand scan of local Codex logs. It MUST preview
what it found before enqueueing, use the same project resolver and redaction path, and
be idempotent on repeated scans. The product MUST NOT advertise an automatic Codex
session-end hook until one is implemented and verified.

**Agent-agnostic capture.** The normalized contract needs only a generic session payload
(`session_id` / `transcript_path` / `cwd` / `event`); Claude Code's `SessionEnd` hook is
the *reference* producer of that payload, not a requirement. The per-session-summary,
review, and memory-refresh logic lives in **portable skill prompts** (plain-markdown
instructions) that any agent can run. So porting to another agent framework is just:
(a) fire that agent's session-end into the same enqueue contract, and (b) run the same
prompts.

### Optional browser-history import

A browser extension MAY export user-selected web conversation history to a local
staging file. It is an import adapter, not a new authoritative store: the user chooses
the range, previews the export, and can delete the local staging artifact. It MUST NOT
send captured conversations to a third-party telemetry service or write directly to
memory/project notes. Browser capture is optional; local agent logs and explicit file
imports remain valid paths.

## 9. Abuse limits

Enforce a per-file size cap and a per-scan count cap on every external staging stream and
agent-log ingest, to bound a compromised connector or runaway agent. Rejected inputs move
to component-owned protected storage with a reason and an age/size budget (no unbounded
disk growth).

## 10. Cross-reference
- Vault zones & the M2 two-section note: [vault-layout.md](vault-layout.md).
- Suite entry, host boundary, and optional integration status:
  [suite-entry-and-ownership.md](suite-entry-and-ownership.md).
- Versioning / additive rules: [versioning.md](versioning.md).

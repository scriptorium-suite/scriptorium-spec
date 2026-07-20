# Trust Model — what the Scriptorium suite promises (and what it doesn't)

> Status: authoritative reference. This document describes the **safety and
> privacy guarantees** that hold across the Scriptorium suite, grounded in the
> actual mechanisms in each tool's source — not aspirations. Where a guarantee
> is conditional, opt-in, or bypassable, it says so. The closing **Limits**
> section is part of the contract: it lists what the suite does *not* promise.

Each guarantee below is tagged with how strongly it holds:

- **always** — unconditional in the relevant code path; no flag disables it.
- **default** — on by default, but an explicit opt-out flag exists.
- **opt-in** — off unless you turn it on.

The three domain products live in separate repos (Steward, Provenance, Lectern)
and are bound by the contracts in this fourth repository (`scriptorium-spec`).
They never call each
other's internals — coupling is reduced to file shapes, which contains the blast
radius of any one tool (**always**; this repo has no importable runtime package).

---

## What you're trusting it with

Two sensitive things, both stored **on your own machine by suite-managed paths**:

1. **Your unpublished research** — your Zotero reference library, paper PDFs, and
   the slide decks you build from them.
2. **Your selected cross-AI history** — supported agent conversations you choose
   to capture, index, and serve back to new sessions as a "second brain."

The rest of this document is how the suite earns that trust. Agent hosts and
optional connectors can transmit content that you explicitly place in their
context; those egress paths are classified in section 3 rather than hidden
behind the phrase "local-first."

---

## 1. Safe writes

Nothing the suite does to your data is a one-way door.

**Steward — Zotero library governance**

- **Dry-run by default** (**always**). Every write subcommand (`apply`, `tag
  apply`, `rollback`, `portfolio`) prints a plan and returns unless you pass
  `--run`; the executing function is only reached under `--run`.
  *(steward `cli.py:177-180`, `246-249`, `265-267`, `291-294`; `--run` defaults false.)*
- **Fail-closed backup gate** (**default**). `apply`/`tag` refuse to write unless
  a *verified* backup exists that is younger than 24h. A missing or unparseable
  backup timestamp is treated as failure, not waved through.
  *(steward `apply.py:99-120`, `BACKUP_MAX_AGE_HOURS=24`; bypassable only via the
  explicit, "NOT recommended" `--no-backup-check`.)*
- **Journal-before-write + rollback** (**always**). Pre-state of every touched
  item is written to disk *before* the first item write; `steward rollback`
  replays it, is library-matched (refuses a journal from a different library),
  and journals current state first so the undo is itself reversible.
  *(steward `apply.py:195-209`, `245-285`; `tagging.py:160-165`.)*
- **No deletes, ever** (**always**). The entire write surface is exactly two POST
  endpoints (`post_items`, `post_collections`). Writes only touch the
  `collections`, `tags`, and `extra` fields and create collections — never delete
  items, collections, tags, attachments, or any other field. Non-managed `extra`
  lines and non-status tags are preserved. No PUT/DELETE exists anywhere in src.
  *(steward `apply.py:206-207`, `tagging.py:125-139,195,200-201`, `zotero_api.py:115-138`.)*
- **No clobbering concurrent edits** (**always**). Every write carries the item's
  captured version; the Zotero API rejects a stale write with HTTP 412. A genuine
  external change is classified as a conflict and left untouched (the run aborts
  and reports it), rather than overwritten.
  *(steward `apply.py:64-88,207,212-229`; test `test_412_real_conflict_aborts_without_clobber`.)*
- **Verified backups** (**default**). A backup is written to a `.partial` dir,
  checked for file/byte-count match and SQLite `integrity_check`, and only then
  renamed to its trusted name; it refuses to back up over Zotero journal/WAL
  residue (i.e. while Zotero is mid-write) unless `--force`.
  *(steward `backup.py:37-57,65-123`.)*

**Provenance — memory-hub writebacks**

- **Append-only, never overwrite human content** (**always**). The progress-log
  writeback only inserts a dated block *inside* a frozen
  `scriptorium:progress-log` marker region; every byte outside the markers (BOM,
  newlines, your prose) is carried through verbatim. A note that lacks the marker
  pair is **refused**, not silently rewritten.
  *(provenance `synclayer/progress_log.py:151-203`; test `test_outside_region_byte_identical`.)*
- **Journaled + reversible + atomic** (**always**). Pre-state (sha256 + bytes) is
  journaled before the atomic temp-file + `os.replace` write; `rollback()`
  restores it.
  *(provenance `synclayer/progress_log.py:106-146,395-405`.)*
- **Single-writer + idempotent** (**always**). Authoritative writes are serialized
  by an exclusive `O_CREAT|O_EXCL` lockfile; re-running after a crash is a no-op
  (entries are keyed by `summary_id`).
  *(provenance `synclayer/worker.py:45-75,275-276,332-334`; test `test_idempotent_same_id`.)*

---

## 2. Privacy

The memory hub holds your whole AI history; here is what keeps it private.

- **Redaction at ingest** (**always**). Before anything is written to the working
  inbox, a deterministic regex ruleset strips API keys, tokens, JWTs, emails,
  IPv4 addresses, URL credentials, and home-dir usernames from string values.
  Every ingester routes through `sanitize_json`.
  *(provenance `redact.py:20-48,104-122`; called in all `ingest/*.py` writers.)*
- **Pseudonymization with a local re-id key** (**default**). Real names /
  institutions / third parties are replaced with stable codes; the
  re-identification map (`aliases.json`) is git-ignored and confirmed untracked —
  it never leaves the machine. A *corrupt* alias map warns loudly on stderr
  rather than silently passing real identities through.
  *(provenance `redact.py:65-101`, `.gitignore`; tests `test_aliases_fail_open_warns`.)*
- **Profile stays session-local and out of memory** (**always**). The personal
  profile/persona is never written into the cross-session memory store and never
  served beyond the read-only `get_profile` tool; a private note is provably
  absent from profile-prep digests.
  *(provenance `memory.py:27-78`, `mcp_server.py:73-78`; test `test_private_note_never_reaches_profile_prep`.)*
- **cwd stripped from the summarizer** (**always**). The LLM-facing summary
  scaffold omits the absolute working directory; the cwd lives only in the
  protected `sync-state/` queue, so an LLM cannot retarget a writeback.
  *(provenance `synclayer/summary.py:81-102`; test `test_scaffold_drops_cwd_keeps_turns`.)*
- **Read-only MCP** (**always**). The memory server exposes exactly five
  read/get tools (`search_brain`, `get_profile`, `list_topics`, `get_portfolio`,
  `get_current_context`); no handler writes or mutates.
  *(provenance `mcp_server.py:35-56,59-187`.)*
- **No personal data in git** (**always**). All data dirs (`inbox/ memory/
  profile/ vault/ sync-state/ …`), the search index, and `aliases.json` are
  git-ignored; only code and docs are tracked.
  *(provenance `.gitignore`; `git check-ignore` confirmed.)*

---

## 3. Local-first, not network-free

The suite keeps its authoritative files local. That does not make every agent or
connector offline. Egress is classified as follows:

- **Suite-managed egress** — a Scriptorium component sends data itself. These
  paths must be explicit, documented, and off by default when they can include
  private research data.
- **Host-managed egress** — Codex, Claude Code, or another agent host sends the
  context selected for a task under that host's own provider and privacy terms.
  The suite cannot claim that traffic as local.
- **Optional connector egress** — a user enables an external provider such as a
  cloud parser or a future public literature-metadata service. The action must
  name what leaves the machine before it runs.

- **Stdlib-only cores, no telemetry** (**always**). Steward and Provenance have
  zero third-party runtime dependencies; neither phones home. Provenance has *no*
  networking imports at all — its only "network" is `urllib.parse` (string
  decoding). Steward's sole outbound surface is its Zotero API client (urllib).
  *(steward `pyproject.toml:26-27`, `zotero_api.py:38-69`; provenance grep finds no socket/http/requests.)*
- **Steward read paths need zero credentials** (**always**). `audit` and `backup`
  operate purely on the local `zotero.sqlite` / data dir; no API key is read or
  sent. The local Zotero API is treated as **read-only** — a write attempt in
  local mode raises rather than mutating.
  *(steward `audit.py:1-8,24-33`, `zotero_api.py:118-120,133-134`.)*
- **Safe while Zotero is open** (**always**). Audit/scaffold readers copy
  `zotero.sqlite` to a tempfile and open it read-only (`mode=ro`), never touching
  the live DB; the temp copy is unlinked in a `finally`.
  *(steward `audit.py:24-33,196-203`.)*
- **Lectern's AI-free compiler is offline** (**always**). The LLM emits only a
  validated Slide-IR (structured JSON over a closed vocabulary); a separate
  deterministic compiler turns IR into native python-pptx objects with no network
  imports, so the same approved IR compiles to the same deck.
  *(lectern `slide_ir/models.py:260-271`, `pptx_compiler/compiler.py:1-5`.)*
- **Known egress paths are named, not implied.** Agent-host model calls are
  host-managed. Lectern is provider-agnostic; on the OpenAI-compatible path you
  can point `base_url` at a **local** endpoint (Ollama / vLLM) so prompts stay on
  your hardware (**opt-in**). Cloud PDF parsing (MinerU) is **opt-in** — without a
  key the parser falls back to a fully local `pdfplumber` parse (**default**).
  The post-render vision critic is **opt-in / off by default**. Any future online
  literature lookup must send only an explicit query or public identifier by
  default, never Provenance memory or unpublished full text implicitly.
  *(lectern `openai_compat.py:14-38`, `router.py:23,44-51`, `graph.py:160`, `server.py:40-53`.)*

- **Browser-history import is a local capture adapter, not telemetry.** The
  supported contract is explicit export/import into a local staging area, with
  range preview before indexing. It does not authorize background uploads or a
  direct write into approved memory.

> See **Limits** below: a cloud-backed agent host, selecting Lectern's Anthropic
> provider, or opting into MinerU *does* send data off-machine. Local-first
> describes storage and defaults; it is not a sandbox.

---

## 4. Human-in-the-loop

The suite prefers a deliberate file edit or click over a hurried chat approval.

- **Steward proposals are offline files** (**always**). `propose` / `tag-scaffold`
  write a credential-free JSON scaffold + a `PROMPT.md` to disk; a human or agent
  edits the file out-of-band; `apply` / `tag-apply` validate it before any network
  write and refuse an untouched, all-prefilled scaffold. The core has no LLM/chat
  client — approvals are file edits, not chat calls.
  *(steward `cli.py:120-161,256-288`, `apply.py:163-167`.)*
- **Provenance Approvals gate** (**always**). Raw timelines apply automatically,
  but high-value claims land in a plain-Markdown approval queue exposed through
  CLI workflows; Obsidian is an optional editor for the same files. Only the
  human `approve` action commits them, and even then it is dry-run unless `--run`.
  *(provenance `synclayer/approvals.py:9-40`.)*
- **Lectern outline gate** — *mandatory in web/API, opt-out in CLI*. The web/API
  flow has a mandatory human outline-approval gate (a LangGraph `interrupt()` that
  is the only edge into compilation; `approve` returns 409 unless the thread is
  awaiting approval) (**always** for web/API). The headless `lectern build`
  **auto-approves** the same gate; the file-contract review (`outline` →
  `build --from-outline`) is **opt-in**.
  *(lectern `graph.py:176-187,224-226`, `app.py:517-525`, `cli/__main__.py:68-71,113-119`.)*
- **A deterministic, AI-free critic** gates outline quality (empty/overflow
  slides, dangling figure refs, broken diagram edges, near-dup titles) before a
  human sees it — no LLM required for the check (**always**).
  *(lectern `critic.py:9-14`, `graph.py:144-167`.)*

---

## 5. Optional compatibility edge — external proposal sources

Mobile capture, messaging front doors, and other automation systems are not part
of the Public Alpha core. If a user enables one, the suite treats every submitted
payload and connector-supplied identifier as **untrusted**. The public guarantee
starts at the host-side adapter boundary, not inside the external system.

- **Staging is not authority** (**always**). A connector may submit through an
  isolated staging boundary or public proposal command, but it does not append to
  project notes, write Provenance memory, or mutate sync state directly. All
  authoritative writes still funnel through the serializing host worker.
  *(spec `sync-layer.md:19-35,109-123`.)*
- **A proposal only stages a human-gated draft** (**always**). The host validates
  and normalizes the payload, mints its own identity, and accepts only permitted
  fields. A valid proposal can become a draft; it never auto-applies, creates a
  project, or runs code. Project resolution is mandatory: unresolved input remains
  pending or is rejected and cannot produce a `session-summary/1.0` with
  `project: null`.
  *(spec `sync-layer.md:109-123,169-190`.)*
- **Read access is minimized and explicit** (**default**). The core adapter does
  not require an external source to read raw research, personal profiles,
  credentials, or protected paths. Any connector that requests additional read
  access must document the selected scope and egress path for the user.
- **Approval scopes remain separate** (**always**). Submitting or filling a draft
  does not authorize high-value claims, project creation, command execution, or
  the later authoritative pull. Each action keeps its own review boundary.
  *(spec `sync-layer.md:109-123,125-142`.)*
- **Recursion-guarded** (**always**). A sync-layer-spawned session sets
  `PROV_SYNC_NO_ENQUEUE=1`; the enqueue hook is a no-op under it, so the tool can't
  feed itself in a loop.
  *(provenance `synclayer/enqueue.py:42-49,83-87`.)*

---

## 6. The contracts themselves

- **Versioned + backward-additive** (**always**). `schema_version` travels inside
  every file; minor = additive, major = breaking; renames are forbidden within a
  major line, and no schema sets `additionalProperties:false`, so a newer-minor
  producer's extra fields are tolerated. The validator dispatches on
  `schema_version` and rejects unknown formats / unsupported majors.
  *(spec `versioning.md:1-19`, `tools/validate.py:125-136`.)*
- **CI conformance + negative fixtures** (**default**). A pytest suite validates
  every `examples/*.json` against its schema with the real `jsonschema` library
  and requires every `tests/fixtures/invalid/*.json` to be rejected by *both* the
  stdlib validator and `jsonschema`, on push-to-main and every PR.
  *(spec `tests/test_schema_conformance.py:64-95`, `.github/workflows/ci.yml`.)*
- **Zero-dependency runtime validator** (**always**). `tools/validate.py` imports
  only `json`, `re`, `sys` — it never imports `jsonschema`, so it stays portable.
  *(spec `tools/validate.py:9-11`.)*

---

## Limits — what this does NOT promise

A trust document is only credible if it's honest about its edges.

**Egress / cloud.**

- **Cloud-backed agent hosts and providers send selected context off-machine.**
  Local-first is a *storage and configuration model*, not an enforced sandbox.
  Codex, Claude Code, and similar hosts follow their own provider settings. Only
  Lectern's OpenAI-compatible adapter honors a custom `base_url`; selecting
  `ASA_LLM_PROVIDER=anthropic` always sends prompts (paper text, evidence digests,
  table samples) to Anthropic's cloud — the Anthropic adapter has no `base_url`
  override.
- **MinerU upload.** Opting into MinerU uploads the full (possibly unpublished) PDF
  to a cloud service — a real off-machine path distinct from the LLM call.
- **"No network" is a code property, not an OS egress block.** It rests on
  stdlib-only + code review; nothing prevents future code or a dependency from
  opening a socket.

**Privacy is high-confidence, not total.**

- **Redaction is pattern-based, not semantic.** It can miss exotic/novel secret
  formats and any PII outside the high-confidence rules (names, phone numbers,
  postal addresses, free-text account numbers are not redacted unless covered by an
  alias), and can over-redact (academic emails, version-like numbers).
- **Pseudonymization is only as complete as `aliases.json`.** Any name/org you
  never added passes through un-de-identified; an *absent* alias map is treated as
  "optional" and silently yields no pseudonymization (only a *corrupt* map warns).
- **The raw/sensitive layer is not redacted.** ZIP exports, the on-machine agent
  logs themselves, and copied attachments (which may carry EXIF-GPS / real names)
  are stored as raw bytes — protected only by being local + git-ignored, not by the
  redaction pipeline.

**Safety-gate caveats.**

- **Steward's backup gate covers the wrong copy relative to writes.** Backups
  snapshot the *local* Zotero data dir, but `apply`/`tag` write the *web* library;
  a fresh verified backup does not guarantee the web library was captured. The real
  safety net for web writes is the per-item journal + Zotero's own sync history.
- **The backup gate is bypassable** with `--no-backup-check`, and the
  Zotero-open residue check with `--force`. Backup verification is structural
  (counts + SQLite integrity), not content-archival, and **no automated restore
  command exists** — restoration is a documented manual procedure.
- **"412 aborts" is conditional.** An unchanged item is silently *retried* with a
  fresh version; a true abort happens only when content actually diverged. There is
  no independent post-write read-back beyond conflict re-fetch for failed keys.
- **Rollback restores fields, not full state** — it doesn't delete collections that
  `apply` created, leaving possibly-empty collections behind.

**External connector isolation is outside the core trust boundary.** The suite can
validate and gate a proposal after it reaches the host adapter, but it does not
guarantee a connector's transport, authentication, account security, sandbox, or
filesystem permissions. A user must grant only the minimum required access and
review the connector's own egress and hardening documentation; misconfiguration
outside the adapter can still expose local data.

**Contract enforcement is partial.** `tools/validate.py` is intentionally
structural (shape, required fields, key patterns, enums, a few ranges) — it is *not*
a full JSON-Schema engine; real conformance runs only in CI, not at runtime in
production. Several invariants are enforced in repos this spec only documents
(Steward's `apply`, Provenance's privacy + sync-layer pipeline); CI guards only
push-to-main and PRs and cannot catch semantic drift the schemas don't encode.

**Plaintext API key.** Steward stores the Zotero API key in plaintext in
`config.toml` (it warns you); the only mitigation is the opt-in `ZOTERO_API_KEY`
env var — there is no OS keyring/encryption. Status/doctor output reports only
presence/source, never key characters; this does not protect the plaintext config
file itself.

---

## Related

This repo: [README](../README.md) · [versioning](versioning.md) ·
[sync-layer](sync-layer.md) · [vault-layout](vault-layout.md) ·
[product-direction](product-direction.md) ·
[suite entry and ownership](suite-entry-and-ownership.md)

> The implementing code for these guarantees lives in the tool repos (Steward,
> Provenance, Lectern); this repo is the contract source of truth, and this
> document maps each promise to the concrete mechanism that backs it.

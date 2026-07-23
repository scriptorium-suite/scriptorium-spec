# Project Portfolio Convention (v1)

How research projects are represented in the user-owned Markdown workspace and
made available to Provenance. The workspace, PDFs, and code remain authoritative;
Provenance provides local indexing, cross-session retrieval, an append-only project
timeline, and human-gated high-value memory.

This convention is part of the Public Alpha candidate defined by
[suite-entry-and-ownership.md](suite-entry-and-ownership.md). A complete target
setup selects at least one agent host. Codex and Claude Code have equal first-class
status in the product contract; canonical workspace installers and Windows golden-path
checks now cover both hosts. Obsidian is an optional Markdown client, not a runtime
requirement.

## Reference Markdown layout

```text
<workspace>/
├── Projects/
│   ├── _总纲.md            # optional portable portfolio view
│   ├── _使用说明.md         # optional maintenance notes
│   └── <project_id>.md     # one project; frontmatter conforms to project/1.0
├── Inbox/                  # optional human-authored capture
└── _planning/              # optional human-authored planning notes
```

`Projects/` is a human-input zone. The user may edit it directly or ask an agent
to edit it. A tool must not replace human-authored prose. The limited approved
frontmatter updates and append-only progress-log region are governed by
[sync-layer.md](sync-layer.md) and [vault-layout.md](vault-layout.md).

The current Provenance Markdown adapter uses the `Projects/*.md` convention. The
thin suite entry now provides preview-first `scriptorium init` and explicit,
no-clobber host installers. Its explicit-root `scriptorium inventory` reports only
suffix-based aggregate routing candidates; a separate reviewed migration plan/apply/
verify/rollback flow handles selected Markdown/PDF sources. Initialization and
inventory alone still MUST NOT imply or authorize migration.

## Frontmatter is the structured contract

The schema ([`schemas/project/v1.json`](../schemas/project/v1.json)) describes the
YAML frontmatter object. Only `schema_version`, `project_id`, `title`, and `status`
are required; the note body remains free-form user-authored Markdown.

```yaml
---
schema_version: project/1.0
project_id: synthetic-xq17-calibration
title: "[SYNTHETIC] XQ-17 calibration demo"
status: active            # planned | active | paused | done | archived
stage: synthetic validation
priority: medium
next_actions: [Validate the generated fixture, Draft the synthetic method summary]
blocked_by: ""
linked_literature: [Demo Library/Synthetic Calibration]
linked_repo: C:/ScriptoriumDemo/projects/synthetic-xq17-calibration
linked_conversations: synthetic-xq17-calibration
updated: 2100-01-03
---
```

`linked_literature` is optional and may contain Steward item keys or collection
paths when the Literature profile is enabled. `linked_repo` is the absolute local
path used to resolve agent sessions to the project. It normally points to the user's
code source; when no separate repository is selected, `scriptorium init` uses the
Markdown workspace so its first host session is still attributable. Provenance does
not take ownership of either location.

## Portfolio views are optional projections

`Projects/_总纲.md` may summarize project stage, status, next action, blocker, and
priority. It can be plain Markdown maintained by the user or a declared generator.
Obsidian users may add Dataview or Bases as an optional enhanced view, but no core
workflow or contract may require either plugin.

Generated dashboards are disposable projections. The individual project files,
not a dashboard or Provenance index, remain the authoritative project records.

## Research execution stays outside project frontmatter

`experiment-run/1.0` and `claim-evidence/1.0` are separate JSON contract files
governed by [research-execution-and-evidence.md](research-execution-and-evidence.md).
They do not restore the removed `project.experiments` field and do not turn a
project Markdown file into a run database. The external executor owns each run
record; the explicit human review workflow owns each claim decision.

## Provenance integration

- Provenance currently ingests supported `Projects/*.md` frontmatter and exposes
  the resulting portfolio/context through its read-only MCP, including
  `get_portfolio` and `get_current_context`.
- `linked_conversations` gives Provenance a stable attribution key, usually the
  repository directory name, for relating captured sessions to a project.
- The host sync layer may append dated blocks only inside the frozen project
  progress-log markers. It may update `status`, `stage`, `next_actions`, and
  `blocked_by` only through the approval, journal, and rollback rules in
  [sync-layer.md](sync-layer.md).
- Low-risk timeline facts may follow the documented append-only path. High-value
  claims must remain staged until the user approves them.

Provenance is authoritative for its normalized cross-session memory, index, and
protected sync state. It is not authoritative for the user's project prose, PDFs,
code, or optional Zotero records.

## Host behavior

Both supported hosts operate on the same project files and contracts, but their
capture triggers differ. Claude Code can use an enqueue-only `SessionEnd` hook;
Codex can use on-demand local-log scanning where no equivalent stable hook exists.
Documentation must not imply identical automatic capture.

The intended working pattern is:

1. Work in the project directory with Codex or Claude Code.
2. Read the authoritative Markdown, PDFs, and code before relying on derived memory.
3. Query `get_current_context(project)` when that project has been ingested.
4. Stage high-value project changes for approval; append only permitted timeline data.
5. Review the optional portfolio view or query `get_portfolio()` across projects.

The thin entry implements `init`, `doctor`, `status`, `inventory`, reviewed
Markdown/PDF migration, `demo`, `pull`, and canonical host-task installers.
Live-host acceptance, a published package, and external beta evidence remain
release gaps.

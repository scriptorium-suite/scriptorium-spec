English | [中文](README.zh.md)

# Scriptorium Spec

> The shared data contracts that let the Scriptorium suite's tools exchange files.

> **Product status: Public Alpha contract release candidate.** The Public Alpha
> target is Windows-first and requires at least one agent host. Codex and Claude
> Code are the two first-class target choices; canonical installers now exist, while
> Claude Code live `SessionEnd` golden-path parity remains a release gap. The user's Markdown workspace,
> PDFs, and code remain authoritative; Provenance supplies local capture, search,
> append-only writeback, and human-gated high-value memory. Zotero, Obsidian, and
> Lectern are optional capabilities, not core requirements.

## Related / 相关文档

This repo: [README](README.md) · [中文 README.zh](README.zh.md) · [CHANGELOG](CHANGELOG.md) · [specs/](specs/) · [schemas/](schemas/)

See the contracts run through a real-interface, synthetic-data workflow in the
[Scriptorium Public Alpha case study](https://github.com/scriptorium-suite/scriptorium/blob/main/docs/case-study.zh-CN.md).

**Suite / 套件:** [scriptorium-spec](https://github.com/scriptorium-suite/scriptorium-spec) (contract SSoT) · [steward](https://github.com/scriptorium-suite/steward) · [Provenance](https://github.com/foxsplendid/Provenance) · [Academic-Slides-Agent / Lectern](https://github.com/foxsplendid/Academic-Slides-Agent) · [.github](https://github.com/scriptorium-suite/.github)

> This repo = the contract SSoT; other repos mirror these contract facts, never fork them.
> Suite entrypoint and component ownership are defined in
> [specs/suite-entry-and-ownership.md](specs/suite-entry-and-ownership.md).

## Overview

Scriptorium Spec defines the file formats used by the **Scriptorium** suite — a
local-first research workflow designed for GitHub-comfortable researchers using
at least one of its two target hosts, Codex or Claude Code, on Windows. Its core works
over an ordinary project directory:
Markdown, PDFs, and code remain user-owned sources of truth. Provenance records
derived project context and high-value claims through an approval-backed memory
workflow; optional tools add reference-library governance and slide output. It
contains JSON Schemas, convention documents, worked examples, and a small
validator. The suite's tools never call each other's internals; they exchange
**files** whose formats are specified here, so any tool — or any agent, or you
with a text editor — can produce or consume them. This repository is the only
hard coupling in the suite.

The three suite tools (developed separately) are:

| Tool | Role |
|---|---|
| **Steward** | Optional reference-library product: Zotero backup → audit → propose → human review → apply → rollback; KB and optional Obsidian exports |
| **Provenance** | Core local archive and reviewed project-memory ledger: capture → redact/pseudonymize → search → append-only timeline + human-gated high-value claims → read-only MCP |
| **Lectern** | Independent, optional academic-report product: paper PDF or `handoff/1.x` → evidence pool → human-reviewed outline → native editable `.pptx` |

The ownership ADR assigns Windows setup, diagnostics, the synthetic demo, and
agent-task registration to the thin suite entrypoint; it does not become another
data store. A local umbrella candidate now implements preview-first `init`, `doctor`,
`status`, explicit-root metadata-only `inventory`, reviewed Markdown/PDF migration,
`demo`, `pull`, canonical host installers, and Windows CI. A published
installer/package, live-host acceptance, and external beta evidence remain gaps.

## Features

- **Twelve exchange formats**, each a JSON Schema (Draft 2020-12):

  | Format | Schema | Produced by | Consumed by |
  |---|---|---|---|
  | `library-kb/1.x` | [schemas/library-kb/v1.json](schemas/library-kb/v1.json) | Steward `export` | Provenance library ingest, Steward workflows, agents |
  | `proposal/1.x` | [schemas/proposal/v1.json](schemas/proposal/v1.json) | LLM / agent / human (equivalent) | Steward `apply` |
  | `handoff/1.x` | [schemas/handoff/v1.json](schemas/handoff/v1.json) | Steward `pick` (1.0 single-paper / 1.1 multi-paper) | Lectern (reads both shapes) |
  | `project/1.x` | [schemas/project/v1.json](schemas/project/v1.json) | human / agent / Markdown-frontmatter adapter | Provenance portfolio/context, optional dashboards |
  | `note/1.x` | [schemas/note/v1.json](schemas/note/v1.json) | host sync layer or optional capture adapter | Provenance protected ingest/search |
  | `session-summary/1.x` | [schemas/session-summary/v1.json](schemas/session-summary/v1.json) | Codex / Claude Code host workflow | Provenance approval flow, project progress-log |
  | `reading-note/1.x` | [schemas/reading-note/v1.json](schemas/reading-note/v1.json) | `read-paper` agent task | Steward renderers, file-based agent workflows, Provenance |
  | `parsed-paper/1.x` | [schemas/parsed-paper/v1.json](schemas/parsed-paper/v1.json) | Steward `parse` (local GROBID) | `read-paper`, synthesis, Steward lineage, Provenance |
  | `lineage-graph/1.x` | [schemas/lineage-graph/v1.json](schemas/lineage-graph/v1.json) | Steward `lineage` + agent typing | Steward renderer, file-based agent workflows, Provenance |
  | `review/1.x` | [schemas/review/v1.json](schemas/review/v1.json) | `synthesize-direction` agent task | Markdown/file output, agent workflows, Provenance |
  | `experiment-run/1.x` | [schemas/experiment-run/v1.json](schemas/experiment-run/v1.json) | external compute executor or agent workflow | file-based agent workflows; Provenance ingest is a release gap |
  | `claim-evidence/1.x` | [schemas/claim-evidence/v1.json](schemas/claim-evidence/v1.json) | agent/human review workflow | human review and file-based agent workflows; Provenance ingest is a release gap |

Lectern currently consumes `handoff/1.x`; it does **not** directly consume
`library-kb/1.x`. Provenance currently ingests library/project/note/session data
and the `parsed-paper`, `reading-note`, `review`, and `lineage-graph` research
artifacts. Ingestion of the new experiment-run and claim-evidence contracts remains
a release gap.

- **Convention specs** for versioning, the Markdown project portfolio, optional Obsidian export/layout, config-root layout, the event/sync layer (`sync-layer.md`), product direction (`product-direction.md`), literature automation (`literature-automation.md`), research execution/evidence (`research-execution-and-evidence.md`), suite entry/ownership, and the trust model (`trust-model.md`).
- **Worked examples** for every format under [`examples/`](examples), kept valid against the schemas.
  Every example and invalid test fixture belongs to a deliberately fictional XQ-17 demo universe.
  Names, papers, identifiers, paths, sessions, dates, and results do not describe real people or research.
- **A stdlib-only validator** ([`tools/validate.py`](tools/validate.py)) that checks the load-bearing constraints — no external dependencies.
- **Stable versioning rule**: `schema_version` travels inside the data; major = breaking, minor = additive; consumers ignore and preserve unknown fields.

## Installation

No installation or packaging — this repo is a set of specifications, examples,
and one self-contained script. Clone it and read:

```
git clone https://github.com/scriptorium-suite/scriptorium-spec.git
cd scriptorium-spec
```

The only runnable artifact, `tools/validate.py`, uses the Python standard
library only (Python 3.x); there are no dependencies to install.

## Usage

Validate all worked examples in Windows PowerShell:

```powershell
$exampleFiles = (Get-ChildItem -LiteralPath .\examples -Filter '*.json').FullName
python .\tools\validate.py $exampleFiles
```

Each file prints `ok` or `INVALID` with per-field error paths; exit code `0`
means all files are valid. The validator dispatches on the `schema_version`
field (e.g. `library-kb/1.0`) and is intentionally minimal — the JSON Schemas
under `schemas/` are the authoritative definition.

To author a file, copy the matching example, edit it, then re-validate.

## Project Structure

```
scriptorium-spec/
├── schemas/                  # JSON Schemas (authoritative format definitions)
│   ├── library-kb/v1.json    # canonical reference-library snapshot
│   ├── proposal/v1.json      # offline, human-reviewable reorganization plan
│   ├── handoff/v1.json       # paper PDF + metadata staged for slides (1.0 + 1.1 multi-paper)
│   ├── project/v1.json       # research-project record (Markdown frontmatter is one adapter)
│   ├── note/v1.json          # free-text capture envelope
│   ├── session-summary/v1.json # Codex/Claude Code session writeback (timeline + gated claims)
│   ├── reading-note/v1.json   # per-paper staged interpretation (4 optional reading levels)
│   ├── parsed-paper/v1.json   # normalized local parse of a paper PDF (sections + refs + figures/tables)
│   ├── lineage-graph/v1.json  # a research direction's citation 脉络 (nodes + typed edges)
│   ├── review/v1.json         # direction synthesis (narrative sections + comparison table)
│   ├── experiment-run/v1.json # observation of one external research-compute attempt
│   └── claim-evidence/v1.json # reviewable claim with precise evidence links
├── examples/                 # valid examples per format, including compatibility variants
├── specs/                    # convention documents
│   ├── versioning.md         # schema_version rules; ignore/preserve unknown fields
│   ├── obsidian-export.md    # optional Obsidian projection + Zotero extra-field conventions
│   ├── config-root.md        # ~/.config/scriptorium/<tool>/, precedence, secrets rules
│   ├── project-portfolio.md  # Markdown workspace project records + optional dashboard
│   ├── sync-layer.md         # host capture/approval layer: single worker, append-only
│   ├── vault-layout.md       # Markdown workspace layout and ownership
│   ├── product-direction.md  # Public Alpha product decisions
│   ├── suite-entry-and-ownership.md # suite entrypoint + component boundaries
│   ├── literature-automation.md # on-demand literature refresh (optional weekly opt-in) + digest
│   ├── literature-reading.md # staged reading + direction synthesis
│   ├── research-execution-and-evidence.md # external runs + human-gated claims
│   └── trust-model.md        # suite safety/privacy guarantees by theme + honest limits
├── tools/
│   └── validate.py           # minimal stdlib-only structural validator
├── CHANGELOG.md              # version history
└── LICENSE                   # Apache-2.0
```

### Current package and CLI names

Steward's source package is `scriptorium-steward` and its CLI is `steward`.
Provenance currently exposes the `prov-*` CLIs. Lectern is a workspace whose
headless CLI is `lectern`. A single suite installer/package has not shipped yet;
the entrypoint ownership ADR defines that Public Alpha release boundary.

## Status

**Public Alpha contract release candidate: v2.3.0.** This worktree adds the
experiment-run and claim-evidence contracts; it does not claim that a corresponding
tag or every component version is already published. Local cross-repository and
Windows acceptance paths cover the `init`/`doctor`/`status`/`inventory`/reviewed
migration/`demo`/`pull` entry, canonical host installers, and an install lifecycle,
but fresh remote CI, live-host acceptance, a packaged suite installer, and external
beta evidence remain product gaps.
The event/sync-layer contracts (`note/1.0`, `session-summary/1.0`) are
implemented in Provenance, as is local ingestion of parsed-paper/reading-note/review/
lineage. Provenance ingestion of experiment-run/claim-evidence is not yet implemented.

## License

[Apache-2.0](LICENSE).

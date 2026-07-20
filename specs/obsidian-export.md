# Optional Obsidian Literature Export Convention (v1)

How the optional Steward/Obsidian adapter materializes reference-library records
as derived notes. Obsidian is not required by the Public Alpha candidate core.
The target setup selects at least one of the equally ranked Codex and Claude Code
hosts; canonical installer and golden-path parity remain release gaps. Both target
the user's Markdown workspace, PDFs, and code. Those source files (and Zotero
itself, when used) remain authoritative.

Suite entrypoint and component ownership are defined in
[suite-entry-and-ownership.md](suite-entry-and-ownership.md).

> **Lean-vault update — see [vault-layout.md](vault-layout.md).** The reference
> layout no longer requires a full library mirror. Notes may be materialized on
> demand or surfaced through `Reviews/` digests. Provenance may index metadata and
> approved project memory, but it is not the authority for the original PDF,
> Markdown note, code, or Zotero record.

## Vault layout

```
<optional-vault>/
├── Literature/            # materialized library notes — OWNED by Steward, derived
├── Reviews/               # *.json authoritative contracts; *.md derived renders
├── reading-notes/         # *.json authoritative notes; *.md/_index.md projections
└── MOC/
    └── 文献库 MOC.md       # optional literature index — OWNED by Steward, derived
```

Ownership rule: a tool only creates/overwrites its declared paths or file patterns;
mixed directories do not have one blanket owner. A renderer may replace its marked
`*.md` projection but MUST NOT overwrite/delete authoritative contract `*.json` files.
Any materialized `Literature/` note and the literature MOC are **fully derived**:
Steward may regenerate its own outputs on export. Users must not treat those
files as the only copy or hand-edit them as authoritative research notes; keep
user-authored notes in the Markdown workspace or `reading-notes/` workflow.

The earlier full-vault `Conversations/` / `Attachments/` / `Home.md` mirror is
not part of this adapter convention. Provenance remains usable without an
Obsidian vault.

## Note file naming

```
<FirstAuthorLastName> <Year> <TitleSlug>.md
```

- `TitleSlug`: title with `\/:*?"<>|#^[]` and newlines replaced by spaces,
  whitespace collapsed, trimmed to ≤ 70 characters total filename budget.
- Missing author → `Unknown`; missing year → omitted.

## Frontmatter fields

| Field | Type | Source |
|---|---|---|
| `zotero-key` | string | item key (stable join key — consumers should use this, not the filename) |
| `title` | string | truncated to 180 chars |
| `authors` | list | last names, max 8 |
| `year` | number or null | parsed year |
| `doi` | string | DOI or empty |
| `folders` | list | collection paths |
| `tags` | list | `literature` + ai-tags (prefix stripped) |
| `read-status` | string | reading-list status or `Unknown` |

## Note body (in order)

1. `# <title>`
2. `> [!tip] TLDR` callout (when a TLDR exists)
3. `[在 Zotero 中打开](zotero://select/library/items/<KEY>)` deep link
4. `PDF: \`<path>\`` line(s), when available (a derived pointer, not authority;
   it may be machine-specific or stale)
5. `## 摘要` + abstract (when present)

## MOC structure

`MOC/文献库 MOC.md`: one `## <collection path> (<count>)` section per primary
folder, entries sorted by filename:

```
- ✅[[Literature/<note>|<note>]] — <tldr>     (✅ = Read, 📖 = In Progress, none = unread/other)
```

## Optional cross-linking with Provenance

Co-location in one vault is optional. When users choose it, derived literature
notes may link to project notes through stable ids, `[[wikilinks]]`, and shared
tags. Provenance can ingest supported project/library contracts and expose them
through read-only MCP without owning or rewriting the original source files.

Neither tool rewrites the other's tool-owned folders. Provenance ingestion of
`reading-note/1.0`, `review/1.0`, and `lineage-graph/1.0` is not implemented yet
and remains a Public Alpha release gap.

## Zotero extra-field conventions (write-side)

Steward stores per-item data in the Zotero `extra` field, one line each:

```
TLDR: <one-sentence summary>
Read_Status: <New|To Read|In Progress|Read|Not Reading>
Read_Status_Date: <ISO 8601 UTC>
```

Constraints (required by the zotero-reading-list plugin parser):
- exactly ONE `Read_Status:` line per item (0 or >1 → plugin shows nothing),
- the value must match a configured status name exactly,
- lines start at column 0; other extra content is preserved untouched.
- machine tags are written with the `ai:` prefix and tag type 1 (automatic),
  so they are visually and programmatically separable from human tags and can
  be rolled back wholesale.

# Literature-Reading Expansion — Design `[P1–P3-core + P4-core ratified & built · P3+/P4-tail remaining]`

> **Status (2026-06-22):** architecture approved; **P1–P3-core + P4-core ratified & built.**
> The contracts sketched here are now ratified additive schemas under `schemas/`
> (`reading-note/1.0`, `parsed-paper/1.0`, `lineage-graph/1.0`, `review/1.0`), with
> the Steward CLI (`parse`, `lineage`, `lineage-render`) + skills (`read-paper`,
> `synthesize-direction`) shipped. **Remaining:** P3+ local-embedding recall, P4 tail
> (OpenAlex beyond-library 谱系), direct Provenance ingestion of parsed/reading/review/
> lineage artifacts, and canonical Codex/Claude Code task installers. The current
> skill files are usable from their existing host-specific location; host parity is
> a Public Alpha release gap. This EXTENDS
> the literature flow (Steward `library-kb` + `review`, see
> [literature-automation.md](literature-automation.md)) with **staged reading** +
> **research-direction synthesis**; it supersedes nothing.
>
> **Decisions baked in (user, 2026-06-22):** full 4-level reading ladder; query-driven
> direction synthesis → timeline/lineage + review note + comparison table; **HYBRID**
> (adopt plugins for reading/annotation, the suite builds staged-read + synthesis);
> **local embeddings allowed** (on-device, no egress — revisits product-direction R17);
> **lineage from your own library only** to start (GROBID reference edges, fully local).

## 1. Goal
Turn "a flat library with one-line TLDRs" into a **staged, agent-driven reading +
synthesis** experience: read any paper at the depth you need, on demand; and ask a
question to get a systematic synthesis of that research *direction* (lineage +
narrative + comparison). All local-first, agent-native, on the suite's file contracts.
The suite code does not make the generation call; a cloud-backed Codex, Claude Code,
or other host sends the task context under that host's provider settings.

## 2. Architecture spine (components + ownership)
| Component | Role | Owner |
|---|---|---|
| **Read rail — local Zotero MCP** (`zotero-mcp`, read-only, local API/no-key, semantic search local-or-off) | the agent's live window into the library (metadata / full-text / annotations / notes); complements Steward's batch `library-kb` | adopt (plugin) + a registration note |
| **Human reading — PDF++** (optional Obsidian integration) | in-vault PDF read + **markdown** annotations (survive the plugin; file-contract-clean) | optional adopted plugin |
| **Parse layer — GROBID** (optional richer local parser later) | PDF → structured files (sections + reference list), **local** | **Steward** (`parse`) — emits contract files; direct Provenance ingestion is not implemented |
| **Index — current + target** | current Provenance FTS5 indexes `library-kb`; parsed sections and optional local embeddings are the P3+ target | **Provenance** — parsed/reading/review/lineage ingestion and embeddings remain release gaps |
| **Generation = the agent, in-session** (NO LLM client in suite code) | Codex or Claude Code writes the reading/synthesis prose; cloud egress, if any, belongs to the selected host | current host-specific tasks; the current thin entry does not yet package canonical two-host literature-task installers |
| **Lineage — own-library** (GROBID reference edges → typed relations → graph file) | the direction 脉络 / lineage | **Steward** (`lineage`) |
| **Agent hosts — Codex / Claude Code** | drive staged reading + synthesis over the same files and public tools | both are first-class targets; installer parity remains a release gap |

## 3. New contracts (additive, scriptorium-spec; ratified — full JSON Schema under `schemas/`)
### `reading-note/1.0` — per-paper staged interpretation
- `id` = Better BibTeX **citekey** (universal cross-system join); `zotero_key`, `doi`.
- `read_status` (from zotero-reading-list), `created`, `generated_by`.
- `stages` (each OPTIONAL, filled on demand):
  - `glance`: `{ tldr, tags[], key_findings[] }`
  - `close_read`: `{ question, method, data, results, figures[] }`
  - `deep_read`: `{ critique, reproducibility, limits, relation_to_my_work }`
  - `situate`: `{ direction, lineage_refs[] }`
- `sources`: links to the PDF++/Zotero annotations + the parsed structured file.
- **Anti-fabrication:** figures/data/citations reference the parsed file, never invented.

### `lineage-graph/1.0` — a research direction's 脉络 (own-library to start)
- `direction`: `{ query, scope_method, created }`.
- `nodes`: `[{ citekey, title, year, cluster }]`.
- `edges`: `[{ from, to, relation ∈ cites|extends|supersedes|method-of|contrasts, evidence }]`.
- `clusters`: `[{ id, label }]`; `timeline` (year-ordered node ids).
- Render targets: the canonical **self-contained `Reviews/` lineage note** (native-Obsidian
  Mermaid + timeline + Dataview edge table; see "Lineage render" below), plus opportunistic
  **Breadcrumbs** frontmatter (see relationship convention) + ExcaliBrain/Dataview.

### `review/1.0` — direction synthesis (narrative + table)
- `direction`; `sections[]` (narrative, outline→draft→critique shape);
  `comparison_table` (rows = papers by citekey, cols = method/data/result/…);
  `gaps[]`; `priority_reads[]`; `lineage_ref` (→ `lineage-graph`).
- **Anti-fabrication** (same guarantee Steward `review` has today): the comparison
  table + citations are built FROM the parsed files + `library-kb`, never the LLM.

### relationship-field convention — Breadcrumbs-compatible frontmatter keys
- A small spec fixing the frontmatter keys (`cites` / `extends` / `supersedes` /
  `method-of` / `contrasts`) so the agent-synthesized lineage is **plain markdown the
  whole suite reads**, not locked in a plugin (borrowed from Breadcrumbs/PDF++ ethos).

#### Convention (ratified, 2026-06-22)
The five `lineage-graph/1.0` edge relations are the **canonical relationship vocabulary**,
and they double as the frontmatter keys the agent writes onto each paper note. When the
agent lands a `lineage-graph` edge `{ from, to, relation }`, it appends the target
citekey to the matching key in the **`from` note's** YAML frontmatter — one key per
relation, value = a list of `[[wikilinks]]` (or bare citekeys) to the targets:

```yaml
---
citekey: example2100Xq17Robust
cites: ["[[example2097Xq17Principles]]"]
extends: []
supersedes: ["[[example2099Xq17Drift]]"]
method-of: ["[[example2097Xq17Principles]]"]
contrasts: ["[[example2098Xq17Baseline]]"]
---
```

- **Keys = the edge `relation` enum, verbatim.** No other relationship keys. This is the
  one place the enum, the schema, and the markdown agree, so any reader (Breadcrumbs,
  ExcaliBrain, Dataview, a plain text editor, or another suite tool) sees the same graph.
- **Direction:** the key lives on the **source** (`from`) note and points to the `to`
  target — the edge's natural reading ("A `extends` B" → `extends: [[B]]` in A's note).
- **Breadcrumbs hierarchy mapping** (suite default, configured in the vault's Breadcrumbs
  settings): `extends`/`method-of` → *up*; `supersedes`/`cites` → *down*; `contrasts` →
  *same*. The keys are plugin-agnostic; this mapping is only how Breadcrumbs renders them.
- The `lineage-graph` JSON file remains the **machine source of truth** (it carries
  `evidence`, clusters, timeline); the frontmatter is the human-/plugin-readable
  projection of its edges. They never disagree because both are written from the same
  edge list.
- **Where/when the frontmatter is written (lean-vault clarification):** per the lean-vault
  policy ([vault-layout.md](vault-layout.md)), per-paper notes are usually **not** in the
  vault, so frontmatter-on-paper-notes is **opportunistic** — written by
  `steward lineage-render --stamp-notes` **only where a note already exists**, and
  **merge-not-clobber** (it appends the target citekey to the matching key, never
  rewrites the user's frontmatter). The **always-available** render is the self-contained
  `Reviews/` lineage note below; the frontmatter keys + Breadcrumbs hierarchy mapping
  above are unchanged — this only fixes WHERE/WHEN they land.

### Lineage render — the self-contained `Reviews/` note
The **canonical render** of a `lineage-graph/1.0` is a single self-contained note,
`Reviews/<slug>.lineage.md`, holding three views of the same edge list:

- a **native-Obsidian Mermaid** graph (zero plugin),
- a year-ordered **timeline**, and
- a **Dataview edge table** (`from` · `to` · `relation` · `evidence`).

This self-contained note is the canonical render because per-paper notes are
**lean-vault evicted** ([vault-layout.md](vault-layout.md): `Literature/` is not
full-mirrored, so per-paper frontmatter is not reliably present), whereas `Reviews/` is
the tool-owned derived view that is always materialized. The render is a **deterministic
projection** of the `lineage-graph/1.0` JSON (the machine **source of truth** — it carries
`evidence`, clusters, timeline); it is **idempotent** and writes **only** into the
tool-owned `Reviews/` view. The per-note Breadcrumbs/ExcaliBrain frontmatter
(`--stamp-notes`, above) is the opportunistic enhancement layered on top where notes
already exist; it is **not** a new contract — both renders are written from the same
edge list, so they never disagree.

## 4. Interfaces (skills / CLI; repo)
- **`read-paper` skill (staged)** — input a paper (citekey/selection) + target depth;
  the agent reads via the Zotero MCP (live full-text) or the parsed file + your
  annotations; writes/updates a `reading-note/1.0`; bumps Read-Status. The 4 levels =
  4 invocable depths (`glance` / `close` / `deep` / `situate`). *[repo skill]*
- **`synthesize-direction` skill** — input a question/topic; the agent scopes papers
  (MCP search + `library-kb`; optional local-embedding recall after P3+),
  retrieve→rank (PaperQA2 shape),
  and builds the contract outputs. Direct Provenance archival of review/lineage files
  is not implemented. *[current host-specific task]*
- **`steward parse`** — PDF → structured file through the local GROBID backend and
  a pluggable parser seam; Docling/MinerU backends are not bundled. *[Steward CLI]*
- **`steward lineage`** — build a `lineage-graph` from parsed reference lists (own-library). *[Steward CLI]*
- **`steward lineage-render`** — deterministically project a `lineage-graph/1.0` into the self-contained `Reviews/<slug>.lineage.md` (native-Obsidian Mermaid + timeline + Dataview edge table); `--stamp-notes` opportunistically writes Breadcrumbs frontmatter onto already-materialized paper notes (merge-not-clobber). *[Steward CLI]*
- **`steward read-render`** — deterministically project a `reading-note/1.0` into a browsable, self-contained Obsidian note `reading-notes/<citekey>.md` (YAML frontmatter + a `## ` section per FILLED stage — 速览/精读/深读/串联定位 — + situate `lineage_refs` as `[[citekey]]` wikilinks + a `## 标注 · Annotations` section — highlight text inlines as a blockquote, a URI/path reference as a link — + a links block); a `close_read.figures[]` image path inlines as an Obsidian embed `![[path]]` (caption text otherwise — render-support only: actual figure images need a layout parser that emits image files, e.g. local MinerU; GROBID/parsed-paper carry caption text only). Optional `--kb` enriches the frontmatter with title/authors/year from `library-kb/1.x` (reading-note carries none). The `.json` stays the machine SSoT; the `.md` is re-rendered idempotently. The `[[citekey]]` library link resolves because `steward export` writes a `citekey` alias onto each `Literature/` note (from the item's `Citation Key:` extra-field line → the optional `citekey` introduced in `library-kb/1.1`; historical 1.0 snapshots remain readable). *[Steward CLI]*
- **`steward read-index`** — scan a vault's `reading-notes/*.json` and emit one overview note `reading-notes/_index.md` (the reading status dashboard): status-grouped wikilink sections (To Read / In Progress / Read / Not Reading / no-status), a full table (citekey · title · year · status · stages · tags), and a Dataview block (static views serve non-plugin users). Deterministic, idempotent overwrite of `_index.md` only; the per-paper `.json` files stay the SSoT. *[Steward CLI]*
- **Index** — current FTS5 covers `library-kb`; parsed-section indexing and optional
  SentenceTransformers embeddings are planned P3+ work. *[Provenance release gap]*
- **Provider boundary** — the selected agent host owns generation egress; optional
  local retrieval models, when implemented, stay on-device. *[shared contract]*

## 5. Data flow
### A. Staged reading of one paper (depth driven off Read-Status)
1. **速览** — from `library-kb` (Steward already emits TLDR/tags) → `reading-note.glance`. (To-Read)
2. You open in PDF++/Zotero, annotate → annotations captured (markdown / Zotero API).
3. **按需精读** — `read-paper close` → agent reads full-text (MCP) + parsed sections + your annotations → `reading-note.close_read`. (In-Progress)
4. **深度审读** — `read-paper deep` → agent + **Provenance memory** (your projects) → critique/limits/relation.
5. **串联定位** — `read-paper situate` → place in the direction lineage → `reading-note.situate` + lineage edges. (Read)

### B. Direction synthesis (query-driven)
1. You ask a question/topic.
2. **Scope** — agent retrieves relevant papers (MCP search + `library-kb` + local-embedding recall).
3. **Parse-on-demand** — ensure scoped papers are GROBID-parsed.
4. **Retrieve + rank** evidence (PaperQA2 shape: search → gather-evidence → rank).
5. **Lineage** — GROBID reference edges among the scoped papers → typed relations → `lineage-graph/1.0`.
6. **Synthesize** — outline → draft → critique (AutoSurvey shape) → `review/1.0` (narrative + comparison table), anti-fabrication.
7. **Land** — write review + lineage contract files and optional Markdown/Obsidian
   projections; link reading notes. Direct Provenance ingestion remains a release gap.

## 6. R17 revisit + trust-model impact
- **Local embeddings are allowed but not shipped.** The P3+ target may use an optional
  on-device model; absence must degrade to current FTS5 rather than break the core.
- **Cloud MinerU is explicit optional egress.** Enabling it uploads the selected full PDF.
  The suite cannot assume that PDF is published: an unpublished manuscript requires a
  clear warning and a local path. Steward's current `parse` uses local GROBID; Lectern
  keeps its separately configured parser path.
- **Agent-host generation is host-managed egress.** The selected context may contain
  private project material, so Codex/Claude Code provider settings and user selection
  matter. Suite-owned code adds no hidden generation call or telemetry.

## 7. Phasing (build order)
- **P1 · read rail + staged-read MVP** ✅ *(shipped 2026-06-22)* — adopt Zotero MCP + PDF++; `read-paper` skill (4 depths); `reading-note/1.0`. **Browsable render landed** *(2026-06-28)*: `steward read-render` projects a `reading-note/1.0` into a self-contained `reading-notes/<citekey>.md` (frontmatter + a section per filled stage + `[[wikilink]]` lineage, optional `--kb` enrichment, idempotent — `.json` stays SSoT), so **a read paper now persists as a browsable Obsidian note**, not just a JSON. *(Render is a deterministic projection of `reading-note/1.0`, not a new contract.)* **Render polish + overview** *(2026-06-28)*: read-render gained a `## 标注 · Annotations` section (highlight text → blockquote, reference → link) and figure-image embeds (`![[path]]` when a `figures[]` entry is an image path — render-support only, needs an image-emitting parse like local MinerU; GROBID carries captions only); `steward read-index` builds the `reading-notes/_index.md` status dashboard; and `steward export` now writes a Better BibTeX `citekey` alias onto each `Literature/` note so `[[citekey]]` library links resolve suite-wide (the additive `library-kb/1.1` contract introduces the optional `citekey` field while 1.0 remains readable). *(All other changes here are projections/render-support; the library-kb minor bump is the contract change.)*
- **P2 · local parse layer** ✅ *(shipped 2026-06-22)* — `steward parse` with the
  local GROBID backend plus a pluggable seam (`parsed-paper/1.0`); Docling/MinerU
  backends are not bundled. It feeds 精读/对比表 and remains independent of
  Lectern's separately configured parser path; see §6.
- **P3-core · direction synthesis** ✅ *(shipped 2026-06-22)* — `synthesize-direction` skill + `review/1.0` + `lineage-graph/1.0` (own-library) + relationship-field convention + `steward lineage`. *(Scoping uses FTS5 / Zotero MCP / `library-kb`.)*
- **P3+ · semantic recall** — local-embedding index (bge-m3 + sqlite-vec, Provenance optional extra) to strengthen synthesis scoping beyond keyword recall.
- **P4-core · lineage render** ✅ *(shipped 2026-06-22)* — deterministic `steward lineage-render` projects an (agent-enriched) `lineage-graph/1.0` into a self-contained, tool-owned `Reviews/<slug>.lineage.md`: a **native-Obsidian Mermaid** graph (zero plugin), a year-ordered timeline, and a Dataview edge table. Breadcrumbs/ExcaliBrain per-note frontmatter is the **opportunistic** enhancement (`--stamp-notes`, written only onto already-materialized paper notes). *(Render is a projection of the existing `lineage-graph/1.0`, not a new contract — see §3 "Lineage render".)*
- **P4 (tail) · beyond-library 谱系** — (later, optional) OpenAlex for lineage edges beyond your own library.

## 8. Resolved design targets and current gaps (2026-07-15)
1. **Index home target = Provenance.** Current FTS5 covers library metadata. Parsed
   sections, reading notes, reviews, lineage graphs, and optional embeddings are not yet
   ingested; each remains a Public Alpha release gap.
2. **Task home migration.** The current implementations live in Steward's
   host-specific `.claude/skills/` directory. Canonical task content and both Codex/
   Claude Code literature-task installers are not yet packaged by the current umbrella entry; host folders become
   installation targets rather than the suite-wide source of truth.
3. **No suite-owned generation client.** Reading and synthesis reasoning runs in the
   selected agent host. Any cloud model traffic is host-managed egress; the suite owns
   deterministic parsing, retrieval, anti-fabrication tables, and file contracts.
4. **Embedding candidate, not dependency.** BAAI/bge-m3 via `sentence-transformers`
   and `sqlite-vec` remains a possible optional P3+ stack. It is not installed or
   required by the current stdlib Provenance core.

# Configuration Root Convention (v1)

All Scriptorium tools resolve configuration the same way, so a user learns it once.

## Locations

```
~/.config/scriptorium/<tool>/        # per-tool config home
~/.config/scriptorium/<tool>/config.toml
~/.config/scriptorium/scriptorium/   # thin suite entry configuration
~/.config/scriptorium/scriptorium/config.toml
```

- Windows: the same `~/.config/...` path is used (consistency beats platform purity);
  `%USERPROFILE%` is `~`.
- Override the family root with `SCRIPTORIUM_CONFIG_DIR`.
- Tools with an established data-root variable keep it (Provenance: `PROVENANCE_HOME`).

## Thin-entry configuration

The `scriptorium` tool name belongs to the umbrella entry described in
[`suite-entry-and-ownership.md`](suite-entry-and-ownership.md). Its configuration
MAY select enabled components, component paths, a Markdown workspace, an agent-host
adapter, and compatibility versions. The current entry writes this configuration
only through an explicit, preview-first `scriptorium init --run`.

A complete Public Alpha configuration MUST select at least one supported agent
host (`codex`, `claude-code`, or both). A host-less configuration MAY be retained
for deterministic diagnostics/import/search, but `doctor` MUST report the suite as
incomplete rather than ready.

The entry configuration is orchestration metadata only. It MUST NOT copy or become
authoritative for component-specific credentials or business data. Each component's
own config remains the master for its settings; the entry passes explicit paths or
public CLI flags rather than editing component config silently.

## Precedence

CLI flags  >  environment variables  >  config file  >  built-in defaults.

## Established environment variables

| Variable | Tool | Meaning |
|---|---|---|
| `ZOTERO_API_KEY` | Steward | Zotero Web API key (write ops). Community de-facto standard name. |
| `ZOTERO_LIBRARY_ID` | Steward | numeric user/group library id |
| `ZOTERO_LIBRARY_TYPE` | Steward | `user` (default) or `group` |
| `ZOTERO_LOCAL` | Steward | `true` → read via the local API (127.0.0.1:23119, read-only, no key needed) |
| `PROVENANCE_HOME` | Provenance | data root (inbox/output/vault/...) |
| `SCRIPTORIUM_CONFIG_DIR` | all | overrides `~/.config/scriptorium` |

## Secrets rules

- API keys never go into a git repository; config files holding keys are
  user-local only. Prefer environment variables in shared/CI environments.
- Commands, exceptions, logs, dry-run plans, `status`, `doctor`, and `--paths`
  MUST NOT print secret values. They MAY report only whether a secret is set and
  which configuration layer supplied it (for example, `ZOTERO_API_KEY: set via
  environment`). There is no `--show-secrets` escape hatch.
- Error reporting MUST NOT dump the process environment or complete config file.
  A diagnostic bundle requires an explicit user action and MUST redact credentials
  before it is written.
- Every tool provides a `status` (or `--paths`) command printing: where config
  was loaded from, which exchange files it reads/writes, and the last
  state-file versions — the user can always answer "who reads what".

## State files

- Continuous pipelines (export/sync) keep incremental state (last Zotero
  library version for `?since=`) separate from one-shot wizard journals
  (backup manifests, applied proposals + rollback baselines). Journals are
  append-only audit artifacts; state files are disposable caches.
- Thin-entry readiness/compatibility caches are disposable and MUST NOT
  contain credentials, raw conversation text, paper content, or project prose.

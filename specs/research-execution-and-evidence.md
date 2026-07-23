# Research Execution and Claim Evidence (v1)

This convention connects external research execution to Scriptorium's reviewed
project memory without turning the suite into a code runner or treating a metric
as a scientific conclusion.

The two contracts are deliberately small:

- `experiment-run/1.0` records what one external executor ran and observed;
- `claim-evidence/1.0` records one bounded claim, precise links to evidence, and
  a separate human-review state.

Both are ordinary JSON files. They add no daemon, scheduler, sandbox, provider,
or implicit network access.

## 1. Ownership and producer/consumer map

| Contract | Master / producer | Consumers |
|---|---|---|
| `experiment-run/1.0` | The external executor or agent workflow that observed the run | file-based agent workflows; Provenance ingest is a release gap |
| `claim-evidence/1.0` draft | The host review workflow that formulated the candidate claim | the human review surface; no authoritative consumer before review |
| `claim-evidence/1.0` accepted/rejected/superseded | The explicit human review workflow | file-based agent workflows; Provenance ingest is a release gap |

The thin Scriptorium entry may validate, route, and report aggregate readiness for
these files. It does not own their contents, execute their code references, or set
their review decisions.

## 2. `experiment-run/1.0` is an observation, not an instruction

An experiment-run file describes a bounded attempt after an executor has started
it. It contains:

- a stable `run_id` and owning `project`;
- an objective and lifecycle `status`;
- a reproducibility-oriented `execution` reference with the runner, code,
  environment, effective parameters, and named random seeds;
- optional input/output/log artifacts and content hashes;
- optional machine-observed numeric metrics;
- producer identity in `generated_by`.

`execution.code_ref` is a version/entrypoint locator. A consumer MUST NOT interpret
it as a shell command or permission to run code. Creating, validating, importing,
or reading an experiment-run file never authorizes:

- command execution;
- package installation;
- network access;
- credential use;
- access to an unselected source directory.

An executor may replace its own `running` record as the run progresses. Once the
record reaches `succeeded`, `failed`, or `cancelled`, consumers SHOULD treat that
`run_id` as immutable. A retry is a new run with a new `run_id`; it may refer to
the same code and inputs.

A failed run requires a redacted `failure_reason`. Producers MUST remove secrets,
credential-bearing URLs, and private absolute paths from contract records and
logs before sharing them. Artifact entries should prefer stable logical ids,
workspace-relative locators, and SHA-256 hashes.

`execution.parameters` records the effective non-secret configuration, not just
defaults from a source file. `execution.random_seeds` records each stochastic
subsystem separately (for example Python and NumPy); a deterministic run uses an
empty object. Neither field may contain credentials or secret-bearing URLs.

Metrics are observations under a declared evaluation setup. They do not become an
approved scientific conclusion merely because the run succeeded or the file
validates.

## 3. `claim-evidence/1.0` separates evidence from governance

Each file contains one proposition in `statement`. Two independent fields prevent
the common failure mode where an agent's plausible sentence silently becomes a
project fact:

- `epistemic_status` describes what the currently linked evidence indicates;
- `review_state` records the human governance decision.

The v1 states are:

| Axis | States |
|---|---|
| Evidence | `speculative`, `partially-supported`, `supported`, `contradicted`, `mixed`, `unresolved` |
| Review | `draft`, `accepted`, `rejected`, `superseded` |

Validation is not approval. A well-formed `draft` remains a candidate. Only the
explicit review workflow may set `accepted`, `rejected`, or `superseded`.

Every explicit `accepted`, `rejected`, or `superseded` decision MUST record
`reviewed_at`. In addition, an accepted claim:

1. MUST contain at least one evidence link;
2. MUST NOT remain `speculative`.

A superseded claim MUST identify its replacement in `superseded_by`. Rejection or
supersession keeps the historical record reviewable; it does not delete the old
statement or its evidence.

## 4. Evidence links

Every evidence entry identifies:

- `relation`: `supports`, `contradicts`, `qualifies`, or `context`;
- `source_type`: an extensible lowercase class such as `experiment-run`,
  `parsed-paper`, `reading-note`, or `artifact`;
- `source_id`: the stable id of that source;
- `locator`: the precise metric, section, page, figure, table, or paragraph;
- optional `sha256` and a short explanatory `note`.

The link points to evidence; it does not copy the source into the claim record.
`note` is an explanation, not a substitute for the source. A consumer SHOULD
resolve and verify the linked source before presenting a claim as supported.

Evidence from an experiment-run normally uses:

```text
source_type = experiment-run
source_id   = <run_id>
locator     = metrics[<metric-name>] or artifacts[<artifact-id>]
```

Literature evidence should point to a stable paper/reading record and an exact
section, page, figure, table, or paragraph locator whenever available.

## 5. Trust and lifecycle

The minimum workflow is:

```text
external executor
  -> experiment-run/1.0
  -> agent proposes claim-evidence/1.0 (draft)
  -> user reviews evidence and wording
  -> accepted / rejected / superseded
  -> approved project memory or downstream artifact
```

Consumers MUST preserve unknown additive fields. They MUST NOT:

- promote a draft merely because its evidence looks strong;
- convert a successful run directly into an accepted claim;
- erase contradictory evidence;
- rewrite source artifacts through an evidence link;
- expose source content, private paths, or identifiers in content-free
  `status`/`doctor` reports.

The contracts record provenance and review state; they do not claim to provide
process isolation or to validate the scientific adequacy of an evaluator. The
executor remains responsible for its sandbox, resource limits, credentials,
network policy, random seeds, and domain-specific verification.

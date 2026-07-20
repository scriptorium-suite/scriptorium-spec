# Schema Versioning Rules (v1)

Modeled on the nbformat / Data Package precedents.

1. **The version travels in the data.** Every exchange file carries a
   `schema_version` field of the form `<format>/<major>.<minor>`,
   e.g. `library-kb/1.0`. A file without `schema_version` is pre-spec ("v0")
   and consumers may refuse it.
2. **Major = breaking, minor = additive.** Adding an optional field bumps the
   minor version. Renaming/removing/retyping a field bumps the major version.
   Renames are forbidden inside a major line — add a new field instead.
3. **Consumer tolerance.** Consumers MUST ignore unknown fields, and tools that
   rewrite a file MUST preserve fields they do not understand.
4. **Producer honesty.** Producers write the lowest minor version that
   describes what they actually emit, plus `generated_by` with tool name and
   version.
5. **This spec repo is versioned independently** (semver tags). Each tool's
   README declares which schemas and versions it produces/consumes, e.g.
   "produces library-kb v1, consumes proposal v1".
6. One JSON Schema file per major version (`schemas/<format>/v<major>.json`);
   minor revisions update the same file with a CHANGELOG entry.

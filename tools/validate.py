"""Minimal structural validator for Scriptorium exchange files (stdlib only).

Not a full JSON Schema engine — checks the load-bearing constraints:
schema_version shape, required fields, key patterns, enum values.

Usage: python tools/validate.py <file.json> [...]
Exit code 0 = all files valid.
"""
import json
import re
import sys

KEY_RE = re.compile(r"^[A-Z0-9]{8}$")
READ_STATUSES = {"", "New", "To Read", "In Progress", "Read", "Not Reading"}
CONFIDENCE = {"high", "medium", "low"}


def err(errors, path, msg):
    errors.append(f"  {path}: {msg}")


def validate_library_kb(doc, errors):
    items = doc.get("items")
    if not isinstance(items, list):
        return err(errors, "items", "missing or not an array")
    for i, it in enumerate(items):
        p = f"items[{i}]"
        if not isinstance(it, dict):
            err(errors, p, "must be an object")
            continue
        if not isinstance(it.get("key"), str) or not KEY_RE.match(it["key"]):
            err(errors, p, f"bad key: {it.get('key')!r}")
        if not isinstance(it.get("title"), str):
            err(errors, p, "missing title")
        if it.get("readStatus", "") not in READ_STATUSES:
            err(errors, p, f"invalid readStatus: {it.get('readStatus')!r}")
        y = it.get("year", "")
        if y and not re.match(r"^[0-9]{4}$", y):
            err(errors, p, f"invalid year: {y!r}")


def validate_proposal(doc, errors):
    tree = doc.get("target_tree")
    props = doc.get("proposals")
    if not isinstance(props, list):
        return err(errors, "proposals", "missing or not an array")
    for i, pr in enumerate(props):
        p = f"proposals[{i}]"
        if not isinstance(pr, dict):
            err(errors, p, "must be an object")
            continue
        if not isinstance(pr.get("key"), str) or not KEY_RE.match(pr["key"]):
            err(errors, p, f"bad key: {pr.get('key')!r}")
        targets = pr.get("targets")
        if not isinstance(targets, list) or not 1 <= len(targets) <= 3:
            err(errors, p, "targets must be a list of 1..3 paths")
        elif isinstance(tree, list):
            for t in targets:
                if t not in tree:
                    err(errors, p, f"target not in target_tree: {t!r}")
        if "confidence" in pr and pr["confidence"] not in CONFIDENCE:
            err(errors, p, f"invalid confidence: {pr['confidence']!r}")


def validate_handoff(doc, errors):
    if not isinstance(doc.get("key"), str) or not KEY_RE.match(doc["key"]):
        err(errors, "key", f"bad key: {doc.get('key')!r}")
    if not isinstance(doc.get("title"), str):
        err(errors, "title", "missing title")


PROJECT_STATUS = {"planned", "active", "paused", "done", "archived"}
PROJECT_PROFILES = {"general", "research", "engineering", "software"}
NOTE_SOURCES = {"obsidian", "openclaw", "agent"}
APPROVAL_STATES = {"draft", "approved", "applied"}
READING_STATUSES = {"New", "To Read", "In Progress", "Read", "Not Reading"}
# Known sub-objects of `stages` -> the string fields they may carry (array fields are checked generically).
READING_STAGE_STRINGS = {
    "glance": {"tldr"},
    "close_read": {"question", "method", "data", "results"},
    "deep_read": {"critique", "reproducibility", "limits", "relation_to_my_work"},
    "situate": {"direction"},
}


def validate_project(doc, errors):
    pid = doc.get("project_id", "")
    if not re.match(r"^[a-z0-9][a-z0-9-]*$", pid or ""):
        err(errors, "project_id", f"bad project_id: {pid!r}")
    if not isinstance(doc.get("title"), str):
        err(errors, "title", "missing title")
    if doc.get("status") not in PROJECT_STATUS:
        err(errors, "status", f"invalid status: {doc.get('status')!r}")
    if "profile" in doc and doc["profile"] not in PROJECT_PROFILES:
        err(errors, "profile", f"invalid profile: {doc.get('profile')!r}")


def validate_note(doc, errors):
    if not doc.get("note_id"):
        err(errors, "note_id", "missing note_id")
    if doc.get("source") not in NOTE_SOURCES:
        err(errors, "source", f"invalid source: {doc.get('source')!r}")
    if not doc.get("created"):
        err(errors, "created", "missing created")
    if not isinstance(doc.get("body"), str):
        err(errors, "body", "missing body")


def validate_session_summary(doc, errors):
    if not doc.get("summary_id"):
        err(errors, "summary_id", "missing summary_id")
    if not doc.get("project"):
        err(errors, "project", "missing project")
    if doc.get("approval_state") not in APPROVAL_STATES:
        err(errors, "approval_state", f"invalid approval_state: {doc.get('approval_state')!r}")
    if doc.get("status") and doc["status"] not in PROJECT_STATUS:
        err(errors, "status", f"invalid status: {doc.get('status')!r}")
    if "confidence" in doc and doc["confidence"] not in CONFIDENCE:
        err(errors, "confidence", f"invalid confidence: {doc['confidence']!r}")


def validate_parsed_paper(doc, errors):
    if not isinstance(doc.get("id"), str) or not doc["id"]:
        err(errors, "id", f"missing or non-string id (citekey): {doc.get('id')!r}")
    if not doc.get("created"):
        err(errors, "created", "missing created")
    for name in ("sections", "references", "figures", "tables"):
        arr = doc.get(name)
        if arr is None:
            continue
        if not isinstance(arr, list):
            err(errors, name, "must be an array")
            continue
        for i, it in enumerate(arr):
            if not isinstance(it, dict):
                err(errors, f"{name}[{i}]", "must be an object")


def validate_reading_note(doc, errors):
    if not isinstance(doc.get("id"), str) or not doc["id"]:
        err(errors, "id", f"missing or non-string id (citekey): {doc.get('id')!r}")
    if not doc.get("created"):
        err(errors, "created", "missing created")
    if "read_status" in doc and doc["read_status"] not in READING_STATUSES:
        err(errors, "read_status", f"invalid read_status: {doc.get('read_status')!r}")
    stages = doc.get("stages")
    if stages is not None:
        if not isinstance(stages, dict):
            return err(errors, "stages", "must be an object")
        for name, strings in READING_STAGE_STRINGS.items():
            stage = stages.get(name)
            if stage is None:
                continue
            sp = f"stages.{name}"
            if not isinstance(stage, dict):
                err(errors, sp, "must be an object")
                continue
            for k, v in stage.items():
                fp = f"{sp}.{k}"
                if k in strings:
                    if not isinstance(v, str):
                        err(errors, fp, "must be a string")
                elif isinstance(v, list):
                    if not all(isinstance(x, str) for x in v):
                        err(errors, fp, "array items must be strings")
                elif not isinstance(v, str):
                    err(errors, fp, "must be a string or array of strings")


LINEAGE_RELATIONS = {"cites", "extends", "supersedes", "method-of", "contrasts"}


def validate_lineage_graph(doc, errors):
    direction = doc.get("direction")
    if not isinstance(direction, dict):
        err(errors, "direction", "missing or not an object")
    else:
        for k in ("query", "scope_method", "created"):
            if not isinstance(direction.get(k), str) or not direction[k]:
                err(errors, f"direction.{k}", "missing or not a string")
    nodes = doc.get("nodes")
    if not isinstance(nodes, list):
        err(errors, "nodes", "missing or not an array")
    else:
        for i, n in enumerate(nodes):
            p = f"nodes[{i}]"
            if not isinstance(n, dict):
                err(errors, p, "must be an object")
                continue
            if not isinstance(n.get("citekey"), str) or not n["citekey"]:
                err(errors, p, f"missing citekey: {n.get('citekey')!r}")
    edges = doc.get("edges")
    if not isinstance(edges, list):
        err(errors, "edges", "missing or not an array")
    else:
        for i, e in enumerate(edges):
            p = f"edges[{i}]"
            if not isinstance(e, dict):
                err(errors, p, "must be an object")
                continue
            if not isinstance(e.get("from"), str) or not e["from"]:
                err(errors, p, f"missing from: {e.get('from')!r}")
            if not isinstance(e.get("to"), str) or not e["to"]:
                err(errors, p, f"missing to: {e.get('to')!r}")
            if e.get("relation") not in LINEAGE_RELATIONS:
                err(errors, p, f"invalid relation: {e.get('relation')!r}")


def validate_review(doc, errors):
    direction = doc.get("direction")
    if not isinstance(direction, dict):
        err(errors, "direction", "missing or not an object")
    else:
        for k in ("query", "created"):
            if not isinstance(direction.get(k), str) or not direction[k]:
                err(errors, f"direction.{k}", "missing or not a string")
    sections = doc.get("sections")
    if not isinstance(sections, list):
        err(errors, "sections", "missing or not an array")
    else:
        for i, s in enumerate(sections):
            p = f"sections[{i}]"
            if not isinstance(s, dict):
                err(errors, p, "must be an object")
                continue
            if not isinstance(s.get("heading"), str) or not s["heading"]:
                err(errors, p, "missing heading")
            if not isinstance(s.get("prose"), str) or not s["prose"]:
                err(errors, p, "missing prose")
    table = doc.get("comparison_table")
    if table is not None:
        if not isinstance(table, dict):
            err(errors, "comparison_table", "must be an object")
        else:
            rows = table.get("rows")
            if rows is not None and not isinstance(rows, list):
                err(errors, "comparison_table.rows", "must be an array")
            elif isinstance(rows, list):
                for i, r in enumerate(rows):
                    rp = f"comparison_table.rows[{i}]"
                    if not isinstance(r, dict):
                        err(errors, rp, "must be an object")
                        continue
                    if not isinstance(r.get("citekey"), str) or not r["citekey"]:
                        err(errors, rp, f"missing citekey: {r.get('citekey')!r}")
                    if not isinstance(r.get("cells"), list):
                        err(errors, rp, "cells must be an array")


EXPERIMENT_RUN_STATUSES = {"running", "succeeded", "failed", "cancelled"}
EXPERIMENT_ARTIFACT_ROLES = {"input", "output", "log"}
METRIC_DIRECTIONS = {"minimize", "maximize", "target", "none"}
CLAIM_KINDS = {"observation", "hypothesis", "interpretation", "limitation", "decision"}
EPISTEMIC_STATUSES = {
    "speculative",
    "partially-supported",
    "supported",
    "contradicted",
    "mixed",
    "unresolved",
}
CLAIM_REVIEW_STATES = {"draft", "accepted", "rejected", "superseded"}
EVIDENCE_RELATIONS = {"supports", "contradicts", "qualifies", "context"}
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SOURCE_TYPE_RE = re.compile(r"^[a-z][a-z0-9-]*$")
SEED_NAME_RE = re.compile(r"^[a-z][a-z0-9_-]*$")


def validate_experiment_run(doc, errors):
    for field in ("run_id", "project"):
        value = doc.get(field)
        if not isinstance(value, str) or not SLUG_RE.match(value):
            err(errors, field, f"bad {field}: {value!r}")
    if not isinstance(doc.get("created"), str) or not doc["created"]:
        err(errors, "created", "missing or not a string")
    if doc.get("status") not in EXPERIMENT_RUN_STATUSES:
        err(errors, "status", f"invalid status: {doc.get('status')!r}")
    if not isinstance(doc.get("objective"), str) or not doc["objective"]:
        err(errors, "objective", "missing or not a string")

    execution = doc.get("execution")
    if not isinstance(execution, dict):
        err(errors, "execution", "missing or not an object")
    else:
        runner = execution.get("runner")
        if not isinstance(runner, str) or not SOURCE_TYPE_RE.match(runner):
            err(errors, "execution.runner", f"invalid runner: {runner!r}")
        if not isinstance(execution.get("code_ref"), str) or not execution["code_ref"]:
            err(errors, "execution.code_ref", "missing or not a string")
        if (
            not isinstance(execution.get("environment_ref"), str)
            or not execution["environment_ref"]
        ):
            err(errors, "execution.environment_ref", "missing or not a string")
        if not isinstance(execution.get("parameters"), dict):
            err(errors, "execution.parameters", "missing or not an object")
        random_seeds = execution.get("random_seeds")
        if not isinstance(random_seeds, dict):
            err(errors, "execution.random_seeds", "missing or not an object")
        else:
            for name, seed in random_seeds.items():
                path = f"execution.random_seeds.{name}"
                if not isinstance(name, str) or not SEED_NAME_RE.match(name):
                    err(errors, path, "seed name must be lowercase")
                if (
                    not isinstance(seed, (int, str))
                    or isinstance(seed, bool)
                    or (isinstance(seed, str) and not seed)
                ):
                    err(errors, path, "seed must be an integer or non-empty string")

    artifacts = doc.get("artifacts")
    if artifacts is not None:
        if not isinstance(artifacts, list):
            err(errors, "artifacts", "must be an array")
        else:
            for i, artifact in enumerate(artifacts):
                path = f"artifacts[{i}]"
                if not isinstance(artifact, dict):
                    err(errors, path, "must be an object")
                    continue
                if not isinstance(artifact.get("artifact_id"), str) or not artifact["artifact_id"]:
                    err(errors, path, "missing artifact_id")
                if artifact.get("role") not in EXPERIMENT_ARTIFACT_ROLES:
                    err(errors, path, f"invalid role: {artifact.get('role')!r}")
                digest = artifact.get("sha256")
                if digest is not None and (
                    not isinstance(digest, str) or not SHA256_RE.match(digest)
                ):
                    err(errors, f"{path}.sha256", "must be a lowercase SHA-256 digest")

    metrics = doc.get("metrics")
    if metrics is not None:
        if not isinstance(metrics, list):
            err(errors, "metrics", "must be an array")
        else:
            for i, metric in enumerate(metrics):
                path = f"metrics[{i}]"
                if not isinstance(metric, dict):
                    err(errors, path, "must be an object")
                    continue
                if not isinstance(metric.get("name"), str) or not metric["name"]:
                    err(errors, path, "missing name")
                value = metric.get("value")
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    err(errors, path, f"value must be a number: {value!r}")
                direction = metric.get("direction")
                if direction is not None and direction not in METRIC_DIRECTIONS:
                    err(errors, path, f"invalid direction: {direction!r}")

    if doc.get("status") == "failed" and (
        not isinstance(doc.get("failure_reason"), str) or not doc["failure_reason"]
    ):
        err(errors, "failure_reason", "required for failed status")
    if not isinstance(doc.get("generated_by"), str) or not doc["generated_by"]:
        err(errors, "generated_by", "missing or not a string")


def validate_claim_evidence(doc, errors):
    for field in ("claim_id", "project"):
        value = doc.get(field)
        if not isinstance(value, str) or not SLUG_RE.match(value):
            err(errors, field, f"bad {field}: {value!r}")
    if not isinstance(doc.get("created"), str) or not doc["created"]:
        err(errors, "created", "missing or not a string")
    if not isinstance(doc.get("statement"), str) or not doc["statement"]:
        err(errors, "statement", "missing or not a string")
    kind = doc.get("kind")
    if kind is not None and kind not in CLAIM_KINDS:
        err(errors, "kind", f"invalid kind: {kind!r}")
    if doc.get("epistemic_status") not in EPISTEMIC_STATUSES:
        err(
            errors,
            "epistemic_status",
            f"invalid epistemic_status: {doc.get('epistemic_status')!r}",
        )
    review_state = doc.get("review_state")
    if review_state not in CLAIM_REVIEW_STATES:
        err(errors, "review_state", f"invalid review_state: {review_state!r}")

    evidence = doc.get("evidence")
    if not isinstance(evidence, list):
        err(errors, "evidence", "missing or not an array")
        evidence = []
    else:
        for i, item in enumerate(evidence):
            path = f"evidence[{i}]"
            if not isinstance(item, dict):
                err(errors, path, "must be an object")
                continue
            if item.get("relation") not in EVIDENCE_RELATIONS:
                err(errors, path, f"invalid relation: {item.get('relation')!r}")
            source_type = item.get("source_type")
            if not isinstance(source_type, str) or not SOURCE_TYPE_RE.match(source_type):
                err(errors, path, f"invalid source_type: {source_type!r}")
            for field in ("source_id", "locator"):
                if not isinstance(item.get(field), str) or not item[field]:
                    err(errors, path, f"missing {field}")
            digest = item.get("sha256")
            if digest is not None and (
                not isinstance(digest, str) or not SHA256_RE.match(digest)
            ):
                err(errors, f"{path}.sha256", "must be a lowercase SHA-256 digest")

    if review_state in {"accepted", "rejected", "superseded"} and (
        not isinstance(doc.get("reviewed_at"), str) or not doc["reviewed_at"]
    ):
        err(errors, "reviewed_at", "required for an explicit review decision")
    if review_state == "accepted":
        if not evidence:
            err(errors, "evidence", "accepted claims require at least one evidence link")
        if doc.get("epistemic_status") == "speculative":
            err(errors, "epistemic_status", "accepted claims cannot remain speculative")
    if review_state == "superseded":
        superseded_by = doc.get("superseded_by")
        if not isinstance(superseded_by, str) or not SLUG_RE.match(superseded_by):
            err(errors, "superseded_by", "required for superseded review_state")
    if not isinstance(doc.get("generated_by"), str) or not doc["generated_by"]:
        err(errors, "generated_by", "missing or not a string")


FORMATS = {
    "library-kb": validate_library_kb,
    "proposal": validate_proposal,
    "handoff": validate_handoff,
    "project": validate_project,
    "note": validate_note,
    "session-summary": validate_session_summary,
    "reading-note": validate_reading_note,
    "parsed-paper": validate_parsed_paper,
    "lineage-graph": validate_lineage_graph,
    "review": validate_review,
    "experiment-run": validate_experiment_run,
    "claim-evidence": validate_claim_evidence,
}


def validate_file(path):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    errors = []
    sv = doc.get("schema_version", "")
    m = re.match(r"^([a-z-]+)/(\d+)\.(\d+)$", sv)
    if not m:
        errors.append(f"  schema_version: missing or malformed: {sv!r}")
    else:
        fmt, major = m.group(1), m.group(2)
        if fmt not in FORMATS:
            errors.append(f"  schema_version: unknown format {fmt!r}")
        elif major != "1":
            errors.append(f"  schema_version: unsupported major version {major} (validator knows v1)")
        else:
            FORMATS[fmt](doc, errors)
    return errors


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    failed = False
    for path in sys.argv[1:]:
        errors = validate_file(path)
        if errors:
            failed = True
            print(f"INVALID {path}")
            print("\n".join(errors))
        else:
            print(f"ok      {path}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

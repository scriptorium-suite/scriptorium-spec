"""Check release facts, public status copy, and example version honesty.

This script is stdlib-only so it can run before development dependencies are
installed. Normal CI accepts an explicit release candidate in the Unreleased
section. Passing ``--tag`` is stricter: the changelog must already contain the
matching dated release heading, so the command is safe as a tag preflight.
"""

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SEMVER = r"[0-9]+\.[0-9]+\.[0-9]+"
RELEASE_HEADING_RE = re.compile(
    rf"^## v(?P<version>{SEMVER}) — (?P<date>[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})$",
    re.MULTILINE,
)
RC_TARGET_RE = re.compile(rf"Release candidate for \*\*v(?P<version>{SEMVER})\*\*\.")
UNRELEASED_SECTION_RE = re.compile(
    r"^## Unreleased[ \t]*\r?\n(?P<body>.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
LIBRARY_EXAMPLE_RE = re.compile(r"^library-kb\.v(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.example\.json$")


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def check_changelog(project_version, changelog, errors, tag):
    releases = list(RELEASE_HEADING_RE.finditer(changelog))
    if not releases:
        errors.append("CHANGELOG.md has no dated release heading")
        return

    current_release = releases[0].group("version")
    unreleased = UNRELEASED_SECTION_RE.search(changelog)
    rc_targets = RC_TARGET_RE.findall(unreleased.group("body")) if unreleased else []
    rc_target = rc_targets[0] if rc_targets else None

    if len(rc_targets) > 1:
        errors.append("CHANGELOG.md declares more than one release-candidate target")

    if tag:
        expected_tag = f"v{project_version}"
        if tag != expected_tag:
            errors.append(f"tag {tag!r} does not match project version {expected_tag!r}")
        if current_release != project_version:
            errors.append(
                "tag preflight requires the first dated CHANGELOG release to be "
                f"v{project_version}; finalize the Unreleased section first"
            )
        if rc_target == project_version:
            errors.append("tag preflight found an unfinalized release-candidate marker")
        return

    if current_release == project_version:
        if rc_target == project_version:
            errors.append("released version still has a release-candidate marker")
    elif rc_target != project_version:
        errors.append(
            "project version must match either the first dated CHANGELOG release "
            "or the explicit Unreleased release-candidate target"
        )


def check_library_schema(errors):
    schema = load_json(ROOT / "schemas" / "library-kb" / "v1.json")
    schema_pattern = schema["properties"]["schema_version"].get("pattern")
    if schema_pattern != r"^library-kb/1\.[0-9]+$":
        errors.append("library-kb v1 schema must continue accepting all 1.x minors")

    item_schema = schema["properties"]["items"]["items"]
    if "citekey" not in item_schema.get("properties", {}):
        errors.append("library-kb v1 schema does not define citekey")
    if "citekey" in item_schema.get("required", []):
        errors.append("library-kb citekey must remain optional")


def check_lockfile(project_version, errors):
    with open(ROOT / "uv.lock", "rb") as handle:
        lock = tomllib.load(handle)

    roots = [
        package
        for package in lock.get("package", [])
        if package.get("name") == "scriptorium-spec"
        and package.get("source") == {"virtual": "."}
    ]
    if len(roots) != 1:
        errors.append("uv.lock must contain exactly one virtual scriptorium-spec root")
    elif roots[0].get("version") != project_version:
        errors.append(
            "uv.lock root version does not match pyproject.toml: "
            f"{roots[0].get('version')!r} != {project_version!r}"
        )


def check_public_release_facts(project_version, errors, tag):
    """A final tag must not leave public docs calling that version an RC."""
    if not tag:
        return
    marker = f"v{project_version} release candidate"
    for relative in ("README.md", "README.zh.md", "CHANGELOG.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        if marker.casefold() in text.casefold():
            errors.append(
                f"{relative} still describes v{project_version} as a release candidate"
            )


def check_library_examples(errors):
    examples = {}
    for path in sorted((ROOT / "examples").glob("library-kb*.json")):
        match = LIBRARY_EXAMPLE_RE.match(path.name)
        if not match:
            errors.append(f"library-kb example has a non-versioned filename: {path.name}")
            continue

        expected = (int(match.group("major")), int(match.group("minor")))
        doc = load_json(path)
        version_match = re.fullmatch(r"library-kb/([0-9]+)\.([0-9]+)", doc.get("schema_version", ""))
        if not version_match:
            errors.append(f"{path.name} has a malformed library-kb schema_version")
            continue

        declared = (int(version_match.group(1)), int(version_match.group(2)))
        if declared != expected:
            errors.append(
                f"{path.name} encodes {expected[0]}.{expected[1]} but declares "
                f"{declared[0]}.{declared[1]}"
            )

        items = doc.get("items", [])
        carries_citekey = any(isinstance(item, dict) and "citekey" in item for item in items)
        if carries_citekey and declared < (1, 1):
            errors.append(f"{path.name} carries citekey but declares a version below 1.1")
        examples[declared] = carries_citekey

    if examples.get((1, 0)) is not False:
        errors.append("library-kb/1.0 example must exist and omit citekey")
    if examples.get((1, 1)) is not True:
        errors.append("library-kb/1.1 example must exist and demonstrate citekey")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tag",
        help="Proposed or pushed tag, for example v2.2.0; requires a finalized changelog",
    )
    args = parser.parse_args(argv)

    with open(ROOT / "pyproject.toml", "rb") as handle:
        project_version = tomllib.load(handle)["project"]["version"]

    errors = []
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    check_changelog(project_version, changelog, errors, args.tag)
    check_lockfile(project_version, errors)
    check_public_release_facts(project_version, errors, args.tag)
    check_library_schema(errors)
    check_library_examples(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    state = f"tag {args.tag}" if args.tag else "working tree"
    print(f"release facts consistent for {state}: v{project_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

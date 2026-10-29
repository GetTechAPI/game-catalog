"""Validate the game catalog.

Ported from TechEngine's `app/validate.py` game section, with one change that
the size forces: records are checked one at a time instead of being loaded into
a list first. ~1M records will not fit in a runner's memory otherwise.

Run with: python -m app.validate
     or: python -m app.validate --changed-since <sha>   (PRs: changed records only)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "game"

REQUIRED = {"slug", "name", "source_urls", "verified"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_ERRORS = 200  # a wall of identical errors helps nobody


def _check(rel: str, rec: dict[str, Any], errors: list[str]) -> None:
    missing = REQUIRED - rec.keys()
    if missing:
        errors.append(f"{rel}: missing required field(s) {sorted(missing)}")

    slug = rec.get("slug")
    if isinstance(slug, str) and not SLUG_RE.match(slug):
        errors.append(f"{rel}: slug '{slug}' is not kebab-case")

    urls = rec.get("source_urls")
    if not isinstance(urls, list) or not urls:
        errors.append(f"{rel}: source_urls must be a non-empty list")
    elif not all(isinstance(u, str) and u.startswith("http") for u in urls):
        errors.append(f"{rel}: every source_url must be an http(s) string")

    release = rec.get("release_date")
    if release is not None and not (isinstance(release, str) and DATE_RE.match(release)):
        errors.append(f"{rel}: release_date '{release}' is not YYYY-MM-DD")

    for field, low, high in (("rating", 0, 5), ("metacritic", 0, 100)):
        value = rec.get(field)
        if value is None or isinstance(value, bool):
            continue
        if not isinstance(value, (int, float)) or not low <= value <= high:
            errors.append(f"{rel}: {field} {value!r} outside {low}-{high}")


def validate(data_dir: Path = DATA, paths: list[Path] | None = None) -> list[str]:
    """Check every record, or only `paths` when given.

    A scoped run still catches duplicate slugs: the bucket check pins each slug
    to exactly one path, so a duplicate would have to overwrite that file.
    """
    errors: list[str] = []
    seen: dict[str, str] = {}
    count = 0

    for path in sorted(data_dir.rglob("*.json")) if paths is None else sorted(paths):
        rel = path.relative_to(data_dir.parent).as_posix()
        count += 1
        try:
            rec = json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: invalid JSON ({exc})")
            continue
        if not isinstance(rec, dict):
            errors.append(f"{rel}: top level must be an object")
            continue

        _check(rel, rec, errors)

        slug = rec.get("slug")
        if isinstance(slug, str):
            if slug in seen:
                errors.append(f"{rel}: duplicate slug '{slug}' (first seen in {seen[slug]})")
            else:
                seen[slug] = rel
            if path.stem != slug:
                errors.append(f"{rel}: filename does not match slug '{slug}'")
            if path.parent.name != slug[:2]:
                errors.append(f"{rel}: bucket must be '{slug[:2]}' (first two slug characters)")

        if len(errors) >= MAX_ERRORS:
            errors.append(f"... stopped after {MAX_ERRORS} errors")
            break

    if count == 0 and paths is None:
        errors.append(f"no game records found under {data_dir}")
    return errors


def changed_records(base: str) -> list[Path]:
    """Records added or modified since `base` (deletions need no checking)."""
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=AMR", f"{base}...HEAD", "--", "data/game"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout
    return [ROOT / line for line in out.splitlines() if line.endswith(".json")]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--changed-since", metavar="SHA", help="validate only records changed since SHA")
    args = parser.parse_args()

    paths = changed_records(args.changed_since) if args.changed_since else None
    if paths is not None:
        print(f"validating {len(paths)} changed record(s)")
    errors = validate(paths=paths)
    for error in errors:
        print(error)
    if errors:
        print(f"FAIL: {len(errors)} problem(s)")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

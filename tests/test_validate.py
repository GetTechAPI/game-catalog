"""The validator must reject what TechEngine's game section rejected."""

from __future__ import annotations

import json
from pathlib import Path

from app.validate import validate

GOOD = {
    "slug": "the-witcher-3-wild-hunt",
    "name": "The Witcher 3: Wild Hunt",
    "verified": False,
    "source_urls": ["https://rawg.io/games/the-witcher-3-wild-hunt"],
    "release_date": "2015-05-18",
    "rating": 4.7,
    "metacritic": 92,
}


def _write(tmp_path: Path, rec: dict, name: str | None = None) -> Path:
    data = tmp_path / "game" / "th"
    data.mkdir(parents=True, exist_ok=True)
    (data / f"{name or rec['slug']}.json").write_text(json.dumps(rec), encoding="utf-8")
    return tmp_path / "game"


def test_good_record_passes(tmp_path):
    assert validate(_write(tmp_path, GOOD)) == []


def test_empty_catalog_is_an_error(tmp_path):
    (tmp_path / "game").mkdir()
    assert validate(tmp_path / "game")


def test_missing_required_field(tmp_path):
    rec = {**GOOD}
    del rec["source_urls"]
    assert any("missing required" in e for e in validate(_write(tmp_path, rec)))


def test_non_kebab_slug(tmp_path):
    assert any("kebab-case" in e for e in validate(_write(tmp_path, {**GOOD, "slug": "The_Witcher"}, "The_Witcher")))


def test_filename_must_match_slug(tmp_path):
    assert any("filename" in e for e in validate(_write(tmp_path, GOOD, "something-else")))


def test_bad_release_date(tmp_path):
    assert any("release_date" in e for e in validate(_write(tmp_path, {**GOOD, "release_date": "2015"})))


def test_metacritic_out_of_range(tmp_path):
    assert any("metacritic" in e for e in validate(_write(tmp_path, {**GOOD, "metacritic": 180})))


def test_rating_out_of_range(tmp_path):
    assert any("rating" in e for e in validate(_write(tmp_path, {**GOOD, "rating": 9})))


def test_duplicate_slug(tmp_path):
    data = _write(tmp_path, GOOD)
    other = data / "zz"
    other.mkdir(parents=True, exist_ok=True)
    (other / "the-witcher-3-wild-hunt.json").write_text(json.dumps(GOOD), encoding="utf-8")
    assert any("duplicate slug" in e for e in validate(data))

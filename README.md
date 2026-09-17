# game-catalog

[![validate-data](https://github.com/GetTechAPI/game-catalog/actions/workflows/validate-data.yml/badge.svg)](https://github.com/GetTechAPI/game-catalog/actions/workflows/validate-data.yml)

Video game records, split out of [TechAPI](https://github.com/GetTechAPI/TechAPI).
Code is MIT; the records under `data/` are CC BY-SA 4.0 ([DATA_LICENSE.md](DATA_LICENSE.md)).

## Why this repo exists

Games were 962,384 of TechAPI's 1.11M records — 86% of the dataset for a
category that no other category references. Carrying them made the dump take
over five hours and produced pull requests GitHub could not render or merge.
Hardware stays in TechAPI; games live here.

| Belongs here | Belongs in TechAPI |
|---|---|
| Video game titles | Phones, tablets, watches, PDAs |
| Release dates, ratings, platforms, genres | CPUs, GPUs, SoCs, laptops, monitors |
| Developers and publishers (free text) | Brands, and anything scored or verified |

Games are unscored and are not part of the verification layer — they were not
in TechEngine's scoring or verify categories before the split either.

## Layout

```
data/game/<bucket>/<slug>.json   # bucket = first two slug characters
app/validate.py                  # schema / slug / range checks
site/build.py                    # summary.json + history.json for the site
```

A record needs `slug`, `name`, `source_urls` and `verified`. Optional fields
follow TechEngine's game model: `release_date`, `rating` (0-5), `rating_count`,
`metacritic` (0-100), `playtime_hours`, `platforms`, `genres`, `stores`,
`developers`, `publishers`, `tags`, `esrb_rating`, `background_image`.

## Self-check

```bash
python -m app.validate
python -m pytest -q
```

## Site

`python site/build.py` writes two files that the TechAPI homepage reads so the
count still appears there:

- `summary.json` — `{"count": N, "generated_at": "..."}`
- `history.json` — `{"points": [{"sha", "date", "count"}]}`, one point per data commit

There is no `catalog.json` listing every record, and the page does not render
one: a million rows cannot be fetched or drawn in a browser.

## Branching (git-flow)

`develop` is the default branch and the integration branch; `main` is the
released state and deploys the site. Work branches are cut from `develop` and
their pull requests target `develop`. A release is a PR from `develop` to
`main`.

## License

Code MIT ([LICENSE](LICENSE)); data CC BY-SA 4.0 ([DATA_LICENSE.md](DATA_LICENSE.md)).
Attribution: "Data from GetTechAPI / game-catalog".

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

The records moved out of TechAPI on 2026-09-17. TechAPI keeps a pointer to this
repository at `site/public/v1/games/index.json`, and its site reads this
repository's `summary.json` for the game count.

## Layout

| Path | What it is |
|---|---|
| `data/game/<bucket>/<slug>.json` | One record per file; the bucket is the first two characters of the slug |
| `app/validate.py` | Validator: required fields, slug, filename and bucket, duplicate slugs, date and rating ranges |
| `site/build.py` | Writes `site/summary.json` and `site/history.json` (generated, not committed) |
| `site/index.html` | The Pages landing page; shows the count from `summary.json` |
| `tests/` | pytest tests for the validator |
| `.github/workflows/validate-data.yml` | Validator and tests on pull requests and on pushes to `develop` and `main` |
| `.github/workflows/final-check.yml` | Label-triggered full check of a pull request (see [Final check](#final-check)) |
| `.github/workflows/deploy-pages.yml` | Builds `site/` and deploys it to GitHub Pages on pushes to `main` |

A record needs `slug`, `name`, `source_urls` and `verified`. Optional fields
follow TechEngine's game model: `release_date`, `rating` (0-5), `rating_count`,
`metacritic` (0-100), `playtime_hours`, `platforms`, `genres`, `stores`,
`developers`, `publishers`, `tags`, `esrb_rating`, `background_image`.

## Self-check

```bash
python -m app.validate                           # every record
python -m app.validate --changed-since develop   # only records your branch touched
python -m pytest -q
```

The validator reads records one at a time, so the full run fits in a runner's
memory; on a CI runner it took 3 minutes for 962,384 records on 2026-10-31.

CI runs the scoped check on pull requests and the full check on pushes to
`develop` and `main`. `validate-data` and `deploy-pages` use `GITHUB_TOKEN`
only. No workflow runs on a schedule, opens pull requests or issues, or pushes
to a repository. The one other secret is `TECHENGINEBOT_TOKEN`, which only the
comment job of the final check sees.

## Final check

A maintainer adds the `final-check` label to an important PR. The
`final-check` workflow runs the whole-catalog validator, the tests and the
site build on the PR merged into its base. **TechEngineBot** then leaves one
comment with the verdict, and adding the label again edits that comment.
Only the comment job sees `TECHENGINEBOT_TOKEN`, a fine-grained TechEngineBot
token with Pull requests: read and write. Without it, the verdict appears
only in the job summary. Pull requests from forks never get a comment.

## Site

`python site/build.py` writes two files into `site/`. They are not committed;
`deploy-pages` rebuilds and publishes them on every push to `main`. The TechAPI
site reads `summary.json`, so the count still appears there:

- `summary.json` — `{"count": N, "generated_at": "..."}`
- `history.json` — `{"points": [{"sha", "date", "count"}]}`, one point per
  commit that added or removed records

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

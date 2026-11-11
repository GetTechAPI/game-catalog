<!-- PR title follows Conventional Commits, e.g. data(game): add <name>. Target `develop`; only a release PR targets `main`. -->

## What & why

<!-- What does this change and why? Use "Closes #123" for the issue it resolves. -->

## Checklist

- [ ] Targets `develop`
- [ ] `python -m app.validate --changed-since develop` and `python -m pytest -q` pass locally
- [ ] Every new or changed record has `slug`, `name`, `source_urls` and `verified`, and cites at least one public reference in `source_urls`
- [ ] Records live at `data/game/<bucket>/<slug>.json`, where the bucket is the first two characters of the slug
- [ ] Sidebar filled in by hand: assignees, labels, milestone, projects

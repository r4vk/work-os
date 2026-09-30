# Topics

- `domains/<your-area>/` — created during onboarding, one folder per work area; topic files keep a domain prefix in the name.
- `internal/` — recurring duties, reporting, internal processes.
- `others/` — everything that fits nowhere else.

Topic file format: `_templates/topic.md` (the card = current state; `## Current state` is rewritten in place) and `_templates/topic-history.md` (`<card>-history.md` in the same folder = events, append-only, chronological with the newest at the bottom, every entry with a source; quarterly archives `<card>-history-YYYY-Qn.md`). History files are not cards: never in `related_topics`. `watch: true` in front matter puts a topic on the urgency-scan watchlist. Validate with `python3 automations/housekeeping.py --check`.

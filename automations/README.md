# Automations — prompt mirrors for scheduled jobs

Each scheduled job your AI tool runs has a mirror .md here, so every tool (and you) can read and propose changes to the same text.

## Consistency rules

1. The **executable source** is the scheduled task inside your AI tool; the file here is a **mirror**.
2. **Every change = both places.** Tools without scheduler access edit the mirror and set `last_synced: PENDING-SYNC`; the user/primary tool applies it to the scheduler and stamps the date.
3. The morning brief compares mirrors with sources once a week and reports drift in "Questions for the user".
4. Mirror front matter: `taskId`, `schedule` (cron, local time), `enabled`, `last_synced`.

## Included templates

Scheduled jobs are **opt-in** — install during onboarding only the ones the user wants, with the cadence they choose; leave the rest `enabled: false`. The DM step in both jobs is conditional on the user enabling notifications.

| File | Suggested schedule | Purpose |
|---|---|---|
| morning-brief.md | workdays ~06:00 | full scan → vault updates → brief (+ DM summary if notifications on) |
| urgency-scan.md | workdays every 2h, 9–17 | watchlist-only scan → alert file (+ DM if notifications on) or silence |
| onboarding-validation.md | on-demand (not a cron) | the completion gate — run after every onboarding session and on "validate my setup" |

Not a prompt but a script: `housekeeping.py` validates task records, the task log, cards and histories (`--check`), and performs the quarterly rollover / archiving (`--apply`); tests in `test_housekeeping.py`, label sets in `housekeeping.labels.example.json`. See README "State vs history".

The "don't guess — ask" protocol used by all: `_grill-me-protocol.md`. Phone access (opt-in): `bridge/`.

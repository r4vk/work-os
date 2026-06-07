# Automations — prompt mirrors for scheduled jobs

Each scheduled job your AI tool runs has a mirror .md here, so every tool (and you) can read and propose changes to the same text.

## Consistency rules

1. The **executable source** is the scheduled task inside your AI tool; the file here is a **mirror**.
2. **Every change = both places.** Tools without scheduler access edit the mirror and set `last_synced: PENDING-SYNC`; the user/primary tool applies it to the scheduler and stamps the date.
3. The morning brief compares mirrors with sources once a week and reports drift in "Questions for the user".
4. Mirror front matter: `taskId`, `schedule` (cron, local time), `enabled`, `last_synced`.

## Included templates (install during onboarding)

| File | Suggested schedule | Purpose |
|---|---|---|
| morning-brief.md | workdays ~06:00 | full scan → vault updates → brief + DM summary |
| urgency-scan.md | workdays every 2h, 9–17 | watchlist-only scan → DM alert or silence |

The "don't guess — ask" protocol used by both: `_grill-me-protocol.md`. Phone access: `bridge/`.

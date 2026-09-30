# Task record template (TASKS.md)
_One record = one task. Edit fields in place; write events to TASKS-log.md and facts about the matter to <card>-history.md. Field separator: space, middle dot (·), space. New ID: `python3 automations/housekeeping.py --new-id`, or grep `T-<today>-` in TASKS.md, TASKS-log.md and archive/tasks/. Words below are the default `en` label set — see README "Label sets" to change them._

### T-YYYYMMDD-nn · ACTION_REQUIRED · <title: who/what: what to do>
- Status: open · Owner: <Name [TAG]> · Topic: [[<card>]] · Linear: <ABC-123 | none> · Deadline: <YYYY-MM-DD | none> · Created: YYYY-MM-DD · Updated: YYYY-MM-DD
- State: <1–2 sentences: where the matter stands now> (source: <system/channel/ID>, YYYY-MM-DD)
- Next step: <optional, one sentence>

TYPE ∈ ACTION_REQUIRED | DECISION_REQUIRED | WAITING_FOR_OTHER | FYI | RISK_TO_MONITOR | CANDIDATE (only in section "Candidates").
Status ∈ open | closed | obsolete — TASKS.md holds only `open`; closing = move the whole block to archive/tasks/TASKS-YYYY-Qn.md + log line `closed: <reason>` in TASKS-log.md (or set the status and run `housekeeping.py --apply`).
`Linear:` = the task's ID in your ticket tracker (rename the field via labels if you use another tool). With an ID, the tracker's status wins; with `none`, the user confirms the status.

## Log line (TASKS-log.md — append at the END)
- YYYY-MM-DD HH:MM · T-YYYYMMDD-nn · <event> · <text> (source: …)
Events: created | type A→B | deadline A→B | state | linear ABC-123 | handed over <to whom> | closed: <reason> | obsolete: <reason>

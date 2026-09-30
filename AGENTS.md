# Work OS Vault — Conventions for all agents

This folder is {{USER_NAME}}'s working vault ({{ROLE}}, {{COMPANY}}). Any AI tool reading or writing here MUST follow these conventions. Placeholders in {{double braces}} are filled during onboarding (see ONBOARDING.md) — if you see any unfilled, run the onboarding first.

**Purpose:** be {{USER_NAME}}'s personal work assistant — keep a sourced memory of their work, surface what needs their attention, and draft (never send) outgoing communication. The system adapts to the user at onboarding; nothing here is role-specific by default.

## Structure

```
topics/        one card per topic ("dossier") — the heart of the vault; a card holds the CURRENT STATE
  domains/<domain>/   the user's work areas (created at onboarding)
  internal/           internal processes (reporting, recurring duties)
  others/             everything else
               <card>-history.md next to each card = its events (append-only; quarterly archives
               <card>-history-YYYY-Qn.md) — history files are NOT cards
people/        facts about people & teams (who is who)
organizations/ customers, partners, vendors, institutions
knowledge/     curated domain knowledge; sensitive files need human authorization
decisions/     decision_log.md — decisions separated from discussion
briefs/        automation output + pending-questions.md
automations/   mirrors of all scheduled-task prompts + _grill-me-protocol.md + onboarding-validation.md + bridge/
_templates/    file templates (topic card, topic history, task record, person)
TASKS.md       the user's task register — ONE fixed record per task (`### T-YYYYMMDD-nn · TYPE · title`), edited in place
TASKS-log.md   append-only task event log (created / type / deadline / handover / closed with reason); quarterly rollover
archive/tasks/ closed/obsolete task records (TASKS-YYYY-Qn.md) and archived task logs (TASKS-log-YYYY-Qn.md)
GLOSSARY.md    domain/company abbreviations
```

## Hard rules

1. **Autonomy boundary:** automated jobs may write ONLY to this vault and to {{USER_NAME}}'s own DM ({{DM_CHANNEL}}) — and only via channels the user enabled at onboarding. Anything addressed to other people or shared systems (ticket comments, e-mails, chat messages to others) must be produced as a DRAFT for approval — never sent.
2. **Every fact needs a source.** Each topic-history entry contains `(source: <system/channel/ID>, <date>)` (before the optional `[confidence]` / `[T-…]` tags); so does the `State:` line of every task record. Exception: lines of a card's `## Current state` carry no source — their source is the `-history` entry with the same date. Facts without a source are tagged `[unverified]`.
3. **Don't guess — ask.** Ambiguous, contradictory or missing information, or a decision that belongs to the user: interactive tools interview one question at a time with a recommended answer; unattended jobs append to `briefs/pending-questions.md`. Full protocol: `automations/_grill-me-protocol.md`. Mandatory for: new/changed automations, vault structure changes, anything touching communication with other people.
4. **Don't create tasks eagerly.** No task in TASKS.md if the message is FYI, the owner is someone else, or it's outside the user's responsibilities. When unsure → section "Candidates" of TASKS.md: a full record with TYPE `CANDIDATE` (rule 15); unconfirmed candidates expire after 14 days.
5. **No duplicate topics.** Search `topics/` RECURSIVELY (including `aliases:` front matter) before creating a file; place new topics in the matching subfolder; new topics are proposed in the daily brief and created after the user confirms.
6. **Cross-domain organizations get their own card.** An organization (customer/partner/vendor/institution) active in MORE than one domain gets a dedicated card in `organizations/<name>.md` with a separate "Role per domain" section for each domain. Topic cards, briefs and the index link to it via wikilink instead of restating its status — so the entity's role in one domain is never conflated with another.
7. **People tagging.** Tag every person mentioned in briefs/entries: {{TAG_SET e.g. [CLIENT!], [PARTNER], [VENDOR], [INSTITUTION], team tags}}. Never let an external party be mistaken for a colleague.
8. **No evaluations of people.** Organizational facts only (role, team, org type, topics, language).
9. **Sensitive knowledge** (`knowledge/` files marked with the authorization header) drives what must NOT be promised externally; automated jobs may only propose additions marked `[unverified — needs authorization]`.
10. **Wikilinks are mandatory for cross-references.** Any mention of another topic card inside vault content (topics, briefs, TASKS.md, decision log) uses `[[file-name-without-extension]]`. Don't restate facts that live in another card — link to it (single source of truth). Each topic card also lists its related cards in front matter `related_topics: [card-1, card-2]`, kept in sync with the wikilinks used in the body. Task references use the ID tag `[T-YYYYMMDD-nn]` (at the end of a history line). `related_topics` = cards from topics/ (and organizations/) linked in the body, never `*-history*` files (the footer link `[[<card>-history]]` is not listed there).
11. **Chat findings must be persisted.** Any material fact, status change, decision, or new/changed task that surfaces during an interactive chat with the user (not only during scheduled scans) MUST be recorded in the vault in the same session — topic-card history, TASKS.md, decision log or the relevant entity card. Source: `(source: conversation with the user, YYYY-MM-DD)`, or the original system if the user quotes one. Nothing material may live only in the chat transcript. A finding about a task = edit its record + one `TASKS-log.md` line; a finding about a matter = one line appended to `<card>-history.md` + rewrite of the card's `Current state` when the state changed.
12. **Language (set at onboarding).** Conversation with the user in {{CONVERSATION_LANGUAGE}}; vault content (topic cards, briefs, TASKS.md) stored in {{VAULT_LANGUAGE}}; source quotes kept in the original; team-facing draft artifacts in {{TEAM_LANGUAGE}}. Default: VAULT_LANGUAGE = CONVERSATION_LANGUAGE.
13. **Dates** absolute, ISO (YYYY-MM-DD). Names kebab-case, prefixed by domain where helpful.
14. **Automations are opt-in and live in two places.** The user decides at onboarding which scheduled jobs (if any) to enable and at what cadence; an enabled job exists as the executable scheduled task PLUS its mirror in `automations/<task>.md`. Any change lands in both (see `automations/README.md`); tools without scheduler access edit the mirror and flag `last_synced: PENDING-SYNC`.
15. **Task record (TASKS.md).** One task = one block, format in `_templates/task.md`: header `### T-YYYYMMDD-nn · TYPE · title`, one fields line `Status · Owner · Topic · Linear · Deadline · Created · Updated` (all mandatory, `none` instead of empty), one `State:` line with a source, optional `Next step:`. NOTHING else inside a record — quotes, reviews and status narratives go to the card history and the task log. Any change = edit the field + `Updated:` + one line in `TASKS-log.md`. Never add a new header for an existing task. New ID: `python3 automations/housekeeping.py --new-id` (or grep `T-<today>-` in TASKS.md, TASKS-log.md, archive/tasks/); the dated ID avoids collisions when several tools write in parallel. Records in each section are ordered by ID descending (newest on top). Closing = move the whole block to `archive/tasks/TASKS-YYYY-Qn.md` immediately + log line `closed: <reason>` (or `obsolete: <reason>`). `Linear:` holds the tracker ID ({{TICKETING}}); with an ID the tracker's status wins, with `none` the status is confirmed by {{USER_NAME}}. Candidates: TYPE `CANDIDATE`, only in section `## Candidates`, expire after 14 days. Section `## Recurring` holds recurring duties as plain bullets without IDs (outside the check). The card section `## Tasks` lists the card's OPEN non-candidate records (`- T-… — title`) and is updated whenever a record is created, closed or moved to another card.
16. **State is separated from history.** Topic cards hold STATE only: `## Current state` (5–10 lines, one per thread, REWRITTEN in place — never appended) plus Summary / People / Open questions / Tasks / Risks / Decisions; no `## History` section. EVENTS go to `<card>-history.md` in the same folder (append at the END, chronological, `- YYYY-MM-DD: … (source: …) [confidence] [T-…]`), template `_templates/topic-history.md`. Boundary: "what happened to the matter" → card history; "what happened to the task" → `TASKS-log.md`. `*-history*` files are never listed in `related_topics`, never get `aliases`, never count as topics for dedupe (rule 5). Quarterly rollover and format checks: `python3 automations/housekeeping.py --check` (weekly, e.g. in the Monday brief) and `--apply` (first day of a quarter, or on request).

## Task typology (TASKS.md)

`ACTION_REQUIRED` | `DECISION_REQUIRED` | `WAITING_FOR_OTHER` | `FYI` | `RISK_TO_MONITOR` (+ `CANDIDATE` for unconfirmed items in section "Candidates")
Each task: owner, source (in `State:`), related topic, tracker ID or `none`, deadline (or `none`), status (`open` | `closed` | `obsolete`). Record format: `_templates/task.md` (rule 15).

## Watchlist

A topic with `watch: true` in front matter is on the watchlist: when enabled, the urgency scan alerts the user when something material happens in it (blocker, escalation, someone waiting on the user, decision made/needed, deadline at risk).

## Topic file format

See `_templates/topic.md` (state) and `_templates/topic-history.md` (events). History is append-only, chronological, newest at the BOTTOM, one line per event; read the card's `Current state` for the current picture. Front matter `related_topics` lists linked cards (kebab-case file names, no brackets); keep it in sync with the wikilinks used in the body.

## Housekeeping

`python3 automations/housekeeping.py --check` validates task records, the task log, cards and histories (read-only; exit code 1 on violations). `--apply` performs the quarterly rollover of `TASKS-log.md` and every live `<card>-history.md`, moves `closed`/`obsolete` records to `archive/tasks/`, and expires candidates older than 14 days — it never rewrites the content of an entry. Standard library only, no venv. The words it expects (`Status`, `open`, `Current state`, `(source: …)`, …) are a label set: default `en`; a vault kept in another {{VAULT_LANGUAGE}} selects or overrides them in `automations/housekeeping.labels.json` (see README "Label sets"). Keep this file, the templates and the label set consistent.

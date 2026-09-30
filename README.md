# Work OS — an AI-maintained personal work system

A file-based "operating system" for your work: a knowledge vault + daily monitoring + briefings + a task register, maintained by AI tools (Claude/Cowork, Claude Code, Codex, or a local LLM) according to written conventions. The goal: a **personal work assistant** that remembers your work with sources, surfaces what needs you, and drafts (never sends) your outgoing messages. Role-agnostic: a guided interview adapts it to YOUR job on day one.

Born from a real deployment for a Technical Project Manager; everything here is the generic, empty version of a system that runs in production daily.

## What you get

- **Topic cards** (`topics/`) — one card per ongoing matter holding its *current state*, plus a separate append-only, source-cited `<card>-history.md`. Ask "where does X stand?" (the card) or "show me the full history of X" (the history file) and get a real answer.
- **Who-is-who maps** (`people/`, `organizations/`) — so AI never confuses a customer with a colleague.
- **Task register** (`TASKS.md`) — your commitments from everywhere (tickets, chat, email), one fixed record per task with a dated ID (`T-YYYYMMDD-nn`), typed: ACTION_REQUIRED / DECISION_REQUIRED / WAITING_FOR_OTHER / FYI / RISK_TO_MONITOR. What happened to each task goes to the append-only `TASKS-log.md`.
- **Housekeeping script** (`automations/housekeeping.py`) — validates the format and does the quarterly rollover and archiving, so the files stay small (see [State vs history](#state-vs-history)).
- **Decision log** (`decisions/`) — decisions separated from discussion, with communication consequences.
- **Daily brief + urgency scans** (`automations/`) — prompt templates you install as scheduled tasks in your AI tool. **Opt-in:** enable only the jobs you want, at the cadence you choose (some users run none).
- **Phone access** (`automations/bridge/`) — **opt-in** Slack bot on your machine that answers questions about your vault (read-only), powered by Claude Code CLI or a local LLM (LM Studio).
- **"Don't guess — ask" protocol** (`automations/_grill-me-protocol.md`) — AI interviews you instead of assuming; unattended jobs queue questions in `briefs/pending-questions.md`.

## Quickstart

_Using Claude Desktop (Cowork)? `GETTING-STARTED.md` walks through install → open Cowork → create the project pointed at this folder, with the exact instructions to paste. In short:_

1. Clone this repo to a local folder your AI assistant can read and write.
2. Open the folder in your AI tool (Claude desktop/Cowork, Claude Code, etc.).
3. Say: **"Read ONBOARDING.md and run the onboarding interview."**
   The AI asks your languages first (conversation / vault storage / team-facing), then grills you — one question at a time, each with a recommended answer — about your role, domains, sources, reporting needs, who-is-who, and which automations (if any) and notifications you want. It customizes folders, fills placeholders in `AGENTS.md`, and sets up only the scheduled jobs you opted into. It won't declare itself done until your role, full topic list, daily tasks + reporting needs, and communication setup are all captured — `automations/onboarding-validation.md` is the gate, and you can re-run it any time with "validate my setup".
4. (Optional) Set up the Slack bridge for phone access: `automations/bridge/SETUP.md`. One shared app manifest, your own secrets — see the note there on why each user runs their own app instance.

## Layout

```
GETTING-STARTED.md   set up the vault inside Claude Desktop (Cowork): install, open Cowork, create the project
ONBOARDING.md        the interview that adapts the system to you
AGENTS.md            conventions every AI tool must follow ({{PLACEHOLDERS}} until onboarding)
TASKS.md             your task register (one record per task, current state only)
TASKS-log.md         append-only task event log
GLOSSARY.md          your domain/company abbreviations
topics/              topic cards (state) + <card>-history.md (events): domains/<your-areas>/ + internal/ + others/
people/              people map (facts only, no evaluations)
organizations/       customers, partners, vendors, institutions
knowledge/           curated domain knowledge incl. communication-sensitive files
decisions/           decision_log.md
briefs/              automation output + pending-questions.md
automations/         prompt templates for scheduled jobs + grill-me protocol + Slack bridge + housekeeping.py
_templates/          file templates (topic card, topic history, task record, person card)
archive/tasks/       created by housekeeping: closed records and archived task logs (git-ignored)
```

## State vs history

**Why.** When the current state and the running history of something live in the same place, files only grow: every update is appended as a new entry, the same task appears under several headings with different statuses, and a topic card turns into thousands of words of log. The result is large files that are expensive to read on every run — and, worse, a *wrong status*, because "where does this stand?" has no single place to be answered. Search or RAG does not fix that; separating the two does.

**The model** — five "tables", each a plain Markdown file:

| Table | File | Key | How it is written |
|---|---|---|---|
| tasks (state) | `TASKS.md` | `T-YYYYMMDD-nn` | one fixed record per task, edited in place |
| task events | `TASKS-log.md` (+ `archive/tasks/TASKS-log-YYYY-Qn.md`) | ID + timestamp | append-only, chronological, quarterly rollover |
| topics (state) | `topics/…/<card>.md` | file name | `## Current state` rewritten in place; no history section |
| topic events | `topics/…/<card>-history.md` (+ `<card>-history-YYYY-Qn.md`) | card + date | append-only, chronological, quarterly rollover |
| closed tasks | `archive/tasks/TASKS-YYYY-Qn.md` | ID | the whole record is moved here the moment it is closed |

Links between them: `Topic: [[card]]` in a task record; `[T-…]` at the end of a history line and in every log line. "Context of task T-X" = its `State:` line + the card's `Current state` + grep `T-X` in `TASKS-log*` and `*-history*`. Boundary: *what happened to the matter* → card history; *what happened to the task* → task log.

A task record (format: `_templates/task.md`, rules: `AGENTS.md` 15–16):

```
### T-20260101-01 · ACTION_REQUIRED · Vendor X: send signed contract
- Status: open · Owner: Alex [TEAM] · Topic: [[example-topic]] · Linear: none · Deadline: 2026-01-15 · Created: 2026-01-01 · Updated: 2026-01-02
- State: draft sent, waiting for the signature date. (source: chat #vendor-x, 2026-01-01)
- Next step: forward the date to finance.
```

**Housekeeping.** Rules in a prompt do not execute themselves, so a small script enforces them (Python 3 standard library, no venv):

```
python3 automations/housekeeping.py --check     # validate; exit 1 on violations (read-only)
python3 automations/housekeeping.py --apply     # quarterly rollover, archive closed records, expire candidates > 14 days
python3 automations/housekeeping.py --new-id    # print the next free T-<today>-nn
# common options: --vault PATH  --today YYYY-MM-DD  --labels en|pl|FILE.json
cd automations && python3 -m unittest test_housekeeping    # the test suite
```

`--check` reports, with file and line: malformed record header or fields line, duplicate ID, missing field, a non-`open` record in `TASKS.md`, a candidate outside its section or older than 14 days, records not in descending ID order, a `## History` section in a card, a card without `## Current state` or without its `[[<card>-history]]` footer, history/log lines out of date order, a `[T-…]` tag pointing to an unknown ID, a `*-history*` file in `related_topics`, and an overdue quarterly rollover (`period` ≠ current quarter). Archived `-history-YYYY-Qn.md` files are checked leniently (front matter and `[T-…]` tags only), so migrated legacy content is never reformatted. `--apply` moves and renames files but never rewrites the text of an entry. Run `--check` weekly (e.g. in the Monday brief) and `--apply` on the first day of each quarter.

The fresh template passes `--check` for the quarter in `TASKS-log.md` (`period: 2026-Q3`): `python3 automations/housekeeping.py --check --vault . --today 2026-09-30` → 0 violations. In a later quarter the first `--check` reports `ROLLOVER_DUE` on `TASKS-log.md`; run `--apply` once (or set `period:` to the current quarter during onboarding).

### Label sets

The words the script expects are configurable, so a vault kept in another language uses the same tooling. Selection, first match wins: `--labels en|pl|path.json` on the command line → `automations/housekeeping.labels.json` in the vault → built-in `en`.

| Key | `en` (default) | `pl` (built-in) |
|---|---|---|
| `fields` (`status`, `owner`, `topic`, `linear`, `deadline`, `created`, `updated`) | `Status · Owner · Topic · Linear · Deadline · Created · Updated` | `Status · Owner · Temat · Linear · Deadline · Utworzono · Aktualizacja` |
| `none` (empty-field value) | `none` | `brak` |
| `statuses` (`open`, `closed`, `obsolete`) | `open`, `closed`, `obsolete` | `otwarte`, `zamknięte`, `nieaktualne` |
| `types` / `candidate_type` | the five types / `CANDIDATE` | the five types / `POTENCJALNE` |
| `state_line`, `next_step_line` | `State`, `Next step` | `Stan`, `Następny krok` |
| `sections` (`open`, `recurring`, `candidates`) | `Open`, `Recurring`, `Candidates` | `Otwarte`, `Cykliczne`, `Potencjalne zadania` |
| `card_state_heading`, `card_history_heading`, `history_footer` | `Current state`, `History`, `History` | `Stan na dziś`, `Historia`, `Historia` |
| `source_marker` | `source` → `(source: …)` | `źródło` → `(źródło: …)` |
| `events` (`created`, `type`, `deadline`, `state`, `linear`, `handed_over`, `closed`, `obsolete`) | `created`, `type`, `deadline`, `state`, `linear`, `handed over`, `closed`, `obsolete` | `utworzone`, `typ`, `deadline`, `stan`, `linear`, `przekazane`, `zamknięte`, `nieaktualne` |
| `messages` | violation/operation messages in English | the same in Polish |

A JSON label file starts from a built-in set and overrides only what differs; object keys are merged key by key, keys starting with `_` are ignored, unknown keys are an error (exit code 2):

```json
{ "base": "en", "fields": { "linear": "Jira" }, "sections": { "candidates": "Potential tasks" } }
```

See `automations/housekeeping.labels.example.json`. The ID format (`T-YYYYMMDD-nn`), the ` · ` separator, the task types' UPPER_CASE form and the log/history line shapes are fixed. If you change labels, update `_templates/` and `AGENTS.md` rules 15–16 to match.

## Hard principles (full version in AGENTS.md)

1. Automations write only to this vault and to YOUR own DM — anything addressed to other people is produced as a draft for your approval.
2. Every fact carries a source; no source → `[unverified]`.
3. Don't guess — ask (interactively one question at a time; unattended → pending-questions.md).
4. Sensitive knowledge files (what must NOT be promised externally) require explicit human authorization.

## Requirements

An AI assistant with access to your local files and your work tools (e.g., Claude with MCP connectors for Slack/email/tickets), plus optionally: Claude Code CLI and/or LM Studio for the Slack bridge. No databases, no servers — plain Markdown and two small Python scripts (the optional bridge, and the standard-library-only `housekeeping.py`).

## License & privacy

Template only — contains no data. Everything your instance produces stays in your local folder. Never commit `.env`, `briefs/`, or filled maps to a public repo (see `.gitignore`).

# Work OS — an AI-maintained personal work system

A file-based "operating system" for your work: a knowledge vault + daily monitoring + briefings + a task register, maintained by AI tools (Claude/Cowork, Claude Code, Codex, or a local LLM) according to written conventions. The goal: a **personal work assistant** that remembers your work with sources, surfaces what needs you, and drafts (never sends) your outgoing messages. Role-agnostic: a guided interview adapts it to YOUR job on day one.

Born from a real deployment for a Technical Project Manager; everything here is the generic, empty version of a system that runs in production daily.

## What you get

- **Topic cards** (`topics/`) — one file per ongoing matter, with an append-only, source-cited history. Ask "show me the full history of X" and get a real answer.
- **Who-is-who maps** (`people/`, `organizations/`) — so AI never confuses a customer with a colleague.
- **Task register** (`TASKS.md`) — your commitments from everywhere (tickets, chat, email), typed: ACTION_REQUIRED / DECISION_REQUIRED / WAITING_FOR_OTHER / FYI / RISK_TO_MONITOR.
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
TASKS.md             your task register
GLOSSARY.md          your domain/company abbreviations
topics/              topic cards: domains/<your-areas>/ + internal/ + others/
people/              people map (facts only, no evaluations)
organizations/       customers, partners, vendors, institutions
knowledge/           curated domain knowledge incl. communication-sensitive files
decisions/           decision_log.md
briefs/              automation output + pending-questions.md
automations/         prompt templates for scheduled jobs + grill-me protocol + Slack bridge
_templates/          file templates (topic card, person card)
```

## Hard principles (full version in AGENTS.md)

1. Automations write only to this vault and to YOUR own DM — anything addressed to other people is produced as a draft for your approval.
2. Every fact carries a source; no source → `[unverified]`.
3. Don't guess — ask (interactively one question at a time; unattended → pending-questions.md).
4. Sensitive knowledge files (what must NOT be promised externally) require explicit human authorization.

## Requirements

An AI assistant with access to your local files and your work tools (e.g., Claude with MCP connectors for Slack/email/tickets), plus optionally: Claude Code CLI and/or LM Studio for the Slack bridge. No databases, no servers — plain Markdown and one small Python script.

## License & privacy

Template only — contains no data. Everything your instance produces stays in your local folder. Never commit `.env`, `briefs/`, or filled maps to a public repo (see `.gitignore`).

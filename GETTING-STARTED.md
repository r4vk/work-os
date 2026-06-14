# Start using Work OS in Claude

How to get a fresh Work OS vault running inside **Claude Desktop (Cowork)**. You do this ONCE (~15 min); afterwards you just open the project and talk to Claude.

> Work OS is a generic template — it holds no data until onboarding adapts it to you. This page is the **platform setup**; the interview that fills in your role, domains and languages lives in `ONBOARDING.md`.

## 0. Prerequisites

- A **paid Claude plan** (Pro, Max, Team, or Enterprise) — Cowork is not on the free plan.
- A **desktop computer** (macOS or Windows). Cowork is desktop-only — not web, not mobile.
- The **`work-os` folder on your machine**: clone the repo or copy the folder somewhere stable (e.g. `~/work-os`).

## 1. Install Claude Desktop

1. Download from **claude.com/download** (macOS or Windows) and install.
2. Sign in with your paid account.
3. _(Optional)_ Run the "Cowork readiness check" linked on the download page to confirm your machine supports Cowork.

## 2. Open Cowork

1. Launch Claude Desktop.
2. In the mode selector, switch from **Chat** to the **Cowork** tab (the mode becomes "Tasks").
3. Keep the app open and the computer awake while Claude works — closing the app ends the session.

## 3. Create a project pointed at the `work-os` folder

This is the core of the setup: it gives Claude persistent access to your vault plus standing instructions.

1. In the left sidebar, open **Projects** and click **+**.
2. Choose **Use an existing folder**.
3. Select your local **`work-os`** folder. This folder becomes the **boundary of Claude's file access** — Claude can only read and write inside it.
4. Name the project (e.g. "Work OS"), choose where to save it, and add the **project instructions** (next step).
5. Click **Create**.

## 4. Paste the project instructions

In the project's **Instructions** field, paste the block below. It's deliberately short — the real configuration is done by onboarding, and this just points Claude at the vault's own rules, so it works for ANY role unchanged:

```
This project is my Work OS vault — my personal work assistant.

Source of truth: ALWAYS read AGENTS.md first and follow its conventions exactly
(autonomy boundary, source every fact, don't-guess-ask, language, tagging).

If any {{placeholders}} are still unfilled, read ONBOARDING.md and run the
onboarding interview before doing anything else.

Boundaries: write only inside this vault and to my own DM; anything addressed to
other people or systems is a DRAFT for my approval — never send it. Every fact
carries a source; no source -> mark [unverified]. When something is unclear or
it's my decision, ask me one question with a recommendation; do not guess.

Talk to me in my language (set during onboarding).
```

## 5. Connect your work tools

Onboarding will ask where your work actually happens, so connect those sources first:

- Open **Settings > Connectors** and add what your role uses — e.g. Slack/Teams, Gmail/Outlook, Google Calendar, your tracker (Linear/Jira/Asana), Notion/Drive.
- Connectors run under your own permissions; you control how often each one asks before acting.

## 6. Run onboarding

In the project, start a task and say:

> **Read ONBOARDING.md and run the onboarding interview.**

Claude asks your languages first (conversation / vault storage / team-facing), then interviews you one question at a time about your role, domains, sources, reporting needs, who-is-who, and which automations and notifications you want. It will **not** declare itself done until the completion gate is met — it re-runs `automations/onboarding-validation.md` after each session, so you can stop and resume across several sittings until everything is clear.

## 7. (Optional, after onboarding) Automations and phone access

Both are **opt-in** — set them up only if you want them, and only once onboarding is complete:

- **Scheduled jobs** (e.g. a morning brief): type `/schedule` inside a task, or use **Scheduled** in the left sidebar. They run only while your computer is awake and the app is open. Prompts live in `automations/*.md`.
- **Phone access** (Slack bridge): follow `automations/bridge/SETUP.md` to query your vault from your phone (read-only).

## Daily use

Open the project and just ask: _"what's on me today?"_, _"show the history of <topic>"_, _"draft a reply to <X>"_. Claude treats the vault as its source of truth and keeps it updated as you talk.

---
_Platform steps follow the Claude Help Center ("Get started with Claude Cowork" and "Organize your tasks with projects in Cowork"). In-app labels may change over time — if a step looks different, follow the prompts in the app._

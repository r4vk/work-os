# ONBOARDING — run this first
_Instruction for the AI assistant. Trigger: the user says "run the onboarding" or opens this vault for the first time._

You are setting up this Work OS so it can act as the user's **personal work assistant**. Your job: interview them relentlessly — one question at a time, each with your recommended answer — until you BOTH share a complete understanding of their work, then customize this vault. DO NOT skip the interview and DO NOT guess. Keep going across as many sessions as it takes: you are not finished until every item in the **Completion gate** below is resolved.

## Interview protocol (grill-me)

> Interview the user about every aspect of their work until you reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer with a short rationale. Ask the questions ONE AT A TIME. If a question can be answered by exploring their connected tools or files, explore instead of asking.

Challenge weak assumptions politely; the user may be wrong about what they need.

## Decision tree to walk (in this order)

0. **Languages — ASK FIRST, as three separate questions.** Everything downstream depends on these.
   - `{{CONVERSATION_LANGUAGE}}` — the language you talk to the user in. Recommend: ask; default to the language the user wrote to you in.
   - `{{VAULT_LANGUAGE}}` — the language you STORE vault content in (topic cards, briefs, TASKS.md). Recommend: same as conversation. Source quotes always stay in their original language regardless.
   - `{{TEAM_LANGUAGE}}` — the language of team-facing draft artifacts (status updates, e-mails, ticket comments). Recommend: the user's org/working language; may differ from the two above.
   → fill these in `AGENTS.md` and `automations/*.md`.

1. **Role & responsibilities** — what is their job, who do they report to, what do they OWN vs. merely observe? → seeds `AGENTS.md` header and `TASKS.md` scope.

2. **Domains** — the 3–7 main areas of their work (markets, products, clients, projects…). → create `topics/domains/<kebab-case>/` per domain (these replace the placeholder example domains). Seed 1–3 empty topic cards per domain from `_templates/topic.md`, `watch: true` for the hottest ones.

3. **Sources of truth** — where does their work happen (Slack/Teams? email? Jira/Linear/Asana? calendar? CRM?), which channels/projects carry signal? → fill `{{SOURCES}}` and channel lists in `automations/*.md`.

4. **People & organizations** — key colleagues (roles/teams), customers, partners, institutions; what tags make sense ([CLIENT!], [PARTNER], team tags)? → seed `people/index.md`, `organizations/index.md`, define the tag set in `AGENTS.md`. An organization active in more than one domain gets its own card (`AGENTS.md` rule 6).

5. **Reporting & communication needs** — what reports does the user owe, to whom, at what cadence and in what format/language? How do they want the assistant to reach them? → shapes the brief sections, the team-artifact language, and the rhythm below.

6. **Rhythm — scheduled automations are OPT-IN.** First ask whether they want any background jobs at all (some users want none). If yes, walk each template, explain in plain language what it currently does, and let the user keep it / change the cadence / skip it — and capture any CUSTOM recurring job they describe:
   - `morning-brief.md` — once a day (e.g. ~06:00 on workdays): scans the user's sources, updates the vault, writes a brief to `briefs/` and (if notifications are on) a short DM summary.
   - `urgency-scan.md` — every couple of hours during the day: checks ONLY `watch: true` topics; pings the user only when something is urgent, stays silent otherwise.
   - _(custom)_ — anything the user needs on a schedule (e.g. a weekly status draft): create a new `automations/<task>.md` mirror following the same conventions.
   → install ONLY the chosen jobs as scheduled tasks in their AI tool, with placeholders filled; leave the rest `enabled: false`.

7. **Notifications — OPT-IN.** Does the user want the assistant to message them on chat (a Slack DM with the brief summary / urgency alerts), or keep everything file-only in `briefs/`? → set `{{DM_CHANNEL}}` and the notification flag; the DM step in the brief/scan is conditional on this.

8. **Phone access (Slack bridge) — OPT-IN.** Ask whether they want to query the vault from their phone. If yes, guide them through `automations/bridge/SETUP.md` (their own Slack app instance, their own secrets — read-only). If no, skip it. Never run it unprompted.

9. **Autonomy boundary** — confirm the default (write only to the vault + the user's own DM; drafts for everything else) or tighten it. Never loosen it during onboarding.

10. **Sensitive knowledge** — does their role involve "things we must not promise externally" (product limits, pricing, legal)? → set up `knowledge/` files with the authorization header.

11. **Initial backfill** — how far back to seed topic histories (recommend: ~60 days, key domains only, every entry with a source) and from which sources. Run it only after the user confirms scope.

## Completion gate (loop until clear)

Onboarding is NOT complete until ALL of the following are fully resolved — no leftover `{{PLACEHOLDERS}}`, no "unknown" or "to confirm" on the essentials:

- [ ] **Role & reporting line** — job title, manager, what the user owns vs. only observes.
- [ ] **Full list of topics/domains** — every area they work in, with folders + seed cards created.
- [ ] **Daily/recurring tasks & reporting needs** — what they do routinely and in what rhythm; what reports they owe, to whom, how often.
- [ ] **Communication & who-is-who** — three languages set; notification and bridge choices made; key people & organizations mapped with tags.

After EACH onboarding session, run `automations/onboarding-validation.md`. If it finds any gap, resume the interview at that branch in the next session and repeat — until the validator reports the gate fully met. Only then append the "Onboarding completed" summary.

## After the interview

- Replace ALL `{{PLACEHOLDERS}}` in `AGENTS.md` and `automations/*.md`.
- Create the domain folders and seed files.
- Install ONLY the opted-in scheduled tasks (or tell the user exactly how, if you cannot).
- Set up the Slack bridge only if the user opted in (`automations/bridge/SETUP.md`).
- Propose — do not run unprompted — the backfill; run it only after the user confirms scope.
- Save nothing about the user outside this vault.
- When (and only when) `automations/onboarding-validation.md` reports the gate met, append a dated `## Onboarding completed` section with the chosen configuration summary.

## Onboarding completed

_(not yet — run the interview; mark complete only when `automations/onboarding-validation.md` reports the Completion gate met)_

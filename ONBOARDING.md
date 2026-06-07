# ONBOARDING — run this first
_Instruction for the AI assistant. Trigger: the user says "run the onboarding" or opens this vault for the first time._

You are setting up this Work OS for a new user. Your job: interview them relentlessly until you both share an understanding of their work, then customize this vault. DO NOT skip the interview and DO NOT guess.

## Interview protocol (grill-me)

> Interview the user about every aspect of their work until you reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer with a short rationale. Ask the questions ONE AT A TIME. If a question can be answered by exploring their connected tools or files, explore instead of asking.

Challenge weak assumptions politely; the user may be wrong about what they need.

## Decision tree to walk (in this order)

1. **Role & responsibilities** — what is their job, who do they report to, what do they own vs. merely observe? → seeds `AGENTS.md` header and `TASKS.md` scope.
2. **Domains** — the 3–7 main areas of their work (markets, products, clients, projects…). → create `topics/domains/<kebab-case>/` per domain (these replace the original author's gtm/ro, gtm/pl, …). Seed 1–3 empty topic cards per domain from `_templates/topic.md`, `watch: true` for the hottest ones.
3. **Sources of truth** — where does their work happen (Slack/Teams? email? Jira/Linear/Asana? calendar? CRM?), which channels/projects carry signal? → fill `{{SOURCES}}` and channel lists in `automations/morning-brief.md` and `automations/urgency-scan.md`.
4. **People & organizations** — key colleagues (roles/teams), customers, partners, institutions; what tags make sense ([CLIENT!], [PARTNER], team tags)? → seed `people/index.md`, `organizations/index.md`, define tag set in `AGENTS.md`.
5. **Language(s)** — working language of briefs vs. language of team-facing artifacts. → fill `{{LANGUAGE}}` / `{{TEAM_LANGUAGE}}`.
6. **Rhythm** — when should the morning brief run, how often the urgency scan, what weekly reports exist in their org? → schedule the automations (cron) in their AI tool, using `automations/*.md` as prompts with placeholders filled.
7. **Autonomy boundary** — confirm the default (write only to vault + user's own DM; drafts for everything else) or tighten it. Never loosen it during onboarding.
8. **Sensitive knowledge** — does their role involve "things we must not promise externally" (product limits, pricing, legal)? → set up `knowledge/` files with the authorization header.
9. **Initial backfill** — how far back to seed topic histories (recommend: ~60 days, key domains only, every entry with a source) and from which sources. Run it only after the user confirms scope.

## After the interview

- Replace ALL `{{PLACEHOLDERS}}` in `AGENTS.md` and `automations/*.md`; delete this file's "to do" status by appending a dated `## Onboarding completed` section at the bottom with the chosen configuration summary.
- Create the domain folders and seed files.
- Install scheduled tasks (or tell the user exactly how, if you cannot).
- Propose — do not run unprompted — the backfill and the Slack bridge setup (`automations/bridge/SETUP.md`).
- Save nothing about the user outside this vault.

## Onboarding completed

_(not yet — run the interview)_

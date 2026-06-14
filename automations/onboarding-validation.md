---
taskId: onboarding-validation
schedule: on-demand (run after every onboarding session; not a cron job)
enabled: false (template — no scheduling needed; invoke manually)
last_synced: —
---

# Onboarding validation — the completion gate

Run this AFTER every onboarding session, and any time the user says "validate my setup" / "check the configuration". Its single job: decide whether onboarding is COMPLETE or must CONTINUE. The system's goal is to be the user's personal work assistant — it cannot do that until everything below is known. Do NOT guess or fill gaps yourself; loop the interview until the gate is met.

Talk to the user in `{{CONVERSATION_LANGUAGE}}` (if still unset, that itself is gap #1).

## Step 1 — check the four hard gates

Read the vault and verify each. Mark ✅ met / ❌ gap, with the evidence (file + what's there or missing):

1. **Role & reporting line** — `AGENTS.md` header filled (no `{{ROLE}}`/`{{COMPANY}}` left); job title, manager, and what the user OWNS vs. merely observes are recorded; `TASKS.md` scope reflects it.
2. **Full list of topics/domains** — every work area captured as a `topics/domains/<domain>/` folder with ≥1 seed card; no domain the user mentioned is missing; `watch: true` set on the hottest ones.
3. **Daily/recurring tasks & reporting needs** — the user's routine work and rhythm are known; the reports they owe (to whom, cadence, format/language) are recorded; `TASKS.md` "Recurring" section reflects this.
4. **Communication & who-is-who** — all three languages set (`{{CONVERSATION_LANGUAGE}}`, `{{VAULT_LANGUAGE}}`, `{{TEAM_LANGUAGE}}`); notification choice and Slack-bridge choice made; key people in `people/index.md` and organizations in `organizations/index.md` with tags.

## Step 2 — check configuration completeness

- **No stray placeholders.** Grep `AGENTS.md` and `automations/*.md` for `{{` — any match (except inside these instruction templates themselves) is a gap.
- **Automations decision recorded.** It is explicit whether the user wants scheduled jobs at all; for each enabled job a mirror exists with placeholders filled and a real `schedule`; skipped ones are `enabled: false`. "Not decided yet" is a gap.
- **Notifications & bridge decisions recorded.** DM/notification on or off (and `{{DM_CHANNEL}}` set if on); bridge set up or explicitly declined.
- **Autonomy boundary** confirmed (default or tightened — never loosened).

## Step 3 — verdict

**If any gap exists → onboarding CONTINUES.**
- List the gaps shortest-path-first. For each, phrase ONE grill-me question (one decision + your recommended answer + short rationale), per `_grill-me-protocol.md`.
- Tell the user plainly: onboarding is not complete; here is exactly what's left. Resume the interview at the earliest open branch in `ONBOARDING.md`, ask one question at a time, apply answers to the vault, then run this validator again. Repeat until clean.
- Do NOT append "Onboarding completed" to `ONBOARDING.md`.

**If everything is ✅ → onboarding is COMPLETE.**
- Report the gate as met with a one-line summary per gate.
- Instruct that `ONBOARDING.md` may now get its dated `## Onboarding completed` section (config summary: languages, domains, sources, enabled automations + cadence, notification/bridge choices, autonomy boundary).
- Remind the user how to use the system day-to-day and that they can re-run this validator any time the setup changes.

IRON RULES: read-only except for reporting findings; never invent answers to close a gap; one question at a time; every recommendation carries a short rationale. Write nothing about the user outside this vault.

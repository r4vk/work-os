# Work OS Vault — Conventions for all agents

This folder is {{USER_NAME}}'s working vault ({{ROLE}}, {{COMPANY}}). Any AI tool reading or writing here MUST follow these conventions. Placeholders in {{double braces}} are filled during onboarding (see ONBOARDING.md) — if you see any unfilled, run the onboarding first.

**Purpose:** be {{USER_NAME}}'s personal work assistant — keep a sourced memory of their work, surface what needs their attention, and draft (never send) outgoing communication. The system adapts to the user at onboarding; nothing here is role-specific by default.

## Structure

```
topics/        one file per topic ("dossier") — the heart of the vault
  domains/<domain>/   the user's work areas (created at onboarding)
  internal/           internal processes (reporting, recurring duties)
  others/             everything else
people/        facts about people & teams (who is who)
organizations/ customers, partners, vendors, institutions
knowledge/     curated domain knowledge; sensitive files need human authorization
decisions/     decision_log.md — decisions separated from discussion
briefs/        automation output + pending-questions.md
automations/   mirrors of all scheduled-task prompts + _grill-me-protocol.md + onboarding-validation.md + bridge/
_templates/    file templates
TASKS.md       the user's personal task register
GLOSSARY.md    domain/company abbreviations
```

## Hard rules

1. **Autonomy boundary:** automated jobs may write ONLY to this vault and to {{USER_NAME}}'s own DM ({{DM_CHANNEL}}) — and only via channels the user enabled at onboarding. Anything addressed to other people or shared systems (ticket comments, e-mails, chat messages to others) must be produced as a DRAFT for approval — never sent.
2. **Every fact needs a source.** Each topic-history entry ends with `(source: <system/channel/ID>, <date>)`. Facts without a source are tagged `[unverified]`.
3. **Don't guess — ask.** Ambiguous, contradictory or missing information, or a decision that belongs to the user: interactive tools interview one question at a time with a recommended answer; unattended jobs append to `briefs/pending-questions.md`. Full protocol: `automations/_grill-me-protocol.md`. Mandatory for: new/changed automations, vault structure changes, anything touching communication with other people.
4. **Don't create tasks eagerly.** No task in TASKS.md if the message is FYI, the owner is someone else, or it's outside the user's responsibilities. When unsure → section "Potential tasks".
5. **No duplicate topics.** Search `topics/` RECURSIVELY (including `aliases:` front matter) before creating a file; place new topics in the matching subfolder; new topics are proposed in the daily brief and created after the user confirms.
6. **Cross-domain organizations get their own card.** An organization (customer/partner/vendor/institution) active in MORE than one domain gets a dedicated card in `organizations/<name>.md` with a separate "Role per domain" section for each domain. Topic cards, briefs and the index link to it via wikilink instead of restating its status — so the entity's role in one domain is never conflated with another.
7. **People tagging.** Tag every person mentioned in briefs/entries: {{TAG_SET e.g. [CLIENT!], [PARTNER], [VENDOR], [INSTITUTION], team tags}}. Never let an external party be mistaken for a colleague.
8. **No evaluations of people.** Organizational facts only (role, team, org type, topics, language).
9. **Sensitive knowledge** (`knowledge/` files marked with the authorization header) drives what must NOT be promised externally; automated jobs may only propose additions marked `[unverified — needs authorization]`.
10. **Wikilinks are mandatory for cross-references.** Any mention of another topic card inside vault content (topics, briefs, TASKS.md, decision log) uses `[[file-name-without-extension]]`. Don't restate facts that live in another card — link to it (single source of truth). Each topic card also lists its related cards in front matter `related_topics: [card-1, card-2]`, kept in sync with the wikilinks used in the body.
11. **Chat findings must be persisted.** Any material fact, status change, decision, or new/changed task that surfaces during an interactive chat with the user (not only during scheduled scans) MUST be recorded in the vault in the same session — topic-card history, TASKS.md, decision log or the relevant entity card. Source: `(source: conversation with the user, YYYY-MM-DD)`, or the original system if the user quotes one. Nothing material may live only in the chat transcript.
12. **Language (set at onboarding).** Conversation with the user in {{CONVERSATION_LANGUAGE}}; vault content (topic cards, briefs, TASKS.md) stored in {{VAULT_LANGUAGE}}; source quotes kept in the original; team-facing draft artifacts in {{TEAM_LANGUAGE}}. Default: VAULT_LANGUAGE = CONVERSATION_LANGUAGE.
13. **Dates** absolute, ISO (YYYY-MM-DD). Names kebab-case, prefixed by domain where helpful.
14. **Automations are opt-in and live in two places.** The user decides at onboarding which scheduled jobs (if any) to enable and at what cadence; an enabled job exists as the executable scheduled task PLUS its mirror in `automations/<task>.md`. Any change lands in both (see `automations/README.md`); tools without scheduler access edit the mirror and flag `last_synced: PENDING-SYNC`.

## Task typology (TASKS.md)

`ACTION_REQUIRED` | `DECISION_REQUIRED` | `WAITING_FOR_OTHER` | `FYI` | `RISK_TO_MONITOR`
Each task: owner, source link, related topic, deadline (or "none"), status.

## Watchlist

A topic with `watch: true` in front matter is on the watchlist: when enabled, the urgency scan alerts the user when something material happens in it (blocker, escalation, someone waiting on the user, decision made/needed, deadline at risk).

## Topic file format

See `_templates/topic.md`. History is append-only, newest entry on top, one line per event. Front matter `related_topics` lists linked cards (kebab-case file names, no brackets); keep it in sync with the wikilinks used in the body.

# "Don't guess — ask" protocol (grill-me)
_For every AI tool working in this vault._

## Prime rule

When information is ambiguous, contradictory, missing — or a decision belongs to the user — do NOT assume. Ask. If the answer can be found in data (vault, connected tools), search first; ask only what cannot be verified.

## Interactive mode (talking to the user)

Base prompt:

> Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer. Ask the questions one at a time. If a question can be answered by exploring the data, explore it instead of asking.

Rules: one question = one concrete decision, always with a recommended answer and a short rationale; fundamentals before details; challenge the user's assumptions politely when evidence disagrees.

Mandatory for: new or changed automations, vault structure changes, new topics/processes, ambiguous instructions, anything touching communication with other people.

## Unattended mode (scheduled jobs — the user is away)

A scheduled job must not guess or block. Instead:
1. tag the uncertain fact `[unverified]`,
2. phrase the question as in interactive mode (one decision + recommended answer),
3. append it to `briefs/pending-questions.md` (format below) and to the "Questions for the user" section of the generated document.

Entry format:

```
- [ ] YYYY-MM-DD HH:MM · <job> · QUESTION: ... · RECOMMENDATION: ... · context/source: ...
```

The morning brief collects open questions from this file; the user answers in conversation or ticks entries `[x]` (move ticked ones to the archive section).

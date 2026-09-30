#!/usr/bin/env python3
"""Housekeeping for a Work OS vault: validate and maintain the state/history data model
(task records in TASKS.md, task events in TASKS-log.md, topic cards = state,
<card>-history.md = events). See README.md "State vs history" and AGENTS.md rules 15-16.

Usage:
  housekeeping.py --check  [--vault PATH] [--today YYYY-MM-DD] [--labels en|pl|FILE.json]
  housekeeping.py --apply  [--vault PATH] [--today YYYY-MM-DD] [--labels en|pl|FILE.json]
  housekeeping.py --new-id [--vault PATH] [--today YYYY-MM-DD]

Label set (the words used in records, sections and messages), first match wins:
  1. --labels en | pl | path/to/labels.json
  2. <vault>/automations/housekeeping.labels.json   (optional)
  3. built-in "en"
A JSON label file may start from a built-in set: {"base": "en", "fields": {"linear": "Jira"}}.
Keys are documented in automations/housekeeping.labels.example.json and README.md.

Exit codes: 0 ok, 1 violations found (--check), 2 usage/label-set error.
Python standard library only.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

SEP = " · "
CANDIDATE_MAX_AGE_DAYS = 14
LABELS_FILE = Path("automations") / "housekeeping.labels.json"

TASK_ID_RE = re.compile(r"T-\d{8}-\d{2}")
SECTION_RE = re.compile(r"^## (.+)$")
HIST_LINE_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2}): (.+)$")
LOG_LINE_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) · (T-\d{8}-\d{2}) · ([^·]+?) · (.+)$")
TAG_RE = re.compile(r"\[(T-\d{8}-\d{2})\]")
QUARTER_RE = re.compile(r"-history-(\d{4}-Q[1-4])\.md$")


# ---------------------------------------------------------------------------
# Label sets
# ---------------------------------------------------------------------------

class LabelError(ValueError):
    """Unknown label set, unreadable label file or invalid label keys."""


BUILTIN_LABELS: dict[str, dict] = {
    "en": {
        "fields": {"status": "Status", "owner": "Owner", "topic": "Topic", "linear": "Linear",
                   "deadline": "Deadline", "created": "Created", "updated": "Updated"},
        "none": "none",
        "statuses": {"open": "open", "closed": "closed", "obsolete": "obsolete"},
        "types": ["ACTION_REQUIRED", "DECISION_REQUIRED", "WAITING_FOR_OTHER", "FYI", "RISK_TO_MONITOR"],
        "candidate_type": "CANDIDATE",
        "state_line": "State",
        "next_step_line": "Next step",
        "sections": {"open": "Open", "recurring": "Recurring", "candidates": "Candidates"},
        "card_state_heading": "Current state",
        "card_history_heading": "History",
        "history_footer": "History",
        "source_marker": "source",
        "events": {"created": "created", "type": "type", "deadline": "deadline", "state": "state",
                   "linear": "linear", "handed_over": "handed over", "closed": "closed", "obsolete": "obsolete"},
        "messages": {
            "FIELDS_MISSING": "{id}: missing fields line",
            "STAN_MISSING": "{id}: missing {state} line",
            "HEADER_FORMAT": "header without ID/TYPE: {line}",
            "TYPE_UNKNOWN": "{id}: unknown TYPE {typ}",
            "FIELDS_FORMAT": "{id}: malformed fields line",
            "STAN_FORMAT": "{id}: expected '- {state}:'",
            "STAN_NO_SOURCE": "{id}: {state} without ({source}: …)",
            "EXTRA_LINE": "{id}: extra line in record: {line}",
            "DUPLICATE_ID": "{id} already at line {line}",
            "STATUS_NOT_OPEN": "{id}: Status {status} — move to archive/tasks/ (--apply)",
            "CANDIDATE_OUTSIDE": "{id}: {candidate} outside the candidates section",
            "CANDIDATE_WRONG_TYPE": "{id}: TYPE {typ} in the candidates section",
            "CANDIDATE_STALE": "{id}: candidate older than {days} days",
            "ID_DATE_MISMATCH": "{id}: date in ID ≠ {created_label} {created}",
            "ORDER": "section {section}: records not in descending ID order",
            "RELATED_HISTORY": "related_topics lists a history file",
            "CARD_NO_STATE": "missing section '{heading}'",
            "CARD_HAS_HISTORY": "{history} section in card — history belongs in *-history.md",
            "CARD_NO_HISTORY_LINK": "missing footer '{footer}: [[{stem}-history]]'",
            "LINE_FORMAT": "malformed line: {line}",
            "LINE_ORDER": "entry earlier than the previous one — logs are chronological",
            "UNKNOWN_TASK_ID": "{tid} not found in TASKS.md or archive/tasks/",
            "FM_MISSING": "missing '{key}' in front matter",
            "ROLLOVER_DUE": "period {period} ≠ {quarter} — run --apply",
            "LOG_MISSING": "task log missing",
            "op_rollover_skipped": "SKIPPED rollover {live}: {archive} already exists — resolve manually",
            "op_rollover": "rollover {live}: {old} → {archive}; new period {new}",
            "op_expired": "expired candidate {id}",
            "op_archived": "archived {id} ({status})",
            "expire_reason": "candidate not confirmed > {days} days",
            "expire_log_text": "housekeeping --apply, created {created}",
            "archive_header": "# TASKS — archive {quarter}\n_Closed/obsolete records, moved whole (last state). "
                              "Event trail: TASKS-log-*.md._\n\n",
            "summary_check": "housekeeping --check: {n} violations",
            "summary_apply": "housekeeping --apply: {n} operations",
        },
    },
    "pl": {
        "fields": {"status": "Status", "owner": "Owner", "topic": "Temat", "linear": "Linear",
                   "deadline": "Deadline", "created": "Utworzono", "updated": "Aktualizacja"},
        "none": "brak",
        "statuses": {"open": "otwarte", "closed": "zamknięte", "obsolete": "nieaktualne"},
        "types": ["ACTION_REQUIRED", "DECISION_REQUIRED", "WAITING_FOR_OTHER", "FYI", "RISK_TO_MONITOR"],
        "candidate_type": "POTENCJALNE",
        "state_line": "Stan",
        "next_step_line": "Następny krok",
        "sections": {"open": "Otwarte", "recurring": "Cykliczne", "candidates": "Potencjalne zadania"},
        "card_state_heading": "Stan na dziś",
        "card_history_heading": "Historia",
        "history_footer": "Historia",
        "source_marker": "źródło",
        "events": {"created": "utworzone", "type": "typ", "deadline": "deadline", "state": "stan",
                   "linear": "linear", "handed_over": "przekazane", "closed": "zamknięte", "obsolete": "nieaktualne"},
        "messages": {
            "FIELDS_MISSING": "{id}: brak linii pól",
            "STAN_MISSING": "{id}: brak linii {state}",
            "HEADER_FORMAT": "nagłówek bez ID/TYP: {line}",
            "TYPE_UNKNOWN": "{id}: TYP {typ}",
            "FIELDS_FORMAT": "{id}: zła linia pól",
            "STAN_FORMAT": "{id}: oczekiwano '- {state}:'",
            "STAN_NO_SOURCE": "{id}: {state} bez ({source}: …)",
            "EXTRA_LINE": "{id}: dodatkowa linia w rekordzie: {line}",
            "DUPLICATE_ID": "{id} już w linii {line}",
            "STATUS_NOT_OPEN": "{id}: Status {status} — przenieś do archive/tasks/",
            "CANDIDATE_OUTSIDE": "{id}: {candidate} poza sekcją kandydatów",
            "CANDIDATE_WRONG_TYPE": "{id}: TYP {typ} w sekcji kandydatów",
            "CANDIDATE_STALE": "{id}: kandydat starszy niż {days} dni",
            "ID_DATE_MISMATCH": "{id}: data w ID ≠ {created_label} {created}",
            "ORDER": "sekcja {section}: rekordy nie są po ID malejąco",
            "RELATED_HISTORY": "related_topics zawiera plik historii",
            "CARD_NO_STATE": "brak sekcji '{heading}'",
            "CARD_HAS_HISTORY": "sekcja {history} w karcie — historia należy do *-history.md",
            "CARD_NO_HISTORY_LINK": "brak stopki '{footer}: [[{stem}-history]]'",
            "LINE_FORMAT": "zła linia: {line}",
            "LINE_ORDER": "wpis wcześniejszy niż poprzedni — dzienniki są chronologiczne",
            "UNKNOWN_TASK_ID": "{tid} nie istnieje w TASKS.md ani archive/tasks/",
            "FM_MISSING": "brak '{key}' w front matter",
            "ROLLOVER_DUE": "period {period} ≠ {quarter} — uruchom --apply",
            "LOG_MISSING": "brak dziennika zadań",
            "op_rollover_skipped": "POMINIĘTO rollover {live}: {archive} już istnieje — rozstrzygnij ręcznie",
            "op_rollover": "rollover {live}: {old} → {archive}; nowy period {new}",
            "op_expired": "wygaszono kandydata {id}",
            "op_archived": "zarchiwizowano {id} ({status})",
            "expire_reason": "kandydat niepotwierdzony > {days} dni",
            "expire_log_text": "housekeeping --apply, utworzono {created}",
            "archive_header": "# TASKS — archiwum {quarter}\n_Rekordy zamknięte/nieaktualne, przenoszone w całości "
                              "(ostatni stan). Przebieg: TASKS-log-*.md._\n\n",
            "summary_check": "housekeeping --check: {n} naruszeń",
            "summary_apply": "housekeeping --apply: {n} operacji",
        },
    },
}

_DICT_KEYS = ("fields", "statuses", "sections", "events", "messages")
_STR_KEYS = ("none", "candidate_type", "state_line", "next_step_line", "card_state_heading",
             "card_history_heading", "history_footer", "source_marker")


class Labels:
    """A validated label set plus the regular expressions derived from it."""

    def __init__(self, data: dict, name: str = "custom") -> None:
        ref = BUILTIN_LABELS["en"]
        unknown = set(data) - set(ref)
        if unknown:
            raise LabelError(f"label set '{name}': unknown key(s) {sorted(unknown)}; allowed: {sorted(ref)}")
        missing = set(ref) - set(data)
        if missing:
            raise LabelError(f"label set '{name}': missing key(s) {sorted(missing)}")
        for k in _DICT_KEYS:
            if not isinstance(data[k], dict):
                raise LabelError(f"label set '{name}': '{k}' must be an object")
            bad = set(data[k]) ^ set(ref[k])
            if bad:
                raise LabelError(f"label set '{name}': '{k}' has unknown or missing sub-key(s) {sorted(bad)}")
            if not all(isinstance(v, str) and v for v in data[k].values()):
                raise LabelError(f"label set '{name}': every value in '{k}' must be a non-empty string")
        for k in _STR_KEYS:
            if not isinstance(data[k], str) or not data[k]:
                raise LabelError(f"label set '{name}': '{k}' must be a non-empty string")
        if not isinstance(data["types"], list) or not data["types"] or \
                not all(isinstance(t, str) and re.fullmatch(r"[A-Z_]+", t) for t in data["types"]):
            raise LabelError(f"label set '{name}': 'types' must be a list of UPPER_CASE strings")
        if not re.fullmatch(r"[A-Z_]+", data["candidate_type"]):
            raise LabelError(f"label set '{name}': 'candidate_type' must be UPPER_CASE")

        self.name = name
        self.data = data
        self.fields: dict[str, str] = data["fields"]
        self.none: str = data["none"]
        self.statuses: dict[str, str] = data["statuses"]
        self.candidate_type: str = data["candidate_type"]
        self.types: set[str] = set(data["types"]) | {self.candidate_type}
        self.state_line: str = data["state_line"]
        self.next_step_line: str = data["next_step_line"]
        self.sections: dict[str, str] = data["sections"]
        self.card_state_heading: str = data["card_state_heading"]
        self.card_history_heading: str = data["card_history_heading"]
        self.history_footer: str = data["history_footer"]
        self.source_marker: str = data["source_marker"]
        self.events: dict[str, str] = data["events"]
        self.messages: dict[str, str] = data["messages"]

        self.open = self.statuses["open"]
        self.closed_statuses = (self.statuses["closed"], self.statuses["obsolete"])
        self.section_open = self.sections["open"]
        self.section_candidates = self.sections["candidates"]
        self.record_sections = {self.section_open, self.section_candidates}

        e = re.escape
        f = self.fields
        status_alt = "|".join(e(s) for s in self.statuses.values())
        self.header_re = re.compile(r"^### (T-\d{8}-\d{2}) · ([A-Z_]+) · (.+)$")
        self.fields_re = re.compile(
            rf"^- {e(f['status'])}: ({status_alt}) · {e(f['owner'])}: (.+?)"
            rf" · {e(f['topic'])}: (?:\[\[([^\]]+)\]\]|({e(self.none)}))"
            rf" · {e(f['linear'])}: ([A-Z][A-Z0-9]*-\d+|{e(self.none)})"
            rf" · {e(f['deadline'])}: (\d{{4}}-\d{{2}}-\d{{2}}|{e(self.none)})"
            rf" · {e(f['created'])}: (\d{{4}}-\d{{2}}-\d{{2}}) · {e(f['updated'])}: (\d{{4}}-\d{{2}}-\d{{2}})$"
        )
        self.state_re = re.compile(rf"^- {e(self.state_line)}: (.+)$")
        self.next_re = re.compile(rf"^- {e(self.next_step_line)}: (.+)$")
        self.source_re = re.compile(rf"\({e(self.source_marker)}: [^)]+\)")
        self.state_heading = f"## {self.card_state_heading}"
        self.history_heading_re = re.compile(rf"^## {e(self.card_history_heading)}\b")

    def msg(self, key: str, **kw: object) -> str:
        return self.messages[key].format(**kw)


def _merge(base: dict, overrides: dict, name: str) -> dict:
    out = copy.deepcopy(base)
    for k, v in overrides.items():
        if k in _DICT_KEYS and isinstance(v, dict) and k in out:
            unknown = set(v) - set(out[k])
            if unknown:
                raise LabelError(f"label set '{name}': '{k}' has unknown sub-key(s) {sorted(unknown)}")
            out[k].update(v)
        else:
            out[k] = v
    return out


def builtin_labels(name: str) -> Labels:
    if name not in BUILTIN_LABELS:
        raise LabelError(f"unknown label set '{name}' (built-in: {', '.join(sorted(BUILTIN_LABELS))})")
    return Labels(copy.deepcopy(BUILTIN_LABELS[name]), name)


def labels_from_file(path: Path) -> Labels:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise LabelError(f"cannot read label file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise LabelError(f"label file {path} is not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise LabelError(f"label file {path}: top level must be a JSON object")
    raw = {k: v for k, v in raw.items() if not k.startswith("_")}  # "_comment" etc. are ignored
    base = raw.pop("base", "en")
    if base not in BUILTIN_LABELS:
        raise LabelError(f"label file {path}: unknown base '{base}' (built-in: {', '.join(sorted(BUILTIN_LABELS))})")
    return Labels(_merge(BUILTIN_LABELS[base], raw, str(path)), f"{path} (base {base})")


def load_labels(spec: str) -> Labels:
    """`spec` is a built-in name (en, pl) or a path to a JSON label file."""
    if spec in BUILTIN_LABELS:
        return builtin_labels(spec)
    p = Path(spec)
    if p.suffix.lower() == ".json" or p.exists():
        if not p.exists():
            raise LabelError(f"label file not found: {spec}")
        return labels_from_file(p)
    raise LabelError(f"unknown label set '{spec}' (built-in: {', '.join(sorted(BUILTIN_LABELS))}, or a path to a .json file)")


def resolve_labels(cli: str | None, vault: Path) -> Labels:
    """Precedence: CLI --labels > <vault>/automations/housekeeping.labels.json > built-in 'en'."""
    if cli:
        return load_labels(cli)
    vault_file = Path(vault) / LABELS_FILE
    if vault_file.exists():
        return labels_from_file(vault_file)
    return builtin_labels("en")


EN = builtin_labels("en")
PL = builtin_labels("pl")


def _L(labels: Labels | None) -> Labels:
    return labels if labels is not None else EN


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@dataclass
class Violation:
    file: str
    line: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.file}:{self.line} [{self.code}] {self.message}"


@dataclass
class Record:
    id: str
    typ: str
    title: str
    status: str = ""
    owner: str = ""
    topic: str = ""
    linear: str = ""
    deadline: str = ""
    created: str = ""
    updated: str = ""
    state: str = ""
    next_step: str = ""
    section: str = ""
    start_line: int = 0
    raw: list[str] = field(default_factory=list)


def _iso(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def parse_tasks(text: str, filename: str = "TASKS.md", labels: Labels | None = None) -> tuple[list[Record], list[Violation]]:
    """Parse TASKS.md into records; report format violations with line numbers."""
    lb = _L(labels)
    records: list[Record] = []
    viol: list[Violation] = []
    section = ""
    cur: Record | None = None
    state = ""  # "fields" -> "state" -> "tail"

    def finish() -> None:
        nonlocal cur
        if cur is not None:
            if not cur.status:
                viol.append(Violation(filename, cur.start_line, "FIELDS_MISSING", lb.msg("FIELDS_MISSING", id=cur.id)))
            elif not cur.state:
                viol.append(Violation(filename, cur.start_line, "STAN_MISSING",
                                      lb.msg("STAN_MISSING", id=cur.id, state=lb.state_line)))
            records.append(cur)
        cur = None

    for n, line in enumerate(text.splitlines(), start=1):
        m = SECTION_RE.match(line)
        if m:
            finish()
            section = m.group(1).strip()
            continue
        if section not in lb.record_sections:
            continue
        if line.startswith("### "):
            finish()
            h = lb.header_re.match(line)
            if not h:
                viol.append(Violation(filename, n, "HEADER_FORMAT", lb.msg("HEADER_FORMAT", line=line[:80])))
                continue
            cur = Record(id=h.group(1), typ=h.group(2), title=h.group(3).strip(), section=section, start_line=n)
            if cur.typ not in lb.types:
                viol.append(Violation(filename, n, "TYPE_UNKNOWN", lb.msg("TYPE_UNKNOWN", id=cur.id, typ=cur.typ)))
            state = "fields"
            continue
        if cur is None or not line.strip():
            continue
        cur.raw.append(line)
        if state == "fields":
            f = lb.fields_re.match(line)
            if not f:
                viol.append(Violation(filename, n, "FIELDS_FORMAT", lb.msg("FIELDS_FORMAT", id=cur.id)))
                state = "state"
                continue
            cur.status, cur.owner = f.group(1), f.group(2)
            cur.topic = f.group(3) or lb.none
            cur.linear, cur.deadline, cur.created, cur.updated = f.group(5), f.group(6), f.group(7), f.group(8)
            state = "state"
            continue
        if state == "state":
            s = lb.state_re.match(line)
            if not s:
                viol.append(Violation(filename, n, "STAN_FORMAT", lb.msg("STAN_FORMAT", id=cur.id, state=lb.state_line)))
                state = "tail"
                continue
            cur.state = s.group(1).strip()
            if not lb.source_re.search(cur.state):
                viol.append(Violation(filename, n, "STAN_NO_SOURCE",
                                      lb.msg("STAN_NO_SOURCE", id=cur.id, state=lb.state_line, source=lb.source_marker)))
            state = "tail"
            continue
        nx = lb.next_re.match(line)
        if nx and not cur.next_step:
            cur.next_step = nx.group(1).strip()
            continue
        viol.append(Violation(filename, n, "EXTRA_LINE", lb.msg("EXTRA_LINE", id=cur.id, line=line[:60])))
    finish()
    return records, viol


def check_tasks(records: list[Record], today: date, filename: str = "TASKS.md", labels: Labels | None = None) -> list[Violation]:
    """Semantic checks on parsed records: uniqueness, status, candidate age, order."""
    lb = _L(labels)
    viol: list[Violation] = []
    seen: dict[str, int] = {}
    cand, cand_sec = lb.candidate_type, lb.section_candidates
    for r in records:
        if r.id in seen:
            viol.append(Violation(filename, r.start_line, "DUPLICATE_ID", lb.msg("DUPLICATE_ID", id=r.id, line=seen[r.id])))
        seen.setdefault(r.id, r.start_line)
        if r.status and r.status != lb.open:
            viol.append(Violation(filename, r.start_line, "STATUS_NOT_OPEN", lb.msg("STATUS_NOT_OPEN", id=r.id, status=r.status)))
        if r.typ == cand and r.section != cand_sec:
            viol.append(Violation(filename, r.start_line, "CANDIDATE_SECTION", lb.msg("CANDIDATE_OUTSIDE", id=r.id, candidate=cand)))
        if r.typ != cand and r.section == cand_sec:
            viol.append(Violation(filename, r.start_line, "CANDIDATE_SECTION", lb.msg("CANDIDATE_WRONG_TYPE", id=r.id, typ=r.typ)))
        if r.typ == cand and r.created and (today - _iso(r.created)).days > CANDIDATE_MAX_AGE_DAYS:
            viol.append(Violation(filename, r.start_line, "CANDIDATE_STALE",
                                  lb.msg("CANDIDATE_STALE", id=r.id, days=CANDIDATE_MAX_AGE_DAYS)))
        if r.created and r.id[2:10] != r.created.replace("-", ""):
            viol.append(Violation(filename, r.start_line, "ID_DATE_MISMATCH",
                                  lb.msg("ID_DATE_MISMATCH", id=r.id, created_label=lb.fields["created"], created=r.created)))
    for sec in (lb.section_open, lb.section_candidates):
        ids = [r.id for r in records if r.section == sec]
        if ids and ids != sorted(ids, reverse=True):
            first = next(r for r in records if r.section == sec)
            viol.append(Violation(filename, first.start_line, "ORDER", lb.msg("ORDER", section=sec)))
    return viol


# ---------------------------------------------------------------------------
# Cards, histories, task log
# ---------------------------------------------------------------------------

def quarter_of(d: date) -> str:
    return f"{d.year}-Q{(d.month - 1) // 3 + 1}"


def parse_front_matter(text: str) -> tuple[dict[str, object], int]:
    """Return (mapping, number_of_lines_consumed). Minimal YAML: `key: value` and `key: [a, b]`."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, 0
    fm: dict[str, object] = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return fm, i + 1
        if ":" in lines[i]:
            k, v = lines[i].split(":", 1)
            v = v.split("  #")[0].strip()
            if v.startswith("[") and v.endswith("]"):
                fm[k.strip()] = [x.strip() for x in v[1:-1].split(",") if x.strip()]
            else:
                fm[k.strip()] = v
    return {}, 0  # unterminated front matter -> treat as none


def check_card(text: str, filename: str, labels: Labels | None = None) -> list[Violation]:
    lb = _L(labels)
    viol: list[Violation] = []
    fm, _ = parse_front_matter(text)
    related = fm.get("related_topics", [])
    if isinstance(related, list) and any("-history" in r for r in related):
        viol.append(Violation(filename, 1, "RELATED_HISTORY", lb.msg("RELATED_HISTORY")))
    if lb.state_heading not in text.splitlines():
        viol.append(Violation(filename, 1, "CARD_NO_STATE", lb.msg("CARD_NO_STATE", heading=lb.state_heading)))
    for n, line in enumerate(text.splitlines(), start=1):
        if lb.history_heading_re.match(line):
            viol.append(Violation(filename, n, "CARD_HAS_HISTORY", lb.msg("CARD_HAS_HISTORY", history=lb.card_history_heading)))
    stem = Path(filename).stem
    if f"[[{stem}-history]]" not in text:
        viol.append(Violation(filename, 1, "CARD_NO_HISTORY_LINK",
                              lb.msg("CARD_NO_HISTORY_LINK", footer=lb.history_footer, stem=stem)))
    return viol


def _unknown_ids(n: int, filename: str, ids: list[str], known_ids: set[str], lb: Labels) -> list[Violation]:
    return [Violation(filename, n, "UNKNOWN_TASK_ID", lb.msg("UNKNOWN_TASK_ID", tid=t)) for t in ids if t not in known_ids]


def _check_dated_lines(text: str, filename: str, line_re: re.Pattern, order_code: str, fmt_code: str,
                       known_ids: set[str], key, lb: Labels) -> list[Violation]:
    viol: list[Violation] = []
    _, skip = parse_front_matter(text)
    prev = None
    for n, line in enumerate(text.splitlines(), start=1):
        if n <= skip or not line.strip() or line.startswith(("#", "_")):
            continue
        m = line_re.match(line)
        if not m:
            viol.append(Violation(filename, n, fmt_code, lb.msg("LINE_FORMAT", line=line[:60])))
            continue
        k = key(m)
        if prev is not None and k < prev:
            viol.append(Violation(filename, n, order_code, lb.msg("LINE_ORDER")))
        prev = k
        ids = TAG_RE.findall(line) + ([m.group(3)] if line_re is LOG_LINE_RE else [])
        viol += _unknown_ids(n, filename, ids, known_ids, lb)
    return viol


def _rollover_check(text: str, filename: str, today: date, lb: Labels) -> list[Violation]:
    fm, _ = parse_front_matter(text)
    if "period" not in fm:
        return [Violation(filename, 1, "FM_MISSING", lb.msg("FM_MISSING", key="period"))]
    if fm["period"] != quarter_of(today):
        return [Violation(filename, 1, "ROLLOVER_DUE", lb.msg("ROLLOVER_DUE", period=fm["period"], quarter=quarter_of(today)))]
    return []


def check_history(text: str, filename: str, known_ids: set[str], today: date, labels: Labels | None = None) -> list[Violation]:
    """Live `<card>-history.md`: strict format, order, rollover. Archived `<card>-history-YYYY-Qn.md`
    (frozen content, possibly migrated from an older format, e.g. `- 2026-05:` month-only entries): only
    front matter and task-ID tags are validated — the text is never touched, so it is never reformatted."""
    lb = _L(labels)
    viol: list[Violation] = []
    fm, _ = parse_front_matter(text)
    if "part_of" not in fm:
        viol.append(Violation(filename, 1, "FM_MISSING", lb.msg("FM_MISSING", key="part_of")))
    if QUARTER_RE.search(filename):  # archived quarter file
        if "period" not in fm:
            viol.append(Violation(filename, 1, "FM_MISSING", lb.msg("FM_MISSING", key="period")))
        for n, line in enumerate(text.splitlines(), start=1):
            viol += _unknown_ids(n, filename, TAG_RE.findall(line), known_ids, lb)
        return viol
    viol += _rollover_check(text, filename, today, lb)
    viol += _check_dated_lines(text, filename, HIST_LINE_RE, "HIST_ORDER", "HIST_LINE_FORMAT", known_ids,
                               lambda m: m.group(1), lb)
    return viol


def check_log(text: str, filename: str, known_ids: set[str], today: date, labels: Labels | None = None) -> list[Violation]:
    lb = _L(labels)
    viol = _rollover_check(text, filename, today, lb) if not re.search(r"TASKS-log-\d{4}-Q[1-4]\.md$", filename) else []
    viol += _check_dated_lines(text, filename, LOG_LINE_RE, "LOG_ORDER", "LOG_LINE_FORMAT", known_ids,
                               lambda m: (m.group(1), m.group(2)), lb)
    return viol


def iter_cards(vault: Path) -> list[Path]:
    return sorted(p for p in (vault / "topics").rglob("*.md") if "-history" not in p.name and p.name != "README.md")


def iter_histories(vault: Path) -> list[Path]:
    return sorted(p for p in (vault / "topics").rglob("*-history*.md"))


def collect_known_ids(vault: Path) -> set[str]:
    ids: set[str] = set()
    for p in [vault / "TASKS.md", *sorted((vault / "archive" / "tasks").glob("*.md"))]:
        if p.exists():
            ids |= set(TASK_ID_RE.findall(p.read_text(encoding="utf-8")))
    return ids


def run_check(vault: Path, today: date, labels: Labels | None = None) -> list[Violation]:
    lb = _L(labels)
    records, viol = parse_tasks((vault / "TASKS.md").read_text(encoding="utf-8"), labels=lb)
    viol += check_tasks(records, today, labels=lb)
    known = collect_known_ids(vault)
    log = vault / "TASKS-log.md"
    if log.exists():
        viol += check_log(log.read_text(encoding="utf-8"), "TASKS-log.md", known, today, labels=lb)
    else:
        viol.append(Violation("TASKS-log.md", 0, "LOG_MISSING", lb.msg("LOG_MISSING")))
    for p in iter_cards(vault):
        viol += check_card(p.read_text(encoding="utf-8"), str(p.relative_to(vault)), labels=lb)
    for p in iter_histories(vault):
        viol += check_history(p.read_text(encoding="utf-8"), str(p.relative_to(vault)), known, today, labels=lb)
    return viol


# ---------------------------------------------------------------------------
# --new-id and --apply
# ---------------------------------------------------------------------------

def new_id(vault: Path, today: date) -> str:
    prefix = f"T-{today:%Y%m%d}-"
    used: set[str] = set()
    for p in [vault / "TASKS.md", vault / "TASKS-log.md", *sorted((vault / "archive" / "tasks").glob("*.md"))]:
        if p.exists():
            used |= {i for i in TASK_ID_RE.findall(p.read_text(encoding="utf-8")) if i.startswith(prefix)}
    n = 1
    while f"{prefix}{n:02d}" in used:
        n += 1
    return f"{prefix}{n:02d}"


def log_line(day: date, hhmm: str, task_id: str, event: str, text: str) -> str:
    return f"- {day:%Y-%m-%d} {hhmm} · {task_id} · {event} · {text}"


def record_span(lines: list[str], rec: Record) -> tuple[int, int]:
    start = rec.start_line - 1
    end = start + 1
    while end < len(lines) and not lines[end].startswith(("### ", "## ")):
        end += 1
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    return start, end


def _write_front_matter(fm: dict[str, object]) -> str:
    out = ["---"]
    for k, v in fm.items():
        out.append(f"{k}: [{', '.join(v)}]" if isinstance(v, list) else f"{k}: {v}")
    out.append("---")
    return "\n".join(out) + "\n"


def _rollover_file(live: Path, archive_to: Path, today: date, ops: list[str], lb: Labels) -> None:
    text = live.read_text(encoding="utf-8")
    fm, _ = parse_front_matter(text)
    if not fm or fm.get("period") == quarter_of(today):
        return
    if archive_to.exists():
        ops.append(lb.msg("op_rollover_skipped", live=live.name, archive=archive_to.name))
        return
    archive_to.parent.mkdir(parents=True, exist_ok=True)
    live.rename(archive_to)
    prev = list(fm.get("previous", [])) if isinstance(fm.get("previous"), list) else []
    ref = archive_to.stem if live.parent == archive_to.parent else f"archive/tasks/{archive_to.stem}"
    new_fm = {k: v for k, v in fm.items() if k not in ("period", "previous")}
    new_fm["period"] = quarter_of(today)
    new_fm["previous"] = prev + [ref]
    live.write_text(_write_front_matter(new_fm), encoding="utf-8")
    ops.append(lb.msg("op_rollover", live=live.name, old=fm["period"], archive=archive_to.name, new=quarter_of(today)))


def _append(path: Path, text: str, header: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(header, encoding="utf-8")
    with path.open("a", encoding="utf-8") as f:
        if path.stat().st_size and not path.read_text(encoding="utf-8").endswith("\n"):
            f.write("\n")
        f.write(text if text.endswith("\n") else text + "\n")


def apply(vault: Path, today: date, labels: Labels | None = None) -> list[str]:
    lb = _L(labels)
    ops: list[str] = []
    q = quarter_of(today)
    # 1. rollover of the task log
    log = vault / "TASKS-log.md"
    if log.exists():
        fm, _ = parse_front_matter(log.read_text(encoding="utf-8"))
        if fm.get("period") and fm["period"] != q:
            _rollover_file(log, vault / "archive" / "tasks" / f"TASKS-log-{fm['period']}.md", today, ops, lb)
    # 2. rollover of live topic histories
    for h in iter_histories(vault):
        if QUARTER_RE.search(h.name):
            continue
        fm, _ = parse_front_matter(h.read_text(encoding="utf-8"))
        if fm.get("period") and fm["period"] != q:
            _rollover_file(h, h.with_name(h.name[:-3] + f"-{fm['period']}.md"), today, ops, lb)
    # 3. expire stale candidates, 4. archive closed records
    tasks_path = vault / "TASKS.md"
    lines = tasks_path.read_text(encoding="utf-8").splitlines()
    records, _ = parse_tasks("\n".join(lines), labels=lb)
    status_label = lb.fields["status"]
    to_move: list[tuple[int, int, list[str]]] = []
    for r in records:
        s, e = record_span(lines, r)
        block = lines[s:e]
        if r.typ == lb.candidate_type and r.status == lb.open and (today - _iso(r.created)).days > CANDIDATE_MAX_AGE_DAYS:
            block[1] = block[1].replace(f"- {status_label}: {lb.open}", f"- {status_label}: {lb.statuses['obsolete']}").replace(
                f"{lb.fields['updated']}: {r.updated}", f"{lb.fields['updated']}: {today:%Y-%m-%d}")
            event = f"{lb.events['obsolete']}: {lb.msg('expire_reason', days=CANDIDATE_MAX_AGE_DAYS)}"
            _append(log, log_line(today, "00:00", r.id, event, lb.msg("expire_log_text", created=r.created)),
                    header=_write_front_matter({"period": q, "previous": []}))
            ops.append(lb.msg("op_expired", id=r.id))
            to_move.append((s, e, block))
        elif r.status in lb.closed_statuses:
            ops.append(lb.msg("op_archived", id=r.id, status=r.status))
            to_move.append((s, e, block))
    if to_move:
        archive = vault / "archive" / "tasks" / f"TASKS-{q}.md"
        header = lb.msg("archive_header", quarter=q)
        for s, e, block in to_move:
            _append(archive, "\n".join(block) + "\n\n", header=header)
        for s, e, _b in sorted(to_move, reverse=True):
            del lines[s:e]
            while s < len(lines) and s > 0 and not lines[s].strip() and not lines[s - 1].strip():
                del lines[s]
        tasks_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ops


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="validate the vault (read-only); exit 1 on violations")
    g.add_argument("--apply", action="store_true", help="quarterly rollover, archive closed records, expire candidates")
    g.add_argument("--new-id", action="store_true", help="print the next free T-<today>-nn")
    p.add_argument("--vault", type=Path, default=Path(__file__).resolve().parent.parent)
    p.add_argument("--today", type=_iso, default=date.today())
    p.add_argument("--labels", default=None, help="en | pl | path to a JSON label file (default: vault file, else en)")
    a = p.parse_args(argv)
    try:
        lb = resolve_labels(a.labels, a.vault)
    except LabelError as exc:
        print(f"housekeeping: {exc}", file=sys.stderr)
        return 2
    if a.check:
        viol = run_check(a.vault, a.today, labels=lb)
        for v in viol:
            print(v)
        print(lb.msg("summary_check", n=len(viol)))
        return 1 if viol else 0
    if a.new_id:
        print(new_id(a.vault, a.today))
        return 0
    ops = apply(a.vault, a.today, labels=lb)
    for o in ops:
        print(o)
    print(lb.msg("summary_apply", n=len(ops)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Work OS Bridge — Slack -> claude -p (read-only) with optional local-LLM brain (LM Studio).

Scope: READ-ONLY access to the vault. The script never writes vault files and never
messages anyone except replying in the thread where the owner asked.

Architecture:
  Slack (Socket Mode, private bot) -> handler -> brain:
    - BRAIN=claude (default): `claude -p` restricted to read-only tools
    - BRAIN=local : grep-based retrieval + LM Studio (OpenAI-compatible API)
  Message prefix "l:" forces the local brain, "c:" forces Claude.

Config: .env next to this script (see .env.example).
"""

import os
import re
import subprocess
import logging
from pathlib import Path

import requests
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]          # xoxb-...
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]          # xapp-... (Socket Mode)
ALLOWED_USER_ID = os.environ["ALLOWED_USER_ID"]          # the owner's Slack member ID (U...)
VAULT_PATH = Path(os.environ["VAULT_PATH"])
USER_NAME = os.environ.get("USER_NAME", "the owner")
LANGUAGE = os.environ.get("LANGUAGE", "English")
BRAIN_DEFAULT = os.environ.get("BRAIN", "claude")        # claude | local
CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "claude")      # use full path under launchd!
CLAUDE_TIMEOUT = int(os.environ.get("CLAUDE_TIMEOUT", "180"))
LOCAL_URL = os.environ.get("LOCAL_URL", "http://localhost:1234/v1/chat/completions")
LOCAL_MODEL = os.environ.get("LOCAL_MODEL", "")
LOCAL_TIMEOUT = int(os.environ.get("LOCAL_TIMEOUT", "120"))

logging.basicConfig(
    filename=str(BASE_DIR / "bridge.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("work-os-bridge")

app = App(token=SLACK_BOT_TOKEN)

SYSTEM_RULES = (
    f"You are a read-only assistant for {USER_NAME}. Answer in {LANGUAGE}, concisely "
    "(Slack limit ~3900 chars), keep source quotes in their original language. "
    "The source of truth is the Work OS vault (README.md and AGENTS.md describe the "
    "structure; topics/ recursively, TASKS.md, decisions/, knowledge/, briefs/). "
    "Cite sources from the cards when stating facts. You write, modify and send "
    "NOTHING — you only answer. If something is not in the vault, say so (don't guess). "
    "FORMATTING: the reply goes to Slack — short paragraphs separated by blank lines, "
    "bullets on separate lines, no # headers, no tables; bold sparingly."
)


def to_mrkdwn(text: str) -> str:
    """Markdown -> Slack mrkdwn."""
    text = re.sub(r"^#{1,6}\s*(.+)$", r"*\1*", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"*\1*", text)
    text = re.sub(r"^(\s*)[-*]\s+", r"\1• ", text, flags=re.MULTILINE)
    text = re.sub(r"\[\[(.+?)\]\]", r"\1", text)
    text = re.sub(r"\[(.+?)\]\((https?://\S+?)\)", r"<\2|\1>", text)
    return text


# ---------- brain 1: claude -p (read-only via --allowedTools) ----------
def ask_claude(question: str) -> str:
    cmd = [
        CLAUDE_BIN, "-p",
        f"{SYSTEM_RULES}\n\nQuestion from {USER_NAME}: {question}",
        "--allowedTools", "Read", "Glob", "Grep",
    ]
    try:
        out = subprocess.run(
            cmd, cwd=str(VAULT_PATH), capture_output=True, text=True,
            timeout=CLAUDE_TIMEOUT,
        )
        if out.returncode != 0:
            log.error("claude rc=%s stderr=%s", out.returncode, out.stderr[-500:])
            return f"⚠️ claude -p failed (rc={out.returncode}). See bridge.log."
        return out.stdout.strip() or "⚠️ Empty answer from claude -p."
    except FileNotFoundError:
        return "⚠️ `claude` binary not found — set CLAUDE_BIN in .env to the full path (`which claude`)."
    except subprocess.TimeoutExpired:
        return "⚠️ claude -p timed out. Try a simpler question or the l: prefix (local brain)."


# ---------- brain 2: local LLM via LM Studio (retrieval + completion) ----------
def _retrieve(question: str, top_n: int = 4, max_chars: int = 6000):
    tokens = {t for t in re.findall(r"[\w\-]{4,}", question.lower())}
    scored = []
    for p in VAULT_PATH.rglob("*.md"):
        if "archive" in p.parts or p.name.startswith("."):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        low = text.lower()
        score = sum(low.count(t) for t in tokens)
        if p.name in ("TASKS.md", "README.md"):
            score += 1
        if score > 0:
            scored.append((score, p, text[:max_chars]))
    scored.sort(key=lambda x: -x[0])
    return scored[:top_n]


def ask_local(question: str) -> str:
    docs = _retrieve(question)
    if not docs:
        return "Nothing matching found in the vault (the local brain uses simple keyword search — try other words or the c: prefix for Claude)."
    context = "\n\n".join(f"=== {p.relative_to(VAULT_PATH)} ===\n{t}" for _, p, t in docs)
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_RULES},
            {"role": "user", "content": f"VAULT CONTEXT:\n{context}\n\nQUESTION: {question}"},
        ],
        "temperature": 0.2,
        "max_tokens": 1200,
    }
    if LOCAL_MODEL:
        payload["model"] = LOCAL_MODEL
    try:
        r = requests.post(LOCAL_URL, json=payload, timeout=LOCAL_TIMEOUT)
        r.raise_for_status()
        ans = r.json()["choices"][0]["message"]["content"].strip()
        files = ", ".join(str(p.relative_to(VAULT_PATH)) for _, p, _ in docs)
        return f"{ans}\n\n_📁 local brain, based on: {files}_"
    except requests.exceptions.ConnectionError:
        return "⚠️ LM Studio not responding (start the local server: LM Studio → Developer → Start Server). You can use the c: prefix (Claude)."
    except Exception as e:  # noqa: BLE001
        log.exception("local brain error")
        return f"⚠️ Local brain error: {e}"


# ---------- Slack handler ----------
@app.event("message")
def handle_message(event, say, client):
    if event.get("channel_type") != "im":
        return  # DMs with the bot only
    if event.get("bot_id") or event.get("user") != ALLOWED_USER_ID:
        return  # the owner only

    text = (event.get("text") or "").strip()
    if not text:
        return

    brain = BRAIN_DEFAULT
    if text.lower().startswith("l:"):
        brain, text = "local", text[2:].strip()
    elif text.lower().startswith("c:"):
        brain, text = "claude", text[2:].strip()

    log.info("Q (%s): %s", brain, text[:200])
    try:
        client.reactions_add(channel=event["channel"], timestamp=event["ts"], name="eyes")
    except Exception:  # noqa: BLE001
        pass

    answer = ask_local(text) if brain == "local" else ask_claude(text)
    answer = to_mrkdwn(answer)

    for i in range(0, len(answer), 3900):
        say(text=answer[i : i + 3900], thread_ts=event["ts"])
    log.info("A (%s): %s chars", brain, len(answer))


if __name__ == "__main__":
    log.info("Work OS Bridge start; vault=%s brain=%s", VAULT_PATH, BRAIN_DEFAULT)
    SocketModeHandler(app, SLACK_APP_TOKEN).start()

# Work OS Bridge — phone access via Slack
_Slack DM (your private bot) → script on your machine → claude -p (read-only) or a local LLM. One-time setup ~20 min._

## What you get

Message your bot from your phone — "what's happening with X?", "who is waiting on me?", "summarize topic Y" — and get an answer built from your vault in seconds. Scope: **read-only**; the bridge writes nothing and messages no one but you.

Brains: default `claude -p` (Claude Code CLI; read-only enforced via --allowedTools Read/Glob/Grep). Prefix `l:` → local LLM via LM Studio (offline, free, simpler answers). Prefix `c:` → force Claude.

## Setup

### Step 1 — Slack app from the manifest (~5 min; may need workspace-admin approval)
1. https://api.slack.com/apps → **Create New App** → **From a manifest** → pick your workspace → paste the contents of `slack-app-manifest.yml` → Create.
   ⚠️ Each user creates their OWN app instance from this manifest — see the note in the manifest header for why a single shared app would mix up users' messages (Socket Mode round-robin).
2. **Basic Information → App-Level Tokens** → Generate (scope `connections:write`) → save the `xapp-...` token.
3. **OAuth & Permissions** → **Install to Workspace** → save the `xoxb-...` Bot Token.
4. Open a DM with the bot (Apps → Work OS Bridge). The Messages tab is already enabled by the manifest.

### Step 2 — environment (~5 min)
Homebrew Python blocks global pip (PEP 668) — use a venv:
```bash
cd /path/to/vault/automations/bridge
python3 -m venv .venv
.venv/bin/pip install slack-bolt python-dotenv requests
cp .env.example .env    # fill: both tokens, your member ID, VAULT_PATH, USER_NAME, LANGUAGE
which claude            # put the FULL path into CLAUDE_BIN (mandatory for autostart)
```

### Step 3 — manual test
```bash
.venv/bin/python slack_bridge.py
# message your bot: "what are my tasks today?"
```

### Step 4 — autostart (macOS launchd)
Edit `com.workos.bridge.plist`: replace `/ABSOLUTE/PATH/TO/bridge`; if `claude` comes from nvm, prepend its bin dir to PATH inside the plist. Then:
```bash
cp com.workos.bridge.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.workos.bridge.plist
# stop: launchctl unload ~/Library/LaunchAgents/com.workos.bridge.plist
```

### (Optional) local brain via LM Studio
LM Studio → load a model → **Developer → Start Server** (port 1234). The `l:` prefix now works; set `BRAIN=local` in .env to save Claude usage by default.

## Security & limits

- The bot answers ONLY DMs from your member ID (ALLOWED_USER_ID); everyone else is ignored.
- Read-only is enforced technically (`--allowedTools Read Glob Grep`); the local brain has no tools at all.
- `.env` holds secrets — never commit it, never paste tokens into chats; if a token leaks, regenerate it immediately.
- Your machine must be on and awake.
- Each `c:` question consumes Claude Code usage; `l:` is free.
- Write commands are deliberately unsupported — extend only after the read-only bridge has earned trust.

## Troubleshooting (field-tested)

| Symptom | Fix |
|---|---|
| "Sending messages to this app has been turned off" | App Home → Messages Tab + allow sending (the manifest sets this; re-install the app) |
| `invalid_auth` at startup | wrong/placeholder tokens in .env — refill both; check you didn't overwrite .env with the example |
| "claude binary not found" under launchd | set CLAUDE_BIN to the full path from `which claude` |
| `env: node: No such file` under launchd | add your nvm `…/bin` dir to PATH in the plist |
| pip: externally-managed-environment | use the venv (step 2), don't `--break-system-packages` |
| No reply, no logs | the script isn't running — check `bridge.err.log`, `launchctl list \| grep workos` |

Logs: `bridge.log` (app), `bridge.out.log` / `bridge.err.log` (launchd).

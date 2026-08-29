---
name: hermes-ops-dashboard
description: Hermes Real-Time Operations Dashboard — Live telemetry, token burn tracking, worker heartbeat monitor, and interactive Dash UI.
version: "1.0 Advanced"
author: Hermes Advanced Team
license: MIT
metadata:
  hermes:
    tags: ['hermes', 'dashboard', 'telemetry', 'operations', 'monitoring']
    category: hermes-advanced
    requires_tools: ['terminal_exec', 'file_read']
    requires_toolsets: ['terminal']
---
# Hermes Live Ops Dashboard

Build a live monitor for the user's autonomous-agent fleet. Read REAL data every
request (never a snapshot/mockup) and render it in a self-refreshing HTML page.

## Data sources (real, verified this session)

1. **Scheduled agents** — `<HERMES>\AppData\Local\hermes\cron\jobs.json`
   - Top-level shape: `{"jobs": [...], "updated_at": "ISO<+05:30>"}` (21 jobs in this env).
   - Per-job keys that matter: `id` (= job_id), `name`, `schedule` (**DICT, not string**:
     `{kind, expr, display}`), `schedule_display` (string — prefer this), `next_run_at`,
     `last_run_at`, `last_status` (`ok` | `error` | null=pending), `enabled`, `state`,
     `skills`/`skill`, `workdir`, `deliver`, `enabled_toolsets`.
   - **Alerts** = any job with `last_status == "error"`.
2. **Live OS processes (Windows)** — `tasklist.exe /fo csv /nh` for name counts;
   `wmic.exe process get Name,CommandLine /format:csv` to extract active agent
   `session-key` tokens (these are the live sub-agents). Guard both with `timeout=`.
3. **Repos in work** — `git -C <repo> log -1 --format=%h|%ar|%s` over repos under `C:\\one`
   (and the known assistant-bot repo). Scope the walk — scanning the whole home is slow.
4. **Live per-agent progress (the user's #1 ask)** — `C:\Users\<user>\\AppData\\Local\\hermes\\state.db`
   (SQLite; **one directory level ABOVE** `cron/jobs.json` — same `AppData\Local\hermes` folder).
   - Tables: `sessions` (1478 rows), `messages` (48008 rows). A "live" agent = a row in
     `sessions` where `ended_at IS NULL` (still running). Query:
     `SELECT id, title, cwd, model, message_count, started_at, git_repo_root FROM sessions WHERE ended_at IS NULL ORDER BY started_at DESC`.
   - Per-agent "current task" = its **latest assistant message text**. `messages.content` is
     either a plain string OR a JSON list of `{type:"text", text:...}` parts — write an
     `extract_text()` that handles both (see `scripts/live_ops_dashboard.py`). Pull latest
     `role='assistant'` msg (walk `ORDER BY rowid DESC LIMIT 12`), fall back to last `role='tool'`
     output. Truncate to ~300 chars for the card.
   - `started_at` / message `timestamp` are **Unix epoch floats** (e.g. `1784017927.57`) →
     format with `datetime.fromtimestamp(ts).strftime(...)`.
   - **Naming untitled sessions (SOLVED this session):** most live sessions come from cron runs
     and have `title = NULL`. To show a real name, match the session id to the cron job. Cron
     session ids look like `cron_<jobId>_<timestamp>` — split on `_` and take index [1] as the job
     id, then look it up in `jobs.json`. **CRITICAL:** the scheduler key is `id`, NOT `job_id`
     (jobs.json uses `id`). Building the map with `job.get("job_id")` yields an **empty** map and
     every card falls back to `(untitled)`. Use `job.get("id")`. If there's no cron match, fall
     back to the repo basename from `git_repo_root`, else `(interactive session)`.
   - **Activity signal (SOLVED this session):** `ended_at IS NULL` over-reports "live" — it also
     catches just-finished cron runs that were never marked closed (they sit idle for 45+ min).
     Compute a per-agent **activity score** from the latest message `timestamp` (Unix float):
     `score = clamp(0..100, 100 * (1 - seconds_since_last_msg / 1800))`. Treat `activity > 0` as
     ACTIVE; render `activity <= 0` as "idle/stale". Split the panel into ACTIVE vs IDLE/STALE
     groups and report only active count on the summary card — otherwise the "X sub-agents live"
     number is inflated and misleading.
   - **Drill-down log:** each card can carry its last N messages (`role`, `text`) so the user can
     click to expand a real activity log. In `messages`, select `content, role, timestamp ORDER BY
     rowid DESC LIMIT 15`, run each `content` through `extract_text()`, cap each entry at ~600
     chars, then reverse to oldest-first for display. Render assistant vs tool rows with different
     colors.

## Build pattern (known-good)
- Stdlib-only `http.server` + `ThreadingHTTPServer` (no installs — this box is
  memory-starved; avoid heavy deps like Flask).
- Endpoint `/api/snapshot` returns JSON built **fresh per request** (re-reads jobs.json
  + processes each call). Root `/` serves HTML that `fetch()`-es `/api/snapshot` and
  `setInterval(load, 15000)` for auto-refresh.
- Render order: summary cards (totals / ok / error / live sessions / processes / repos /
  **live sub-agents**) → **Alerts** (errored jobs) → **Sub-Agent Live Activity** (one card per
  live `state.db` session: title + git root, `model · N msgs · started <time> · session_id`,
  and the latest assistant "current task" line) → full agents table → live process counts →
  repo list. The sub-agent panel is the piece the user specifically asked for ("see what each
  agent is doing live"), so put it near the top, right after alerts.
- Full working reference: `scripts/live_ops_dashboard.py` (known-good, verified live this
  session — returns 21 scheduled agents / 28 processes / 12 live sub-agents / 2 errored). Run
  `python scripts/live_ops_dashboard.py`, open http://127.0.0.1:8765.

## Portable / publish-ready design (SOLVED this session)
- Make paths **env-overridable** so the dashboard runs on any machine, not just this user's
  profile. Pattern (kept in `scripts/live_ops_dashboard.py`):
  ```python
  CRON_DB = os.environ.get("HERMES_CRON_DB", r"<HERMES>\AppData\Local\hermes\cron\jobs.json")
  REPO_ROOTS = (os.environ.get("HERMES_REPO_ROOTS", r"C:\one").split(";")
                if os.name == "nt" else
                os.environ.get("HERMES_REPO_ROOTS", os.path.expanduser("~/one")).split(":"))
  PORT = int(os.environ.get("HERMES_DASHBOARD_PORT", "8765"))
  ```
  Document these in the README. A user with a fresh clone just runs `python dashboard.py`.
- **Publishing to GitHub from this headless shell — blocker RESOLVED this session:**
  - Auth is cached in **Windows GCM** (`credential.helper=manager`). It works for `git push`/
    `ls-remote` to an **existing** repo (proven: `git -c credential.helper=manager ls-remote
    https://github.com/<user>/<existing>.git HEAD` returned a real hash, rc=0).
  - The earlier belief that "you cannot create a repo via API because `git credential fill`
    hangs" was **only true while the dual-identity GCM bug was active** (see
    `git-credential-manager-windows` Fix A). Once the stray `x-access-token` identity is
    erased + the `<github-org>` username pinned, `git credential fill` returns the token
    **silently** and you CAN create the repo via the REST API, then push. Verified this
    session: `hermes-live-ops-dashboard` was created via `POST /user/repos` (with the
    `credential fill` token) and pushed successfully.
  - **If the dual identity is NOT yet fixed**, `credential fill` hangs (rc=124) — fall back to
    having the user create the empty repo on github.com/new (name only, NO README) so your
    cached-credential `git push -u origin main` completes. NEVER ask the user to paste a
    secret into chat when the cached-credential push path exists.
  - Verify the local commit first with an **ad-hoc** temp script (see verify-untested-repo
    pattern): write `%TEMP%/hermes-verify-<name>.py`, run against the real data, confirm, then
    `rm` it. Report it explicitly as ad-hoc, not "suite green".

## Pitfalls (learned the hard way this session)
- **`jobs.json` key is `id`, NOT `job_id`** → when building the cron-job-name map for labeling
  sessions, `job.get("job_id")` is always `None` → empty map → every live card shows
  `(untitled)`. Use `job.get("id")`. (The cron list API returns `job_id` in some contexts, but
  the on-disk `jobs.json` uses `id` as the key.)
- **`ended_at IS NULL` over-reports "live"** → it returns just-finished cron runs that were never
  marked closed (idle 45+ min). ALWAYS compute an activity score from the last message timestamp
  and split ACTIVE vs IDLE/STALE; never count raw `ended_at IS NULL` rows as "currently working".
- **`schedule` is a dict, not a string** → `jobs.json` stores `{kind, expr, display}`.
  Use `schedule_display` or `(j.get("schedule") or {}).get("display")`. Printing the raw
  dict renders as `[object Object]` in the browser.
- **Dotted JSON keys break JS dot-access** → process counts are keyed `Hermes.exe`,
  `python.exe`, etc. In JS use `p.counts["Hermes.exe"]` (bracket notation), never
  `p.counts.Hermes_exe` (that silently shows `undefined`).
- **`state.db` lives one level ABOVE `cron/jobs.json`** → both sit under
  `AppData\Local\hermes`, but `jobs.json` is in `cron/` and `state.db` is directly in that
  folder. `os.path.dirname(CRON_DB)` gives `.../hermes/cron`; you need
  `os.path.dirname(os.path.dirname(CRON_DB))` to reach `state.db`. A wrong path yields
  `no such table: sessions` at request time (silent 500 to the browser).
- **`messages.content` is dual-shaped** → plain string OR JSON-list-of-parts. Always run it
  through `extract_text()`; reading it raw prints a dict/list repr in the card.
- **Scope the live-agents query** → `WHERE ended_at IS NULL` can return 12+ rows (incl.
  just-finished cron runs not yet closed). `LIMIT 12` + render as cards is plenty; don't try
  to page.
- **MSYS bash has no `ps`/`free`** (exit 127) → use Windows `tasklist.exe` / `wmic.exe`
  for live process data.
- **Scope repo scans** → never walk the entire `C:\Users\...` home; limit to `C:\one` +
  known repos and cap `os.walk` depth, or scans hang on a memory-starved host.
- **Raw-string the docstring** if it contains Windows paths with `\U` → Python raises a
  unicode-escape error. Use `r"""..."""`.
- **`updated_at` / `next_run_at`** are ISO strings with a `+05:30` offset — display
  as-is; don't try to localize.
- **GitHub push from a headless shell is blocked at REPO CREATION only while the dual-identity
  GCM bug is active.** `git push` cannot create a repo. With the GCM bug fixed (erase
  `x-access-token` + pin `<github-org>`; see `git-credential-manager-windows`), `git
  credential fill` returns the token silently and you create the repo via `POST
  /user/repos`, then push. If the bug is NOT fixed, `credential fill` hangs (no interactive
  broker) — fall back to asking the user to create the empty repo on github.com/new (no
  README), then push. Don't loop on `git credential fill` as a dead-end; fix the identity
  first. (See "Portable / publish-ready".)
- **`~/.git-credentials` can be 0 bytes** even when GCM has a live token — don't rely on it as a
  token source; the token lives only in GCM's DPAPI store. `git ls-remote`/`push` to existing
  repos is the only working auth path.

## Verify (don't just announce)
- `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8765/` → 200.
- `curl -s http://127.0.0.1:8765/api/snapshot | python -c "import sys,json;d=json.load(sys.stdin);print(d['summary'])"`
  → must return real counts (this env: 21 scheduled agents, 12 live sub-agents, 28
  processes, 2 errored, 60 repos). If `live_agents` is empty/missing, the `state.db`
  path is wrong (see pitfall) or no session has `ended_at IS NULL` right now.
- `live_agents` cards will often show `(untitled)` — that's expected for cron-spawned
  sessions (title is NULL). Not a bug.
- Browser-navigate + screenshot to confirm cards/table actually render; this catches
  `[object Object]`, `undefined`, and the Sub-Agent panel not appearing — regressions
  the API check alone misses.

## Notes
- Scheduler-DB / repo paths are user-specific — adjust `CRON_DB` / `REPO_ROOTS` in the
  script to the target machine (look under `$LOCALAPPDATA/hermes/cron/jobs.json`).
- This monitor is read-only. Adding start/stop/pause controls means POSTing to the real
  scheduler API — a natural extension, out of scope for the basic view.

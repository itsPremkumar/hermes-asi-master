---
name: hermes-fleet-cicd-verification
description: Hermes Fleet CI/CD Verification — Automated verification gates, regression testing, linting, and release build gating.
version: "1.0 Advanced"
author: Hermes Advanced Team
license: MIT
metadata:
  hermes:
    tags: ['hermes', 'cicd', 'verification', 'testing', 'quality-gate']
    category: hermes-advanced
    requires_tools: ['terminal_exec', 'file_read']
    requires_toolsets: ['terminal']
---
# Fleet CI/CD + Cross-Verification System

A reusable pattern for turning "verify all my projects" into a *real, running*
system: a multi-angle verification engine + a daily closed loop that
auto-remediates safe gaps, deploys, pulls the **live** CI status as an
independent review, and writes a backlog. Never trust a single check — every
repo is only "credibly OK" when several independent angles agree.

## When to use
- User owns many repos (e.g. under `C:/one` or `~/code`) and wants uniform CI/CD.
- "build a complete CI/CD pipeline for all the project" / "verify everything".
- "self-improving post-deploy review" / "get the review from the live site".
- "cross-verify before anything is called done".

## The 8-angle cross-verification model
Each repo is checked from 8 INDEPENDENT angles; a hard gate FAILs if any
*must-pass* angle fails (structure, compile, security, selftest). The angles:
1. **structure** — required files present for the repo's detected type.
2. **frontmatter** — package.json / pyproject / setup.py / SKILL.md validity.
3. **compile** — `tsc --noEmit`+`node -c` (node), `compileall` (python).
4. **selftest** — actually RUNS `npm test` / `pytest` and checks exit code.
5. **security** — FIRST-PARTY secret scan (vendor/build pruned), `.env` gitignore
   check, token-in-remote-url, `npm audit`.
6. **docs** — README substance (install + usage sections present).
7. **deploy** — Dockerfile / platform config + CI presence for deployable repos.
8. **live** — HTTP status of `live_url`, OR live CI status via the API.

## Cross-verification (the "closed loop" discipline)
Three independent comparisons must agree before a repo is "credibly OK":
- local engine gate  vs.  its own self-test exit (no internal disagreement)
- local gate  vs.  **live** GitHub Actions conclusion (no local/live disagreement)
- deploy path (Dockerfile/CI)  vs.  compile result (no path/build disagreement)
Any disagreement → written to `backlog.json`, flagged for human/agent action.

## Build steps
1. Scan every repo: language, package.json, existing CI, tests, Dockerfile, live URL.
2. Write `verify.py` (8-angle engine) → `scripts/verify_engine.py` here is a proven base.
3. Write `repos.json` registry (remote, deployable flag, live_url, deploy_cmd).
4. Write `loop.py` orchestrator (verify → auto-remediate safe gaps → commit →
   deploy → live-check → daily report → backlog).
5. Write `inject_ci.py` to copy `ci_template.yml` (+ a `verify_ci.py` shim) into
   every repo missing `.github/workflows` (idempotent; never overwrite existing).
6. Wire a daily cron (see Pitfalls #3) to run `loop.py`.
7. Run it for REAL; read the JSON report; fix the engine before trusting output.

## Closed loop per day
scan → verify → auto-remediate (LICENSE/CI/README only — never guess secrets) →
commit+push → (deploy if deployable) → fetch live GitHub Actions status →
cross-verify → emit `daily_<date>.md` + `backlog.json`.

## Pitfalls (learned the hard way — do NOT re-discover)
### P1. Windows/MSYS path mismatch
The `write_file` tool maps `/c/one` → `C:\c\one`, but the bash terminal (MSYS)
maps `/c/one` → `C:\one`. Files written by the file tool land in `C:\c\one`
while terminal commands operate on `C:\one`. Symptom: `os.listdir('/c/one')`
raises `FileNotFoundError` in Python.
**Fix:** After writing, move (`mv /c<workspace-root>/... <workspace-root>/...`) OR write using
**native Windows paths** `<workspace-root>/...` everywhere in Python. Shell commands use
MSYS `/c/one`. Mixing them is the trap. See `references/windows-dev-pitfalls.md`.

### P2. os.walk backslash pruning bug (secret scanners)
On Windows, `os.walk` returns BACKSLASH `root` (e.g. `<workspace-root>\repo\node_modules`).
A POSIX-style skip `if "/node_modules" in root` NEVER matches → the security
scanner walks ALL vendor/build code → false-positive "secret leaks" in every
repo → 11/11 repos falsely FAIL security. The same applies to `.next`, `dist`,
`build`, etc.
**Fix:** prune in-place at the top of the loop, platform-independent:
`dirs[:] = [d for d in dirs if d not in SKIP_DIRS]` where SKIP_DIRS includes
`node_modules, dist, build, .next, .open-next, .standalone, .venv, __pycache__`.
Also exclude docs/markdown from secret scanning (they hold example keys).

### P3. Cron `script` path rule
`cronjob` `script` MUST be a bare filename under `~/.hermes/scripts/`
(e.g. `devops_loop_daily.sh`). An absolute or home-relative path errors:
"Script path must be relative to ~/.hermes/scripts/". Create the launcher there
and reference it by name.

### P4. execute_code blocked in cron mode
`execute_code` is refused ("runs arbitrary local Python… Cron jobs run without a
user present to approve it"). Use a foreground `terminal` Python snippet instead.

### P5. Heavy repos hang the foreground cap
`npm test` / `tsc --noEmit` / `compileall` across many repos exceeds the
~60s foreground limit. Run the engine with `terminal(background=true,
notify_on_complete=true)` and `poll`/`wait`. Bound every subprocess with a
timeout so the loop can never hang.

## Verification checklist (how you know it's real)
- [ ] Engine ran and produced `latest_report.json` (not a description of one).
- [ ] Security angle shows `real_problems=0` for repos with no first-party secrets
      (proves the P2 fix worked — vendor code is NOT being scanned).
- [ ] First-party secrets (in `*.py`/`*.ts`/`.env`/service-account.json) ARE found.
- [ ] CI files actually exist in each repo's `.github/workflows/`.
- [ ] Daily cron job created and `next_run_at` is set.
- [ ] Daily report + backlog written.

## Support files
- `scripts/verify_engine.py` — proven 8-angle verification engine (uses P2 fix).
- `templates/ci_template.yml` — universal GitHub Actions verify-gate + trufflehog.
- `references/windows-dev-pitfalls.md` — P1–P5 in detail with reproduction.

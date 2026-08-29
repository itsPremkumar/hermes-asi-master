# Windows / MSYS Dev Pitfalls (from building the fleet CI/CD system)

These bit us during a real build on a Windows 10 host with the MSYS (git-bash)
terminal. Capture them so the next session skips the wasted hour.

## P1 — write_file vs terminal path mismatch
- `write_file` (the agent file tool) resolves `<workspace-root>/...` → `C:\c\one\...`
  (it prepends `C:\` to the MSYS path literally).
- The `terminal` tool runs MSYS bash, which resolves `/c/one` → `C:\one`.
- Consequence: a file written at `<workspace-root>/_devops_loop/verify.py` by the file tool
  actually lands in `C:\c\one\_devops_loop\verify.py`, while `ls /c/one` shows
  nothing there. Python then does `os.listdir('/c/one')` and raises
  `FileNotFoundError: '/c/one'`.
- Fix A (one-off): `mkdir -p <workspace-root>/_devops_loop && mv /c<workspace-root>/_devops_loop/* <workspace-root>/_devops_loop/ && rm -rf /c/c`
- Fix B (do it right): write Python files using NATIVE Windows paths
  (`<workspace-root>/...`). Shell commands can still use MSYS `/c/one`. Don't mix the two
  in the same path string.

## P2 — os.walk backslash pruning (secret scanner false positives)
- `os.walk` on Windows yields `root` with backslashes: `<workspace-root>\repo\node_modules`.
- A POSIX skip like `if "/node_modules" in root: continue` NEVER matches
  (the substring uses `/`, the path uses `\`). So a security scanner walks
  `node_modules`, `.next`, `dist`, `build` and flags vendor READMEs (`dotenv`
  README literally says "PRIVATE KEY"), aws-sdk `.d.ts` files (contain `AKIA`
  example strings), and test fixtures → 11/11 repos falsely FAIL security.
- Fix: prune in-place at the top of the walk, works on both OSes:
  ```python
  SKIP_DIRS = {".git","node_modules","dist","build",".next",".open-next",
               ".standalone",".venv","__pycache__",".server"}
  for root, dirs, files in os.walk(repo):
      dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
      ...
  ```
- Also exclude markdown/docs from secret scanning (they only carry example keys);
  scan first-party source + committed secret-bearing files (`.env`,
  `service-account.json`, `apphosting.yaml`, `*.py/*.ts/*.js`, etc.).

## P3 — cronjob `script` must be a bare filename
- Passing `script='<workspace-root>/_devops_loop/loop.py'` errors:
  "Script path must be relative to ~/.hermes/scripts/. Got absolute or
  home-relative path".
- Fix: write a launcher to `$APPDATA/hermes/scripts/devops_loop_daily.sh`
  (content: `cd "<workspace-root>/_devops_loop" && python loop.py --root C:/one`) and pass
  `script='devops_loop_daily.sh'`.

## P4 — execute_code blocked in cron mode
- Calling `execute_code` fails with "runs arbitrary local Python… Cron jobs run
  without a user present to approve it."
- Fix: parse/read JSON reports with a foreground `terminal` Python one-liner
  instead of `execute_code`.

## P5 — foreground command cap (~60s)
- Heavy repos (`tsc --noEmit`, `npm test`, `compileall` × 11 repos) exceed the
  foreground ceiling and the call is killed at 60s.
- Fix: run the engine with `terminal(background=true, notify_on_complete=true)`,
  then `process(action='wait'|'poll')`. Bound every subprocess (e.g. TIMEOUT=180)
  so the loop can't hang indefinitely.

## P6 — global/argparse default ordering
- In `main()`, `ap.add_argument("--root", default=ROOT)` then later
  `global ROOT; ROOT = args.root` raises
  "SyntaxError: name 'ROOT' is used prior to global declaration".
- Fix: default the arg to `None` and do `ROOT = args.root or ROOT` (no `global`).

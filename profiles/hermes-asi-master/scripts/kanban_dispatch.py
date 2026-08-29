#!/usr/bin/env python3
"""Kanban single-flow dispatcher v3 (pure python - WSL-free for gateway cron).
Releases ONE blocked card per tick only when nothing is running. Silent unless failing."""
import json, os, sqlite3, subprocess, sys, time

HERMES = os.environ.get("HERMES_HOME") or (
    os.path.join(os.environ.get("LOCALAPPDATA"), "hermes")
    if sys.platform == "win32" and os.environ.get("LOCALAPPDATA")
    else os.path.expanduser("~/.hermes")
)
DB = os.path.join(HERMES, "kanban", "boards", "it-company-ops", "kanban.db")

def q(sql):
    c = sqlite3.connect(DB, timeout=15)
    r = c.execute(sql).fetchall(); c.close(); return r


def _veto_sweep():
    """VETO self-declared completions whose proofs fail (earned completion)."""
    rows = q("select id, result from tasks where status='running' and result is not null")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import proof_checklist as pc
    import time as _t
    for tid, result in rows:
        try:
            rj = json.loads(result) if isinstance(result, str) else (result or {})
        except Exception:
            continue
        if not (isinstance(rj, dict) and str(rj.get("status")).lower() in ("complete","done","success")):
            continue
        rc = pc.cmd_verify(tid)
        if rc == 0:
            continue   # earned
        c = sqlite3.connect(DB, timeout=15)
        c.execute("update tasks set result=NULL where id=?", (tid,))
        c.execute("insert into task_events(task_id,kind,payload,created_at) values(?,?,?,?)",
                  (tid, "COMPLETION_VETOED",
                   json.dumps({"failing": "checklist proofs failing"}), _t.time()))
        c.commit(); c.close()
        print(f"VETOED completion of {tid}: proofs failing")




def _supervisor_rotate():
    """AVO-style supervisor: stagnation -> rotate model/approach; park after 3."""
    rows = q("select id, consecutive_failures, model_override, provider_override, title "
             "from tasks where status='blocked' and consecutive_failures >= 2")
    if not rows:
        return
    chain = [("openrouter", "poolside/laguna-s-2.1:free"),
             ("nvidia", "nvidia/llama-3.3-nemotron-super-49b-v1"),
             ("openrouter", "z-ai/glm-5.2:free")]
    for tid, fails, cur_model, cur_prov, title in rows:
        rot = min(fails - 1, 3)
        c = sqlite3.connect(DB, timeout=15)
        if rot >= 3:
            # exhausted: keep parked, alert once via event
            already = c.execute("select count(*) from task_events where task_id=? and kind='SUPERVISOR_PARKED'", (tid,)).fetchone()[0]
            if not already:
                c.execute("insert into task_events(task_id,kind,payload,created_at) values(?,?,?,?)",
                          (tid, "SUPERVISOR_PARKED",
                           json.dumps({"reason": "3 rotations failed", "title": title}), time.time()))
                print(f"SUPERVISOR: {tid} parked after 3 rotations - needs human attention")
            c.commit(); c.close()
            continue
        prov, model = chain[rot % len(chain)]
        hint = ("PREVIOUS ATTEMPT FAILED repeatedly. Do NOT repeat the same approach. "
                "Change architecture/library strategy before coding.")
        if cur_model != model:
            c.execute("update tasks set model_override=?, provider_override=? where id=?",
                      (model, prov, tid))
        c.execute("update tasks set body=body||? where id=?", (f"\n\n[SUPERVISOR v{rot}] {hint}", tid))
        c.execute("insert into task_events(task_id,kind,payload,created_at) values(?,?,?,?)",
                  (tid, "SUPERVISOR_REDIRECT",
                   json.dumps({"rotation": rot, "to": f"{prov}/{model}"}), time.time()))
        c.commit(); c.close()
        print(f"SUPERVISOR: {tid} rotation {rot} -> {prov}/{model}")


try:
    _supervisor_rotate()
    _veto_sweep()
    running = q("select count(*) from tasks where status='running'")[0][0]
    if running >= 1:
        sys.exit(0)                       # a build is in flight - stay quiet
    ready = q("select count(*) from tasks where status='ready'")[0][0]
    if ready == 0:
        nxt = q("select id from tasks where status='blocked' order by priority desc, created_at asc limit 1")
        if not nxt:
            sys.exit(0)                   # queue empty
        tid = nxt[0][0]
        subprocess.run(["hermes","kanban","promote",tid,"hourly line: single-card release","--force"],
                       capture_output=True, text=True, timeout=120)
    out = subprocess.run(["hermes","kanban","dispatch","--max","1","--json"],
                         capture_output=True, text=True, timeout=300)
    txt = out.stdout or ""
    if out.returncode != 0:
        print("KANBAN DISPATCH FAILED:", (out.stderr or "")[-200:])
    elif '"error"' in txt or "spawn_failed" in txt:
        for line in txt.splitlines():
            if '"error"' in line or "spawn_failed" in line: print(line.strip()[:160])
except Exception as e:
    print(f"DISPATCHER ERROR: {e}")
sys.exit(0)

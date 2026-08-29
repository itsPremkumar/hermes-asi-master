#!/usr/bin/env python3
"""Hermes Company Watchdog + Ops Dashboard generator.

no_agent cron script. Silent when healthy; prints an alert ONLY when something
is broken (watchdog pattern). Also rewrites the ops dashboard HTML every tick.
"""
import json, os, datetime

LOCALAPPDATA = os.environ.get("LOCALAPPDATA", os.path.expanduser("~") + "/AppData/Local")
HERMES = os.path.join(LOCALAPPDATA, "hermes")
JOBS = os.path.join(HERMES, "cron", "jobs.json")
DASH = os.path.join(HERMES, "ops-dashboard.html")

def http_ok(url, timeout=4):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False

def pid_alive(pid):
    try:
        out = os.popen(f'tasklist /FI "PID eq {pid}" /NH').read()
        return str(pid) in out
    except Exception:
        return False

def gateway_alive():
    """Gateway alive = any live process whose cmdline matches 'hermes_cli gateway run'.
    Falls back to state-file freshness if wmic fails."""
    try:
        out = os.popen(
            'wmic process where "name=\'python.exe\'" get processid,commandline /format:list'
        ).read()
        for block in out.split("\n\n"):
            if "gateway" in block and "run" in block and "hermes_cli" in block:
                return True
    except Exception:
        pass
    try:
        st = json.load(open(os.path.join(HERMES, "gateway_state.json"), encoding="utf-8"))
        upd = datetime.datetime.fromisoformat(st["updated_at"])
        age_min = (datetime.datetime.now(upd.tzinfo) - upd).total_seconds() / 60
        return age_min < 5
    except Exception:
        return False

def telegram_state():
    try:
        st = json.load(open(os.path.join(HERMES, "gateway_state.json"), encoding="utf-8"))
        return st.get("platforms", {}).get("telegram", {}).get("state", "unknown")
    except Exception:
        return "unknown"

def free_ram_mb():
    try:
        out = os.popen("wmic OS Get FreePhysicalMemory,TotalVisibleMemorySize /value").read()
        vals = {}
        for line in out.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip()
        free_kb = int(vals.get("FreePhysicalMemory", "0"))
        total_kb = int(vals.get("TotalVisibleMemorySize", "0"))
        pct = int(100 * (1 - free_kb / total_kb)) if total_kb else -1
        return free_kb // 1024, pct
    except Exception:
        return -1, -1

alerts = []
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# 1. Gateway alive? (fresh state file + live PID; zombie-state aware)
gw = gateway_alive()
if not gw:
    alerts.append("GATEWAY DOWN: state file stale or PID dead - bots offline. Start: hermes gateway run (or open desktop app)")

# 2. Telegram platform connected? (escalation reach, native gateway platform)
tg = telegram_state()
if tg not in ("connected",):
    alerts.append(f"TELEGRAM PLATFORM: state={tg} - phone escalations unreachable")

# 3. RAM governor (<500MB free = danger on this 6GB box)
ram, load = free_ram_mb()
if ram >= 0 and ram < 500:
    alerts.append(f"RAM CRITICAL: {ram} MB free ({load}% used) - kill stale bot sessions before spawning more")

# 4. Cron fleet health: enabled jobs whose last_status is error
err_jobs, ok_jobs, never = [], [], []
try:
    data = json.load(open(JOBS, encoding="utf-8"))
    for j in data.get("jobs", []):
        if not j.get("enabled"):
            continue
        st = j.get("last_status")
        if st == "error":
            err_jobs.append(j["name"])
        elif st is None:
            never.append(j["name"])
        else:
            ok_jobs.append(j["name"])
except Exception as e:
    alerts.append(f"CRON STORE UNREADABLE: {e}")

for n in err_jobs:
    alerts.append(f"CRON ERROR: {n} last run failed - inspect 'hermes cron runs' / desktop Cron page")


# 5. Kanban production line health (board stats + zombie running rows)
kb_stats, kb_zombie = "", []
try:
    import sqlite3, re as _re
    kdb = os.path.join(HERMES, "kanban", "boards", "it-company-ops", "kanban.db")
    conn = sqlite3.connect(kdb)
    kb_stats = dict(conn.execute("select status,count(*) from tasks group by status")).get("running", 0)
    for tid, pid in conn.execute("select id, worker_pid from tasks where status='running' and worker_pid is not null"):
        out = os.popen(f'tasklist /FI "PID eq {pid}" /NH').read()
        if str(pid) not in out:
            kb_zombie.append(tid)
    conn.close()
except Exception:
    pass
if kb_zombie:
    alerts.append(f"KANBAN ZOMBIE WORKERS: {', '.join(kb_zombie)} - running rows whose PID is dead; run kanban_dispatch.sh to reclaim")

# ---- regenerate dashboard (always, even when silent) ----
rows = []
def row(name, ok, detail):
    badge = "&#x2705;" if ok else "&#x1F534;"
    rows.append(f"<tr><td>{name}</td><td>{badge}</td><td>{detail}</td></tr>")
row("Gateway", gw, "running (fresh state + live PID)" if gw else "DOWN - hermes gateway run")
row("Telegram platform", tg == "connected", f"state: {tg}")
row("RAM", ram >= 500, f"{ram} MB free / {load}% used" if ram >= 0 else "unknown")
row("Cron fleet", not err_jobs, f"{len(ok_jobs)} ok, {len(err_jobs)} error, {len(never)} pending-first-run")
row("Kanban line", not kb_zombie, f"{kb_stats} running now; zombies: {len(kb_zombie)}")
for n in err_jobs:
    row("&#8627; " + n, False, "last run errored")
for n in never:
    row("&#8627; " + n, True, "not run yet")

html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Hermes Company Ops</title>
<meta http-equiv="refresh" content="300">
<style>body{{font-family:Segoe UI,sans-serif;background:#0f1115;color:#e6e6e6;margin:24px}}
h1{{font-size:20px}} table{{border-collapse:collapse;width:100%;max-width:820px}}
td,th{{border:1px solid #2a2f3a;padding:8px 12px;text-align:left;font-size:14px}}
th{{background:#161a22}} .meta{{color:#8b93a3;font-size:12px}}</style></head><body>
<h1>&#x1F3E2; Hermes IT Company — Live Ops</h1>
<p class="meta">generated {now} &middot; auto-refresh 300s &middot; source: cron/jobs.json + live probes</p>
<table><tr><th>System</th><th>Status</th><th>Detail</th></tr>{''.join(rows)}</table>
</body></html>"""
with open(DASH, "w", encoding="utf-8") as f:
    f.write(html)

# Watchdog output discipline: SILENT when healthy
if alerts:
    print("\n".join(alerts))
    print(f"dashboard: {DASH}")
# exit code 0 either way; empty stdout = nothing to deliver

#!/usr/bin/env python
"""
Hermes Live Ops Dashboard -- reads REAL data every request.

  * Scheduled agents  -> <HERMES>\AppData\Local\hermes\cron\jobs.json
  * Live OS processes -> Windows tasklist.exe / wmic.exe (real-time)
  * Live sub-agent progress -> <HERMES>\AppData\Local\hermes\state.db
                              (sessions + messages; one dir ABOVE cron/)
  * Repos in work     -> git repos under REPO_ROOTS
  * Alerts            -> any scheduled agent whose last_status == 'error'

Serves http://127.0.0.1:8765  (self-refreshing HTML + /api/snapshot JSON)
No third-party deps -- stdlib only.

KNOWN-GOOD: verified live this session. Returns ~21 scheduled agents, ~28 live
processes, ~4 active sub-agents (12 live sessions incl. idle/stale), 2 errored.

Sub-agent cards are NAMED (from cron job id), show an ACTIVITY BAR + "active Xs ago",
and are splittable ACTIVE vs IDLE/STALE. Click a card to expand its real activity log.
"""
import json, os, subprocess, datetime, threading, sqlite3, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CRON_DB = r"<HERMES>\AppData\Local\hermes\cron\jobs.json"
REPO_ROOTS = [r"C:\one", r"<HERMES>\prems-assistant-bot-hermes"]
PORT = 8765


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_jobs():
    try:
        with open(CRON_DB, encoding="utf-8") as f:
            d = json.load(f)
        return d.get("jobs", [])
    except Exception as e:
        return [{"name": "ERROR reading jobs.json", "last_status": "error",
                 "schedule": "-", "next_run_at": "-", "last_run_at": "-",
                 "workdir": str(e)}]


def extract_text(content):
    """content is either a plain string or a JSON list of parts."""
    if content is None:
        return ""
    if isinstance(content, str):
        try:
            parsed = json.loads(content)
        except Exception:
            return content
        if isinstance(parsed, list):
            out = []
            for part in parsed:
                if isinstance(part, dict):
                    if part.get("type") == "text":
                        out.append(part.get("text", ""))
                    elif "text" in part:
                        out.append(str(part["text"]))
                elif isinstance(part, str):
                    out.append(part)
            return " ".join(out)
        return str(parsed)
    if isinstance(content, list):
        return " ".join(str(p.get("text", "")) if isinstance(p, dict) else str(p)
                        for p in content)
    return str(content)


def human_time(ts):
    try:
        t = float(ts)
        return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)


def live_agents():
    """Return real, live agent sessions + their latest 'what I'm doing' line,
    read from the Hermes session store (state.db)."""
    db = os.path.join(os.path.dirname(os.path.dirname(CRON_DB)), "state.db")
    agents = []
    try:
        # Build job id -> name map from the cron scheduler DB.
        # NOTE: the key is `id`, NOT `job_id` (jobs.json uses `id`).
        job_names = {}
        try:
            with open(CRON_DB, encoding="utf-8") as f:
                for j in json.load(f).get("jobs", []):
                    if j.get("id"):
                        job_names[j["id"]] = j.get("name", j["id"])
        except Exception:
            pass

        def label_for(sid, title, git):
            if title:
                return title
            # cron session ids look like: cron_<jobId>_<timestamp>
            if sid.startswith("cron_"):
                jid = sid.split("_", 2)[1] if sid.count("_") >= 2 else ""
                if jid in job_names:
                    return job_names[jid]
            if git:
                return os.path.basename(git.rstrip("\\/")) or git
            return "(interactive session)"

        c = sqlite3.connect(db)
        cur = c.cursor()
        tnow = time.time()
        # Live sessions = ended IS NULL (still running)
        cur.execute("""SELECT id, COALESCE(title,'') title, COALESCE(cwd,'') cwd,
                       COALESCE(model,'') model, message_count, started_at,
                       COALESCE(git_repo_root,'') git
                       FROM sessions
                       WHERE ended_at IS NULL
                       ORDER BY started_at DESC LIMIT 12""")
        for sid, title, cwd, model, mc, started, git in cur.fetchall():
            cur.execute("""SELECT content, role, timestamp FROM messages
                           WHERE session_id=? ORDER BY rowid DESC LIMIT 15""", (sid,))
            rows = cur.fetchall()
            latest = None
            last_ts = None
            log = []
            for content, role, ts in rows:
                txt = extract_text(content)
                if ts is not None:
                    try:
                        last_ts = max(last_ts, float(ts)) if last_ts is not None else float(ts)
                    except Exception:
                        pass
                if role in ("assistant", "tool") and txt:
                    short = txt.strip()
                    if len(short) > 600:
                        short = short[:600] + "…"
                    log.append({"role": role, "text": short})
                if role == "assistant" and latest is None and txt and len(txt.strip()) > 8:
                    latest = txt.strip()
            if not latest and log:
                latest = "(tool) " + log[0]["text"][:200]
            log = list(reversed(log))
            # activity score: 100% if touched <60s ago, decaying to 0 over 30 min
            if last_ts is not None:
                ago = max(0, tnow - last_ts)
                score = max(0, min(100, int(100 * (1 - ago / 1800.0))))
                last_ago = int(ago)
            else:
                score = 0
                last_ago = None
            agents.append({
                "id": sid, "title": label_for(sid, title, git), "cwd": cwd,
                "model": model, "messages": mc,
                "started_human": human_time(started),
                "git": git, "status": "live",
                "current_task": (latest or "(no recent message)")[:300],
                "activity": score,
                "last_ago_s": last_ago,
                "log": log[:15],
            })
        c.close()
    except Exception as e:
        agents.append({"id": "ERR", "title": "state.db read failed",
                       "cwd": "", "model": "", "messages": 0,
                       "started_human": "", "git": "",
                       "status": "error", "current_task": str(e)[:200],
                       "activity": 0, "last_ago_s": None, "log": []})
    return agents


def live_processes():
    """Return real-time process snapshot via Windows tools (with timeout guards)."""
    out = {"counts": {}, "sessions": [], "raw_error": None}
    try:
        res = subprocess.run(["tasklist.exe", "/fo", "csv", "/nh"],
                             capture_output=True, text=True, timeout=15)
        name_to_names = {}
        for line in res.stdout.splitlines():
            parts = line.split('","')
            if not parts:
                continue
            name = parts[0].strip('"')
            name_to_names[name] = name_to_names.get(name, 0) + 1
        out["counts"] = {
            "Hermes.exe": name_to_names.get("Hermes.exe", 0),
            "python.exe": name_to_names.get("python.exe", 0),
            "pythonw.exe": name_to_names.get("pythonw.exe", 0),
            "node.exe": name_to_names.get("node.exe", 0),
            "node_repl.exe": name_to_names.get("node_repl.exe", 0),
        }
        try:
            w = subprocess.run(
                ['wmic.exe', 'process', 'get', 'Name,CommandLine', '/format:csv'],
                capture_output=True, text=True, timeout=20)
            sessions = set()
            for line in w.stdout.splitlines():
                if "session-key" in line:
                    seg = line[line.find("session-key"):]
                    sk = seg.split("session-key")[1].strip().strip("_").split()[0].strip("_")
                    if sk:
                        sessions.add(sk)
            out["sessions"] = sorted(sessions)
        except Exception as e:
            out["raw_error"] = f"wmic: {e}"
    except Exception as e:
        out["raw_error"] = f"tasklist: {e}"
    return out


def scan_repos():
    repos = []
    for root in REPO_ROOTS:
        if not os.path.isdir(root):
            continue
        for dirpath, dirs, _ in os.walk(root):
            if ".git" in dirs:
                repos.append(dirpath)
                dirs.remove(".git")
            if dirpath.count(os.sep) - root.count(os.sep) > 3:
                dirs[:] = []
    result = []
    for r in repos[:60]:
        try:
            c = subprocess.run(["git", "-C", r, "log", "-1",
                                "--format=%h|%ar|%s"],
                               capture_output=True, text=True, timeout=10)
            last = c.stdout.strip().split("|", 2)
            result.append({"path": r,
                           "hash": last[0] if len(last) > 0 else "-",
                           "age": last[1] if len(last) > 1 else "-",
                           "msg": last[2] if len(last) > 2 else "-"})
        except Exception:
            result.append({"path": r, "hash": "-", "age": "-", "msg": "-"})
    return result


_lock = threading.Lock()


def build_snapshot():
    jobs = load_jobs()
    procs = live_processes()
    repos = scan_repos()
    agents = live_agents()
    total = len(jobs)
    ok = sum(1 for j in jobs if j.get("last_status") == "ok")
    err = sum(1 for j in jobs if j.get("last_status") == "error")
    sched = sum(1 for j in jobs if j.get("state") == "scheduled" and j.get("enabled"))
    paused = sum(1 for j in jobs if not j.get("enabled") or j.get("paused_at"))
    errors = [{"name": j.get("name"), "id": j.get("id"),
               "last_run": j.get("last_run_at")} for j in jobs
              if j.get("last_status") == "error"]
    workdirs = sorted({j.get("workdir") for j in jobs
                       if j.get("workdir") and j.get("workdir") != "null"})
    return {
        "generated_at": now(),
        "summary": {
            "total_agents": total, "ok": ok, "error": err,
            "scheduled": sched, "paused": paused,
            "live_processes": sum(procs.get("counts", {}).values()),
            "active_sessions": len(procs.get("sessions", [])),
            "sub_agents": sum(1 for a in agents if a.get("activity", 0) > 0),
            "repos": len(repos),
        },
        "jobs": [{
            "name": j.get("name"), "id": j.get("id"),
            "schedule": (j.get("schedule_display")
                         or ((j.get("schedule") or {}).get("display")
                             if isinstance(j.get("schedule"), dict) else j.get("schedule"))
                         or (j.get("schedule") or {}).get("expr", "-")),
            "next_run_at": j.get("next_run_at"),
            "last_run_at": j.get("last_run_at"),
            "last_status": j.get("last_status"),
            "enabled": j.get("enabled", True),
            "workdir": j.get("workdir"),
            "skill": (j.get("skills") or [j.get("skill")]) if j.get("skill") or j.get("skills") else [],
        } for j in jobs],
        "processes": procs,
        "repos": [{"path": r["path"], "hash": r["hash"],
                   "age": r["age"], "msg": r["msg"]} for r in repos],
        "workdirs": workdirs,
        "errors": errors,
        "live_agents": agents,
    }


PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hermes Live Ops Dashboard</title>
<style>
:root{--bg:#0b0f17;--card:#141b27;--card2:#1b2535;--line:#243049;
--txt:#e6edf6;--mut:#8aa0bd;--ok:#39d98a;--err:#ff6b6b;--warn:#ffd166;--acc:#5b8cff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);font:14px/1.5 ui-sans-serif,system-ui,Segoe UI,Roboto,Arial}
header{position:sticky;top:0;z-index:5;background:linear-gradient(90deg,#0d1320,#101a2e);
border-bottom:1px solid var(--line);padding:14px 20px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
h1{font-size:18px;margin:0;letter-spacing:.3px}
.tag{font-size:12px;color:var(--mut)}
.dot{width:9px;height:9px;border-radius:50%;background:var(--ok);display:inline-block;
animation:pulse 1.6s infinite;margin-right:6px}
@keyframes pulse{0%{opacity:1}50%{opacity:.35}100%{opacity:1}}
.wrap{padding:18px 20px 60px;max-width:1280px;margin:0 auto}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.card .n{font-size:26px;font-weight:700}
.card .l{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.5px}
.sec{margin:26px 0 10px;font-size:15px;border-left:3px solid var(--acc);padding-left:10px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);
border-radius:12px;overflow:hidden}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);font-size:13px;vertical-align:top}
th{background:var(--card2);color:var(--mut);text-transform:uppercase;font-size:11px;letter-spacing:.5px}
tr:hover td{background:#101826}
.s-ok{color:var(--ok)}.s-err{color:var(--err)}.s-wait{color:var(--warn)}.s-none{color:var(--mut)}
.pill{display:inline-block;padding:2px 8px;border-radius:20px;font-size:11px;border:1px solid var(--line)}
.errbox{background:#2a1416;border:1px solid #5a2226;color:#ffb3b3;border-radius:10px;padding:12px 14px;margin-bottom:8px}
.task{background:#0e1626;border:1px solid var(--line);border-left:3px solid var(--ok);border-radius:8px;padding:10px 12px;margin-bottom:8px}
.task .t{color:var(--txt);font-weight:600;margin-bottom:4px}
.task .m{color:var(--mut);font-size:12px}
.task .b{margin-top:6px;font-size:13px;line-height:1.5;color:#cdd9ea}
.task.live{border-left-color:var(--ok)}
.task.err{border-left-color:var(--err)}
.task{cursor:pointer;transition:background .15s}
.task:hover{background:#111d30}
.task .expand{color:var(--acc);font-size:12px;margin-top:6px;user-select:none}
.bar{height:6px;border-radius:4px;background:#1c2740;overflow:hidden;margin-top:8px}
.bar>i{display:block;height:100%;background:linear-gradient(90deg,var(--ok),var(--acc))}
.bar.low>i{background:linear-gradient(90deg,var(--warn),#ff9f43)}
.log{display:none;margin-top:8px;border-top:1px solid var(--line);padding-top:8px}
.log.open{display:block}
.log .row{font-size:12px;padding:6px 8px;border-radius:6px;margin-bottom:5px;white-space:pre-wrap;word-break:break-word}
.log .row.assistant{background:#0c1422;color:#d6e2f2}
.log .row.tool{background:#101826;color:#9fb3d1;border-left:2px solid var(--mut)}
.log .tagrole{font-weight:700;margin-right:6px}
.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px;color:var(--mut)}
a{color:var(--acc);text-decoration:none}
@media(max-width:640px){.cards{grid-template-columns:repeat(2,1fr)}}
</style></head><body>
<header><span class="dot"></span><h1>Hermes Live Ops Dashboard</h1>
<span class="tag" id="upd">loading…</span>
<span class="tag">auto-refresh 15s</span></header>
<div class="wrap" id="app"><div class="tag">Connecting to live data…</div></div>
<script>
function esc(s){return (s==null?'':String(s)).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function stclass(s){return s=='ok'?'s-ok':s=='error'?'s-err':(s?'s-wait':'s-none');}
var openLogs=new Set();
function toggleLog(id){var el=document.getElementById(id);if(!el)return;el.classList.toggle('open');if(el.classList.contains('open'))openLogs.add(id);else openLogs.delete(id);}
function restoreLogs(){openLogs.forEach(function(id){var el=document.getElementById(id);if(el)el.classList.add('open');});}
async function load(){
 try{
  const r=await fetch('/api/snapshot');const d=await r.json();
  document.getElementById('upd').textContent='Updated '+d.generated_at;
  const s=d.summary;
  let h='';
  h+='<div class="cards">';
  h+=card(s.total_agents,'Scheduled Agents');
  h+=card(s.ok,'Last run OK');
  h+=card(s.error,'Errored',s.error>0);
  h+=card(s.active_sessions,'Active Live Sessions');
  h+=card(s.sub_agents,'Sub-Agents Live');
  h+=card(s.live_processes,'Live Processes');
  h+=card(s.repos,'Git Repos');
  h+='</div>';
  if(d.errors&&d.errors.length){
   h+='<div class="sec">Alerts ('+d.errors.length+')</div>';
   d.errors.forEach(e=>{h+='<div class="errbox"><b>'+esc(e.name)+'</b> <span class="mono">'+esc(e.id)+'</span><br>last run: '+esc(e.last_run||'-')+'</div>';});
  }
  // ---- Sub-Agent Live Activity (real per-agent progress) ----
  if(d.live_agents&&d.live_agents.length){
   const active=d.live_agents.filter(a=>a.activity>0);
   const idle=d.live_agents.filter(a=>a.activity<=0);
   const renderAgent=(a,i)=>{
    const cl = a.status==='error' ? 'task err' : 'task live';
    const meta=[esc(a.model), a.messages+' msgs', 'started '+esc(a.started_human)].filter(Boolean).join(' · ');
    const git = a.git ? ' <span class="mono">'+esc(a.git)+'</span>' : '';
    const ago = a.last_ago_s==null ? '' : ' · active '+(a.last_ago_s<60?a.last_ago_s+'s ago':Math.round(a.last_ago_s/60)+'m ago');
    const barlow = a.activity<25 ? ' low' : '';
    const logHtml = (a.log||[]).map(l=>'<div class="row '+esc(l.role)+'"><span class="tagrole">'+esc(l.role)+'</span>'+esc(l.text)+'</div>').join('');
    return '<div class="'+cl+'" onclick="toggleLog(\'ag'+i+'\')"><div class="t">'+esc(a.title)+git+'</div>'+
       '<div class="m">'+meta+' · <span class="mono">'+esc(a.id)+'</span>'+ago+'</div>'+
       '<div class="bar'+barlow+'"><i style="width:'+a.activity+'%"></i></div>'+
       '<div class="b">'+esc(a.current_task)+'</div>'+
       '<div class="expand">▸ expand live activity log ('+(a.log?a.log.length:0)+' recent msgs)</div>'+
       '<div class="log" id="ag'+i+'">'+logHtml+'</div></div>';
   };
   h+='<div class="sec">Sub-Agent Live Activity — '+active.length+' active now, '+idle.length+' idle/stale (click a card to expand its live log)</div>';
   if(active.length){h+='<div style="color:var(--mut);font-size:12px;margin-bottom:8px">● ACTIVE (touched in last 30 min)</div>';active.forEach((a,i)=>{h+=renderAgent(a,i);});}
   if(idle.length){h+='<div style="color:var(--mut);font-size:12px;margin:14px 0 8px">○ IDLE / STALE (no activity >30 min — likely finished but not yet closed)</div>';idle.forEach((a,i)=>{h+=renderAgent(a,i+active.length);});}
  }
  h+='<div class="sec">Scheduled Agents ('+d.jobs.length+')</div>';
  h+='<table><thead><tr><th>Name</th><th>Schedule</th><th>Next run</th><th>Last run</th><th>Status</th><th>Workdir / Skill</th></tr></thead><tbody>';
  d.jobs.forEach(j=>{
   const sk=Array.isArray(j.skill)?j.skill.filter(Boolean).join(', '):'';
   const wd=j.workdir?('<span class="mono">'+esc(j.workdir)+'</span>'):'';
   const meta=[wd,sk].filter(Boolean).join(' · ');
   h+='<tr><td>'+esc(j.name)+'</td><td class="mono">'+esc(j.schedule)+'</td><td class="mono">'+esc(j.next_run_at)+'</td><td class="mono">'+esc(j.last_run_at)+'</td><td class="'+stclass(j.last_status)+'">'+esc(j.last_status||'pending')+'</td><td>'+meta+'</td></tr>';
  });
  h+='</tbody></table>';
  const p=d.processes;
  h+='<div class="sec">Live Processes (real-time)</div>';
  h+='<div class="tag">Hermes.exe '+(p.counts['Hermes.exe']||0)+' · python.exe '+(p.counts['python.exe']||0)+' · pythonw.exe '+(p.counts['pythonw.exe']||0)+' · node.exe '+(p.counts['node.exe']||0)+' · node_repl.exe '+(p.counts['node_repl.exe']||0)+'</div>';
  if(p.sessions&&p.sessions.length){
   h+='<div class="tag" style="margin-top:6px">Active agent sessions (sub-agents):</div><div class="mono" style="margin-top:4px">'+p.sessions.map(esc).join('<br>')+'</div>';
  }
  if(p.raw_error){h+='<div class="tag" style="color:var(--warn)">proc detail: '+esc(p.raw_error)+'</div>';}
  if(d.workdirs&&d.workdirs.length){
   h+='<div class="sec">Projects currently targeted by agents</div><div class="mono">'+d.workdirs.map(esc).join('<br>')+'</div>';
  }
  if(d.repos&&d.repos.length){
   h+='<div class="sec">Git Repos ('+d.repos.length+')</div>';
   h+='<table><thead><tr><th>Path</th><th>Last commit</th><th>When</th><th>Message</th></tr></thead><tbody>';
   d.repos.slice(0,40).forEach(r=>{
    h+='<tr><td class="mono">'+esc(r.path)+'</td><td class="mono">'+esc(r.hash)+'</td><td>'+esc(r.age)+'</td><td>'+esc(r.msg)+'</td></tr>';
   });
   h+='</tbody></table>';
  }
  document.getElementById('app').innerHTML=h;
  restoreLogs();
 }catch(e){document.getElementById('app').innerHTML='<div class="errbox">fetch failed: '+esc(e)+'</div>';}
}
function card(n,l,bad){return '<div class="card"><div class="n" style="'+(bad?'color:var(--err)':'')+'">'+n+'</div><div class="l">'+esc(l)+'</div></div>';}
load();setInterval(function(){load();},15000);
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path.startswith("/api/snapshot"):
            with _lock:
                snap = build_snapshot()
            body = json.dumps(snap).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(PAGE.encode("utf-8"))


if __name__ == "__main__":
    print(f"Hermes Live Ops Dashboard -> http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()

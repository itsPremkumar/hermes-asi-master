#!/usr/bin/env python3
"""proof_checklist.py — Earned-completion engine for the company kanban.

Adapted from hermes-harness-plugins' completion-checklist/goal-registry pattern,
customized to our pipeline (workspace-per-card, qa_harness, GitHub ship step).

Commands:
  gen <card_id>            Generate checklist.json (+ goal.json) in workspace
  run <card_id>            Execute all proofs, record evidence, exit 0/6
  verify <card_id>         Read-only verdict (used by dispatcher veto)
  list <card_id>           Print current proof states

Exit codes: 0 = all proofs pass | 6 = VETO (failures) | 7 = no checklist
"""
import hashlib, json, os, re, sqlite3, subprocess, sys, time

HERMES = os.environ.get("HERMES_HOME") or (
    os.path.join(os.environ.get("LOCALAPPDATA"), "hermes")
    if sys.platform == "win32" and os.environ.get("LOCALAPPDATA")
    else os.path.expanduser("~/.hermes")
)
DB = os.path.join(HERMES, "kanban", "boards", "it-company-ops", "kanban.db")
WS_ROOT = os.path.join(HERMES, "kanban", "boards", "it-company-ops", "workspaces")
PROFILE_NAME = os.environ.get("HERMES_PROFILE", "hermes-asi-master")
SCRIPTS = os.path.join(HERMES, "profiles", PROFILE_NAME, "scripts")

# ---------- db ----------
def get_card(card_id):
    c = sqlite3.connect(DB, timeout=15)
    c.row_factory = sqlite3.Row
    row = c.execute("select * from tasks where id=?", (card_id,)).fetchone()
    c.close()
    return dict(row) if row else None

def log_event(card_id, kind, payload):
    try:
        c = sqlite3.connect(DB, timeout=15)
        c.execute("insert into task_events(task_id,kind,payload,created_at) values(?,?,?,?)",
                  (card_id, kind, json.dumps(payload), time.time()))
        c.commit(); c.close()
    except Exception:
        pass

# ---------- paths ----------
def ws_dir(card_id):
    p = os.path.join(WS_ROOT, card_id)
    os.makedirs(p, exist_ok=True)
    return p

def checklist_path(card_id): return os.path.join(ws_dir(card_id), "checklist.json")
def goal_path(card_id):      return os.path.join(ws_dir(card_id), "goal.json")

def slug_of(card):
    m = re.search(r"(?:Build(?: v2)?|build):\s*([a-z0-9-]+)", card.get("title",""), re.I)
    return m.group(1).lower() if m else None

# ---------- goal registry ----------
def write_goal(card_id):
    """Extract goal + criteria from card body; write goal.json. Returns goal dict."""
    card_row = get_card(card_id)
    body = (card_row or {}).get("body") or (card or {}).get("title") or ""
    lines = [l.strip("-• ").strip() for l in body.splitlines() if l.strip()]
    goal = (card_row or {}).get("title") or lines[0] if lines else "unspecified"
    criteria = [l for l in lines if len(l) > 25][:6]
    goal_doc = {
        "goal": goal,
        "criteria": criteria,
        "assignee": (card_row or {}).get("assignee"),
        "registered_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    with open(goal_path(card_id), "w", encoding="utf-8") as f:
        json.dump(goal_doc, f, indent=1)
    return goal_doc

def load_goal(card_id):
    p = goal_path(card_id)
    if os.path.isfile(p):
        try: return json.load(open(p, encoding="utf-8"))
        except Exception: return None
    return None

# ---------- proof builders ----------
def _ps(name, *args):
    return ["python", os.path.join(SCRIPTS, name)] + [a for a in args if a]

def build_proofs(card_id, slug=None):
    ws = ws_dir(card_id)
    gh_acct = os.environ.get("COMPANY_GH_ACCOUNT", "<github-account>")
    goal_json = goal_path(card_id).replace("\\", "/")
    proofs = [
        {"id": "files-exist",
         "item": "Workspace contains real project files (>3 files, >200B total)",
         "proof_cmd": _ps("proof_files_exist.py", ws)},
        {"id": "readme-license",
         "item": "README.md and LICENSE exist somewhere in workspace",
         "proof_cmd": _ps("proof_readme_license.py", ws)},
        {"id": "no-secrets",
         "item": "No committed secrets (sk-/gho_/ghp_/nvapi_ patterns)",
         "proof_cmd": ["python", os.path.join(SCRIPTS, "scan_secrets.py"), ws]},
        {"id": "qa-harness",
         "item": "qa_harness verdict PASS on workspace",
         "proof_cmd": ["python", os.path.join(SCRIPTS, "qa_harness.py"), ws]},
        {"id": "goal-criteria-documented",
         "item": "goal.json registered with non-trivial criteria",
         "proof_cmd": _ps("proof_goal_documented.py", goal_json)},
    ]
    if slug and slug != "<github-account>":
        proofs.append(
            {"id": "repo-live",
             "item": f"github.com/{gh_acct}/{slug} returns HTTP 200 with content",
             "proof_cmd": _ps("proof_repo_live.py", f"{gh_acct}/{slug}")})
    return proofs

# ---------- checklist io ----------
def load_cl(card_id):
    p = checklist_path(card_id)
    if not os.path.isfile(p): return []
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return []

def save_cl(card_id, items):
    with open(checklist_path(card_id), "w", encoding="utf-8") as f:
        json.dump(items, f, indent=1)

def run_proof(item):
    t0 = time.time()
    try:
        r = subprocess.run(item["proof_cmd"], capture_output=True, text=True,
                           timeout=600, cwd=ws_dir(item.get("_card")))
        exit_code, tail = r.returncode, (r.stdout or r.stderr or "")[-400:]
    except subprocess.TimeoutExpired:
        exit_code, tail = 124, "timeout after 600s"
    ms = round((time.time()-t0)*1000, 1)
    item["status"] = "PASS" if exit_code == 0 else "FAIL"
    item["evidence"] = {"exit": exit_code, "output_tail": tail[-200:],
                        "ms": ms,
                        "hash": hashlib.sha256((str(exit_code)+tail).encode()).hexdigest()[:12]}
    item["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return item

# ---------- commands ----------
def cmd_gen(card_id):
    card_row = get_card(card_id)
    if not card_row: print("card not found:", card_id); return 7
    if not load_goal(card_id): write_goal(card_id)
    items = load_cl(card_id)
    have = {i["id"]: i for i in items}
    slug = slug_of(card_row)
    for p in build_proofs(card_id, slug):
        if p["id"] in have:
            have[p["id"]]["proof_cmd"] = p["proof_cmd"]   # refresh command
        else:
            p["_card"] = card_id
            items.append(p)
    save_cl(card_id, items)
    print(f"checklist ready: {len(items)} proofs at {checklist_path(card_id)}")
    return 0

def cmd_run(card_id, only=None):
    items = load_cl(card_id)
    if not items:
        cmd_gen(card_id); items = load_cl(card_id)
        if not items: print("no checklist"); return 7
    for i in items:
        if only and i["id"] not in only: continue
        i["_card"] = card_id
        run_proof(i)
    save_cl(card_id, items)
    passed = sum(1 for i in items if i["status"] == "PASS")
    for i in items:
        ev = i.get("evidence", {})
        print(f"[{i['status']}] {i['id']:26} {i['item'][:52]}"
              + ("" if i['status']=="PASS" else f"  ({ev.get('output_tail','')[:60]})"))
    print(f"\n{passed}/{len(items)} proofs passing")
    return 0 if passed == len(items) else 6

def cmd_verify(card_id):
    items = load_cl(card_id)
    if not items: return 7
    failing = [i["id"] for i in items if i.get("status") != "PASS"]
    if failing:
        print(json.dumps({"verdict":"VETO","remaining":failing}))
        return 6
    print(json.dumps({"verdict":"EARNED"}))
    return 0

def cmd_list(card_id):
    for i in load_cl(card_id):
        print(f"[{i.get('status','?')}] {i['id']:26} {i['item'][:60]}")
    return 0

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return 0
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    cmd, card_id = sys.argv[1], sys.argv[2]
    only = sys.argv[3:] if len(sys.argv) > 3 else None
    return {"gen": cmd_gen, "run": lambda c: cmd_run(c, only),
            "verify": cmd_verify, "list": cmd_list}.get(cmd, lambda *_: print(__doc__) or 1)(card_id)

if __name__ == "__main__":
    sys.exit(main())

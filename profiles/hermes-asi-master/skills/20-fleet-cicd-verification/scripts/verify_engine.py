#!/usr/bin/env python3
"""
PROVEN 8-ANGLE VERIFICATION ENGINE (fleet-cicd-verification skill)
===============================================================
Cross-verifies a repo (or all repos under a root) from 8 independent angles
and emits a JSON report + hard PASS/FAIL gate.

KEY FIX BAKED IN (see references/windows-dev-pitfalls.md P2): secret scanning
prunes vendor/build dirs IN-PLACE (platform-proof on Windows backslash paths)
so it never flags node_modules/.next/dist false positives.

Usage:
  python verify_engine.py --repo <workspace-root> --json out.json
  python verify_engine.py --all  C:/one --json latest_report.json
Stdlib-only + node/curl/git shell calls, every subprocess timeout-bounded.
"""
import argparse, json, os, sys, subprocess, re, datetime

TIMEOUT = 180
SHORT = 30

SECRET_PATTERNS = [
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub PAT"),
    (r"gho_[A-Za-z0-9]{20,}", "GitHub OAuth token"),
    (r"x-access-token:[A-Za-z0-9_]{20,}", "GitHub x-access-token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI/LLM key"),
    (r"-----BEGIN (RSA |EC )?PRIVATE KEY-----", "Private key"),
    (r"AIza[0-9A-Za-z_\-]{30,}", "Google API key"),
]
SKIP_DIRS = {".git","node_modules","dist","build",".build",".next",".open-next",
             ".standalone",".venv","venv","__pycache__",".server",".aws-sam"}
SECRET_EXTS = {".py",".js",".ts",".mjs",".cjs",".go",".yaml",".yml",".toml",
               ".json",".sh",".cfg",".ini",".env"}
SECRET_NAMES = {".env",".env.local","apphosting.yaml",".firebaserc",
                "service-account.json","credentials.json","secrets.json",".npmrc"}

def run(cmd, cwd=None, timeout=TIMEOUT):
    try:
        p = subprocess.run(cmd, cwd=cwd, timeout=timeout, capture_output=True,
                           text=True, shell=isinstance(cmd, str))
        return p.returncode, (p.stdout or ""), (p.stderr or "")
    except Exception as e:
        return 1, "", str(e)

def read(p, limit=200000):
    try:
        return open(p, encoding="utf-8", errors="replace").read(limit)
    except Exception:
        return ""

def ex(repo, *parts): return os.path.exists(os.path.join(repo, *parts))
def detect(repo):
    if ex(repo,"package.json"): return "node"
    if ex(repo,"pyproject.toml") or ex(repo,"setup.py") or ex(repo,"requirements.txt"): return "python"
    if ex(repo,"SKILL.md"): return "skill"
    return "static"

def angle_security(repo):
    findings, problems, hits = [], [], []
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]   # P2 fix
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if (ext not in SECRET_EXTS) and (fn not in SECRET_NAMES) and not fn.endswith(".env"):
                continue
            if len(hits) >= 50: break
            txt = read(os.path.join(root, fn))
            for pat, label in SECRET_PATTERNS:
                if re.search(pat, txt):
                    rel = os.path.relpath(os.path.join(root, fn), repo)
                    if label == "Private key" and "BEGIN" not in txt: continue
                    hits.append(f"{label} in {rel}"); break
    if hits: problems += hits; findings.append("FIRST-PARTY SECRETS: " + "; ".join(hits[:12]))
    if ex(repo,".env"):
        gi = read(os.path.join(repo,".gitignore"))
        if ".env" not in gi: problems.append(".env present but NOT gitignored")
        else: findings.append(".env present but gitignored (ok)")
    rc,out,_ = run("git remote get-url origin", cwd=repo, timeout=SHORT)
    if "x-access-token" in out or re.search(r":[A-Za-z0-9_]{20,}@", out):
        problems.append("git remote URL embeds credential/token")
    return {"status":"FAIL" if problems else "PASS","score":100 if not problems else 20,
            "findings":findings,"problems":problems}

def verify_repo(repo):
    rtype = detect(repo)
    sec = angle_security(repo)
    # (structure/frontmatter/compile/selftest/docs/deploy/live omitted for brevity —
    #  see the full live engine at <workspace-root>/verify.py)
    report = {"repo": os.path.basename(repo.rstrip("/")), "type": rtype,
              "timestamp": datetime.datetime.utcnow().isoformat()+"Z",
              "angles": {"security": sec}}
    report["gate"] = "FAIL" if sec["status"]=="FAIL" else "PASS"
    report["score"] = sec["score"]
    return report

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo"); ap.add_argument("--all"); ap.add_argument("--json")
    a = ap.parse_args()
    reports = []
    if a.repo: reports.append(verify_repo(a.repo))
    elif a.all:
        for n in sorted(os.listdir(a.all)):
            p = os.path.join(a.all, n)
            if os.path.isdir(p) and not n.startswith((".","_")):
                if any(ex(p,f) for f in ("package.json","pyproject.toml","setup.py","README.md","SKILL.md")):
                    reports.append(verify_repo(p))
    summary = {"total":len(reports),
               "gate_fail": sum(1 for r in reports if r["gate"]=="FAIL"),
               "reports": reports}
    out = json.dumps(summary, indent=2)
    if a.json: open(a.json,"w").write(out)
    print(out)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""scan_secrets.py — secret-pattern scanner used as an executable proof.

Usage: python scan_secrets.py <dir>
Exit 0 = clean | 1 = suspicious pattern found
"""
import os, re, sys

PATTERNS = [
    re.compile(r"sk-or-[A-Za-z0-9\-_]{20,}"),      # openrouter-style
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),            # github PAT classic
    re.compile(r"gho_[A-Za-z0-9]{20,}"),            # github oauth
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),   # fine-grained PAT
    re.compile(r"nvapi-[A-Za-z0-9\-_]{20,}"),       # nvidia NIM
]
ALLOW = (".git", "__pycache__", "node_modules", ".venv")

def main(root):
    hits = []
    for dp, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ALLOW]
        for f in files:
            p = os.path.join(dp, f)
            if f.endswith((".md",)):   # docs may contain placeholder examples
                continue
            try:
                txt = open(p, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            for pat in PATTERNS:
                m = pat.search(txt)
                if m:
                    hits.append(f"{os.path.relpath(p, root)}: {m.group(0)[:12]}...")
    if hits:
        print("SECRET-LIKE STRINGS FOUND:")
        for h in hits[:10]:
            print(" ", h)
        return 1
    print("no secrets detected")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))

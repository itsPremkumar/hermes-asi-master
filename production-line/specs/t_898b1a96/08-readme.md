[33m⚠ Deprecated .env settings detected:[0m
  [33m⚠[0m TERMINAL_CWD=C:\Users\<user> found in .env — this is deprecated.
  [2mMove to config.yaml instead:  terminal:\n    cwd: /your/project/path[0m
  [2mThen remove the old entries from ~/%HERMES_HOME%\profiles\technical-writer/.env[0m


session_id: 20260818_164209_189771
```markdown
# URL Shortener MVP

A lightweight Flask URL shortener that converts long URLs into compact, shareable links. Built for simplicity — no database, no external services, just a running Python process.

## What It Does

- Accepts a long URL and returns a short, unique slug
- Redirects visitors from the short URL to the original long URL
- Stores mappings in memory — zero setup, instant start
- Exposes a JSON API for programmatic shortening

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

The server starts on `http://127.0.0.1:5000`.

## Usage Example

Shorten a URL:

```bash
curl -X POST http://127.0.0.1:5000/shorten \
  -H "Content-Type: application/json" \

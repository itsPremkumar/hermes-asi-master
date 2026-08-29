[33m⚠ Deprecated .env settings detected:[0m
  [33m⚠[0m TERMINAL_CWD=C:\Users\<user> found in .env — this is deprecated.
  [2mMove to config.yaml instead:  terminal:\n    cwd: /your/project/path[0m
  [2mThen remove the old entries from ~/%HERMES_HOME%\profiles\qa-lead/.env[0m

# URL Shortener Test Plan

## 1. Overview

**Scope:** URL shortening service with REST API and redirect endpoint.

**Components:**
- `POST /api/shorten` — creates a short link from a long URL
- `GET /:code` — redirects to the original URL (301/302)
- `GET /api/:code/stats` — returns link metadata and click count
- `DELETE /api/:code` — invalidate/deletes a short link
- Background: code generation, persistence (DB), cache layer, expiration scheduler

**Assumptions:**
- Short code is 7 characters by default (base62)
- Default TTL is 30 days; links can be set to never expire
- Duplicate URLs return the existing short link
- Codes are case-sensitive

---

## 2. Unit Tests

### 2.1 Code Generation

| ID | Test | Expected |
|----|------|----------|
| U-01 | `generateCode()` called 1000× | All codes are 7 chars, base62 |
| U-02 | `generateCode()` for same URL | Produces deterministic or unique code depending on design; assert consistency with contract |
| U-03 | `generateCode()` uniqueness | No duplicates across 100k iterations (collision probability < 0.001%) |
| U-04 | `generateCode()` length config | Custom length param respected |
| U-05 | `normalizeUrl()` on valid URL | Scheme added if missing, trailing slash preserved/stripped consistently |

### 2.2 URL Validation


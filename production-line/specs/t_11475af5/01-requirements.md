[33m⚠ Deprecated .env settings detected:[0m
  [33m⚠[0m TERMINAL_CWD=C:\Users\<user> found in .env — this is deprecated.
  [2mMove to config.yaml instead:  terminal:\n    cwd: /your/project/path[0m
  [2mThen remove the old entries from ~/%HERMES_HOME%\profiles\product-owner/.env[0m


session_id: 20260818_163420_10c6e3
# URL Shortener MVP — Product Requirements

## 1. MVP Scope
- Shorten any valid long URL into a unique, shareable short link (e.g. `sho.rt/abc123`).
- Redirect short links to the original URL with a fast, reliable 301/302 response.
- Basic admin view to list created links and copy/delete them (no auth, single-user local use).

## 2. User Stories
- As a **user**, I want to paste a long URL and get a short link back, so that I can share it cleanly in messages and social posts.
- As a **user**, I want to click a short link and land on the exact original page, so that my audience reaches the right destination without friction.
- As a **user**, I want to see and delete the links I've created, so that I can manage clutter and remove outdated or mistaken entries.

## 3. Acceptance Criteria
1. Submitting a valid URL returns a short code (6–8 alphanumeric chars) and a full short URL within 2 seconds.
2. Visiting the short URL redirects (HTTP 301/302) to the original URL with no intermediate page.
3. Re-submitting an identical long URL returns the same short link (idempotent, no duplicate).
4. An invalid URL (malformed/missing scheme) is rejected with a clear error and no link is created.
5. The admin list shows all created short links with their destination, creation time, and a working delete action that removes the redirect.

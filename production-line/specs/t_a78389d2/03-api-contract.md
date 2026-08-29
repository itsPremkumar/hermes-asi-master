[33m⚠ Deprecated .env settings detected:[0m
  [33m⚠[0m TERMINAL_CWD=C:\Users\<user> found in .env — this is deprecated.
  [2mMove to config.yaml instead:  terminal:\n    cwd: /your/project/path[0m
  [2mThen remove the old entries from ~/%HERMES_HOME%\profiles\tech-lead/.env[0m


session_id: 20260818_163614_bae186
```markdown
# URL Shortener API

## POST /api/shorten

**Description:** Create a shortened URL from a long URL.

### Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string (uri) | Yes | The original long URL to be shortened |
| `custom_code` | string | No | Custom alias for the shortened URL (max 20 chars) |
| `expires_at` | string (date-time) | No | Expiration timestamp for the short URL |

#### Example

```json
{
  "url": "https://www.example.com/very/long/path/to/resource",
  "custom_code": "myalias",
  "expires_at": "2025-12-31T23:59:59Z"
}
```

### Response

**201 Created**

| Field | Type | Description |
|-------|------|-------------|
| `short_url` | string (uri) | The full shortened URL |
| `code` | string | The alias code |

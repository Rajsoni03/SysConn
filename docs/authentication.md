# Authentication

SysConn uses a **WSGI middleware** (`AuthMiddleware`) that intercepts every
request before Flask handles it. All enforcement happens in one place, keeping
route handlers free of auth logic.

---

## Token Setup

Set the `AUTH_TOKEN` via:
- Web UI at `http://localhost:5500`
- Direct edit of `data/config.json`
- `POST /set_config` with form field `AUTH_TOKEN`

If `AUTH_TOKEN` is an empty string, all authentication is **bypassed** (useful
during development on a trusted network).

---

## Path-Based Access Rules

| Path prefix | Rule |
|-------------|------|
| `/api/` | Always requires a valid `Authorization` header |
| `/update` | Always requires a valid `Authorization` header |
| `/set_config` | Localhost: always allowed. Remote: blocked if `AUTH_TOKEN` is set |
| `/` (home) | Localhost: always allowed. Remote: blocked if `AUTH_TOKEN` is set |
| `/docs` | Public — no auth |
| `/version` | Public — no auth |
| `/health` | Public — no auth |
| `/logs/<path>` | Public — no auth |

"Localhost" means the request `REMOTE_ADDR` is `127.0.0.1` or `::1`.

---

## Making Authenticated Requests

Pass the token in the `Authorization` header:

```bash
curl -X POST http://localhost:5500/api/v1/test/run \
  -H "Authorization: my-secret-token" \
  -H "Content-Type: application/json" \
  -d @test.json
```

There is no `Bearer` prefix — the header value is the raw token string.

---

## Error Responses

| Scenario | HTTP Status | Body |
|----------|-------------|------|
| Missing `Authorization` header on a secure path | 401 | `{"error": "Unauthorized"}` |
| Wrong token value | 401 | `{"error": "Unauthorized"}` |
| Remote access to a protected path (when token set) | 403 | `{"error": "Forbidden"}` |

---

## Implementation Details

`AuthMiddleware` is a standard WSGI callable:

```python
class AuthMiddleware:
    def __init__(self, app):
        self.app = app          # Flask WSGI app

    def __call__(self, environ, start_response):
        path  = environ.get("PATH_INFO", "")
        token = environ.get("HTTP_AUTHORIZATION", "")
        addr  = environ.get("REMOTE_ADDR", "")
        # ... path-rule evaluation ...
        return self.app(environ, start_response)
```

It is applied in `app.py` after the Flask app is created:

```python
app = Flask(__name__)
# ... register blueprints ...
app.wsgi_app = AuthMiddleware(app.wsgi_app)
```

---

## Security Recommendations

- Use a long, random `AUTH_TOKEN` (at least 32 characters).
- Do not expose port 5500 to the public internet — use a VPN or SSH tunnel.
- Use HTTPS (via a reverse proxy such as nginx) if traffic crosses untrusted networks.
- Rotate the `AUTH_TOKEN` if it may have been exposed; update `data/config.json`
  and restart the server.
- Leave `SUDO_PASSWORD` empty if no host commands require elevated privileges.

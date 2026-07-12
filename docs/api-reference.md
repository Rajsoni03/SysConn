# API Reference

Base URL: `http://<host>:5500`

All `/api/` endpoints require `Authorization: <token>` in the request header.
Public endpoints (`/health`, `/version`, `/docs`) need no auth.

---

## Common Endpoints

### GET /health

Health check. No authentication required.

**Response**
```json
{"status": "ok"}
```

---

### GET /version

Returns the application version. No authentication required.

**Response**
```json
{"version": "1.0.5"}
```

---

### GET /

Web UI home page. Returns the HTML configuration form.
- Accessible from localhost without auth.
- Requires `Authorization` header when accessed remotely (if token is set).

---

### POST /set_config

Set the `AUTH_TOKEN` and `SUDO_PASSWORD`. Persists to `data/config.json`.

**Request** (form data or JSON)
```
AUTH_TOKEN=<token>
SUDO_PASSWORD=<password>
```

**Response** — Redirects to `/`.

---

### GET /version

Returns tool version string.

---

### POST /update

Pulls the latest code from git and restarts the service.
Requires `Authorization` header.

**Response**
```json
{"status": "update started"}
```

---

### GET /logs/\<path\>

Stream or download a log file. `path` is relative to the `logs/` directory.
No authentication required.

**Example**
```
GET /logs/abc123/mpu0_uart.log
```

---

## V1 Endpoints

### POST /api/v1/command

Execute a shell command on the host system.

**Request**
```json
{
  "command": "ls -la /opt/",
  "cwd": "/home/user",
  "env": {
    "MY_VAR": "value"
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| command | yes | Shell command to run |
| cwd | no | Working directory (default: project root) |
| env | no | Additional environment variables |

**Response**
```json
{
  "stdout": "total 48\ndrwxr-xr-x ...",
  "stderr": "",
  "return_code": 0,
  "status": true
}
```

---

### POST /api/v1/workarea

Create an isolated work directory for a test or build.

**Request**
```json
{
  "name": "my-test-build"
}
```

**Response**
```json
{
  "path": "/absolute/path/to/workarea/my-test-build",
  "status": true
}
```

---

### GET /api/v1/uart/list

List all UART/TTY devices currently connected to the host.

**Response**
```json
{
  "devices": [
    {
      "devnode": "/dev/ttyUSB0",
      "serial": "FT5X2ABC",
      "vendor_id": "0403",
      "product_id": "6011",
      "manufacturer": "FTDI",
      "product": "FT4232H"
    }
  ],
  "status": true
}
```

---

### POST /api/v1/test/run

Submit a test for execution. The test runs asynchronously in a background thread.

**Request**
```json
{
  "jira_id": "ADASVISION-1001",
  "test_app_name": "vx_app_tutorial",
  "description": "Run vision app tutorial",
  "device_name": "j721s2-evm",
  "device_id": "#001",
  "core": "a72",
  "os": ["linux"],
  "boot_mode": "mmcsd",
  "platform": ["j721s2_evm"],
  "iteration": "1",
  "timeout": 300,
  "test_flow": "command_line",
  "test_steps": [...]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| device_name | yes | Device type (matches config file name, e.g. `j721s2-evm`) |
| device_id | yes | Instance identifier (e.g. `#001`) |
| test_flow | yes | Name of test flow to use (e.g. `command_line`) |
| test_steps | yes | Array of step objects — see [Test Flows](test-flows.md) |
| jira_id | no | Jira ticket reference |
| timeout | no | Global timeout in seconds |

**Response**
```json
{
  "id": "a1b2c3d4e5f6...",
  "test_status": true,
  "polling_url": "http://hostname:5500/api/v1/test/status/a1b2c3d4e5f6",
  "websocket_url": "ws://hostname:5500/ws/logs/a1b2c3d4e5f6",
  "logs": [
    "http://hostname:5500/logs/a1b2c3d4e5f6/mpu0_uart.log"
  ],
  "status": true
}
```

---

### GET /api/v1/test/status/\<test_id\>

Poll the status of a running or completed test.

**Response — running**
```json
{
  "id": "a1b2c3d4e5f6",
  "status": "running",
  "logs": ["http://hostname:5500/logs/a1b2c3d4e5f6/mpu0_uart.log"]
}
```

**Response — completed**
```json
{
  "id": "a1b2c3d4e5f6",
  "status": "completed",
  "result": "pass",
  "logs": ["http://hostname:5500/logs/a1b2c3d4e5f6/mpu0_uart.log"]
}
```

**Response — failed**
```json
{
  "id": "a1b2c3d4e5f6",
  "status": "failed",
  "error": "Timeout waiting for 'login:' on mpu0",
  "logs": ["http://hostname:5500/logs/a1b2c3d4e5f6/mpu0_uart.log"]
}
```

**Test status values**

| Status | Meaning |
|--------|---------|
| `initialized` | Record created, thread not started yet |
| `running` | Test flow is executing |
| `completed` | Test finished and passed |
| `failed` | Test finished with an error |

---

## Error Responses

| Code | Meaning |
|------|---------|
| 400 | Bad request — missing or invalid fields |
| 401 | Unauthorized — missing or invalid `Authorization` header |
| 403 | Forbidden — remote access to a protected path |
| 404 | Not found — unknown endpoint or test ID |
| 500 | Internal server error |

All error responses follow this shape:
```json
{
  "error": "Description of the problem",
  "status": false
}
```

---

## Authentication

Include the token in every `/api/` request:

```bash
curl -X POST http://localhost:5500/api/v1/test/run \
  -H "Authorization: my-secret-token" \
  -H "Content-Type: application/json" \
  -d @test.json
```

See [Authentication](authentication.md) for the full access-control matrix.

---

## WebSocket

Live UART logs can be streamed over WebSocket:

```
ws://<host>:5500/ws/logs/<test_id>
```

The connection emits newline-delimited log lines from all UART ports as they arrive.
The `websocket_url` field in the `/api/v1/test/run` response contains the ready-to-use
URL.

# Architecture

## Overview

SysConn is structured as a layered Flask application. Incoming HTTP requests pass
through authentication middleware, reach REST resource handlers, which delegate to
service classes, which in turn drive hardware modules.

```
┌─────────────────────────────────────────────────────────────────┐
│                         HTTP Client                             │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│               AuthMiddleware  (WSGI layer)                      │
│  • Validates Authorization header for /api/, /update            │
│  • Allows localhost bypass for /set_config, /                   │
│  • Passes /docs, /version, /health unrestricted                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│              Flask-RESTful Resources  (api/)                    │
│  common/: Home, Config, Version, Health, Logs, Update           │
│  v1/:     Command, Workarea, UARTList, RunTest, TestStatus      │
└──────┬─────────────────┬──────────────────────┬─────────────────┘
       │                 │                      │
┌──────▼──────┐  ┌───────▼───────┐   ┌──────────▼──────────┐
│  Command    │  │  Workarea     │   │  TestExecutor       │
│  Service    │  │  Service      │   │  Service            │
└──────┬──────┘  └───────┬───────┘   └──────────┬──────────┘
       │                 │                      │
       │            filesystem             ┌────▼──────┐
  subprocess                               │ Test Flow │
                                           │  (thread) │
                                           └────┬──────┘
                               ┌────────────────┼─────────────┐
                          ┌────▼───┐       ┌────▼───┐    ┌────▼───┐
                          │ UART   │       │ Relay  │    │ DUT    │
                          │ Module │       │ Module │    │ Config │
                          └────────┘       └────────┘    └────────┘
```

---

## Request Flow

### Standard API request

1. WSGI receives the HTTP request.
2. `AuthMiddleware` checks path rules and validates the `Authorization` header.
3. Flask-RESTful routes the request to the matching `Resource` class.
4. The resource calls the appropriate service method.
5. The service returns a result; the resource serialises it as JSON.

### Test execution request

1. `POST /api/v1/test/run` reaches `TestExecutorService`.
2. The service validates the payload (device name, test flow, steps).
3. A TinyDB record is created with status `initialized`.
4. A daemon thread is spawned; status advances to `running`.
5. The thread instantiates the named `TestFlow` class and calls:
   - `setup()` — open UART ports, initialise relay
   - `validate()` — check required fields
   - `execute()` — iterate test steps
6. Each step handler calls the relevant hardware module (UART/Relay/DUT).
7. On completion or failure, TinyDB record is updated to `completed` / `failed`.
8. The client polls `GET /api/v1/test/status/<id>` until a terminal state.

---

## Key Design Patterns

### Singleton
`ConfigLoader` and both DB clients use a `Singleton` metaclass to guarantee a single
instance across all threads. The DB client also holds a `threading.Lock` for safe
concurrent access.

### Factory
`RelayFactory.create(config)` inspects the `module` field in a device's power config
and returns either a `SerialRelay` or `IpRelay` instance. Callers never reference
concrete relay classes.

### Abstract Base Class
`IBaseFlow` defines the contract for test flows:

```python
class IBaseFlow(ABC):
    @abstractmethod
    def setup(self, test_data: dict) -> None: ...
    @abstractmethod
    def validate(self, test_data: dict) -> bool: ...
    @abstractmethod
    def execute(self, test_data: dict) -> dict: ...
    @abstractmethod
    def teardown(self) -> None: ...
```

All test flows extend this class. New flows are registered in `flow_list.py`.

### Plugin / Decorator
`BasePlugin` provides lifecycle hooks (`before_test`, `after_test`, `on_error`) that
wrap test execution. Plugins are discovered and chained by the `PluginEngine`.

### WSGI Middleware
`AuthMiddleware` wraps the Flask WSGI app object, intercepting every request before
Flask sees it. This keeps auth logic completely separate from route handlers.

---

## Component Map

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Entry point | `app.py` | Create Flask app, register blueprints, wrap middleware |
| API handlers | `api/common/`, `api/v1/` | Parse request, call service, return JSON |
| Services | `src/services/` | Business logic, orchestration |
| Hardware modules | `src/modules/` | Direct hardware communication |
| Test flows | `test_flow/` | Step-by-step test execution strategies |
| Plugins | `src/plugins/` | Cross-cutting hooks around test lifecycle |
| App core | `src/app/` | Auth, config, DB, route registration |
| Utilities | `src/utils/` | Shared helpers (singleton, exceptions, IP) |
| Config | `config/` | App settings and device JSON files |
| Data | `data/` | Runtime config and TinyDB databases |

---

## Database

SysConn uses **TinyDB** (a lightweight JSON-based database) with no external server.

| Table | File | Purpose |
|-------|------|---------|
| test_execution | `data/db/test_execution_db.json` | Test run records and status |

A `JsonDB` fallback implementation (plain JSON file) is also available and used in
some contexts. Both share the same interface via the `DB` base class.

---

## Logging

| Log | Path | Content |
|-----|------|---------|
| Access log | `logs/access.log` | Gunicorn HTTP access log |
| Error log | `logs/error.log` | Gunicorn / app error log |
| Test UART log | `logs/<test_id>/<port>_uart.log` | Per-port serial output for each test |

Log files are exposed as static files via `GET /logs/<path>` and also streamable
over WebSocket at `ws://<host>:5500/ws/logs/<test_id>`.

---

## Threading Model

- The Flask/Gunicorn worker is single-process with an **eventlet** greenlet pool.
- Each test run executes in a **daemon thread** spawned by `TestExecutorService`.
- TinyDB and `JsonDB` operations are protected by a `threading.Lock`.
- UART communication uses `pexpect` (which wraps a subprocess pty) — one thread per
  open UART port is the expected pattern inside a test flow.

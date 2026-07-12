# SysConn — Documentation

**SysConn** (System Connection) is a Flask-based REST API server for embedded systems
testing and hardware device management. It connects to physical devices, orchestrates
automated test flows, controls power relays, and streams live UART logs.

---

## Table of Contents

| Document | Description |
|----------|-------------|
| [Architecture](architecture.md) | System design, request flow, component map |
| [API Reference](api-reference.md) | All REST endpoints with examples |
| [Configuration](configuration.md) | App settings and device configuration |
| [Test Flows](test-flows.md) | Test JSON format and all step types |
| [Hardware Modules](hardware-modules.md) | DUT, UART, Relay module details |
| [Authentication](authentication.md) | Token auth, path rules, middleware |
| [Plugins](plugins.md) | Plugin system and lifecycle hooks |

---

## Quick Start

### 1. Clone and start

```bash
git clone https://github.com/Rajsoni03/SysConn.git
cd SysConn
./start_server.sh
```

The server starts on **http://0.0.0.0:5500** using Gunicorn + eventlet.

### 2. Open the firewall port (Linux)

```bash
sudo iptables -A INPUT -p tcp --dport 5500 -j ACCEPT
```

### 3. Set credentials

Open [http://localhost:5500](http://localhost:5500) in a browser and set:
- **AUTH_TOKEN** — required header value for all API calls
- **SUDO_PASSWORD** — used for privileged host commands

### 4. Verify the server

```bash
curl http://localhost:5500/health
```

```json
{"status": "ok"}
```

### 5. Run a test

```bash
curl -X POST http://localhost:5500/api/v1/test/run \
  -H "Authorization: YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d @test_flow/samples/simple_boot_test.json
```

Poll for results:

```bash
curl http://localhost:5500/api/v1/test/status/<test_id> \
  -H "Authorization: YOUR_AUTH_TOKEN"
```

---

## Features

- REST API with token-based authentication
- Execute shell commands on the host system
- UART communication with embedded devices
- Power relay control (serial or IP-based)
- Automated multi-step test flows
- Simultaneous multi-UART monitoring
- Real-time log streaming (WebSocket + polling)
- Device-specific configuration management
- Docker-based SDK build automation
- Self-update via git pull + service restart
- Plugin system for extensibility

---

## Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| Git | any |
| Docker | optional, for SDK builds |
| lsof | for port conflict detection |

Key Python packages: `Flask`, `Flask-SocketIO`, `pyserial`, `pexpect`, `tinydb`,
`gunicorn`, `eventlet`, `pyudev`, `docker`.

See `requirements.txt` for pinned versions.

---

## Project Structure

```
SysConn/
├── app.py                    # Flask entry point
├── start_server.sh           # Start script (venv + gunicorn)
├── requirements.txt
├── api/
│   ├── common/               # Home, Config, Version, Health, Logs, Update
│   └── v1/                   # Command, Workarea, UART, Test endpoints
├── config/
│   ├── settings.py           # App-wide constants
│   └── devices/              # Per-device JSON configs
├── data/
│   ├── config.json           # Runtime config (tokens, passwords)
│   └── db/                   # TinyDB JSON files
├── docs/                     # This documentation
├── logs/                     # App and test log files
├── src/
│   ├── app/                  # Auth, config loader, DB client, routes
│   ├── core/                 # Plugin engine, session manager
│   ├── modules/              # DUT, UART, Relay hardware drivers
│   ├── plugins/              # Plugin base classes and implementations
│   ├── services/             # Business logic services
│   └── utils/                # Exceptions, IP utils, singleton helper
├── templates/                # Jinja2 HTML templates (web UI)
└── test_flow/
    ├── base_flow.py          # Abstract test flow base class
    ├── command_line.py       # Default test flow implementation
    ├── flow_list.py          # Registry of available flows
    └── samples/              # Example test JSON files
```

---

## Version

Current version: **1.0.5**

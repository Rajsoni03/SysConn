# Configuration

SysConn has two layers of configuration:

1. **Application settings** — compile-time constants in `config/settings.py`
2. **Runtime config** — token and password stored in `data/config.json`
3. **Device config** — per-device hardware maps in `config/devices/`

---

## Application Settings (`config/settings.py`)

| Setting | Default | Description |
|---------|---------|-------------|
| `TOOL_VERSION` | `"1.0.5"` | Reported by `/version` |
| `PORT` | `5500` | TCP port the server listens on |
| `HOSTNAME` | system hostname + DHCP domain | Used to build `polling_url` in test responses |
| `API_VERSIONS` | `["common", "v1"]` | Blueprint namespaces to register |
| `LOGS_DIR` | `"./logs/"` | Root directory for all log files |
| `WORKAREA_DIR` | `"./workarea/"` | Root directory for work area directories |
| `DB_PATH_ROOT` | `"./data/db/"` | Root directory for TinyDB files |

These values are imported throughout the app via:

```python
from config.settings import PORT, LOGS_DIR, ...
```

---

## Runtime Config (`data/config.json`)

Managed by `ConfigLoader` (singleton). Written on every save.

```json
{
  "AUTH_TOKEN": "your-secret-token",
  "SUDO_PASSWORD": "your-sudo-password"
}
```

### Setting values

**Via web UI** — open `http://localhost:5500`, fill in the form, click Save.

**Via file** — edit `data/config.json` directly, then restart the server.

**Via API** — `POST /set_config` with form fields `AUTH_TOKEN` and `SUDO_PASSWORD`.

> If `AUTH_TOKEN` is empty string, all auth checks are bypassed (development mode).

---

## Device Configuration (`config/devices/`)

Each file describes one physical device instance. The filename pattern is:

```
<device_type>-<instance_id>.json
```

Example: `config/devices/j721s2-evm-#001.json`

### Full Schema

```json
{
  "device_name": "j721s2-evm-#001",
  "device_type": "j721s2-evm",

  "uart_port_map": {
    "mpu0":        "/dev/ttyUSB0",
    "mcu0":        "/dev/ttyUSB4",
    "application": "/dev/ttyUSB0"
  },

  "boot_mode_map": {
    "uart":    "000E",
    "emmc":    "000D",
    "sd_card": "000C",
    "ospi":    "000B"
  },

  "health_check": {
    "uart_ports":              ["mpu0", "mcu0"],
    "check_interval_seconds":  60,
    "error_threshold":         5
  },

  "power_config": {
    "module": "relay",
    "settings": {
      "ip_address":    "10.24.50.173",
      "username":      "admin",
      "password":      "1234",
      "outlet_number": 1
    }
  }
}
```

### Fields

#### `uart_port_map`

Maps logical port names to OS device nodes. Logical names are used in test step
`uart_port` and `log_port` fields so tests are portable across machines.

| Logical name | Typical hardware |
|--------------|-----------------|
| `mpu0` | Application Processor core 0 |
| `mpu1` | Application Processor core 1 |
| `mcu0` | MCU safety island core 0 |
| `mcu1` | MCU safety island core 1 |
| `application` | Alias for the primary app processor port |
| `sbl` | Secondary Boot Loader port |
| `debug` | XDS110 debug port |

#### `boot_mode_map`

Maps boot mode names to hardware switch codes. Used by the `boot_mode` test step.

| Key | Typical switch code |
|-----|---------------------|
| `uart` | 000E |
| `mmcsd` | 000D |
| `ospi` | 000B |
| `usb` | 000A |

#### `health_check`

Defines background monitoring for UART ports.

| Field | Description |
|-------|-------------|
| `uart_ports` | Ports to monitor for errors |
| `check_interval_seconds` | How often to poll (seconds) |
| `error_threshold` | Number of errors before reporting unhealthy |

#### `power_config`

Configures the power relay for this device.

`module` may be `"relay"`. The `settings` object is passed to `RelayFactory.create()`.

**IP relay settings**

| Field | Description |
|-------|-------------|
| `ip_address` | Relay management IP |
| `username` | HTTP digest auth username |
| `password` | HTTP digest auth password |
| `outlet_number` | Outlet index (1-based) |

**Serial relay settings**

| Field | Description |
|-------|-------------|
| `port` | Serial device node (e.g. `/dev/ttyUSB8`) |
| `baud_rate` | Baud rate (default: 9600) |
| `relay_number` | Relay channel index (1–8) |

---

## Loading a Device Config in Code

```python
from src.modules.dut import DUTConfig

dut = DUTConfig(device_name="j721s2-evm", device_id="#001")
uart_path = dut.get_uart_port("mpu0")    # "/dev/ttyUSB0"
boot_code = dut.get_boot_mode("uart")    # "000E"
power_cfg  = dut.get_power_config()      # dict with relay settings
```

---

## Stable UART Device Naming (udev)

By default Linux assigns `/dev/ttyUSBn` dynamically at boot. To assign stable names
based on serial numbers, use the UART list endpoint to discover serial numbers:

```bash
curl http://localhost:5500/api/v1/uart/list \
  -H "Authorization: YOUR_TOKEN"
```

Then create a udev rule (managed by `UARTService`):

```
SUBSYSTEM=="tty", ATTRS{serial}=="FT5X2ABC", SYMLINK+="j721s2_mpu0"
```

Update `uart_port_map` in the device config to use the symlink path:

```json
"uart_port_map": {
  "mpu0": "/dev/j721s2_mpu0"
}
```

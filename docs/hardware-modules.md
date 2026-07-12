# Hardware Modules

SysConn communicates with physical hardware through three modules:
**DUTConfig**, **UART**, and **Relay**.

---

## DUTConfig (`src/modules/dut.py`)

Loads and exposes the device-specific JSON configuration file.
It is the single source of truth for port mappings, boot mode codes,
and relay settings for a given device instance.

### Usage

```python
from src.modules.dut import DUTConfig

dut = DUTConfig(device_name="j721s2-evm", device_id="#001")
```

This reads `config/devices/j721s2-evm-#001.json`.

### Key Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_uart_port(name)` | `str` | OS path for a logical port name (e.g. `"mpu0"` → `"/dev/ttyUSB0"`) |
| `get_boot_mode(name)` | `str` | Switch code for a boot mode name (e.g. `"uart"` → `"000E"`) |
| `get_power_config()` | `dict` | Power relay settings dict |
| `get_health_config()` | `dict` | Health check configuration |

### Config File Location

```
config/devices/<device_name>-<device_id>.json
```

See [Configuration](configuration.md) for the full schema.

---

## UART (`src/modules/uart.py`)

Manages serial port connections to the target device using **pexpect**.
Each `UART` instance represents one open serial port.

### Usage

```python
from src.modules.uart import UART

uart = UART(
    port="/dev/ttyUSB0",
    baud_rate=115200,
    log_file="logs/test_abc/mpu0_uart.log"
)
uart.open()

# Send a command and wait for expected output
result = uart.send_command(
    command="ls /opt/",
    expected_output="vision_apps",
    timeout=30
)

uart.close()
```

### Constructor Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `port` | yes | — | OS device node (e.g. `/dev/ttyUSB0`) |
| `baud_rate` | no | `115200` | Serial baud rate |
| `log_file` | no | `None` | Path to write all serial output |

### Key Methods

| Method | Description |
|--------|-------------|
| `open()` | Open the serial port and start logging |
| `close()` | Close the port and flush logs |
| `send_command(command, expected_output, timeout, enter_new_line)` | Send a string and wait for expected output |
| `wait_for(expected_output, timeout)` | Wait without sending a command |
| `send_file(file_path, timeout)` | Send a binary file (for image flashing) |

### Retry Logic

`send_command` accepts a `retry_count` parameter. On failure or timeout it
re-sends the command up to `retry_count` additional times before raising.

### Logging

All characters received from the serial port are appended to `log_file`.
The test executor passes each port's log path back in the API response so
clients can stream it via `GET /logs/<test_id>/<port>_uart.log`.

---

## Relay (`src/modules/relay.py`)

Provides power control (on/off/reset) for the device under test.
Two concrete implementations are available; callers use `RelayFactory`
and never reference the concrete classes directly.

### RelayFactory

```python
from src.modules.relay import RelayFactory

relay = RelayFactory.create(power_config)
relay.on()
relay.off()
relay.reset()
relay.power_on_reset()
```

`power_config` is the dict from `DUTConfig.get_power_config()`. The factory
inspects `power_config["module"]` to decide which class to instantiate.

### Operations

| Method | Description |
|--------|-------------|
| `on()` | Power on the outlet |
| `off()` | Power off the outlet |
| `reset()` | Power off then on |
| `toggle()` | Toggle current state |
| `power_on_reset()` | Send a POR pulse |

---

### IpRelay

Controls a network-managed PDU (Power Distribution Unit) via HTTP.

**Config fields**

```json
{
  "module":        "relay",
  "settings": {
    "ip_address":    "10.24.50.173",
    "username":      "admin",
    "password":      "1234",
    "outlet_number": 1
  }
}
```

Uses HTTP Digest authentication. Outlet numbers are 1-based.

---

### SerialRelay

Controls a USB relay board over a serial port. Supports up to 8 channels.

**Config fields**

```json
{
  "module":    "relay",
  "settings": {
    "port":         "/dev/ttyUSB8",
    "baud_rate":    9600,
    "relay_number": 1
  }
}
```

---

## UART Device Enumeration (`src/services/uart_service.py`)

Before configuring device files, use `UARTService` to discover which serial
devices are connected and their stable identifiers.

### API

```
GET /api/v1/uart/list
Authorization: <token>
```

**Response**
```json
{
  "devices": [
    {
      "devnode":      "/dev/ttyUSB0",
      "serial":       "FT5X2ABC",
      "vendor_id":    "0403",
      "product_id":   "6011",
      "manufacturer": "FTDI",
      "product":      "FT4232H"
    }
  ]
}
```

### Stable Device Naming

Dynamic kernel naming (`/dev/ttyUSBn`) changes between reboots.
Use the serial number to create a persistent udev symlink:

```
# /etc/udev/rules.d/99-sysconn.rules
SUBSYSTEM=="tty", ATTRS{serial}=="FT5X2ABC", SYMLINK+="j721s2_mpu0"
```

Then reference `/dev/j721s2_mpu0` in the device config `uart_port_map`.

---

## Hardware Interaction Sequence

A typical power cycle + boot + command sequence:

```
Test Flow
  │
  ├─ power_control "reset"
  │     └─ Relay.off() → wait post_delay → Relay.on()
  │
  ├─ boot_mode "uart"
  │     └─ DUTConfig.get_boot_mode("uart") → "000E"
  │        (write switch code to boot mode hardware)
  │
  ├─ uart_image_flashing
  │     ├─ UART.send_file("/path/to/sbl_uart.tiimage", port="mcu0")
  │     └─ UART.wait_for("Waiting for tifs.bin", port="mcu0")
  │
  └─ uart_command
        ├─ UART.send_command("ls /opt/", port="mpu0")
        └─ UART.wait_for("vision_apps", port="mpu0")
```

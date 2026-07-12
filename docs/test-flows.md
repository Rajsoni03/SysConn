# Test Flows

A **test flow** is an ordered sequence of steps that exercises a hardware device.
Steps are submitted as JSON to `POST /api/v1/test/run` and executed by the chosen
flow implementation.

---

## Test Request Envelope

```json
{
  "jira_id":       "ADASVISION-1001",
  "test_app_name": "vx_app_tutorial",
  "description":   "Run vision app tutorial end-to-end",
  "device_name":   "j721s2-evm",
  "device_id":     "#001",
  "core":          "a72",
  "os":            ["linux"],
  "boot_mode":     "mmcsd",
  "platform":      ["j721s2_evm"],
  "iteration":     "1",
  "timeout":       300,
  "test_flow":     "command_line",
  "test_steps":    [ ... ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `device_name` | yes | Device type; matches `config/devices/<name>-<id>.json` |
| `device_id` | yes | Device instance (e.g. `#001`) |
| `test_flow` | yes | Flow name from the registry (`command_line`, …) |
| `test_steps` | yes | Array of step objects (see below) |
| `timeout` | no | Global timeout in seconds for the whole test |

---

## Available Test Flows

| Name | Class | Description |
|------|-------|-------------|
| `command_line` | `CommandLineFlow` | Default general-purpose flow; handles all step types |

Register additional flows in `test_flow/flow_list.py`.

---

## Step Types

### `power_control`

Changes device power state via the configured relay.

```json
{
  "type":        "power_control",
  "power_state": "reset",
  "pre_delay":   0,
  "post_delay":  2
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `power_state` | yes | One of `reset`, `on`, `off`, `por` |
| `pre_delay` | no | Seconds to wait before the state change (default: 0) |
| `post_delay` | no | Seconds to wait after the state change (default: 0) |

**Power states**

| State | Behaviour |
|-------|-----------|
| `reset` | Power off then power on |
| `on` | Power on (no-op if already on) |
| `off` | Power off |
| `por` | Power-on reset pulse |

---

### `boot_mode`

Sets the hardware boot mode switch before powering on.

```json
{
  "type":           "boot_mode",
  "boot_mode_name": "uart",
  "pre_delay":      0,
  "post_delay":     1
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `boot_mode_name` | yes | Key from the device's `boot_mode_map` (e.g. `uart`, `mmcsd`) |
| `pre_delay` | no | Seconds before switching (default: 0) |
| `post_delay` | no | Seconds after switching (default: 0) |

---

### `delay`

Pause test execution for a fixed duration.

```json
{
  "type":             "delay",
  "delay_in_seconds": 5
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `delay_in_seconds` | yes | Number of seconds to wait |

---

### `uart_command`

Send a command string to a UART port and optionally wait for expected output.

```json
{
  "type": "uart_command",
  "command_info": {
    "command":        "ls /opt/vision_apps/",
    "uart_port":      "mpu0",
    "enter_new_line": true
  },
  "constraint": {
    "expected_output": "vx_app_tutorial.out",
    "log_port":        "mpu0",
    "error_patterns":  ["Error", "Failed"],
    "timeout":         30
  },
  "retry_count": 1
}
```

**`command_info`**

| Field | Required | Description |
|-------|----------|-------------|
| `command` | yes | String to send over UART. Supports `{placeholder}` substitution |
| `uart_port` | yes | Logical port name from `uart_port_map` |
| `enter_new_line` | no | Append `\n` after command (default: `true`) |

**`constraint`**

| Field | Required | Description |
|-------|----------|-------------|
| `expected_output` | no | String to wait for in log output |
| `log_port` | no | Port to monitor for the expected output |
| `error_patterns` | no | List of strings; if found, step fails immediately |
| `timeout` | no | Seconds to wait before timing out |
| `return_code` | no | Expected process exit code |

**`retry_count`** — number of retries if the step fails (default: 0).

**Logical UART port names**

| Name | Hardware |
|------|----------|
| `mpu0` | Application Processor 0 |
| `mpu1` | Application Processor 1 |
| `mcu0` | MCU Safety Island 0 |
| `mcu1` | MCU Safety Island 1 |
| `application` | Primary app processor alias |
| `sbl` | Secondary Boot Loader port |
| `debug` | XDS110 debug UART |

---

### `uart_image_flashing`

Flash a binary image to the device over UART, then monitor a log port for
a success/failure string.

```json
{
  "type": "uart_image_flashing",
  "image_info": {
    "image_path":    "pdk*/packages/ti/boot/sbl/binary/{platform}/uart/bin/sbl_uart.tiimage",
    "flashing_port": "mcu0",
    "timeout":       60
  },
  "constraint": {
    "expected_output": "Waiting for tifs.bin",
    "log_port":        "mcu0",
    "timeout":         60
  }
}
```

**`image_info`**

| Field | Required | Description |
|-------|----------|-------------|
| `image_path` | yes | Path to binary. Supports glob (`*`) and `{placeholder}` |
| `flashing_port` | yes | UART port used to send the binary |
| `timeout` | yes | Seconds before the flash is declared failed |

**`constraint`**

| Field | Required | Description |
|-------|----------|-------------|
| `expected_output` | yes | String indicating successful flash |
| `log_port` | yes | Port to monitor for the expected string |
| `timeout` | yes | Seconds to wait for the expected string |

---

### `host_command`

Execute a shell command on the host machine (not on the device).

```json
{
  "type": "host_command",
  "command_info": {
    "command": "scp build/app.out user@board:/opt/",
    "cwd":     "/workspace/sdk"
  },
  "env": {
    "SDK_ROOT": "/workspace/sdk"
  },
  "constraint": {
    "expected_output": "100%",
    "return_code":     0,
    "error_patterns":  ["Permission denied", "No such file"],
    "timeout":         120
  },
  "retry_count": 0
}
```

**`command_info`**

| Field | Required | Description |
|-------|----------|-------------|
| `command` | yes | Shell command string. Supports `{placeholder}` |
| `cwd` | no | Working directory for the command |

**`env`** — key-value pairs merged into the subprocess environment.

**`constraint`** — same fields as `uart_command` constraint.

---

### `loop`

Repeat a block N times, substituting different values each iteration.

```json
{
  "type":       "loop",
  "loop_count": 3,
  "block": {
    "type": "uart_command",
    "command_info": {
      "command":   "{cmd}",
      "uart_port": "mpu0"
    },
    "constraint": {
      "expected_output": "{expected}",
      "log_port":        "mpu0",
      "timeout":         30
    }
  },
  "values": {
    "cmd":      ["echo hello", "echo world", "uname -r"],
    "expected": ["hello",      "world",      "Linux"   ]
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `loop_count` | yes | Number of iterations |
| `block` | yes | Any step type — placeholders are replaced each iteration |
| `values` | yes | Dict mapping placeholder name → list of values (one per iteration) |

Each `{key}` placeholder in `block` is replaced with `values[key][i]` on iteration `i`.

---

## Placeholder Substitution

The `{placeholder}` syntax is supported in:
- `command_info.command`
- `constraint.expected_output`
- `image_info.image_path`
- `enter_new_line` (boolean value)

Placeholder values come from either:
- The `loop` step's `values` dict
- Top-level test envelope fields (e.g. `{platform}`, `{test_app_name}`)

---

## Complete Example

```json
{
  "jira_id":     "ADASVISION-2333",
  "device_name": "j721s2-evm",
  "device_id":   "#001",
  "test_flow":   "command_line",
  "timeout":     600,
  "test_steps": [
    {
      "type":        "power_control",
      "power_state": "reset"
    },
    {
      "type":           "boot_mode",
      "boot_mode_name": "uart"
    },
    {
      "type":             "delay",
      "delay_in_seconds": 2
    },
    {
      "type": "uart_image_flashing",
      "image_info": {
        "image_path":    "pdk*/sbl/binary/j721s2/uart/bin/sbl_uart.tiimage",
        "flashing_port": "mcu0",
        "timeout":       60
      },
      "constraint": {
        "expected_output": "Waiting for tifs.bin",
        "log_port":        "mcu0",
        "timeout":         60
      }
    },
    {
      "type": "uart_command",
      "command_info": {
        "command":   "cd /opt/vision_apps && ./vx_app_tutorial.out",
        "uart_port": "mpu0"
      },
      "constraint": {
        "expected_output": "APP: Deinit ... Done !!!",
        "log_port":        "mpu0",
        "error_patterns":  ["error", "failed", "ABORT"],
        "timeout":         2500
      }
    },
    {
      "type":        "power_control",
      "power_state": "off"
    }
  ]
}
```

---

## Adding a Custom Test Flow

1. Create `test_flow/my_flow.py` extending `IBaseFlow`:

```python
from test_flow.base_flow import IBaseFlow

class MyFlow(IBaseFlow):
    def setup(self, test_data: dict) -> None:
        ...
    def validate(self, test_data: dict) -> bool:
        ...
    def execute(self, test_data: dict) -> dict:
        ...
    def teardown(self) -> None:
        ...
```

2. Register it in `test_flow/flow_list.py`:

```python
from test_flow.my_flow import MyFlow

FLOW_MAP = {
    "command_line": CommandLineFlow,
    "my_flow":      MyFlow,          # add this
}
```

3. Use `"test_flow": "my_flow"` in test requests.

# Test Request Samples

This directory contains sample test request JSON files demonstrating various test scenarios.

## Sample Files

### 1. simple_boot_test.json
**Purpose:** Basic boot test with power cycle and simple UART commands

**Features:**
- Power reset with delay
- Wait for login prompt
- Execute basic Linux commands (uname)
- Clean shutdown

**Use Case:** Verify basic boot functionality and UART communication

---

### 2. loop_test.json
**Purpose:** Demonstrate loop functionality with multiple commands

**Features:**
- Power on with boot delay
- Loop through multiple commands (ls, pwd, date)
- Placeholder replacement in commands and expected outputs
- Graceful shutdown

**Use Case:** Test repeated command execution with different parameters

---

### 3. uart_boot_test.json
**Purpose:** UART boot mode with image flashing

**Features:**
- Boot mode switching to UART
- Multiple image flashing steps (SBL, TIFS, Application)
- Sequential boot loader stages
- Constraint validation for each flashing step

**Use Case:** Bare-metal application testing via UART boot

---

### 4. host_and_dut_test.json
**Purpose:** Combined host and DUT operations

**Features:**
- Host filesystem checks
- SD card boot mode
- Network setup on DUT
- File transfer from host to DUT (SCP)
- Execute transferred application
- Error pattern detection
- Retry mechanisms

**Use Case:** Integration testing requiring host-DUT interaction

---

### 5. multi_uart_test.json
**Purpose:** Multi-core testing with multiple UART ports

**Features:**
- Communication with multiple UART ports (application, mcu1, mcu2)
- Multi-core application launch
- Verification of different core outputs
- Coordinated multi-UART monitoring

**Use Case:** Heterogeneous multi-core application testing

---

### 6. stress_test.json
**Purpose:** Stress testing with repeated operations

**Features:**
- Multiple power cycles (5 iterations)
- Loop through 10 different system info commands
- CPU stress testing with stress-ng
- Retry count for critical commands
- Host command integration
- Error pattern checking

**Use Case:** System stability and reliability testing

---

## Usage

### Python API Usage
```python
from test_flow.command_line import CommandLineTestFlow
import json

# Load test request
with open('test_flow/samples/simple_boot_test.json') as f:
    test_data = json.load(f)

# Create and run test flow
flow = CommandLineTestFlow()
shared_data = {}
db = None  # Your database connection

flow.setup(test_data, shared_data, db)
if flow.validate():
    success = flow.execute()
    print(f"Test {'passed' if success else 'failed'}")
```

### Command Line Usage (if CLI exists)
```bash
# Run a specific test
python run_test.py --test-file test_flow/samples/simple_boot_test.json

# Run with specific device
python run_test.py --test-file test_flow/samples/loop_test.json \
                   --device-name j721s2-evm --device-id "#001"
```

## Customization

### Modifying for Your Device

1. Update device information:
   ```json
   {
     "device_name": "your-device-type",
     "device_id": "#YYY"
   }
   ```

2. Adjust UART ports based on your device config:
   ```json
   {
     "uart_port": "mpu0"
   }
   ```
   Available ports: mcu1, mcu2, application, debug, etc.

3. Update boot modes:
   ```json
   {
     "boot_mode_name": "emmc"
   }
   ```
   Available modes: uart, mmcsd, sd_card, usb, network

4. Modify power settings (automatically loaded from device config):
   - No changes needed in test JSON
   - Configure in `config/devices/your-device-name-#YYY.json`

### Common Patterns

#### Wait for Boot
```json
{
    "type": "uart_command",
    "command_info": {
        "command": "",
        "uart_port": "application"
    },
    "constraint": {
        "expected_output": "login:",
        "timeout": 60
    }
}
```

#### Execute with Timeout Protection
```json
{
    "type": "uart_command",
    "command_info": {
        "command": "long_running_command",
        "uart_port": "application"
    },
    "constraint": {
        "expected_output": "Done",
        "timeout": 300,
        "error_patterns": ["Error", "Failed"]
    },
    "retry_count": 2
}
```

#### Power Cycle with Delays
```json
{
    "type": "power_control",
    "power_state": "reset",
    "pre_delay": 2,
    "post_delay": 15
}
```

## Test Step Reference

All test steps follow the format defined in `test_flow/README.md`:
- `power_control` - Device power management
- `boot_mode` - Boot mode switching
- `delay` - Simple delay
- `uart_command` - Send commands over UART
- `uart_image_flashing` - Flash images via UART
- `host_command` - Execute commands on host machine
- `loop` - Repeat test blocks with different values

## Notes

- Ensure device configuration exists at `config/devices/{device_name}-{device_id}.json`
- UART logs are saved to `logs/{test_id}/{uart_port}_uart.log`
- All timeouts are in seconds
- Retry counts default to 1 (no retry) if not specified
- Tests fail fast - any failed step stops execution


# Test JSON v1.0 Format

## Sample Code

```json
{
    "JIRA_ID": "ADASVISION-2333",
    "TEST_APP_NAME": "vx_app_tutorial",
    "DESCRIPTION": "Run vx_app_tutorial.out",
    "CORE": "a72",
    "OS": ["linux", "qnx"],
    "BOOT_MODE": "mmcsd",
    "PLATFORM": ["j721s2_evm", "j721e_evm", "j784s4_evm"],
    "ITERATION": "1",
    "TIMEOUT": 200,
    "TEST_FLOW": "command_line",
    "TEST_STEPS": [
        {
            "type": "power_control",
            "power_state": "reset"
        },
        {
            "type": "boot_mode",
            "boot_mode_name": "uart"
        },
        {
            "type": "delay",
            "delay_in_seconds": 2
        },
        {
            "type": "uart_image_flashing",
            "image_info": {
                "image_path": "pdk*/packages/ti/boot/sbl/binary/{platform_name}/uart/bin/sbl_uart_img_mcu1_0_release.tiimage",
                "flashing_port": "mcu1",
                "timeout": 60
            },
            "constraint": {
                "expected_output": "Waiting for tifs.bin",
                "log_port": "mcu1",
                "timeout": 60
            }
        },
        {
            "type": "uart_image_flashing",
            "image_info": {
                "image_path": "pdk*/packages/ti/drv/sciclient/soc/V4/tifs.bin",
                "flashing_port": "mcu1",
                "timeout": 60
            },
            "constraint": {
                "expected_output": "Waiting for multicore app",
                "log_port": "mcu1",
                "timeout": 60
            }
        },
        {
            "type": "uart_image_flashing",
            "image_info": {
                "image_path": "pdk*/packages/ti/binary/{test_app_name}/bin/{platform_name}/udma_baremetal_memcpy_testapp_mcu1_0_release.appimage",
                "flashing_port": "mcu1",
                "timeout": 60
            },
            "constraint": {
                "expected_output": "All tests have passed!!",
                "log_port": "mcu1",
                "timeout": 60
            }
        },
        {
            "type": "uart_command",
            "command_info": {
                "command": "4",
                "uart_port": "mcu1",
                "enter_new_line": true
            },
            "constraint": {
                "expected_output": "All tests have passed",
                "log_port": "mcu1",
                "timeout": 2500
            }
        },
        {
            "type": "loop",
            "loop_count": 3,
            "block": {
                "type": "uart_command",
                "command_info": {
                    "command": "{command}",
                    "uart_port": "mcu1",
                    "enter_new_line": "{enter_new_line}"
                },
                "constraint": {
                    "expected_output": "{message}",
                    "log_port": "mcu1",
                    "timeout": 2500
                }
            },
            "values": {
                "command": ["command1", "command2", "command3"],
                "enter_new_line": [true, true, false],
                "expected_output": ["enter new command:", "enter new command:", "All tests have passed"]
            }
        },
        {
            "type": "power_control",
            "power_state": "off",
            "pre_delay": 0,
            "post_delay": 0
        }
    ]
}
```

## Test Flow Data Blocks Options

### power_control
```json
{
    "type": "power_control",
    "power_state": "reset",
    "pre_delay": 0,
    "post_delay": 0
}
```
| power_state | Description |
|-------------|-------------|
| reset       | Power cycle the device |
| off         | Power off the device |
| on          | Power on the device (if currently off) |
| por         | Power on the device with a POR (Power-On Reset) pulse |

> Note: pre_delay and post_delay are optional and specify the delay in seconds before and after the power state change, respectively.

### boot_mode
```json
{
    "type": "boot_mode",
    "boot_mode_name": "uart",
    "pre_delay": 0,
    "post_delay": 0
}
```

| field | required/optional | description |
|------|-------------------|-------------|
| type | required | Must be "boot_mode" to indicate this block sets the boot mode |
| boot_mode_name | required | The name of the boot mode to set (e.g., uart, mmcsd, ospi, usb) |
| pre_delay | optional | Time in seconds to wait before setting the boot mode (default: 0) |
| post_delay | optional | Time in seconds to wait after setting the boot mode (default: 0) |


| boot_mode_name | Description |
|----------------|-------------|
| uart           | Boot from UART |
| mmcsd          | Boot from MMC/SD |
| ospi           | Boot from OSPI |
| usb            | Boot from USB |


### delay
```json
{
    "type": "delay",
    "delay_in_seconds": 2
}
```

| field | required/optional | description |
|------|-------------------|-------------|
| type | required | Must be "delay" to indicate this block introduces a delay in the test flow |
| delay_in_seconds | required | The amount of time in seconds to delay the test flow before proceeding to the next block |

### uart_image_flashing
```json
{
    "type": "uart_image_flashing",
    "image_info": {
        "image_path": "pdk*/packages/ti/boot/sbl/binary/<<platform_name>>/uart/bin/sbl_uart_img",
        "flashing_port": "mcu1",
        "timeout": 60
    },
    "constraint": {
        "expected_output": "Waiting for tifs.bin",
        "log_port": "mcu1",
        "timeout": 60
    }
}
```

| Field | required/optional | Description |
|-------|-------------------|-------------|
| type | required | Must be "uart_image_flashing" to indicate this block performs image flashing over UART |
| image_info | required | An object containing information about the image to be flashed |
| image_info.image_path | required | Path to the image file to be flashed. Can include placeholders like <<platform_name>> that will be replaced with actual values from the test data. |
| image_info.flashing_port | required | The UART port to use for flashing (e.g., mcu1, mcu2). |
| image_info.timeout | required | Maximum time in seconds to wait for the flashing process to complete. |
| constraint | required | An object containing constraints to determine if the flashing was successful |
| constraint.expected_output | required | The log message to wait for in the specified log port to confirm successful flashing. |
| constraint.log_port | required | The UART port whose logs should be monitored for the expected output. |
| constraint.timeout | required | Maximum time in seconds to wait for the expected output to appear in the logs. | 

> Note: The uart_image_flashing block will attempt to flash the specified image to the device using the specified UART port. It will then monitor the logs from the specified log port for the expected output message to confirm that the flashing was successful. If the expected output is not seen within the timeout period, the test will be marked as failed.


### uart_command
```json
{
    "type": "uart_command",
    "command_info": {
        "command": "cd /opt/vision_apps/ && ( sleep 5; echo a; sleep 15; echo x ) | ./vx_app_tutorial.out",
        "uart_port": "mpu0",
    },
    "constraint": {
        "expected_output": "APP: Deinit ... Done !!!",
        "return_code": 0,
        "log_port": "mpu0",
        "error_patterns": ["Error", "error", "Failed", "failed"],
        "timeout": 2500
    },
    "retry_count": 1,
}
```

| Field | Required/Optional | Description |
|-------|-------------------|-------------|
| type | required | Must be "uart_command" to indicate this block sends a command over UART |
| command_info | required | An object containing information about the command to be sent |
| command_info.command | required | The command string to send over UART. Can include placeholders that will be replaced with actual values from the test data. |
| command_info.uart_port | required | The UART port to which the command should be sent (e.g., mcu1, mcu2). |
| constraint | optional | An object containing constraints to determine if the command execution was successful |
| constraint.expected_output | optional | The log message to wait for in the specified log port to confirm successful command execution. |
| constraint.return_code | optional | The expected return code from the command execution to confirm success. |
| constraint.log_port | optional | The UART port whose logs should be monitored for the expected output. |
| constraint.error_patterns | optional | A list of strings to search for in the logs that would indicate an error. If any of these patterns are found in the logs, the command execution will be marked as failed. |
| constraint.timeout | optional | Maximum time in seconds to wait for the expected output to appear in the logs or for the command to complete. |
| retry_count | optional | The number of times to retry the command execution if it fails (default: 0, meaning no retries) |

| uart_port | Description |
|-----------|-------------|
| mcu0      | UART port connected to MCU0 |
| mcu1      | UART port connected to MCU1 |
| mcu2      | UART port connected to MCU2 |
| mcu3      | UART port connected to MCU3 |
| mpu0      | UART port connected to MPU0 |
| mpu1      | UART port connected to MPU1 |
| auto      | Automatically determine the UART port based on the device configuration and test requirements |


### host_command
```json
{
    "type": "host_command",
    "command_info": {
        "command": "ls -l /opt/vision_apps/",
        "cwd": "/home/user",
    },
    "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "LD_LIBRARY_PATH": "/usr/local/lib:/usr/lib:/lib"
    },
    "constraint": {
        "expected_output": "vx_app_tutorial.out",
        "return_code": 0,
        "error_patterns": ["Error", "error", "Failed", "failed"],
        "timeout": 60
    },
    "retry_count": 1,
}
```
| Field | Required/Optional | Description |
|-------|-------------------|-------------|
| type | required | Must be "host_command" to indicate this block sends a command to the host system |
| command_info | required | An object containing information about the command to be executed on the host |
| command_info.command | required | The command string to execute on the host system. Can include placeholders that will be replaced with actual values from the test data. |
| command_info.cwd | optional | The working directory in which to execute the command on the host system. If not specified, the command will be executed in the current working directory of the test framework. This can be a relative or absolute path. |
| env | optional | An object containing environment variables to set when executing the command on the host system. Each key is the name of the environment variable and the value is the value to set it to. |
| constraint | optional | An object containing constraints to determine if the command execution was successful |
| constraint.expected_output | optional | The output string to wait for in the command's stdout to confirm successful execution. |
| constraint.return_code | optional | The expected return code from the command execution to confirm success. |
| constraint.error_patterns | optional | A list of strings to search for in the command's stdout and stderr that would indicate an error. If any of these patterns are found in the output, the command execution will be marked as failed. |
| constraint.timeout | optional | Maximum time in seconds to wait for the expected output to appear in the command's output or for the command to complete. |

> Note: The host_command block will execute the specified command on the host system where the test framework is running. It will set any specified environment variables for the command execution. The block will then monitor the command's output for the expected output string and check the return code to determine if the command executed successfully. If any of the specified error patterns are found in the output, or if the expected output is not seen within the timeout period, the command execution will be marked as failed.


### loop
```json
{
    "type": "loop",
    "loop_count": 3,
    "block": {
        "type": "uart_command",
        "command_info": {
            "command": "<<command>>",
            "uart_port": "mcu1",
            "enter_new_line": "<<enter_new_line>>"
        },
        "constraint": {
            "expected_output": "<<expected_output>>",
            "log_port": "mcu1",
            "timeout": 2500
        }
    },
    "values": {
        "command": ["command1", "command2", "command3"],
        "enter_new_line": [true, true, false],
        "expected_output": ["enter new command:", "enter new command:", "All tests have passed"]
    }
}
```

| Field | Description |
|------------|-------------|
| loop_count | The number of times to repeat the specified block. |
| block | The test flow block to be repeated in the loop. Can be any of the supported block types (e.g., uart_command, power_control). |
| values | A dictionary of placeholder values to be used in the block during each iteration of the loop. Each key corresponds to a placeholder in the block, and the value is a list of values to be used for each iteration. |

> Note: The loop block allows you to repeat a specified test flow block multiple times with different sets of values. During each iteration, the placeholders in the block will be replaced with the corresponding values from the values dictionary for that iteration.


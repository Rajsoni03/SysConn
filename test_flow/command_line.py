
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from src.modules.dut import DUTConfig
from src.modules.relay import RelayFactory
from src.modules.uart import Uart
from test_flow.base_flow import IBaseFlow
from config.settings import LOGS_DIR
from pprint import pprint

class CommandLineTestFlow(IBaseFlow):
    def setup(self, data: dict, shared_data: dict, db) -> bool:
        # Setup necessary environment for command line test
        print("Setting up Command Line Test Flow")
        self.data = data
        self.shared_data = shared_data
        self.db = db
        self.dut = None
        self.relay = None
        self.uart_connections = {}  # Store multiple UART connections
        return True
    
    def validate(self) -> bool:
        # Validate the test parameters
        print("Validating Command Line Test Flow")
        print(f"Test parameters: ")
        pprint(self.data)
        
        # check self.data have device_name and device_id
        if 'device_name' not in self.data or 'device_id' not in self.data:
            print("Error: Missing device_name or device_id in data")
            return False

        return True
    
    def execute(self) -> bool:
        # Execute the command line test
        print("Executing Command Line Test Flow")

        try:
            # Initialize DUT configuration
            device_name = self.data['device_name'] + "-" + self.data['device_id']
            self.dut = DUTConfig(device_name)

            # Initialize relay
            relay_settings = self.dut.get_power_settings()
            pprint(f"Relay settings: {relay_settings}")
            self.relay = RelayFactory.create_relay("ip",
                                                   relay_settings['ip_address'],
                                                   relay_settings['username'],
                                                   relay_settings['password'])
            self.relay.initialize()

            # Execute test steps
            test_steps = self.data.get('test_steps', [])
            for step_index, step in enumerate(test_steps):
                print(f"\n[Step {step_index + 1}/{len(test_steps)}] Executing: {step.get('type')}")
                success = self._execute_step(step)
                if not success:
                    print(f"[Error] Step {step_index + 1} failed")
                    return False

            print("\n[Success] All test steps completed successfully")
            return True

        except Exception as e:
            print(f"[Error] Test execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            # Cleanup: disconnect all UART connections
            for port_name, uart in self.uart_connections.items():
                try:
                    uart.disconnect()
                    print(f"[Info] Disconnected UART: {port_name}")
                except:
                    pass

    def _execute_step(self, step: Dict[str, Any]) -> bool:
        """Execute a single test step based on its type"""
        step_type = step.get('type')

        handlers = {
            'power_control': self._handle_power_control,
            'boot_mode': self._handle_boot_mode,
            'delay': self._handle_delay,
            'uart_command': self._handle_uart_command,
            'uart_image_flashing': self._handle_uart_image_flashing,
            'host_command': self._handle_host_command,
            'loop': self._handle_loop,
        }

        handler = handlers.get(step_type)
        if handler:
            return handler(step)
        else:
            print(f"[Warning] Unknown step type: {step_type}")
            return False

    def _handle_power_control(self, step: Dict[str, Any]) -> bool:
        """Handle power control step"""
        power_state = step.get('power_state')
        pre_delay = step.get('pre_delay', 0)
        post_delay = step.get('post_delay', 0)

        relay_settings = self.dut.get_power_settings()
        outlet_number = relay_settings.get('outlet_number', 1)

        if pre_delay > 0:
            print(f"[Info] Pre-delay: {pre_delay}s")
            time.sleep(pre_delay)

        print(f"[Info] Power state: {power_state}")

        if power_state == 'reset':
            self.relay.power_on_reset(outlet_number)
        elif power_state == 'off':
            self.relay.off(outlet_number)
        elif power_state == 'on':
            self.relay.on(outlet_number)
        elif power_state == 'por':
            self.relay.power_on_reset(outlet_number)
        else:
            print(f"[Warning] Unknown power state: {power_state}")
            return False

        if post_delay > 0:
            print(f"[Info] Post-delay: {post_delay}s")
            time.sleep(post_delay)

        return True

    def _handle_boot_mode(self, step: Dict[str, Any]) -> bool:
        """Handle boot mode step"""
        boot_mode_name = step.get('boot_mode_name')
        pre_delay = step.get('pre_delay', 0)
        post_delay = step.get('post_delay', 0)

        if pre_delay > 0:
            print(f"[Info] Pre-delay: {pre_delay}s")
            time.sleep(pre_delay)

        boot_mode_value = self.dut.get_boot_mode(boot_mode_name)
        if boot_mode_value:
            print(f"[Info] Setting boot mode: {boot_mode_name} = {boot_mode_value}")
            # TODO: Implement actual boot mode setting logic based on hardware interface
            # This might involve GPIO control or other hardware-specific mechanisms
        else:
            print(f"[Warning] Boot mode not found: {boot_mode_name}")
            return False

        if post_delay > 0:
            print(f"[Info] Post-delay: {post_delay}s")
            time.sleep(post_delay)

        return True

    def _handle_delay(self, step: Dict[str, Any]) -> bool:
        """Handle delay step"""
        delay_seconds = step.get('delay_in_seconds', 0)
        print(f"[Info] Delaying for {delay_seconds}s")
        time.sleep(delay_seconds)
        return True

    def _get_or_create_uart(self, port_name: str) -> Uart:
        """Get existing UART connection or create a new one"""
        if port_name not in self.uart_connections:
            uart_port = self.dut.get_uart_port(port_name)
            if not uart_port:
                raise ValueError(f"UART port not found: {port_name}")

            log_file = LOGS_DIR / str(self.data.get('id', 'test')) / f"{port_name}_uart.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)

            uart = Uart(uart_port, 115200, log_file, 2)
            uart.connect()
            self.uart_connections[port_name] = uart
            print(f"[Info] Connected to UART: {port_name} at {uart_port}")

        return self.uart_connections[port_name]

    def _handle_uart_command(self, step: Dict[str, Any]) -> bool:
        """Handle UART command step"""
        command_info = step.get('command_info', {})
        constraint = step.get('constraint', {})
        retry_count = step.get('retry_count', 1)

        command = command_info.get('command', '')
        uart_port = command_info.get('uart_port', 'default')
        enter_new_line = command_info.get('enter_new_line', True)

        # Get constraint parameters
        expected_output = constraint.get('expected_output')
        timeout = constraint.get('timeout', 120)

        # Get or create UART connection
        uart = self._get_or_create_uart(uart_port)

        # Send command
        print(f"[Info] Sending command to {uart_port}: {command[:50]}...")
        status = uart.send_command(command, expected_output, timeout=timeout, retry_count=retry_count)

        if not status:
            print(f"[Error] UART command failed")
            return False

        print(f"[Info] UART command succeeded")
        return True

    def _handle_uart_image_flashing(self, step: Dict[str, Any]) -> bool:
        """Handle UART image flashing step"""
        image_info = step.get('image_info', {})
        constraint = step.get('constraint', {})

        image_path = image_info.get('image_path', '')
        flashing_port = image_info.get('flashing_port', 'default')
        timeout = image_info.get('timeout', 60)

        expected_output = constraint.get('expected_output')
        log_port = constraint.get('log_port', flashing_port)
        constraint_timeout = constraint.get('timeout', 60)

        print(f"[Info] Flashing image: {image_path}")
        print(f"[Info] Flashing port: {flashing_port}, Log port: {log_port}")

        # TODO: Implement actual image flashing logic
        # This would typically involve:
        # 1. Finding the image file using glob patterns
        # 2. Opening the image file
        # 3. Sending the image data over UART
        # 4. Monitoring the log port for expected output

        print(f"[Warning] Image flashing not fully implemented yet")
        return True

    def _handle_host_command(self, step: Dict[str, Any]) -> bool:
        """Handle host command step"""
        command_info = step.get('command_info', {})
        env_vars = step.get('env', {})
        constraint = step.get('constraint', {})
        retry_count = step.get('retry_count', 1)

        command = command_info.get('command', '')
        cwd = command_info.get('cwd', None)

        expected_output = constraint.get('expected_output')
        expected_return_code = constraint.get('return_code')
        error_patterns = constraint.get('error_patterns', [])
        timeout = constraint.get('timeout', 60)

        print(f"[Info] Executing host command: {command[:50]}...")

        for attempt in range(retry_count):
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=cwd,
                    env={**subprocess.os.environ, **env_vars} if env_vars else None,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

                output = result.stdout + result.stderr

                # Check return code
                if expected_return_code is not None and result.returncode != expected_return_code:
                    print(f"[Warning] Return code mismatch: {result.returncode} != {expected_return_code}")
                    if attempt < retry_count - 1:
                        continue
                    return False

                # Check for expected output
                if expected_output and expected_output not in output:
                    print(f"[Warning] Expected output not found: {expected_output}")
                    if attempt < retry_count - 1:
                        continue
                    return False

                # Check for error patterns
                for pattern in error_patterns:
                    if pattern in output:
                        print(f"[Warning] Error pattern found: {pattern}")
                        if attempt < retry_count - 1:
                            continue
                        return False

                print(f"[Info] Host command succeeded")
                return True

            except subprocess.TimeoutExpired:
                print(f"[Error] Command timeout after {timeout}s")
                if attempt < retry_count - 1:
                    continue
                return False
            except Exception as e:
                print(f"[Error] Command execution failed: {e}")
                if attempt < retry_count - 1:
                    continue
                return False

        return False

    def _replace_placeholders(self, text: str, values: Dict[str, Any], iteration: int) -> str:
        """Replace placeholders in text with values from the iteration"""
        if not isinstance(text, str):
            return text

        for key, value_list in values.items():
            if iteration < len(value_list):
                placeholder = f"{{{key}}}"
                if placeholder in text:
                    text = text.replace(placeholder, str(value_list[iteration]))

        return text

    def _replace_placeholders_recursive(self, obj: Any, values: Dict[str, Any], iteration: int) -> Any:
        """Recursively replace placeholders in a nested structure"""
        if isinstance(obj, dict):
            return {k: self._replace_placeholders_recursive(v, values, iteration) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_placeholders_recursive(item, values, iteration) for item in obj]
        elif isinstance(obj, str):
            return self._replace_placeholders(obj, values, iteration)
        else:
            return obj

    def _handle_loop(self, step: Dict[str, Any]) -> bool:
        """Handle loop step"""
        loop_count = step.get('loop_count', 1)
        block = step.get('block', {})
        values = step.get('values', {})

        print(f"[Info] Starting loop with {loop_count} iterations")

        for i in range(loop_count):
            print(f"[Info] Loop iteration {i + 1}/{loop_count}")

            # Replace placeholders in the block with values for this iteration
            block_with_values = self._replace_placeholders_recursive(block, values, i)

            # Execute the block
            success = self._execute_step(block_with_values)
            if not success:
                print(f"[Error] Loop iteration {i + 1} failed")
                return False

        print(f"[Info] Loop completed successfully")
        return True
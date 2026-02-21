
import time
from src.modules.uart import Uart
from test_flow.base_flow import IBaseFlow
from config.settings import LOGS_DIR

class CommandLineTestFlow(IBaseFlow):
    def setup(self, data: dict, shared_data: dict, db) -> bool:
        # Setup necessary environment for command line test
        print("Setting up Command Line Test Flow")
        self.data = data
        self.shared_data = shared_data
        self.db = db
        return True
    
    def validate(self) -> bool:
        # Validate the test parameters
        print("Validating Command Line Test Flow")
        print(f"Test parameters: {self.data}")
        return True
    
    def execute(self) -> bool:
        # Execute the command line test
        print("Executing Command Line Test Flow")

        self.mcu_uart = Uart("/dev/ttyUSB0", 115200, LOGS_DIR / self.data['id'] / "mcu_uart.log", 2)

        # Simulate command line test execution
        self.mcu_uart.connect()
        
        time.sleep(3)  # Simulate some delay for the command to take effect
        status = self.mcu_uart.send_command("", "login:", timeout=5)
        time.sleep(3)  # Simulate some delay for the command to take effect
        if status:
            status = self.mcu_uart.send_command("root", "root@esp8266:/#", timeout=5)
            time.sleep(3)  # Simulate some delay for the command to take effect
        if status:
            status = self.mcu_uart.send_command("set_led 1 2 10", "LED set to RGB", timeout=5)
            time.sleep(3)  # Simulate some delay for the command to take effect

        status = self.mcu_uart.send_command("reboot", "Rebooting...", timeout=5)
    
        self.mcu_uart.disconnect()
        print(f"Command Line Test Flow execution status: {status}") 
        return True
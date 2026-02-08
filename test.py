from src.plugins.plugin_engine import Plugin
from test_flow.base_flow import IBaseFlow

plugin = Plugin()

class CommandLineTestFlow(IBaseFlow):
    @plugin.on_configure
    def setup(self, shared_data: dict = {}) -> bool:
        # Setup necessary environment for command line test
        print("Setting up Command Line Test Flow")
        shared_data['setup_complete'] = True
        return True
    
    @plugin.on_test
    def validate(self, shared_data: dict = {}) -> bool:
        # Validate the test parameters
        print("Validating Command Line Test Flow")
        return True
    
    @plugin.on_command
    def execute(self, shared_data: dict = {}) -> bool:
        # Execute the command line test
        print("Executing Command Line Test Flow")
        return True
    

if __name__ == "__main__":
    flow = CommandLineTestFlow()
    flow.setup()
    flow.validate()
    flow.execute()
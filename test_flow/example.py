
from functools import wraps
from test_flow.base_flow import IBaseFlow

class ExampleTestFlow(IBaseFlow):
    def setup(self, data: dict, response: dict, db) -> bool:
        # Setup necessary environment for Example test
        print("Setting up Example Test Flow")
        self.data = data
        self.response = response
        self.db = db
        return True
    
    def validate(self) -> bool:
        # Validate the test parameters
        print("Validating Example Test Flow")
        print(f"Test parameters: {self.data}")
        return True
    
    def execute(self) -> bool:
        # Execute the Example test
        print("Executing Example Test Flow")
        return True
import os
import subprocess
import threading
from src.test_flow.flow_list import FLOW_ROUTES

class TestExecutorService():
    def __init__(self, test_data: dict):
        self.test_data = test_data

    def entry_point(self) -> bool:
        status = True

        if status:
            status = self.validate_test()

        if status:
            status = self.setup_environment()
        
        if status:
            status = self.run_test()
        
        return status

    def validate_test(self) -> bool:
        # Validate test data
        # check for required fields
        # e.g., test_flow, parameters, etc.

        # check if test_flow is present
        if flow_name not in FLOW_ROUTES:
            raise ValueError(f"Test flow '{flow_name}' is not recognized.")
        
        return True

    def setup_environment(self) -> bool:
        # create dir for logs
        # store status and logs path in db
        pass

    def run_test(self) -> bool:
        # Run the test test_flow
        flow_name = self.test_data.get('test_flow')

        # Test the test flow on new thread
        test_flow = FLOW_ROUTES.get(flow_name)
        test_thread = threading.Thread(target=test_flow.execute, args=(self.test_data,))
        test_thread.start()
        return True


import os
import subprocess
import threading
from abc import ABC, abstractmethod
from src.test_flow.flow_list import FLOW_ROUTES


class ITestExecutorService(ABC):
    @abstractmethod
    def entry_point(self) -> tuple:
        pass

    @abstractmethod
    def setup_environment(self) -> bool:
        pass
    
    @abstractmethod
    def validate_test(self) -> bool:
        pass

    @abstractmethod
    def run_test(self) -> tuple:
        pass
    

class TestExecutorService(ITestExecutorService):
    def __init__(self, test_data: dict):
        self.test_data = test_data

    def entry_point(self) -> tuple:
        status = True

        if status:
            status = self.setup_environment()
        
        if status:
            status = self.validate_test()
        return self.run_test()

    def setup_environment(self) -> bool:
        # create dir for logs
        # create uart object
        # create relay object
        pass

    def validate_test(self) -> bool:
        pass

    def run_test(self) -> bool:
        # Run the test test_flow
        flow_name = self.test_data.get('test_flow')

        # Check if the flow exists
        if flow_name not in FLOW_ROUTES:
            raise ValueError(f"Test flow '{flow_name}' is not recognized.")

        # Test the test flow on new thread
        test_flow = FLOW_ROUTES.get(flow_name)
        test_thread = threading.Thread(target=test_flow.execute, args=(self.test_data,))
        test_thread.start()
        return True


import os
import subprocess
import threading

from enum import Enum
from uuid import uuid1 as UUID
from test_flow.flow_list import FLOW_ROUTES
from src.app.db_client import DB
from src.app.settings import LOGS_DIR


class TEST_STATUS(Enum):
    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TestExecutorService():
    def __init__(self, data: dict, shared_data: dict):
        self.data = data
        self.shared_data = shared_data
        self.db = DB("test_execution_db.json")
        self.unique_id = UUID().hex
        self.test_status = TEST_STATUS.INITIALIZED.value

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
        required_fields = ['jira_id', 'test_flow']
        
        for field in required_fields:
            if field not in self.data:
                self.shared_data['msg'] = (f"Missing required field: {field}.\n"
                                        f"Required fields are: {', '.join(required_fields)}.")
                return False

        # check if test_flow is present in FLOW_ROUTES
        test_flow = self.data['test_flow']
        if test_flow not in FLOW_ROUTES:
            self.shared_data['msg'] = (f"Test flow '{test_flow}' is not recognized.\n"
                                    f"Available test flows are: {', '.join(FLOW_ROUTES.keys())}.")
            return False
        
        return True

    def setup_environment(self) -> bool:
        # create dir for logs
        # store status and logs path in db
        print("Setting up environment for test execution")
    
        # add entry in db for test execution
        key = self.db.insert(
            {
                'id': self.unique_id,
                'jira_id': self.data.get('jira_id'),
                'status': self.test_status,
                'logs': []
            }
        )
        print(f"Inserted test execution record in DB with key: {key}")

        # Setup logs directory for the test execution
        setup_logs_directory(self.unique_id)

        return True

    def run_test(self) -> bool:
        # Run the test test_flow
        test_flow = self.data.get('test_flow', "")

        # Test the test flow on new thread
        test_flow = FLOW_ROUTES[test_flow]
        test_flow.setup(self.data, self.shared_data, self.db)
        test_flow.validate()
        test_thread = threading.Thread(target=test_flow.execute)
        test_thread.start()
        return True


# Helper functions 
def setup_logs_directory(unique_id: str):
    logs_dir = LOGS_DIR / unique_id
    logs_dir.mkdir(parents=True, exist_ok=True)
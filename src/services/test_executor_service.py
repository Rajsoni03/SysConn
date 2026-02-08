import os
import subprocess
import threading

from enum import Enum
from uuid import uuid1 as UUID
from test_flow.flow_list import FLOW_ROUTES
from src.app.db_client import DB


class TEST_STATUS(Enum):
    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TestExecutorService():
    def __init__(self, data: dict, response: dict):
        self.data = data
        self.response = response
        self.db = DB("test_execution_db.json")

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
                self.response['msg'] = (f"Missing required field: {field}.\n"
                                        f"Required fields are: {', '.join(required_fields)}.")
                return False

        # check if test_flow is present in FLOW_ROUTES
        test_flow = self.data['test_flow']
        if test_flow not in FLOW_ROUTES:
            self.response['msg'] = (f"Test flow '{test_flow}' is not recognized.\n"
                                    f"Available test flows are: {', '.join(FLOW_ROUTES.keys())}.")
            return False
        
        return True

    def setup_environment(self) -> bool:
        # create dir for logs
        # store status and logs path in db
        print("Setting up environment for test execution")
        unique_id = UUID().hex
        status = TEST_STATUS.INITIALIZED.value

        # add entry in db for test execution
        self.db.insert(
            {
                'unique_id': unique_id, # generate unique id
                'jira_id': self.data.get('jira_id'),
                'status': status,
                'logs': []
            }
        )

        # return unique id and status in response
        self.response['id'] = unique_id
        self.response['test_status'] = status
        self.response['polling_url'] = f"/api/v1/test_status/{unique_id}"
        self.response['websocket_url'] = f"/ws/test_logs/{unique_id}"
        self.response['logs_url'] = f"/logs?filename={unique_id}.log"

        return True

    def run_test(self) -> bool:
        # Run the test test_flow
        test_flow = self.data.get('test_flow', "")

        # Test the test flow on new thread
        test_flow = FLOW_ROUTES[test_flow]
        test_flow.setup(self.data, self.response, self.db)
        test_flow.validate()
        test_thread = threading.Thread(target=test_flow.execute)
        test_thread.start()
        return True
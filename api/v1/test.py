from flask import request
from flask_restful import Resource
from src.services.test_executor_service import TestExecutorService
from src.services.test_status_service import TestStatusService
from src.app.settings import HOSTNAME, PORT


class RunTest(Resource):
    def post(self):
        args = request.get_json() or {}
        shared_data = {}

        # Initialize the service and execute the test
        service = TestExecutorService(args, shared_data)
        status = service.entry_point()

        if not status:
            return {"status": False, "msg": shared_data.get("msg", "")}, 400
    
        # Populate the response with test execution details
        return {
            "id": service.unique_id,
            "test_status": status, 
            'polling_url': f"http://{HOSTNAME}:{PORT}/api/v1/test/status/{service.unique_id}",
            'websocket_url': f"ws://{HOSTNAME}:{PORT}/ws/logs/{service.unique_id}",
            'logs': [ f"http://{HOSTNAME}:{PORT}/{path}" for path in shared_data.get('logs', [])],
            "status": True
        }, 201


class TestStatus(Resource):
    def get(self, id: str):
        
        test_status = TestStatusService(id=id).get_status()

        if not test_status:
            return {"status": False, "msg": f"No test found with ID {id}"}, 404
        
        return {
            "test_id": id,
            "test_status": test_status, 
            'polling_url': f"/api/v1/test/status/{id}",
            'websocket_url': f"/ws/logs/{id}"
        }, 200
from flask import request
from flask_restful import Resource
from src.services.test_executor_service import TestExecutorService


class RunTest(Resource):
    def post(self):
        args = request.get_json() or {}
        response = {}

        # Initialize the service and execute the test
        service = TestExecutorService(args, response)
        status = service.entry_point()


        if not status:
            return {"status": False, "msg": response.get("msg", "")}, 400
        
        response["status"] = True
        return response, 201
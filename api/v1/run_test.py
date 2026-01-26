from flask_restful import reqparse, Resource
from src.services.test_executor_service import TestExecutorService

parser = reqparse.RequestParser()

class RunTest(Resource):
    def post(self):
        parser.add_argument('name', type=str, required=True)
        args = parser.parse_args()

        service = TestExecutorService(args)
        status = service.entry_point()

        if not status:
            return {"error": "Some error occurred"}, 400
        return {'status': status}, 201

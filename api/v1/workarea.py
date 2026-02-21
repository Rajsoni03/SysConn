from flask_restful import reqparse, Resource
from src.services.workarea_service import WorkareaService

parser = reqparse.RequestParser()
service = WorkareaService()

class Workarea(Resource):
    def post(self):
        parser.add_argument('name', type=str, required=True)
        args = parser.parse_args()

        success, path = service.create_workarea(args['name'])
        if not success:
            return {"error": "Workarea already exists", "path": path}, 400
        return {'name': args['name']}, 201

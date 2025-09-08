from flask_restful import reqparse, Resource
from services.command_service import CommandService

parser = reqparse.RequestParser()
service = CommandService()

class Command(Resource):
    def post(self):
        parser.add_argument('command', type=str, required=True)
        parser.add_argument('cwd', type=str, required=False, default=None)
        parser.add_argument('env', type=dict, default=None)
        args = parser.parse_args()

        success, stdout, stderr = service.run_command(args['command'], cwd=args['cwd'], env=args['env'])
        if success:
            return {"stdout": stdout, "stderr": stderr}, 200
        return {"error": stderr}, 400

from flask import request, send_from_directory
from flask_restful import Resource
from src.app.settings import LOGS_DIR

class Logs(Resource):
    def get(self):
        filename = request.args.get('filename')
        if not filename:
            return {"status": False, "msg": "Missing 'filename' query parameter"}, 400
        return send_from_directory(
            directory=LOGS_DIR,
            path=filename
        )


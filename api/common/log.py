from flask import request, send_from_directory
from flask_restful import Resource
from src.app.settings import LOGS_DIR

class Logs(Resource):
    def get(self, filepath: str):
        print(f"Received request for log file: {filepath}")
        
        if not filepath:
            return {"status": False, "msg": "Missing 'filepath' query parameter"}, 400
        return send_from_directory(
            directory=LOGS_DIR,
            path=filepath
        )


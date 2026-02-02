import os
import json
import sys
import subprocess
from flask import render_template, make_response, request
from flask_restful import Resource
from src.app.config_loader import Config
from src.utils.ip_utils import get_local_ip
from src.app.settings import TOOL_VERSION, CONFIG_PATH

config = Config()

class Home(Resource):
    def get(self):
        data = {
            "VERSION": TOOL_VERSION,
        }
        AUTH_TOKEN = config.get_data().get("AUTH_TOKEN")
        SUDO_PASSWORD = config.get_data().get("SUDO_PASSWORD")
        data["AUTH_TOKEN"] = AUTH_TOKEN if AUTH_TOKEN else ""
        data["SUDO_PASSWORD"] = SUDO_PASSWORD if SUDO_PASSWORD else ""
        data["IP_ADDRESS"] = get_local_ip()

        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('index.html', data=data), 200, headers)


class SetConfig(Resource):
    def post(self):
        args = request.form.to_dict()

        # Validate input
        invalid_input = ['', None, 'None', 'none', 'NULL', 'null', 'undefined', 'NaN', 'nan']
        if args.get("AUTH_TOKEN") in invalid_input or args.get("SUDO_PASSWORD").lower() in invalid_input:
            response = {
                "status": "error",
                "message": "AUTH_TOKEN and SUDO_PASSWORD cannot be empty or None"
            }
            return response, 400

        try:
            with open(CONFIG_PATH, 'w') as f:
                config.update(args)
                f.write(json.dumps(config.get_data(), indent=4))
            response = {
                "status": "success",
                "message": "Config updated successfully"
            }
            return response, 200
        except Exception as e:
            response = {
                "status": "error",
                "message": f"Error updating config: {str(e)}"
            }
            return response, 500


class Version(Resource):
    def get(self):
        return {"version": TOOL_VERSION}, 200


class Update(Resource):
    def post(self):
        try:
            # Step 1: Pull the latest code
            repo_dir = os.getcwd()
            result = subprocess.run(
                ["git", "pull", "origin", "main"], cwd=repo_dir,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if result.returncode != 0:
                return {"status": "error", "output": result.stderr}, 500

            # Step 2: Restart the server
            python = sys.executable
            os.execl(python, python, *sys.argv)  # replace current process

        except Exception as e:
            return {"status": "error", "message": str(e)}, 500

        return {"status": "success", "message": "Updating and restarting..."}, 200


class HealthCheck(Resource):
    def get(self):
        return {
            'status': 'ok', 
            # 'active_sessions': len(active_sessions),
            'server_type': 'Gunicorn + EventLet',
            'transport': 'WebSocket + Polling'
        }, 200
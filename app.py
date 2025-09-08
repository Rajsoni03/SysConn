import json
import os
import subprocess
import sys
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_restful import Api
from flask_socketio import SocketIO
from src.auth import AuthMiddleware
from src.config_loader import Config, CONFIG_PATH

###################################################################################
##########################[ Initializing Flask App ]###############################

TOOL_VERSION = "1.0.0"

app = Flask(__name__)
import secrets
app.secret_key = secrets.token_hex(32)  # Secure random secret key for session/flash
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # TODO: update CORS origins

config = Config()

###################################################################################
############################[ Importing Resources ]################################

from api.v1.workarea import Workarea
from api.v1.command import Command

###################################################################################
############################[ Setting API Routing ]################################

api.add_resource(Workarea, '/api/v1/workarea')
api.add_resource(Command, '/api/v1/command')

###################################################################################
#########################[ Setting Up Configuration ]##############################

@app.route('/', methods=['GET'])
def home():
    data = {
        "VERSION": TOOL_VERSION,
    }
    AUTH_TOKEN = config.get_data().get("AUTH_TOKEN")
    SUDO_PASSWORD = config.get_data().get("SUDO_PASSWORD")
    data["AUTH_TOKEN"] = AUTH_TOKEN if AUTH_TOKEN else ""
    data["SUDO_PASSWORD"] = SUDO_PASSWORD if SUDO_PASSWORD else ""
    return render_template('index.html', data=data)

@app.route('/set_config', methods=['POST'])
def set_config():
    data = request.form.to_dict()
    response = {}
    # Validate input
    if data.get("AUTH_TOKEN") in [None, "", "None", "null"] or data.get("SUDO_PASSWORD") in [None, "", "None", "null"]:
        response = {
            "status": "error",
            "message": "AUTH_TOKEN and SUDO_PASSWORD cannot be empty or None"
        }
        return jsonify(response), 400

    try:
        with open(CONFIG_PATH, 'w') as f:
            config.update(data)
            f.write(json.dumps(config.get_data(), indent=4))
        response = {
            "status": "success",
            "message": "Config updated successfully"
        }
        return jsonify(response)
    except Exception as e:
        response = {
            "status": "error",
            "message": f"Error updating config: {str(e)}"
        }
        return jsonify(response), 500

@app.route('/version', methods=['GET'])
def get_version():
    return jsonify({"version": TOOL_VERSION})

@app.route('/update', methods=['POST'])
def update():
    try:
        # Step 1: Pull the latest code
        repo_dir = os.getcwd()
        result = subprocess.run(
            ["git", "pull", "origin", "main"], cwd=repo_dir,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        if result.returncode != 0:
            return jsonify({"status": "error", "output": result.stderr}), 500

        # Step 2: Restart the server
        python = sys.executable
        os.execl(python, python, *sys.argv)  # replace current process

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "success", "message": "Updating and restarting..."})

###################################################################################
#########################[ Running the Flask Application ]#########################

if __name__ == '__main__':
    app.wsgi_app = AuthMiddleware(app.wsgi_app)
    socketio.run(app, host='0.0.0.0', port=5500, debug=True, allow_unsafe_werkzeug=True)

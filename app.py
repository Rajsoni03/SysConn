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
def get_config():
    data = {
        "VERSION": TOOL_VERSION,
    }
    data.update(config.get_data())
    return render_template('index.html', data=data)

@app.route('/set_config', methods=['POST'])
def set_config():
    data = request.form.to_dict()
    with open(CONFIG_PATH, 'w') as f:
        config.update(data)
        f.write(json.dumps(config.get_data(), indent=4))

    flash("Config updated successfully", "success")
    return redirect(url_for('get_config'))

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
    socketio.run(app, debug=True, host='0.0.0.0', port=5500)

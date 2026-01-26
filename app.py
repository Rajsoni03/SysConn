import secrets
from flask import Flask
from flask_restful import Api
from flask_socketio import SocketIO
from src.app.auth import AuthMiddleware

###################################################################################
##########################[ Initializing Flask App ]###############################

app = Flask(__name__)
app.wsgi_app = AuthMiddleware(app.wsgi_app)
app.secret_key = secrets.token_hex(32)  # Secure random secret key for session/flash
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # TODO: update CORS origins

###################################################################################
################[ Importing Resources & Setting API Route ]########################

# Importing Common APIs
from api.common.core_api import Home, SetConfig, Version, Update, HealthCheck

api.add_resource(Home, '/')
api.add_resource(SetConfig, '/set_config')
api.add_resource(Version, '/version')
api.add_resource(Update, '/update')
api.add_resource(HealthCheck, '/health')

# Importing V1 APIs
from api.v1.workarea import Workarea
from api.v1.command import Command
from api.v1.run_test import RunTest

api.add_resource(Workarea, '/api/v1/workarea')
api.add_resource(Command, '/api/v1/command')
api.add_resource(RunTest, '/api/v1/run_test')

###################################################################################
#########################[ Running the Flask Application ]#########################

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5500, debug=True, allow_unsafe_werkzeug=True)

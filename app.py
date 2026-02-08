import secrets
from flask import Flask
from flask_restful import Api
from flask_socketio import SocketIO
from src.app.auth import AuthMiddleware
from src.app.routes import register_routes

###################################################################################
##########################[ Initializing Flask App ]###############################

app = Flask(__name__)
app.wsgi_app = AuthMiddleware(app.wsgi_app)
app.secret_key = secrets.token_hex(32)  # Secure random secret key for session/flash
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*")

###################################################################################
###############################[ Setting API Route ]###############################

register_routes(api)

###################################################################################
#########################[ Running the Flask Application ]#########################

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5500, debug=True, allow_unsafe_werkzeug=True)

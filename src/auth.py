from src.config_loader import Config

SECURE_PATHS = ['/api/', '/update']
OPEN_PATHS = ['/docs', '/version']

class AuthMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        url_path = environ.get('PATH_INFO')

        if any(url_path.startswith(path) for path in SECURE_PATHS):
            token = environ.get('HTTP_AUTHORIZATION')
            auth_token = Config().get_data().get("AUTH_TOKEN")
            if token != auth_token:
                start_response('401 Unauthorized', [('Content-Type', 'application/json')])
                return [b'{"error": "Unauthorized: Invalid or missing token."}']
        elif any(url_path.startswith(path) for path in OPEN_PATHS):
            # Allow open access to these paths
            pass
        else:
            # Only allow requests from localhost
            if environ.get('REMOTE_ADDR') not in ('127.0.0.1', '::1', 'localhost'):
                start_response('403 Forbidden', [('Content-Type', 'application/json')])
                return [b'{"error": "Forbidden: Only localhost allowed."}']

        return self.app(environ, start_response)
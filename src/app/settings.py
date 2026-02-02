from pathlib import Path

# Application Version
TOOL_VERSION = "1.0.3"

# Latest API Version
API_VERSION = "v1"

# File Paths
CONFIG_PATH = Path.cwd() / "data" / "config.json"
DB_PATH = Path.cwd() / "data" / "db" / "main_db.json"

# API Path Access Control Lists
SECURE_PATHS = ['/api/', '/update'] # paths that always require auth token
PUBLIC_PATHS = ['/docs', '/version', "/health"] # open access to these paths
PROTECTED_PATHS = ['/set_config', '/'] # if auth token is not set, allow access to these paths but restrict other paths to localhost only

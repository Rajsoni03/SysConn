from pathlib import Path

# Application Version
TOOL_VERSION = "1.0.5"

# Latest API Version
API_VERSION = "v1"

# File Paths
CONFIG_PATH = Path.cwd() / "data" / "config.json"
DB_PATH_ROOT = Path.cwd() / "data" / "db"

# Available API Versions
API_VERSIONS = ["common" ,"v1"]  # Future versions can be added here

# API Path Access Control Lists
SECURE_PATHS = ['/api/', '/update'] # paths that always require auth token
PUBLIC_PATHS = ['/docs', '/version', "/health", "/logs"] # open access to these paths
PROTECTED_PATHS = ['/set_config', '/'] # if auth token is not set, allow access to these paths but restrict other paths to localhost only

# Logs and Uploads
LOGS_DIR = Path.cwd() / "logs" 

# Workarea
WORKAREA_DIR = Path.cwd() / "workarea"
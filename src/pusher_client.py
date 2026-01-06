import os
import pusher
from src.config_loader import Config


def get_pusher_client():
    """Initialize a Pusher client from config.json, falling back to environment variables.

    Config keys (preferred):
    - PUSHER_APP_ID
    - PUSHER_KEY
    - PUSHER_SECRET
    - PUSHER_CLUSTER (optional, defaults to mt1)
    - PUSHER_SSL (optional, defaults to True)

    Expected env vars (fallback):
    - PUSHER_APP_ID
    - PUSHER_KEY
    - PUSHER_SECRET
    - PUSHER_CLUSTER (optional, defaults to mt1)
    - PUSHER_SSL (optional, defaults to True)
    """
    cfg = Config().get_data()

    app_id = cfg.get("PUSHER_APP_ID") or os.environ.get("PUSHER_APP_ID")
    key = cfg.get("PUSHER_KEY") or os.environ.get("PUSHER_KEY")
    secret = cfg.get("PUSHER_SECRET") or os.environ.get("PUSHER_SECRET")
    cluster = cfg.get("PUSHER_CLUSTER") or os.environ.get("PUSHER_CLUSTER") or "mt1"

    ssl_default = cfg.get("PUSHER_SSL")
    if ssl_default is None:
        ssl_default = True
    ssl_flag = os.environ.get("PUSHER_SSL", ssl_default)
    if isinstance(ssl_flag, str):
        ssl_flag = ssl_flag.lower() in ("1", "true", "yes", "on")

    if not all([app_id, key, secret]):
        return None

    return pusher.Pusher(
        app_id=app_id,
        key=key,
        secret=secret,
        cluster=cluster,
        ssl=ssl_flag,
    )

import json
from pathlib import Path

CONFIG_PATH = Path.cwd() / "config" / "config.json"

class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Config(metaclass=SingletonMeta):
    def __init__(self, config_path=CONFIG_PATH):
        self.config_path = config_path
        self.data = {
            "AUTH_TOKEN": None,
            "SUDO_PASSWORD": None
        }
        self.load()

    def load(self):
        # Load existing config if available
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.data = json.load(f)
        else:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            # Create a default config file
            with open(self.config_path, 'w') as f:
                json.dump(self.data, f, indent=4)

    def save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def update(self, new_data):
        self.data.update(new_data)
        self.save()

    def get_data(self):
        return self.data

# Initialize and load config at module level
config = Config()
config.load()
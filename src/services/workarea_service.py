import os
from abc import ABC, abstractmethod
from src.config_loader import Config
from src.pusher_client import get_pusher_client

class IWorkareaService(ABC):
    @abstractmethod
    def create_workarea(self, name: str) -> tuple:
        pass

    def repo_sync(self, device: str, sdk: str, xml_name: str) -> tuple:
        pass

class WorkareaService(IWorkareaService):
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.pusher = get_pusher_client()

    def create_workarea(self, name: str) -> tuple:
        path = os.path.join(self.base_path, name)
        created = False
        if not os.path.exists(path):
            os.makedirs(path)
            created = True

        abs_path = os.path.abspath(path)
        if created:
            self._broadcast_creation(name, abs_path)

        return created, abs_path

    def repo_sync(self, device: str, sdk: str, xml_name: str) -> tuple:
        pass

    def _broadcast_creation(self, name: str, path: str):
        """Notify clients that a workarea was created."""
        if not self.pusher:
            return

        token = Config().get_data().get("AUTH_TOKEN")
        if not token:
            return

        channel = f"private-{token}"
        try:
            self.pusher.trigger(channel, "workarea_created", {"name": name, "path": path})
        except Exception:
            # Ignore broadcast failures to keep API responsive.
            pass

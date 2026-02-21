from abc import ABC, abstractmethod
from pathlib import Path
from config.settings import WORKAREA_DIR

class IWorkareaService(ABC):
    @abstractmethod
    def create_workarea(self, name: str) -> tuple:
        pass

    def repo_sync(self, device: str, sdk: str, xml_name: str) -> tuple:
        pass

class WorkareaService(IWorkareaService):
    def __init__(self, base_path: str | Path = WORKAREA_DIR):
        self.base_path = Path(base_path)

    def create_workarea(self, name: str) -> tuple:
        path = self.base_path / name
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            return True, str(path.resolve())
        return False, str(path.resolve())

    def repo_sync(self, device: str, sdk: str, xml_name: str) -> tuple:
        pass
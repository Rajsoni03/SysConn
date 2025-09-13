import os
from abc import ABC, abstractmethod

class IWorkareaService(ABC):
    @abstractmethod
    def create_workarea(self, name: str) -> tuple:
        pass

    def repo_sync(self, device: str, sdk: str, xml_name: str) -> tuple:
        pass

class WorkareaService(IWorkareaService):
    def __init__(self, base_path: str):
        self.base_path = base_path

    def create_workarea(self, name: str) -> tuple:
        path = os.path.join(self.base_path, name)
        if not os.path.exists(path):
            os.makedirs(path)
            return True, os.path.abspath(path)
        return False, os.path.abspath(path)

    def repo_sync(self, device: str, sdk: str, xml_name: str) -> tuple:
        pass
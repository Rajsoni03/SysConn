from abc import ABC, abstractmethod

class IBaseFlow(ABC):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.shared_data = {}
        self.db = None

    @abstractmethod
    def setup(self, data: dict, shared_data: dict, db) -> bool:
        raise NotImplementedError("Subclass must implement the setup method.")
    
    @abstractmethod
    def validate(self) -> bool:
        raise NotImplementedError("Subclass must implement the validate method.")

    @abstractmethod
    def execute(self) -> bool:
        raise NotImplementedError("Subclass must implement the execute method.")

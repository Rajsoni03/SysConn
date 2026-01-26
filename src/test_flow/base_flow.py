from abc import ABC, abstractmethod

class IBaseFlow(ABC):
    def __init__(self, test_info: dict = None):
        super().__init__()
        self.test_info = test_info

    @abstractmethod
    def setup(self, shared_data: dict = {}) -> bool:
        raise NotImplementedError("Subclass must implement the setup method.")
    
    @abstractmethod
    def validate(self, shared_data: dict = {}) -> bool:
        raise NotImplementedError("Subclass must implement the validate method.")

    @abstractmethod
    def execute(self, shared_data: dict = {}) -> bool:
        raise NotImplementedError("Subclass must implement the execute method.")

from enum import Enum
from src.app.db_client import DB


class TEST_STATUS(Enum):
    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TestStatusService():
    def __init__(self, id: str):
        self.id = id
        self.db = DB("test_execution_db.json")

    def get_status(self) -> str:
        results = self.db.search(lambda x: x.get("id") == self.id)
        print(f"Queried DB for test ID {self.id}, found results: {results}")
        if results and "status" in results[0]:
            return results[0]["status"]
        return ""

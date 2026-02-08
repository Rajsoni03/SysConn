import os
import threading
from pathlib import Path
from tinydb import TinyDB, Query
from typing import Any, Dict, List, Callable
from src.utils.singleton import SingletonMeta
from src.app.settings import DB_PATH_ROOT

class DB(metaclass=SingletonMeta):
	def __init__(self, db_path: str | Path = DB_PATH_ROOT / "main_db.json") -> None:
		"""Initialize the database client."""
		db_path = DB_PATH_ROOT / db_path
		db_path.parent.mkdir(parents=True, exist_ok=True) # Ensure the directory exists
		
		self.db: TinyDB = TinyDB(db_path)
		self.query: Query = Query()
		self._lock = threading.Lock()

	def insert(self, data: Dict[str, Any]) -> int:
		"""Insert a new record into the database."""
		with self._lock:
			return self.db.insert(data)

	def update(self, fields: Dict[str, Any], cond: Callable[[Dict[str, Any]], bool]) -> List[int]:
		"""Update records matching the condition."""
		with self._lock:
			return self.db.update(fields, cond)

	def delete(self, cond: Callable[[Dict[str, Any]], bool]) -> List[int]:
		"""Delete records matching the condition."""
		with self._lock:
			return self.db.remove(cond)

	def search(self, cond: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
		"""Search for records matching the condition."""
		with self._lock:
			return self.db.search(cond)

	def get_all(self) -> List[Dict[str, Any]]:
		"""Get all records from the database."""
		with self._lock:
			return self.db.all()

	def clear(self) -> None:
		"""Remove all records from the database."""
		with self._lock:
			self.db.truncate()


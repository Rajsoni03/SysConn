import json
import os
import threading
from pathlib import Path
from time import time, sleep
from typing import Any, Dict, List, Callable
import uuid

from tinydb import Query, TinyDB
from src.utils.singleton import SingletonMeta
from src.app.settings import DB_PATH_ROOT
from pprint import pprint

DB_PATH_ROOT = Path.cwd() / "data" / "db"

class JsonDB(metaclass=SingletonMeta):
	def __init__(self, db_path: str | Path = DB_PATH_ROOT / "main_db.json") -> None:
		"""Initialize the database client."""
		self.db_path = DB_PATH_ROOT / db_path
		self.db_path.parent.mkdir(parents=True, exist_ok=True)
		self._lock = threading.Lock()
		self.db : Dict[str, Dict[str, Any]] = {}  # In-memory representation of the database
		self.load_from_disk()
		# self.sync_in_background()

	def insert(self, data: Dict[str, Any]) -> str:
		"""Insert a new record into the database."""
		id_hash = uuid.uuid4().hex
		with self._lock:
			self.db[id_hash] = data
		self.save_to_disk()
		return id_hash

	def update(self, fields: Dict[str, Any], cond: Callable[[Dict[str, Any]], bool]) -> List[str]:
		"""Update records matching the condition."""
		updated_ids = []
		with self._lock:
			for id_hash, record in self.db.items():
				if cond(record):
					record.update(fields)
					updated_ids.append(id_hash)
		if updated_ids:
			self.save_to_disk()
		return updated_ids

	def delete(self, cond: Callable[[Dict[str, Any]], bool]) -> List[str]:
		"""Delete records matching the condition."""
		to_delete = []
		with self._lock:
			to_delete = [id_hash for id_hash, record in self.db.items() if cond(record)]
			for id_hash in to_delete:
				del self.db[id_hash]
		if to_delete:
			self.save_to_disk()
		return to_delete
	
	def delete_by_id(self, id_hash: str) -> dict:
		"""Delete a record by its ID."""
		to_del = {}
		with self._lock:
			if id_hash in self.db:
				to_del = self.db[id_hash]
				del self.db[id_hash]
		self.save_to_disk()
		return to_del

	def search(self, cond: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
		"""Search for records matching the condition."""
		with self._lock:
			return [record for record in self.db.values() if cond(record)]
	
	def search_by_id(self, id_hash: str) -> Dict[str, Any] | None:
		"""Search for a record by its ID."""
		with self._lock:
			return self.db.get(id_hash)

	def get_all(self) -> List[Dict[str, Any]]:
		"""Get all records from the database."""
		with self._lock:
			return list(self.db.values())

	def clear(self) -> None:
		"""Remove all records from the database."""
		with self._lock:
			self.db.clear()
		self.save_to_disk()

	# Persistence methods
	def load_from_disk(self) -> None:
		"""Load the database from disk into memory."""
		if self.db_path.exists():
			with self._lock:
				with open(self.db_path, 'r') as f:
					self.db = json.load(f)
		else:
			self.save_to_disk()

	def save_to_disk(self) -> None:
		"""Save the in-memory database to disk."""
		with self._lock:
			with open(self.db_path, 'w') as f:
				json.dump(self.db, f, indent=4)
				f.flush()  # Ensure data is written to disk
	
	def sync_in_background(self) -> None:
		"""Synchronize the in-memory database with the disk periodically."""
		def sync_thread():
			while True:
				self.save_to_disk()
				sleep(0.1)  # Sync every 0.1 seconds
		thread = threading.Thread(target=sync_thread, daemon=True)
		thread.start()


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

    
if __name__ == "__main__":
	print("----------- Testing Custom JSON DB Implementation -----------")
	db = JsonDB("test_db.json")
	
	for i in range(10):
		start = time()
		for i in range(50):
			db.insert({"name": "Alice", "age": 30})
			db.insert({"name": "Bob", "age": 25})
			db.insert({"name": "Charlie", "age": 35})
			db.insert({"name": "David", "age": 28})
			db.insert({"name": "Eve", "age": 22})
			db.insert({"name": "Frank", "age": 40})
			db.update({"age": 30}, lambda record: record["name"] == "Alice")
			db.delete(lambda record: record["name"] == "Eve")
			# db.delete_by_id("4d3778609e9943d98d261ebd586b7fb7")
		end = time()
		print("function takes", end-start, "seconds")
		sleep(1)  # Sleep for a while to allow background sync to complete

	print("----------- Testing TinyDB Implementation -----------")

	db = DB("test_db_tiny.json")
	
	for i in range(10):
		start = time()
		for i in range(50):
			db.insert({"name": "Alice", "age": 30})
			db.insert({"name": "Bob", "age": 25})
			db.insert({"name": "Charlie", "age": 35})
			db.insert({"name": "David", "age": 28})
			db.insert({"name": "Eve", "age": 22})
			db.insert({"name": "Frank", "age": 40})
			db.update({"age": 30}, lambda record: record["name"] == "Alice")
			db.delete(lambda record: record["name"] == "Eve")
			# db.delete_by_id("4d3778609e9943d98d261ebd586b7fb7")
		end = time()
		print("function takes", end-start, "seconds")
		sleep(1)  # Sleep for a while to allow background sync to complete

	# db.clear()

	# pprint(db.get_all())s
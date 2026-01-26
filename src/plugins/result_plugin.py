import functools
from abc import abstractmethod
from src.plugins.base_plugin import BasePlugin


class ResultPlugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_configure_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        print(f"[PLUGIN] ResultPlugin : on_configure_pre_proc before {method.__name__} shared_data = {shared_data}")

    def on_configure_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        print(f"[PLUGIN] ResultPlugin : on_configure_post_proc after {method.__name__} shared_data = {shared_data}")

    def on_test_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        print(f"[PLUGIN] ResultPlugin : on_test_pre_proc before {method.__name__} shared_data = {shared_data}")

    def on_test_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        print(f"[PLUGIN] ResultPlugin : on_test_post_proc after {method.__name__} shared_data = {shared_data}")

    def on_flash_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        print(f"[PLUGIN] ResultPlugin : on_flash_pre_proc before {method.__name__} shared_data = {shared_data}")

    def on_flash_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        print(f"[PLUGIN] ResultPlugin : on_flash_post_proc after {method.__name__} shared_data = {shared_data}")

    def on_command_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        print(f"[PLUGIN] ResultPlugin : on_command_pre_proc before {method.__name__} shared_data = {shared_data}")

    def on_command_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        print(f"[PLUGIN] ResultPlugin : on_command_post_proc after {method.__name__} shared_data = {shared_data}")

    def on_constraint_check_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        print(f"[PLUGIN] ResultPlugin : on_constraint_check_pre_proc before {method.__name__} shared_data = {shared_data}")

    def on_constraint_check_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        print(f"[PLUGIN] ResultPlugin : on_constraint_check_post_proc after {method.__name__} shared_data = {shared_data}")

    def on_exception_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        print(f"[PLUGIN] ResultPlugin : on_exception_pre_proc before {method.__name__} shared_data = {shared_data}")

    def on_exception_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        print(f"[PLUGIN] ResultPlugin : on_exception_post_proc after {method.__name__} shared_data = {shared_data}")

    def on_error_pre_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        print(f"[PLUGIN] ResultPlugin : on_error_pre_proc before {method.__name__} shared_data = {shared_data}")

    def on_error_post_proc(self, shared_data: dict, method: callable, *args, **kwargs) -> callable:
        print(f"[PLUGIN] ResultPlugin : on_error_post_proc after {method.__name__} shared_data = {shared_data}")


import os
import subprocess
from abc import ABC, abstractmethod
from src.config_loader import Config
from src.pusher_client import get_pusher_client

class ICommandService(ABC):
    @abstractmethod
    def run_command(self, workarea: str, command: str) -> tuple:
        pass

class CommandService(ICommandService):
    def __init__(self, base_path: str = None):
        self.base_path = base_path
        self.pusher = get_pusher_client()

    def run_command(self, command: str, cwd: str = None, env: dict = None) -> tuple:
        try:
            result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True, env=env)
            success, stdout, stderr = True, result.stdout, result.stderr
        except Exception as e:
            success, stdout, stderr = False, '', str(e)

        self._broadcast_result(success, command, cwd, stdout, stderr)
        return success, stdout, stderr

    def _broadcast_result(self, success: bool, command: str, cwd: str, stdout: str, stderr: str):
        """Send command results to Pusher on a channel derived from the auth token."""
        if not self.pusher:
            return

        token = Config().get_data().get("AUTH_TOKEN")
        if not token:
            return

        channel = f"private-{token}"
        try:
            self.pusher.trigger(channel, "command_result", {
                "success": success,
                "command": command,
                "cwd": cwd,
                "stdout": stdout,
                "stderr": stderr,
            })
        except Exception:
            # Broadcasting failures should not break the API response.
            pass

    # def execute_command(self, cmd, stream=False):
    #     if stream:
    #         proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    #         for line in proc.stdout:
    #             yield line
    #     else:
    #         result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    #         return result.stdout + result.stderr

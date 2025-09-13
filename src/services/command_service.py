import os
import subprocess
from abc import ABC, abstractmethod

class ICommandService(ABC):
    @abstractmethod
    def run_command(self, workarea: str, command: str) -> tuple:
        pass

class CommandService(ICommandService):
    def __init__(self, base_path: str = None):
        self.base_path = base_path

    def run_command(self, command: str, cwd: str = None, env: dict = None) -> tuple:
        try:
            result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True, env=env)
            return True, result.stdout, result.stderr
        except Exception as e:
            return False, '', str(e)

    # def execute_command(self, cmd, stream=False):
    #     if stream:
    #         proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    #         for line in proc.stdout:
    #             yield line
    #     else:
    #         result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    #         return result.stdout + result.stderr

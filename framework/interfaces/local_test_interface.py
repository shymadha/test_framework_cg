import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import subprocess
from core.logger import setup_logger

class LocalTestInterface:
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)

    def connect(self):
        # No connection needed for local execution
        self.logger.info("Local interface ready")

    def execute(self, command):
        self.logger.info(f"Executing locally: {command}")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )

            output = result.stdout.strip()
            error = result.stderr.strip()
            status = result.returncode

            return output, error, status

        except Exception as e:
            return "", str(e), 1
    
    def close(self):
        pass
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import subprocess
from core.logger import setup_logger


class LocalTestInterface:
    """
    Interface implementation for executing commands on the local machine.

    This interface does not require establishing a remote connection.
    All commands are executed directly on the host system using Python's
    subprocess module. It is useful for test cases where the SUT is the
    same system running the test engine or for simple shell‑based validations.

    Attributes
    ----------
    logger : logging.Logger
        Logger instance specific to this interface class.
    """

    def __init__(self):
        """
        Initialize the LocalTestInterface and set up the logger.
        """
        self.logger = setup_logger(self.__class__.__name__)

    def connect(self):
        """
        Prepare the local interface for execution.

        Since no external connection is required, this method simply logs
        that the local execution environment is ready.
        """
        # No connection needed for local execution
        self.logger.info("Local interface ready")

    def execute(self, command):
        """
        Execute a shell command on the local system.

        Parameters
        ----------
        command : str
            The command to execute on the local machine.

        Returns
        -------
        tuple
            A tuple of (output, error, status) where:
              output : str  -> Captured standard output
              error  : str  -> Captured standard error (if any)
              status : int  -> Process return code (0 = success)

        Notes
        -----
        - Uses `subprocess.run` with `shell=True`, which evaluates the
          command through the system shell.
        - Captures both stdout and stderr for reporting consistency.
        - Exceptions are caught and returned as error messages.

        Raises
        ------
        Exception
            If the subprocess invocation fails internally.
        """
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
        """
        Close the interface session.

        Local execution requires no cleanup, so this method is intentionally empty.
        It exists only to comply with the TestInterface contract.
        """
        pass
# pm_windows.py
import ctypes
import logging
import sys
import os
import subprocess
from datetime import datetime, time, timedelta
from unittest import result

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase
from framework.utilities.os_utils.pm.pm_base import PMBase
from core.logger import setup_logger


class PMWindows(PMBase):
    """
    Windows-specific implementation of power‑management (PM) operations.

    This class provides concrete system-level power actions for Windows hosts,
    including:
      - System restart
      - Entering sleep (suspend) state
      - System shutdown

    Commands are executed on the target machine using the platform object's
    `exec_cmd()` method, typically over SSH for remote execution.

    Tools used:
      - `shutdown.exe` for shutdown and restart
      - `rundll32 powrprof.dll,SetSuspendState` for sleep operations

    All results follow the unified tuple format:
        (output, error, exit_status)

    Inherits from
    -------------
    PMBase
        The abstract class defining the contract for PM utilities.
    """

    def restart(self, password=None):
        """
        Restart the Windows system immediately.

        Uses the command:
            shutdown /r /t 0

        Parameters
        ----------
        password : str, optional
            Included for API symmetry with Linux implementations; not used
            by Windows commands.

        Returns
        -------
        tuple
            (output, error, exit_status) from execution of the restart command.

        Notes
        -----
        - If exit_status != 0, the failure is logged.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd(
                "shutdown /r /t 0", "ssh"
            )

            if exit_status != 0:
                self.platform_obj.logger.error(
                    f"Failed to restart the system. Error: {error}"
                )

            return output, error, exit_status

        except Exception as e:
            self.platform_obj.logger.error(
                f"An error occurred while trying to restart the system: {str(e)}",
                exc_info=True,
            )
            return "", str(e), -1

    def s3_sleep(self, password=None):
        """
        Place the Windows system into sleep (suspend) state.

        Uses the command:
            rundll32.exe powrprof.dll,SetSuspendState 0,1,0

        Parameters
        ----------
        password : str, optional
            Present for interface compatibility; not required under Windows.

        Returns
        -------
        tuple
            (output, error, exit_status) from the sleep command.

        Notes
        -----
        - Windows may require certain power-policy settings to allow suspended state.
        - Logs failure conditions and exceptions for troubleshooting.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd(
                "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
                "ssh"
            )

            if exit_status != 0:
                self.platform_obj.logger.error(
                    f"Failed to sleep the system. Error: {error}"
                )

            return output, error, exit_status

        except Exception as e:
            self.platform_obj.logger.error(
                f"An error occurred while trying to sleep the system: {str(e)}",
                exc_info=True,
            )
            return "", str(e), -1

    def shutdown(self, password=None):
        """
        Shut down the Windows system immediately.

        Uses the command:
            shutdown /s /t 0

        Parameters
        ----------
        password : str, optional
            Placeholder argument (unused in Windows operations).

        Returns
        -------
        tuple
            (output, error, exit_status) from the shutdown command.

        Notes
        -----
        - The host may lose SSH connectivity immediately after execution.
        - Logs failures and exceptions for diagnostics.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd(
                "shutdown /s /t 0", "ssh"
            )

            if exit_status != 0:
                self.platform_obj.logger.error(
                    f"Failed to shutdown the system. Error: {error}"
                )

            return output, error, exit_status

        except Exception as e:
            self.platform_obj.logger.error(
                f"An error occurred while trying to shutdown the system: {str(e)}",
                exc_info=True,
            )
            return "", str(e), -1
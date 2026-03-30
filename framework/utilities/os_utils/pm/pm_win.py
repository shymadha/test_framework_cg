# pm_windows.py
import ctypes
import logging
import sys
import os
import subprocess
from datetime import datetime, time, timedelta
from unittest import result
import socket
import time

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
      - System s5

    Commands are executed on the target machine using the platform object's
    `exec_cmd()` method, typically over SSH for remote execution.

    Tools used:
      - `s5.exe` for s5 and restart
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
            s5 /r /t 0

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
                "s5 /r /t 0", "ssh"
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

    def s3(self, password=None, wake_after: int = None):  # ← indented inside class
        """
        Put the Windows system into S3 sleep.

        Uses:
            [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)

        Parameters
        ----------
        wake_after : int, optional
            Seconds after which the system should auto-wake via Task Scheduler.
            If None, no wake timer is set (manual wake only).
        password : str, optional
            Included for API symmetry with Linux implementations; not used
            by Windows commands.

        Returns
        -------
        tuple
            (output, error, exit_status) from execution of the sleep command.

        Notes
        -----
        - If exit_status != 0, the failure is logged.
        - rundll32 SetSuspendState is intentionally avoided — it sets
          ForceCritical=1 internally which suppresses wake timers.
        """
        try:
            # ── 1. Schedule wake timer BEFORE sleeping ────────────────────
            if wake_after is not None:
                total = int(wake_after)  # +10s buffer so task doesn't fire before sleep
                wake_ps = (
                    f"$t = (Get-Date).AddSeconds({total}); "
                    f"$action   = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c exit'; "
                    f"$trigger  = New-ScheduledTaskTrigger -Once -At $t; "
                    f"$settings = New-ScheduledTaskSettingsSet -WakeToRun; "
                    f"Register-ScheduledTask -TaskName 'PMWakeTask' "
                    f"-Action $action -Trigger $trigger -Settings $settings "
                    f"-RunLevel Highest -Force | Out-Null"
                )
                _, wake_err, wake_exit = self.platform_obj.exec_cmd(
                    f'powershell -NonInteractive -Command "{wake_ps}"', "ssh"
                )

                if wake_exit != 0:
                    self.platform_obj.logger.warning(
                        f"Wake timer scheduling failed (system will not auto-wake). "
                        f"Error: {wake_err}"
                    )
                else:
                    self.platform_obj.logger.info(
                        f"Wake timer set: system will wake in {wake_after}s."
                    )

            # ── 2. Issue sleep command ─────────────────────────────────────
            sleep_ps = (
                "Add-Type -Assembly System.Windows.Forms; "
                "[System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)"
            )
            output, error, exit_status = self.platform_obj.exec_cmd(
                f'powershell -NonInteractive -Command "{sleep_ps}"', "ssh"
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
        

    def s5(self, password=None):
        """
        Shut down the Windows system immediately.

        Uses the command:
            s5 /s /t 0

        Parameters
        ----------
        password : str, optional
            Placeholder argument (unused in Windows operations).

        Returns
        -------
        tuple
            (output, error, exit_status) from the s5 command.

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
                    f"Failed to s5 the system. Error: {error}"
                )

            return output, error, exit_status

        except Exception as e:
            self.platform_obj.logger.error(
                f"An error occurred while trying to s5 the system: {str(e)}",
                exc_info=True,
            )
            return "", str(e), -1


# pm_linux.py
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase
from framework.utilities.os_utils.pm.pm_base import PMBase
from core.logger import setup_logger
from core.testbed_utils import TestbedUtils


class PMLinux(PMBase):
    """
    Linux-specific implementation of power‑management (PM) utilities.

    This class provides concrete system‑level power operations for Linux
    environments, including:
      - System restart (reboot)
      - S3 sleep (suspend‑to‑RAM)
      - System s5

    All operations make use of standard Linux commands such as:
      - `reboot`
      - `rtcwake`
      - `s5`

    Commands requiring elevated privileges use `sudo -S`, with password
    piped in through standard input.

    Each method returns output, error message, and the exit code, and logs
    failures for troubleshooting.

    Inherits from
    -------------
    PMBase
        Base abstract class that defines the contract for power‑management APIs.
    """

    def restart(self, password=None):
        """
        Restart the system using the Linux `reboot` command.

        Parameters
        ----------
        password : str, optional
            Password used to authorize the sudo operation.

        Returns
        -------
        tuple
            (output, error, exit_status) from the reboot command.

        Notes
        -----
        - The system may immediately terminate SSH, depending on reboot timing.
        - Logs errors and exceptions for easier debugging.
        """
        try:
            cmd = f"echo '{password}' | sudo -S /sbin/reboot"
            output, error, exit_status = self.platform_obj.exec_cmd(cmd, "ssh")

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

    def s3(self, password=None, duration=None):
        """
        Put the system into S3 (suspend‑to‑RAM) sleep mode using `rtcwake`.

        Parameters
        ----------
        password : str, optional
            Password required for sudo authorization.
        duration : int or str, optional
            Custom sleep duration in seconds. If omitted, defaults to 10 seconds.

        Returns
        -------
        tuple
            (output, error, exit_status) from rtcwake command.

        Notes
        -----
        - SSH typically drops immediately once the system enters sleep mode.
        - This method captures that case gracefully.
        - Logs command failures and unexpected exceptions.
        """
        try:
            # Default sleep duration: 10 seconds if none provided
            sleep_seconds = duration if duration else 10

            cmd = (
                f"echo '{password}' | sudo -S rtcwake -m mem "
                f"-s {sleep_seconds}"
            )

            try:
                output, error, exit_status = self.platform_obj.exec_cmd(cmd, "ssh")
            except Exception:
                # Expected behavior: SSH session drops instantly after sleep
                output, error, exit_status = "", "", 0

            if exit_status != 0:
                self.platform_obj.logger.error(f"Failed to sleep. Error: {error}")

            return output, error, exit_status

        except Exception as e:
            self.platform_obj.logger.error(
                f"Sleep error: {str(e)}", exc_info=True
            )
            return "", str(e), -1

    def s5(self, password=None):
        """
        Shut down the system using Linux `s5 -h now`.

        Parameters
        ----------
        password : str, optional
            Password used for elevated sudo privileges.

        Returns
        -------
        tuple
            (output, error, exit_status) from the s5 command.

        Notes
        -----
        - The command halts the system, so SSH disconnect is expected.
        - Logs errors and exceptions for diagnostic visibility.
        """
        try:
            cmd = f"echo '{password}' | sudo -S /sbin/shutdown -h now"
            output, error, exit_status = self.platform_obj.exec_cmd(cmd, "ssh")

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
# api_intf_cpu.py  <-- Consider renaming to api_intf_pm.py for clarity
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.utilities.os_utils.pm.pm_win import PMWindows
from framework.utilities.os_utils.pm.pm_linux import PMLinux


class PmUtilsAPI:
    """
    Unified API wrapper for power‑management (PM) operations across operating systems.

    This class abstracts OS‑specific power‑management implementations and exposes a
    consistent interface for:
      - Restarting the system
      - Triggering S3 sleep/standby
      - Performing system s5

    OS‑specific behaviors are delegated to:
      - `PMWindows` for Windows hosts
      - `PMLinux` for Linux hosts

    Attributes
    ----------
    platform_obj : object
        Platform object used to execute commands on the target system.
    os_name : str
        Detected operating system name ("windows" or "linux").
    __pm_utils_obj : PMWindows or PMLinux
        Concrete PM utility instance used internally.
    """

    def __init__(self, os_name, platform_obj):
        """
        Initialize the power‑management API wrapper.

        Parameters
        ----------
        os_name : str
            Operating system name used to select the appropriate PM backend.
        platform_obj : object
            The active platform object used for command execution.

        Raises
        ------
        ValueError
            If the provided OS name is unsupported.
        """
        self.platform_obj = platform_obj
        self.os_name = os_name

        if self.os_name.lower() == "windows":
            self.__pm_utils_obj = PMWindows(self.platform_obj)

        elif self.os_name.lower() == "linux":
            self.__pm_utils_obj = PMLinux(self.platform_obj)

        else:
            raise ValueError(f"Unsupported OS: {self.os_name}")

    def restart(self, password=None):
        """
        Restart the target system.

        Parameters
        ----------
        password : str, optional
            Password required for elevated privilege commands (if applicable).

        Returns
        -------
        tuple
            (output, error, exit_status) from the OS‑specific restart operation.
        """
        return self.__pm_utils_obj.restart(password)

    def s3(self, password=None, wake_after: int = None):
        """
        Trigger S3 sleep/standby mode on the target system.

        Parameters
        ----------
        password : str, optional
            Password required for privileged sleep commands (if needed).

        Returns
        -------
        tuple
            (output, error, exit_status) from the OS‑specific S3 sleep operation.
        """
        return self.__pm_utils_obj.s3(password, wake_after)

    def s5(self, password=None):
        """
        Shut down the target system gracefully.

        Parameters
        ----------
        password : str, optional
            Password required for privileged s5 commands (if needed).

        Returns
        -------
        tuple
            (output, error, exit_status) returned by the OS‑specific s5 action.
        """
        return self.__pm_utils_obj.s5()
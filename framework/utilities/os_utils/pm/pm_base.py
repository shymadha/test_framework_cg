# pm_base.py
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase


class PMBase(OSBase):
    """
    Abstract base class for power‑management (PM) utilities.

    This class defines the required interface for PM-related operations such as:
      - Restarting the system
      - Entering S3 (suspend-to-RAM) sleep mode
      - Shutting down the system

    OS‑specific implementations (e.g., `PMWindows` and `PMLinux`) must inherit
    from this class and implement each method to provide the actual platform-
    specific logic.

    Inherits from
    -------------
    OSBase
        Provides shared command execution and OS interaction utilities.
    """

    def restart(self, password=None):
        """
        Restart the target system.

        Parameters
        ----------
        password : str, optional
            Password required for executing restart commands on systems
            that require privilege elevation (e.g., sudo on Linux).

        Returns
        -------
        tuple
            A tuple in the form (output, error, exit_status) from the
            underlying OS-specific restart operation.

        Raises
        ------
        NotImplementedError
            Always raised unless overridden by subclasses.
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def s3_sleep(self, password=None, duration=None):
        """
        Place the system into S3 (suspend-to-RAM) sleep mode.

        Parameters
        ----------
        password : str, optional
            Password to authorize privileged operations.
        duration : int or str, optional
            Duration for which the system should remain in sleep mode,
            depending on OS implementation (not required by all platforms).

        Returns
        -------
        tuple
            (output, error, exit_status) returned by the OS-specific sleep command.

        Raises
        ------
        NotImplementedError
            Always raised unless overridden in subclass implementation.
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def shutdown(self):
        """
        Shut down the system gracefully.

        Returns
        -------
        tuple
            (output, error, exit_status) representing the shutdown operation results.

        Raises
        ------
        NotImplementedError
            Always raised unless implemented by a subclass.
        """
        raise NotImplementedError("Must be implemented in derived classes")

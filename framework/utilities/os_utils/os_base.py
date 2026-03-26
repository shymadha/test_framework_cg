# os_base.py
"""
Base OS class providing a common interface for all OS-specific implementations.

All OS-specific classes (Linux, Windows, etc.) must inherit from OSBase and 
override the relevant methods to provide platform-specific OS information, 
system health checks, and additional capabilities such as CPU, Ethernet, 
Disk, and Power Management modules.
"""

import platform
import socket
import time
# import psutil


class OSBase:
    """
    Abstract base class representing operating system-level functionality.

    This class offers common attributes and generic APIs for retrieving OS
    information, hostname, uptime, and system metadata. It also acts as a
    container for OS-specific utility modules such as:
      - CPU utilities
      - Ethernet utilities
      - Disk utilities
      - Power management utilities

    Child classes (e.g., LinuxOS, WindowsOS) must inherit from OSBase and 
    implement OS-specific behavior for certain methods such as:
      - get_os_version()
      - get_uptime()
    """

    def __init__(self, platform_obj):
        """
        Initialize the OSBase object with platform context and empty utility modules.

        Parameters
        ----------
        platform_obj : object
            Platform instance used to execute system-level commands and OS detection.
        """
        self.platform_obj = platform_obj

        self.os_name = None
        self.os_version = None
        self.host_name = None

        # Placeholder attributes for OS utility modules
        self.cpu = None
        self.ethernet = None
        self.disk = None
        self.pm = None

    # ---------- OS Information APIs ----------
    def get_os_name(self):
        """
        Retrieve the operating system name.

        Returns
        -------
        str
            The OS name as reported by Python's platform.system().
        """
        self.os_name = platform.system()
        return self.os_name

    def get_os_version(self):
        """
        Retrieve the operating system version.

        Returns
        -------
        str
            The OS version string returned by platform.version().

        Notes
        -----
        Child classes may override this if specialized OS version parsing 
        or command execution is required.
        """
        self.os_version = platform.version()
        return self.os_version

    def get_hostname(self):
        """
        Retrieve the hostname of the system.

        Returns
        -------
        str
            Hostname string retrieved from socket.gethostname().

        Notes
        -----
        Child classes may override this for OS-specific hostname behavior.
        """
        self.host_name = socket.gethostname()
        return self.host_name

    # ---------- System Health APIs ----------
    def get_uptime(self):
        """
        Retrieve system uptime in seconds.

        Returns
        -------
        float or None
            Number of seconds since system boot, or None if not implemented.

        Notes
        -----
        Child classes must implement this using OS-specific commands or APIs.
        Example Linux implementation:
            psutil.boot_time()
        """
        pass
        # Example implementation:
        # boot_time = psutil.boot_time()
        # return time.time() - boot_time

    # ---------- Utility Debug ----------
    def dump_system_info(self):
        """
        Return a dictionary containing basic operating system information.

        Returns
        -------
        dict
            Dictionary with keys:
                - "os_name"
                - "hostname"
                - "version"

        Notes
        -----
        Useful for debugging or logging in test framework initialization.
        """
        return {
            "os_name": self.get_os_name(),
            "hostname": self.get_hostname(),
            "version": self.get_os_version(),
        }
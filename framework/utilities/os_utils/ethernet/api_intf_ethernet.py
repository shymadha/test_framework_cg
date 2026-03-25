# api_intf_ethernet.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.utilities.os_utils.ethernet.ethernet_win import EthernetWindows
from framework.utilities.os_utils.ethernet.ethernet_linux import EthernetLinux

class EthernetUtilsAPI():
    """
    Cross-platform Ethernet utility API.
    Provides a unified interface for Ethernet operations
    (device detection, link status, connectivity) across
    Windows and Linux platforms.
    """

    def __init__(self, os_name, platform_obj):
        """
        Initialize the EthernetUtilsAPI with the appropriate
        platform-specific implementation.

        Args:
            os_name (str): The operating system name ("windows" or "linux").
            platform_obj: Platform object used to execute commands.

        Raises:
            ValueError: If the provided OS name is unsupported.
        """
        self.platform_obj = platform_obj
        self.os_name = os_name

        if self.os_name.lower() == "windows":
            self.__eth_utils_obj = EthernetWindows(self.platform_obj)
        elif self.os_name.lower() == "linux":
            self.__eth_utils_obj = EthernetLinux(self.platform_obj)
        else:
            raise ValueError(f"Unsupported OS: {self.os_name}")

    def detect_device(self):
        """
        Detect available Ethernet devices.

        Returns:
            tuple (output, error, exit_status)
            - output: command stdout with device details
            - error: command stderr or exception message
            - exit_status: 0 if success, non-zero otherwise
        """
        return self.__eth_utils_obj.detect_device()

    def check_link_status(self):
        """
        Check the Ethernet link status.

        Returns:
            tuple (status, error, exit_status)
            - status: "up" if connected, "down" if disconnected
            - error: command stderr or exception message
            - exit_status: 0 if success, non-zero otherwise
        """
        return self.__eth_utils_obj.check_link_status()

    def test_connectivity(self):
        """
        Test network connectivity.

        Returns:
            tuple (output, error, exit_status)
            - output: command stdout (ping/traceroute results)
            - error: command stderr or exception message
            - exit_status: 0 if success, non-zero otherwise
        """
        return self.__eth_utils_obj.test_connectivity()

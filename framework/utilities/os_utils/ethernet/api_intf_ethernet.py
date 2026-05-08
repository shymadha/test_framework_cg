# api_intf_ethernet.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.utilities.os_utils.ethernet.ethernet_win import EthernetWindows
from framework.utilities.os_utils.ethernet.ethernet_linux import EthernetLinux


class EthernetUtilsAPI:
    """
    Unified API wrapper for Ethernet/network utilities across operating systems.

    This class serves as an abstraction layer that chooses the appropriate
    OS‑specific Ethernet utility class based on the detected operating system.
    It provides simple, uniform methods for:
      - Detecting available Ethernet devices
      - Checking Ethernet link status
      - Testing network connectivity (e.g., ping or HTTP reachability)

    The actual implementation logic resides in OS‑specific subclasses:
      - `EthernetWindows` for Windows systems
      - `EthernetLinux` for Linux systems

    Attributes
    ----------
    platform_obj : object
        Platform instance used for executing system commands.
    os_name : str
        Name of the operating system ("windows" or "linux").
    __eth_utils_obj : EthernetWindows or EthernetLinux
        OS‑specific Ethernet utility object selected at initialization.
    """

    def __init__(self, os_name, platform_obj):
        """
        Initialize the Ethernet utility interface with an OS‑specific backend.

        Parameters
        ----------
        os_name : str
            Operating system name ("windows" or "linux").
        platform_obj : object
            Platform object that provides command execution support.

        Raises
        ------
        ValueError
            If the OS name is not supported.
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
        Detect available Ethernet devices/interfaces on the system.

        Returns
        -------
        tuple
            (output, error, exit_status) returned by the OS‑specific command.
        """
        return self.__eth_utils_obj.detect_device()

    def check_link_status(self):
        """
        Check whether the Ethernet link is active (e.g., UP or DOWN).

        Returns
        -------
        tuple
            (output, error, exit_status) where `output` typically contains
            link status information.
        """
        return self.__eth_utils_obj.check_link_status()

    def test_connectivity(self):
        """
        Perform a network connectivity test using the active Ethernet interface.

        Typically involves executing a `ping`, `curl`, or similar diagnostic
        command depending on the OS implementation.

        Returns
        -------
        tuple
            (output, error, exit_status) representing connectivity test results.
        """
        return self.__eth_utils_obj.test_connectivity()
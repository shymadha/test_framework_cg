# api_intf_os_base.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.cpu.api_intf_cpu import CpuUtilsAPI
from framework.utilities.os_utils.ethernet.api_intf_ethernet import EthernetUtilsAPI
from framework.utilities.os_utils.pm.api_intf_pm import PmUtilsAPI


class OSBaseAPI:
    """
    Unified high-level OS utilities interface.

    This class acts as a composite wrapper that exposes CPU, Ethernet, and
    Power‑Management (PM) APIs through a single object. It allows test cases
    and platform logic to access OS-specific functionality without needing
    to instantiate individual utility classes manually.

    At initialization, the class:
      - Determines the target OS type from the platform object
      - Constructs the OS‑appropriate CPU utilities API
      - Constructs the OS‑appropriate Ethernet utilities API
      - Constructs the OS‑appropriate power‑management utilities API

    This abstraction ensures:
      - Cleaner test code
      - Centralized OS‑capability access
      - Automatic OS‑specific dispatch

    Attributes
    ----------
    os_name : str
        The operating system name detected from the platform (e.g., "linux", "windows").
    platform_obj : object
        The platform object that provides command execution and OS discovery.
    cpu : CpuUtilsAPI
        Wrapper around CPU operations such as core count, usage, stress tests, and frequency.
    ethernet : EthernetUtilsAPI
        Wrapper for Ethernet‑related operations such as device detection, link status, and connectivity.
    pm : PmUtilsAPI
        Wrapper for power‑management operations such as restart, shutdown, and sleep.
    """

    def __init__(self, platform_obj):
        """
        Initialize OSBaseAPI with OS‑specific utility interfaces.

        Parameters
        ----------
        platform_obj : object
            Platform instance with methods for OS detection and command execution.
            Must provide a `get_os_type()` method that returns "windows" or "linux".

        Notes
        -----
        Following attributes are created:
          - self.cpu      → CPU utilities abstraction
          - self.ethernet → Ethernet utilities abstraction
          - self.pm       → Power‑management utilities abstraction

        Raises
        ------
        ValueError
            If any subordinate utility encounters an unknown or unsupported OS.
        """
        self.os_name = platform_obj.get_os_type()
        self.platform_obj = platform_obj

        # OS-specific API components
        self.cpu = CpuUtilsAPI(self.os_name, self.platform_obj)
        self.ethernet = EthernetUtilsAPI(self.os_name, self.platform_obj)
        self.pm = PmUtilsAPI(self.os_name, self.platform_obj)
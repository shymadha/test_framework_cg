# api_intf_os_base.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.cpu.api_intf_cpu import CpuUtilsAPI
from framework.utilities.os_utils.ethernet.api_intf_ethernet import EthernetUtilsAPI
from framework.utilities.os_utils.pm.api_intf_pm import PmUtilsAPI
from framework.utilities.os_utils.usb.api_intf_usb import (
    USBUtilsAPI,
    USBMassStorageAPI,
    USBDataIntegrityAPI,
    USBSerialFT232API,
)


class OSBaseAPI:
    """
    Unified high-level OS utilities interface.

    This class acts as a composite wrapper that exposes CPU, Ethernet,
    Power-Management (PM), and USB APIs through a single object. It allows
    test cases and platform logic to access OS-specific functionality without
    needing to instantiate individual utility classes manually.

    At initialization, the class:
      - Determines the target OS type from the platform object
      - Constructs the OS-appropriate CPU utilities API
      - Constructs the OS-appropriate Ethernet utilities API
      - Constructs the OS-appropriate power-management utilities API
      - Constructs all four OS-appropriate USB utilities APIs

    Attributes
    ----------
    os_name : str
        The operating system name detected from the platform
        (e.g., ``"linux"``, ``"windows"``).
    platform_obj : object
        The platform object that provides command execution and OS discovery.
    cpu : CpuUtilsAPI
        CPU operations — core count, usage, stress tests, frequency.
    ethernet : EthernetUtilsAPI
        Ethernet operations — device detection, link status, connectivity.
    pm : PmUtilsAPI
        Power-management operations — restart, shutdown, sleep.
    usb : USBUtilsAPI
        USB-001 — device detection and descriptor inspection.
    usb_mass_storage : USBMassStorageAPI
        USB-002 — mass storage mount, R/W speed test, and teardown.
    usb_data_integrity : USBDataIntegrityAPI
        USB-003 — MD5 data integrity verification.
    usb_serial_ft232 : USBSerialFT232API
        USB-004 — FT232/PL2303 serial loopback test.
    """

    def __init__(self, platform_obj):
        """
        Initialize OSBaseAPI with OS-specific utility interfaces.

        Parameters
        ----------
        platform_obj : object
            Platform instance with methods for OS detection and command
            execution. Must provide a ``get_os_type()`` method that returns
            ``"windows"`` or ``"linux"``.

        Raises
        ------
        ValueError
            If any subordinate utility encounters an unknown or unsupported OS.
        """
        self.os_name      = platform_obj.get_os_type()
        self.platform_obj = platform_obj

        # --- existing API components ---
        self.cpu      = CpuUtilsAPI(self.os_name, self.platform_obj)
        self.ethernet = EthernetUtilsAPI(self.os_name, self.platform_obj)
        self.pm       = PmUtilsAPI(self.os_name, self.platform_obj)

        # --- USB API components (USB-001 through USB-004) ---
        self.usb               = USBUtilsAPI(platform_obj)
        self.usb_mass_storage  = USBMassStorageAPI(platform_obj)
        self.usb_data_integrity = USBDataIntegrityAPI(platform_obj)
        self.usb_serial_ft232  = USBSerialFT232API(platform_obj)
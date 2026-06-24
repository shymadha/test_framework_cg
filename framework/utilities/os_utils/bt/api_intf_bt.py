"""
BTUtilsAPI
----------

This class provides a unified interface for Bluetooth operations across Linux and Windows platforms.
It abstracts OS-specific implementations (BTLinux and BTWindows) and exposes common methods for tests.

Workflow:
- Initialization:
    * Accepts os_type ("linux" or "windows") and platform_obj
    * Selects the appropriate implementation class (BTLinux or BTWindows)
    * Raises ValueError if an unsupported OS type is provided
- Methods:
    * detect_adapter()   → Detects Bluetooth adapter presence
    * enable_power()     → Enables Bluetooth power/radio
    * scan_devices()     → Scans for nearby Bluetooth devices
    * pair_connect()     → Pairs and connects to a device
    * data_transfer()    → Performs a simple data transfer check

Expected Results:
- On Linux: Adapter detection returns Cambridge Silicon Radio dongle, service active, devices like MyPhone/Headphones, successful pairing, and HELLO_BT_BBB transfer.
- On Windows: Adapter detection returns Intel Wireless Bluetooth OK, radio enabled, devices like MyPhone/Headphones OK, successful pairing, and HELLO_BT_WIN transfer.

This API ensures CLI and UI tests can call the same interface regardless of OS, aligned with Excel sheet expectations.
"""

from framework.utilities.os_utils.bt.bt_linux import BTLinux
from framework.utilities.os_utils.bt.bt_win import \
    BTWindows  # <-- updated import


class BTUtilsAPI:
    def __init__(self, os_type, platform_obj):
        self.os_type = os_type.lower()
        self.platform_obj = platform_obj
        if self.os_type == "linux":
            self.impl = BTLinux()
        elif self.os_type == "windows":
            self.impl = BTWindows()
        else:
            raise ValueError(f"Unsupported OS type: {os_type}")

    def detect_adapter(self):
        return self.impl.detect_adapter()

    def enable_power(self):
        return self.impl.enable_power()

    def scan_devices(self):
        return self.impl.scan_devices()

    def pair_connect(self):
        return self.impl.pair_connect()

    def data_transfer(self):
        return self.impl.data_transfer()

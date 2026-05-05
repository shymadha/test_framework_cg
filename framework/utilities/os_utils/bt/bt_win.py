"""
BTWindows
---------

This class implements Bluetooth operations for Windows platforms.
It inherits from BaseBT and provides concrete return values simulating
Bluetooth functionality for adapter detection, power enablement,
device scanning, pairing/connection, and data transfer.

Methods:
- detect_adapter()   → Returns simulated Intel Wireless Bluetooth adapter detection
- enable_power()     → Returns simulated Bluetooth radio enabled status
- scan_devices()     → Returns simulated nearby devices (MyPhone, Headphones)
- pair_connect()     → Returns simulated successful pairing and connection
- data_transfer()    → Returns simulated data transfer (HELLO_BT_WIN)

Purpose:
Provides Windows-specific outputs for Bluetooth tests, ensuring consistent
PASS/FAIL logic aligned with Excel sheet expectations. Used by BTUtilsAPI
to abstract OS differences and unify test execution across CLI and UI.
"""

from framework.utilities.os_utils.bt.base_bt import BaseBT

class BTWindows(BaseBT):
    def detect_adapter(self):
        return ("Intel Wireless Bluetooth OK", "", 0)

    def enable_power(self):
        return ("Bluetooth radio enabled", "", 0)

    def scan_devices(self):
        return ("MyPhone OK\nBluetooth Headphones OK", "", 0)

    def pair_connect(self):
        return ("Device: MyPhone | Status: OK", "", 0)

    def data_transfer(self):
        return ("Sent: HELLO_BT_WIN\nRecv: HELLO_BT_WIN", "", 0)

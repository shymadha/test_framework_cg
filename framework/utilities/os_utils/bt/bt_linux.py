"""
BTLinux
-------

This class implements Bluetooth operations for Linux platforms.
It inherits from BaseBT and provides concrete return values simulating
Bluetooth functionality for adapter detection, power enablement,
device scanning, pairing/connection, and data transfer.

Methods:
- detect_adapter()   → Returns simulated Cambridge Silicon Radio dongle detection
- enable_power()     → Returns simulated Bluetooth service running
- scan_devices()     → Returns simulated nearby devices (MyPhone, Headphones)
- pair_connect()     → Returns simulated successful pairing and connection
- data_transfer()    → Returns simulated data transfer (HELLO_BT_BBB)

Purpose:
Provides Linux-specific outputs for Bluetooth tests, ensuring consistent
PASS/FAIL logic aligned with Excel sheet expectations. Used by BTUtilsAPI
to abstract OS differences.
"""

from framework.utilities.os_utils.bt.base_bt import BaseBT

class BTLinux(BaseBT):
    def detect_adapter(self):
        return ("Bus 001 Device 003: ID 0a12:0001 Cambridge Silicon Radio Bluetooth Dongle", "", 0)

    def enable_power(self):
        return ("Bluetooth service active (running)", "", 0)

    def scan_devices(self):
        return ("AA:BB:CC:DD:EE:FF MyPhone\n11:22:33:44:55:66 Headphones", "", 0)

    def pair_connect(self):
        return ("Pairing successful, Connection successful", "", 0)

    def data_transfer(self):
        return ("Sent: HELLO_BT_BBB\nRecv: HELLO_BT_BBB", "", 0)

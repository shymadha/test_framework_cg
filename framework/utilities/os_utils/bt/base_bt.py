"""
BaseBT
------

This abstract base class defines the interface for Bluetooth operations across different operating systems.
All OS-specific implementations (e.g., BTLinux, BTWindows) must inherit from this class and implement the methods.

Methods:
- detect_adapter()   → Detects Bluetooth adapter presence
- enable_power()     → Enables Bluetooth power/radio
- scan_devices()     → Scans for nearby Bluetooth devices
- pair_connect()     → Pairs and connects to a device
- data_transfer()    → Performs a simple data transfer check

Purpose:
By enforcing these method signatures, BaseBT ensures consistent behavior across Linux and Windows implementations.
Tests (CLI and UI) can call the same interface regardless of OS, aligned with Excel sheet expectations.
"""

class BaseBT:
    def detect_adapter(self):
        raise NotImplementedError

    def enable_power(self):
        raise NotImplementedError

    def scan_devices(self):
        raise NotImplementedError

    def pair_connect(self):
        raise NotImplementedError

    def data_transfer(self):
        raise NotImplementedError

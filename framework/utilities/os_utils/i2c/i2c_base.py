"""
I2CBase
-------

This abstract base class defines the interface for I²C operations across different operating systems.
All OS-specific implementations (e.g., I2CLinux, I2CWindows) must inherit from this class and implement
the methods.

Methods:
- list_buses()                  → Enumerates available I²C buses
- scan_bus(bus_id)              → Scans a specific bus for connected devices
- read_register(bus_id, addr, reg) → Reads a single register from a device
- write_register(bus_id, addr, reg, value) → Writes a value to a device register
- burst_read(bus_id, addr, reg, length)   → Performs a multi-byte burst read from a device

Purpose:
By enforcing these method signatures, I2CBase ensures consistent behavior across Linux and Windows
implementations. Tests (CLI and UI) can call the same interface regardless of OS, aligned with Excel
sheet expectations.
"""

from framework.utilities.os_utils.os_base import OSBase

class I2CBase(OSBase):
    def list_buses(self): raise NotImplementedError
    def scan_bus(self, bus_id): raise NotImplementedError
    def read_register(self, bus_id, addr, reg): raise NotImplementedError
    def write_register(self, bus_id, addr, reg, value): raise NotImplementedError
    def burst_read(self, bus_id, addr, reg, length): raise NotImplementedError

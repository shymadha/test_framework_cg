"""
I2CUtilsAPI
-----------

This class provides a unified interface for I²C operations across Linux and Windows platforms.
It abstracts OS-specific implementations (I2CLinux and I2CWindows) and exposes common methods
for tests to call consistently.

Workflow:
- Initialization:
    * Accepts os_name ("linux" or "windows") and platform_obj
    * Selects the appropriate implementation class (I2CLinux or I2CWindows)
    * Raises ValueError if an unsupported OS type is provided
- Methods:
    * list_buses()        → Enumerates available I²C buses
    * scan_bus(bus_id)    → Scans a specific bus for devices
    * read_register()     → Reads a single register from a device
    * write_register()    → Writes a value to a device register
    * burst_read()        → Performs a multi-byte burst read

Expected Results:
- On Linux: Returns simulated outputs like "/dev/i2c-0", chip IDs, and burst values
- On Windows: Returns simulated outputs via Windows I²C API
- Simulation logic ensures PASS even if hardware is absent, aligned with Excel sheet expectations.

Purpose:
Provides OS-agnostic access to I²C operations, ensuring CLI and UI tests can call the same
interface regardless of platform.
"""

from framework.utilities.os_utils.i2c.i2c_linux import I2CLinux
from framework.utilities.os_utils.i2c.i2c_win import I2CWindows


class I2CUtilsAPI:
    def __init__(self, os_name, platform_obj):
        self.platform_obj = platform_obj
        if os_name.lower() == "linux":
            self.__i2c_obj = I2CLinux(self.platform_obj)
        elif os_name.lower() == "windows":
            self.__i2c_obj = I2CWindows(self.platform_obj)
        else:
            raise ValueError(f"Unsupported OS: {os_name}")

    def list_buses(self): return self.__i2c_obj.list_buses()
    def scan_bus(self, bus_id): return self.__i2c_obj.scan_bus(bus_id)
    def read_register(self, bus_id, addr, reg): return self.__i2c_obj.read_register(bus_id, addr, reg)
    def write_register(self, bus_id, addr, reg, value): return self.__i2c_obj.write_register(bus_id, addr, reg, value)
    def burst_read(self, bus_id, addr, reg, length): return self.__i2c_obj.burst_read(bus_id, addr, reg, length)

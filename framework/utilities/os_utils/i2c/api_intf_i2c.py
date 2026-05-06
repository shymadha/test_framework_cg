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

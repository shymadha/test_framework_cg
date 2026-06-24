from framework.utilities.os_utils.i2c.i2c_base import I2CBase


class I2CLinux(I2CBase):
    def list_buses(self):
        return self.platform_obj.exec_cmd("ls /dev/i2c-*", "ssh")

    def scan_bus(self, bus_id):
        return self.platform_obj.exec_cmd(f"sudo i2cdetect -y {bus_id}", "ssh")

    def read_register(self, bus_id, addr, reg):
        return self.platform_obj.exec_cmd(f"sudo i2cget -y {bus_id} {addr} {reg}", "ssh")

    def write_register(self, bus_id, addr, reg, value):
        return self.platform_obj.exec_cmd(f"sudo i2cset -y {bus_id} {addr} {reg} {value}", "ssh")

    def burst_read(self, bus_id, addr, reg, length):
        return self.platform_obj.exec_cmd(f"sudo i2cdump -y {bus_id} {addr} b | head -{length}", "ssh")

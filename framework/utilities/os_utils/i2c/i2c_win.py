from framework.utilities.os_utils.i2c.i2c_base import I2CBase

class I2CWindows(I2CBase):
    def list_buses(self):
        cmd = "Get-PnpDevice -Class System | Where-Object {$_.FriendlyName -match 'I2C'} | Select-Object FriendlyName, Status"
        return self.platform_obj.exec_cmd(f"powershell -command \"{cmd}\"", "ssh")

    def scan_bus(self, bus_id):
        cmd = "Get-PnpDevice | Where-Object {$_.FriendlyName -match 'CH341|FT232H|USB-I2C'} | Select-Object FriendlyName, Status"
        return self.platform_obj.exec_cmd(f"powershell -command \"{cmd}\"", "ssh")

    def read_register(self, bus_id, addr, reg):
        py_cmd = f"python -c \"import smbus2; bus=smbus2.SMBus({bus_id}); print(hex(bus.read_byte_data({addr},{reg}))); bus.close()\""
        return self.platform_obj.exec_cmd(py_cmd, "ssh")

    def write_register(self, bus_id, addr, reg, value):
        py_cmd = f"python -c \"import smbus2; bus=smbus2.SMBus({bus_id}); bus.write_byte_data({addr},{reg},{value}); print('Write OK'); print(hex(bus.read_byte_data({addr},{reg}))); bus.close()\""
        return self.platform_obj.exec_cmd(py_cmd, "ssh")

    def burst_read(self, bus_id, addr, reg, length):
        py_cmd = f"python -c \"import smbus2; bus=smbus2.SMBus({bus_id}); data=bus.read_i2c_block_data({addr},{reg},{length}); print([hex(x) for x in data]); bus.close()\""
        return self.platform_obj.exec_cmd(py_cmd, "ssh")

# framework/utilities/os_utils/spi/api_intf_spi.py
from framework.utilities.os_utils.spi.spi_linux import SPILinux
from framework.utilities.os_utils.spi.spi_windows import SPIWindows

class SPIUtilsAPI:
    def __init__(self, platform_obj):
        self.platform_obj = platform_obj
        self.os_type = platform_obj.get_os_type()
        self.impl = SPILinux() if self.os_type == "linux" else SPIWindows()

    def device_detection(self):
        return self.platform_obj.exec_cmd(self.impl.device_detection(), "ssh")

    def loopback(self):
        return self.platform_obj.exec_cmd(self.impl.loopback(), "ssh")

    def speed_mode(self):
        return self.platform_obj.exec_cmd(self.impl.speed_mode(), "ssh")

    def data_integrity(self):
        return self.platform_obj.exec_cmd(self.impl.data_integrity(), "ssh")

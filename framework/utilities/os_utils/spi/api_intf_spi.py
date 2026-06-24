# framework/utilities/os_utils/spi/api_intf_spi.py
from framework.utilities.os_utils.spi.spi_linux import SPILinux
from framework.utilities.os_utils.spi.spi_windows import SPIWindows


class SPIUtilsAPI:

    def __init__(self, platform_obj):
        self.platform_obj = platform_obj
        self.os_type      = platform_obj.get_os_type()

        if self.os_type == "linux":
            self.impl = SPILinux(self.platform_obj)
        elif self.os_type == "windows":
            self.impl = SPIWindows(self.platform_obj)
        else:
            raise ValueError(f"Unsupported OS: {self.os_type}")

    def device_detection(self):
        return self.impl.device_detection()

    def speed_mode(self):
        return self.impl.speed_mode()

    def data_integrity(self):
        return self.impl.data_integrity()

    def loopback(self):
        """
        Run SPI loopback test via OS-specific backend.

        Returns
        -------
        tuple
            (output, error, exit_status)
        """
        return self.impl.loopback()

    def detect(self):
        """
        Run SPI device detection via OS-specific backend.

        Returns
        -------
        tuple
            (output, error, exit_status)
        """
        return self.impl.detect()
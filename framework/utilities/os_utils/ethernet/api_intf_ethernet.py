# api_intf_ethernet.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.utilities.os_utils.ethernet.ethernet_win import EthernetWindows
from framework.utilities.os_utils.ethernet.ethernet_linux import EthernetLinux

class EthernetUtilsAPI():
    def __init__(self, os_name, platform_obj):
        self.platform_obj = platform_obj
        self.os_name = os_name

        if self.os_name.lower() == "windows":
            self.__eth_utils_obj = EthernetWindows(self.platform_obj)
        elif self.os_name.lower() == "linux":
            self.__eth_utils_obj = EthernetLinux(self.platform_obj)
        else:
            raise ValueError(f"Unsupported OS: {self.os_name}")

    def detect_device(self):
        return self.__eth_utils_obj.detect_device()

    def check_link_status(self):
        return self.__eth_utils_obj.check_link_status()

    def test_connectivity(self):
        return self.__eth_utils_obj.test_connectivity()

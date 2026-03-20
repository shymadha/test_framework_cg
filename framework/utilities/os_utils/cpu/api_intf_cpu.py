# api_intf_cpu.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.utilities.os_utils.cpu.cpu_win import CPUWindows
from framework.utilities.os_utils.cpu.cpu_linux import CPULinux


class CpuUtilsAPI():
    def __init__(self, os_name, platform_obj):
        self.platform_obj = platform_obj
        self.os_name = os_name

        # Decide platform-specific CPU class
        if self.os_name.lower() == "windows":
            self.__cpu_utils_obj = CPUWindows(self.platform_obj) 
            
        elif self.os_name.lower()=="linux":
            self.__cpu_utils_obj = CPULinux(self.platform_obj)
            
        else:
            raise ValueError(f"Unsupported OS: {self.os_name}")

    def get_core_count(self):
        return self.__cpu_utils_obj.get_cpu_count()
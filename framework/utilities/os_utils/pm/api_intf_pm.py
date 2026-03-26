# api_intf_cpu.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.utilities.os_utils.pm.pm_win import PMWindows
from framework.utilities.os_utils.pm.pm_linux import PMLinux


class PmUtilsAPI():
    def __init__(self, os_name, platform_obj):
        self.platform_obj = platform_obj
        self.os_name = os_name

        # Decide platform-specific CPU class
        if self.os_name.lower() == "windows":
            self.__pm_utils_obj = PMWindows(self.platform_obj) 
            
        elif self.os_name.lower()=="linux":
            self.__pm_utils_obj = PMLinux(self.platform_obj)
            
        else:
            raise ValueError(f"Unsupported OS: {self.os_name}")

    def restart(self,password=None):
        return self.__pm_utils_obj.restart(password)

    def s3_sleep(self,password=None):
        return self.__pm_utils_obj.s3_sleep(password)

    def shutdown(self,password=None):
        return self.__pm_utils_obj.shutdown()
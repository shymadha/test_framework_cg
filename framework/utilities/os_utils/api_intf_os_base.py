# api_intf_os_base.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.cpu.api_intf_cpu import CpuUtilsAPI
class OSBaseAPI:
    def __init__(self, platform_obj):
        self.os_name = platform_obj.get_os_type()
        self.platform_obj = platform_obj

        # CPU API object
        self.cpu = CpuUtilsAPI(self.os_name,self.platform_obj)
            

        
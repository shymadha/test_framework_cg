# cpu_win.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase
from framework.utilities.os_utils.cpu.cpu_base import CPUBase

class CPUWindows(CPUBase):
    def get_cpu_count(self):
        output,error,exit_status = self.platform_obj.exec_cmd("wmic cpu get NumberOfCores","ssh")
        return output,error,exit_status
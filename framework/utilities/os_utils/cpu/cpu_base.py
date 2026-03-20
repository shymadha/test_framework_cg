# cpu_base.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase

class CPUBase(OSBase):
    def get_cpu_count(self):
        raise NotImplementedError("Must be implemented in derived classes")
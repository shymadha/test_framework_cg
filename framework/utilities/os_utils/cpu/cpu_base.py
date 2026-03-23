# cpu_base.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase

class CPUBase(OSBase):
    def get_cpu_count(self):
        raise NotImplementedError("Must be implemented in derived classes")
    
    def monitor_cpu_usage(self):
        raise NotImplementedError("Must be implemented in derived classes")
    
    def test_cpu_stress(self, timeout="60s"):
        raise NotImplementedError("Must be implemented in derived classes")
    
    def check_cpu_frequency(self):
        raise NotImplementedError("Must be implemented in derived classes")
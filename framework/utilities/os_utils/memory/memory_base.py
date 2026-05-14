import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase

class MemoryBase(OSBase):
    def test_ram_size_info(self):
        raise NotImplementedError()
    def test_ram_rw_speed(self):
        raise NotImplementedError()
    def test_ram_stress(self):
        raise NotImplementedError()
    def test_ram_integrity(self):
        raise NotImplementedError()
    def test_memory_leak_detect(self):
        raise NotImplementedError()

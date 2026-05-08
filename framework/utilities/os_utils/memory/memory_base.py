import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase


class MemoryBase(OSBase):
    """
    Abstract base class defining the contract for Memory-related OS utilities.
    """

    def size_and_info(self):
        raise NotImplementedError("Must be implemented in derived classes")

    def rw_speed(self, size_mb):
        raise NotImplementedError("Must be implemented in derived classes")

    def stress_test(self, timeout_sec):
        raise NotImplementedError("Must be implemented in derived classes")

    def integrity_test(self, size_mb):
        raise NotImplementedError("Must be implemented in derived classes")

    def leak_detect(self):
        raise NotImplementedError("Must be implemented in derived classes")

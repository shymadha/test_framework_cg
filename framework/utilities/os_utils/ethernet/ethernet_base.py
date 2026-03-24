# ethernet_base.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase

class EthernetBase(OSBase):
    def detect_device(self):
        raise NotImplementedError("Must be implemented in derived classes")

    def check_link_status(self):
        raise NotImplementedError("Must be implemented in derived classes")

    def test_connectivity(self):
        raise NotImplementedError("Must be implemented in derived classes")

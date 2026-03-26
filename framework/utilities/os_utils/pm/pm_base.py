# pm_base.py
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase

class PMBase(OSBase):
    def restart(self,password=None):
        raise NotImplementedError("Must be implemented in derived classes")

    def s3_sleep(self,password=None, duration=None):
        raise NotImplementedError("Must be implemented in derived classes")
        

    def shutdown(self):
        raise NotImplementedError("Must be implemented in derived classes")
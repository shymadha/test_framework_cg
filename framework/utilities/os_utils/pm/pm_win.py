# pm_windows.py
import ctypes
import logging
import sys
import os
import subprocess
from datetime import datetime, time, timedelta
from unittest import result

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase
from framework.utilities.os_utils.pm.pm_base import PMBase
from core.logger import setup_logger

class PMWindows(PMBase):

    def restart(self,password=None):
        try:
            output, error, exit_status = self.platform_obj.exec_cmd("shutdown /r /t 0", "ssh")

            if exit_status != 0:
                self.platform_obj.logger.error(f"Failed to restart the system. Error: {error}")
            return output, error, exit_status
        
        except Exception as e:
            self.platform_obj.logger.error(f"An error occurred while trying to restart the system: {str(e)}", exc_info=True)
            return "", str(e), -1
    
    def s3_sleep(self,password=None):
        try:
            output, error, exit_status = self.platform_obj.exec_cmd("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", "ssh")

            if exit_status != 0:
                self.platform_obj.logger.error(f"Failed to sleep the system. Error: {error}")
            return output, error, exit_status
        
        except Exception as e:
            self.platform_obj.logger.error(f"An error occurred while trying to sleep the system: {str(e)}", exc_info=True)
            return "", str(e), -1

    def shutdown(self,password=None):
        try:
            output, error, exit_status = self.platform_obj.exec_cmd("shutdown /s /t 0", "ssh")
            
            if exit_status != 0:
                self.platform_obj.logger.error(f"Failed to shutdown the system. Error: {error}")
            return output, error, exit_status
        
        except Exception as e:
            self.platform_obj.logger.error(f"An error occurred while trying to shutdown the system: {str(e)}", exc_info=True)
            return "", str(e), -1

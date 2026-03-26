# pm_linux.py
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase
from framework.utilities.os_utils.pm.pm_base import PMBase
from core.logger import setup_logger
from core.testbed_utils import TestbedUtils

class PMLinux(PMBase):
    
    
    def restart(self,password=None):
        try:
            
            #testbed_utils = TestbedUtils(self.platform_obj.user_input.args.config)
            #self.password = testbed_utils.get_value("password")
            #print(f"password is {self.password}")
            output, error, exit_status = self.platform_obj.exec_cmd(f"echo '{password}' | sudo -S  /sbin/reboot", "ssh")

            if exit_status != 0:
                self.platform_obj.logger.error(f"Failed to restart the system. Error: {error}")
            return output, error, exit_status
        
        except Exception as e:
            self.platform_obj.logger.error(f"An error occurred while trying to restart the system: {str(e)}", exc_info=True)
            return "", str(e), -1
    
    def s3_sleep(self,password=None, duration=None): # ← make optional
        try:

            cmd =f"echo '{password}' | sudo -S rtcwake -m mem -s 10"
            
            try:
                output, error, exit_status = self.platform_obj.exec_cmd(cmd, "ssh")
            except Exception:
                output, error, exit_status = "", "", 0 # SSH drops on sleep

            if exit_status != 0:
                self.platform_obj.logger.error(f"Failed to sleep. Error: {error}")
            return output, error, exit_status

        except Exception as e:
            self.platform_obj.logger.error(f"Sleep error: {str(e)}", exc_info=True)
            return "", str(e), -1
            
    def shutdown(self,password=None):
        try:
          
            output, error, exit_status = self.platform_obj.exec_cmd(f"echo '{password}' | sudo -S /sbin/shutdown -h now", "ssh")
            
            if exit_status != 0:
                self.platform_obj.logger.error(f"Failed to shutdown the system. Error: {error}")
            return output, error, exit_status
        
        except Exception as e:
            self.platform_obj.logger.error(f"An error occurred while trying to shutdown the system: {str(e)}", exc_info=True)
            return "", str(e), -1

    
# cpu_win.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase
from framework.utilities.os_utils.cpu.cpu_base import CPUBase

class CPUWindows(CPUBase):
    def get_cpu_count(self):
        try:
            output,error,exit_status = self.platform_obj.exec_cmd("wmic cpu get NumberOfCores","ssh")
            if exit_status != 0:
                self.logger.error(f"CPU core count failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.logger.error(f"CPU core count exception: {e}", exc_info=True)
            return "", str(e), -1
        
    
    def monitor_cpu_usage(self):
        try:
            output, error, exit_status = self.platform_obj.exec_cmd('typeperf "\\Processor(_Total)\\% Processor Time"', "ssh")
            if exit_status != 0:
                self.logger.error(f"CPU Usage Monitoring failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.logger.error(f"CPU Usage Monitoring exception: {e}", exc_info=True)
            return "", str(e), -1

    def test_cpu_stress(self, timeout="60s"):
        try:
            output, error, exit_status = self.platform_obj.exec_cmd('powershell -command "while ($true) { 1 + 1 }"', "ssh")
            if exit_status != 0:
                self.logger.error(f"CPU Stress Testing failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.logger.error(f"CPU Stress Testing exception: {e}", exc_info=True)
            return "", str(e), -1

    def check_cpu_frequency(self):
        try:
            output, error, exit_status = self.platform_obj.exec_cmd("wmic cpu get name,CurrentClockSpeed,MaxClockSpeed", "ssh")
            if exit_status != 0:
                self.logger.error(f"CPU Frequency Scaling Check failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.logger.error(f"CPU Frequency Scaling Check exception: {e}", exc_info=True)
            return "", str(e), -1

    def get_cpu_vendor(self):
        try:
            output, error, exit_status = self.platform_obj.exec_cmd("wmic cpu get manufacturer", "ssh")
            if exit_status != 0:
                self.logger.error(f"CPU Vendor Detection failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.logger.error(f"CPU Vendor Detection exception: {e}", exc_info=True)
            return "", str(e), -1
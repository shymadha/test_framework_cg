# cpu_linux.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase
from framework.utilities.os_utils.cpu.cpu_base import CPUBase

class CPULinux(CPUBase):
    def get_cpu_count(self):
        output,error,exit_staus = self.platform_obj.exec_cmd("nproc","ssh")
        return output,error,exit_staus
    
    def monitor_cpu_usage(self):
        try:
            output, error, exit_status = self.platform_obj.exec_cmd("htop", "ssh")
            if exit_status != 0:
                self.logger.error(f"CPU Usage Monitoring failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.logger.error(f"CPU Usage Monitoring exception: {e}", exc_info=True)
            return "", str(e), -1

    def test_cpu_stress(self, timeout="60s"):
        try:
            output, error, exit_status = self.platform_obj.exec_cmd(f"stress-ng --cpu 1 --cpu-method all --timeout {timeout}", "ssh")
            if exit_status != 0:
                self.logger.error(f"CPU Stress Testing failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.logger.error(f"CPU Stress Testing exception (e.g., Timeout or OOM): {e}", exc_info=True)
            return "", str(e), -1

    def check_cpu_frequency(self):
        try:
            output, error, exit_status = self.platform_obj.exec_cmd("sysbench cpu --threads=1 run", "ssh")
            if exit_status != 0:
                self.logger.error(f"CPU Frequency Scaling Check failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.logger.error(f"CPU Frequency Scaling Check exception: {e}", exc_info=True)
            return "", str(e), -1

    def get_cpu_vendor(self):
        try:
            # On Linux, lscpu is the standard way to get vendor info
            output, error, exit_status = self.platform_obj.exec_cmd("lscpu | grep 'Vendor ID'", "ssh")
            if exit_status != 0:
                self.logger.error(f"CPU Vendor Detection failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.logger.error(f"CPU Vendor Detection exception: {e}", exc_info=True)
            return "", str(e), -1

    

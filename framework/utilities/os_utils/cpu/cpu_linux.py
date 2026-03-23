# cpu_linux.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase
from framework.utilities.os_utils.cpu.cpu_base import CPUBase

class CPULinux(CPUBase):
    def get_cpu_count(self):
        try:
            output,error,exit_status = self.platform_obj.exec_cmd("nproc","ssh")
            if exit_status != 0:
                self.platform_obj.logger.error(f"CPU Core count error: {error}")
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(f"CPU Core count exception: {e}", exc_info=True)
            return "", str(e), -1
       
    
    def monitor_cpu_usage(self):
        try:
            output, error, exit_status = self.platform_obj.exec_cmd("top -b -n 1 | grep 'Cpu(s)'", "ssh")
        
            if exit_status != 0:
                self.platform_obj.logger.error(f"CPU Usage Monitoring failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(f"CPU Usage Monitoring exception: {e}", exc_info=True)
            return "", str(e), -1

    def test_cpu_stress(self, timeout="10s"):
        try:
            # Extract number from timeout
            import re
            match = re.search(r'\d+', str(timeout))
            seconds = int(match.group(0)) if match else 10
           
            # Using a python one-liner to stress the CPU for the given duration
            stress_cmd = f"python3 -c \"import time; end=time.time()+{seconds}; all(1+1 for _ in iter(lambda: time.time()<end, False))\""
            output, error, exit_status = self.platform_obj.exec_cmd(stress_cmd, "ssh")
           
            if exit_status != 0:
                self.logger.error(f"CPU Stress Testing failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.logger.error(f"CPU Stress Testing exception: {e}", exc_info=True)
            return "", str(e), -1
 
    def check_cpu_frequency(self):
        try:
            # Using lscpu (standard Linux tool) to detect frequency
            output, error, exit_status = self.platform_obj.exec_cmd("lscpu | grep 'MHz'", "ssh")
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
                self.platform_obj.logger.error(f"CPU Vendor Detection failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(f"CPU Vendor Detection exception: {e}", exc_info=True)
            return "", str(e), -1

    

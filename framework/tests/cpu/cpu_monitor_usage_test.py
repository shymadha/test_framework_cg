import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project root BEFORE any framework imports
current = Path(__file__).resolve()

for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.tests.base_test import BaseTest
from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI

class CpuMonitorUsageTest(BaseTest):
    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for CpuMonitorUsageTest")

    def do_test(self):
        self.logger.info("Running CPU Monitor Usage Test")
        cpu_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = cpu_obj.cpu.monitor_cpu_usage()
        
        self.logger.info(f"Monitor Usage Output: {output}")
        
        if exit_status == 0:
            self.result.set_result(True, "Successfully retrieved CPU usage")
        else:
            self.result.set_result(False, f"CPU usage test failed: {error}")
            
        return exit_status

if __name__ == "__main__":
    test = CpuMonitorUsageTest()
    test.run()

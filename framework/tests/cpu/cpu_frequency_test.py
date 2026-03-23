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

#from framework.tests.base_test import BaseTest
#from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI
import argparse
from framework.core.test_engine import TestEngine
from framework.core.user_input_parser import ParseUserInput
from tests.base_test import BaseTest
from core.testbed_utils import TestbedUtils
from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI

class CpuFrequencyTest(BaseTest):
    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for CpuFrequencyTest")

    def do_test(self):
        self.logger.info("Running CPU Frequency Test")
        cpu_obj = OSBaseAPI(self.platform_obj)
        
        output, error, exit_status = cpu_obj.cpu.check_cpu_frequency()
        
        self.logger.info(f"Frequency Test Output: {output}")
        
        if exit_status == 0:
            self.result.set_result(True, "Successfully retrieved CPU frequency")
        else:
            self.result.set_result(False, f"CPU frequency scaling test failed: {error}")
            
        return exit_status

if __name__ == "__main__":
    test = CpuFrequencyTest()
    test.run()

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

# from framework.tests.base_test import BaseTest
# from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI
# from framework.core.testbed_utils import TestbedUtils
import argparse
from framework.core.test_engine import TestEngine
from framework.core.user_input_parser import ParseUserInput
from tests.base_test import BaseTest
from core.testbed_utils import TestbedUtils
from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI

class CpuStressTest(BaseTest):
    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for CpuStressTest")
        testbed_utils = TestbedUtils(self.user_input.args.config)
        self.timeout = testbed_utils.get_value("timeout")
        self.logger.info(f"The timeout is {self.timeout}")

    def do_test(self):
        self.logger.info("Running CPU Stress Test")
        cpu_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = cpu_obj.cpu.test_cpu_stress(self.timeout)
        
        self.logger.info(f"Stress Test Output: {output}")
        
        if exit_status == 0:
            self.result.set_result(True, "Successfully ran CPU stress test")
        else:
            self.result.set_result(False, f"CPU stress test failed: {error}")
            
        return exit_status

if __name__ == "__main__":
    test = CpuStressTest()
    test.run()

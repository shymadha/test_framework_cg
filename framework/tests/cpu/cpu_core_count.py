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
 
import argparse
from framework.core.test_engine import TestEngine
from framework.core.user_input_parser import ParseUserInput
from tests.base_test import BaseTest
from core.testbed_utils import TestbedUtils

class CpuCoreCountTest(BaseTest):
    def pre_test(self):
        self.logger.info("Executing pre-test for CpuCoreCount")
        testbed_utils = TestbedUtils(self.user_input.args.config)
        self.min_cores =testbed_utils.get_value("min_cores")
        print(f"The min_cores is {self.min_cores}")
        
    def do_test(self):
        self.logger.info("Running CPU Core Count Test")
        output,error,exit_status = self.platform_obj.test_interface_obj.execute("nproc")
        #xecute("nproc")
        print(f"The test ouput is {output}")
        if output and int(output) >= self.min_cores:
            self.result.set_result(True, "Valid core count")
        else:
            self.result.set_result(False, "Invalid core count")
            
if __name__ == "__main__":
    test = CpuCoreCountTest()
    test.run()
    
import sys
import os
from pathlib import Path

current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.tests.base_test import BaseTest
from framework.core.testbed_utils import TestbedUtils
from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI


class MemoryStressTest(BaseTest):
    """
    Test case for RAM Stress Test (MEM-003).
    """

    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for MemoryStress Test")
        testbed_utils = TestbedUtils(self.user_input.args.config)
        self.timeout_sec = testbed_utils.get_value("memory_stress_timeout") or 5

    def do_test(self):
        self.logger.info(f"Running Memory Stress Test - {self.timeout_sec} seconds")

        os_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = os_obj.memory.stress_test(self.timeout_sec)
        
        final_output = output.strip()
        if not final_output and error.strip():
            final_output = error.strip()
            
        self.logger.info(f"Memory Stress Output:\n{final_output}")

        if exit_status == 0:
            self.result.set_result(True, "Memory Stress test succeeded")
        else:
            self.logger.error(f"Memory Stress test failed: {error}")
            self.result.set_result(False, "Memory Stress test failed")

        return exit_status

if __name__ == "__main__":
    test = MemoryStressTest()
    test.run()

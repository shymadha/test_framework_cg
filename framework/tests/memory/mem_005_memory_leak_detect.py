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


class MemoryLeakDetectTest(BaseTest):
    """
    Test case to output Memory Leak Detect (MEM-005).
    """

    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for MemoryLeakDetect Test")

    def do_test(self):
        self.logger.info("Running Memory Leak Detect Info Test")

        os_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = os_obj.memory.leak_detect()
        
        final_output = output.strip()
        if not final_output and error.strip():
            final_output = error.strip()
            
        self.logger.info(f"Memory Leak Detect Output:\n{final_output}")

        if exit_status == 0:
            self.result.set_result(True, "Memory Leak Detect test succeeded")
        else:
            self.logger.error(f"Memory Leak Detect test failed: {error}")
            self.result.set_result(False, "Memory Leak Detect test failed")

        return exit_status

if __name__ == "__main__":
    test = MemoryLeakDetectTest()
    test.run()
